from django.test import TestCase, Client
from django.urls import reverse
import json

class SearchApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.search_url = reverse('semantic_search')

    def test_empty_query(self):
        """Test that an empty query returns a 400 error."""
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "MISSING_QUERY")
        self.assertIn("message", data["error"])

    def test_invalid_limit(self):
        """Test that non-numeric limit returns a 400 error."""
        response = self.client.get(self.search_url, {'q': 'blue coral', 'limit': 'abc'})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], "INVALID_LIMIT")

    def test_valid_search(self):
        """Test that a valid query returns search results."""
        response = self.client.get(self.search_url, {'q': 'blue shallow coral', 'limit': 3})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 3)
        self.assertEqual(data["query"], "blue shallow coral")
        # Ensure first result has expected keys
        first_result = data["results"][0]
        self.assertIn("species_name", first_result)
        self.assertIn("score", first_result)
        self.assertIn("color", first_result)
        self.assertIn("habitat", first_result)
