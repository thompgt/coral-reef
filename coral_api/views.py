from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache
from django.conf import settings
import duckdb
from .model_loader import ModelLoader
import os
import hashlib


class SearchAnonThrottle(AnonRateThrottle):
    scope = "search_anon"


class SearchUserThrottle(UserRateThrottle):
    scope = "search_user"

class SemanticSearchView(APIView):
    """
    Search endpoint that vectorizes the user query and performs 
    cosine similarity search on DuckDB.
    """
    throttle_classes = [SearchAnonThrottle, SearchUserThrottle]

    @staticmethod
    def _error_response(http_status, code, message, details=None):
        """Return a consistent error payload for all API failures."""
        return Response(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {}
                }
            },
            status=http_status
        )

    @staticmethod
    def _cache_key(query_text, limit):
        raw_key = f"{query_text.lower()}|{limit}"
        digest = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
        return f"semantic_search:{digest}"

    def throttled(self, request, wait):
        return self._error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMIT_EXCEEDED",
            "Too many search requests. Please try again shortly.",
            {"wait_seconds": int(wait) if wait else None}
        )

    def get(self, request):
        query_text = request.query_params.get('q', '').strip()
        limit_raw = request.query_params.get('limit', 10)

        if not query_text:
            return self._error_response(
                status.HTTP_400_BAD_REQUEST,
                "MISSING_QUERY",
                "Query parameter 'q' is required.",
                {"parameter": "q"}
            )

        try:
            limit = int(limit_raw)
        except (TypeError, ValueError):
            return self._error_response(
                status.HTTP_400_BAD_REQUEST,
                "INVALID_LIMIT",
                "Query parameter 'limit' must be an integer.",
                {"parameter": "limit", "value": str(limit_raw)}
            )

        if limit < 1 or limit > 100:
            return self._error_response(
                status.HTTP_400_BAD_REQUEST,
                "INVALID_LIMIT_RANGE",
                "Query parameter 'limit' must be between 1 and 100.",
                {"parameter": "limit", "value": limit, "min": 1, "max": 100}
            )

        cache_key = self._cache_key(query_text, limit)
        cached_payload = cache.get(cache_key)
        if cached_payload:
            return Response(cached_payload, status=status.HTTP_200_OK)

        try:
            # 1. Load Singleton Model
            model = ModelLoader.get_model()
            
            # 2. Vectorize Query
            query_vector = model.encode([query_text])[0]
            
            # 3. Connect to DuckDB
            db_path = "coral_morph.db"
            if not os.path.exists(db_path):
                return self._error_response(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DATABASE_NOT_FOUND",
                    "Search database file was not found.",
                    {"path": db_path}
                )
            
            con = duckdb.connect(db_path)
            
            # 4. Perform Similarity Search
            sql = """
            SELECT 
                species_name, 
                color, 
                habitat, 
                abundance,
                list_cosine_similarity(embedding, ?) AS score,
                description
            FROM corals
            ORDER BY score DESC
            LIMIT ?
            """
            
            results = con.execute(sql, [query_vector.tolist(), limit]).fetchdf()
            con.close()
            
            # 5. Format Response
            search_results = []
            for _, row in results.iterrows():
                search_results.append({
                    "species_name": row['species_name'],
                    "color": row['color'],
                    "habitat": row['habitat'],
                    "abundance": row['abundance'],
                    "score": round(float(row['score']), 4),
                    "description": row['description']
                })
                
            response_payload = {
                "query": query_text,
                "results": search_results
            }
            cache_timeout = getattr(settings, "SEARCH_CACHE_TTL", 300)
            cache.set(cache_key, response_payload, timeout=cache_timeout)
            return Response(response_payload, status=status.HTTP_200_OK)

        except Exception as e:
            return self._error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "SEARCH_FAILED",
                "Unexpected error while processing search request.",
                {"reason": str(e)}
            )
