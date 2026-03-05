from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import duckdb
from .model_loader import ModelLoader
import os

class SemanticSearchView(APIView):
    """
    Search endpoint that vectorizes the user query and performs 
    cosine similarity search on DuckDB.
    """
    def get(self, request):
        query_text = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))

        if not query_text:
            return Response({"error": "Query 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Load Singleton Model
            model = ModelLoader.get_model()
            
            # 2. Vectorize Query
            query_vector = model.encode([query_text])[0]
            
            # 3. Connect to DuckDB
            db_path = "coral_morph.db"
            if not os.path.exists(db_path):
                return Response({"error": "Database file not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
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
                
            return Response({
                "query": query_text,
                "results": search_results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
