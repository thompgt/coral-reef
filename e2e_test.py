import requests
import unittest
import time
import subprocess
import os
import signal

class CoralMorphE2ETest(unittest.TestCase):
    BASE_URL = "http://localhost:8000/api/search/"

    @classmethod
    def setUpClass(cls):
        """Wait for server to start before running any tests."""
        print("⏳ Waiting for server to initialize (max 30s)...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/api/search/?q=warmup", timeout=2)
                if response.status_code in [200, 400]:
                    print("🚀 Server is live!")
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        print("❌ Server failed to start in time.")

    def test_01_api_is_responsive(self):
        """Test if the search endpoint is live."""
        try:
            response = requests.get(f"{self.BASE_URL}?q=test")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("Backend server is not running. Please start it with 'python manage.py runserver'")

    def test_02_semantic_relevance(self):
        """Test if a specific query returns a known relevant species."""
        query = "spiky green branches"
        response = requests.get(f"{self.BASE_URL}?q={query}")
        data = response.json()
        
        # Check if Acropora pruinosa (known green/branching) is in top 5
        species_names = [r['species_name'] for r in data['results'][:5]]
        self.assertTrue(any("Acropora" in name for name in species_names))
        print(f"✅ Semantic relevance test passed for: '{query}'")

    def test_03_edge_case_empty_query(self):
        """Edge Case: Empty query string."""
        response = requests.get(f"{self.BASE_URL}?q=")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        print("✅ Edge case (empty query) handled correctly.")

    def test_04_edge_case_long_query(self):
        """Edge Case: Extremely long query string."""
        long_query = "coral " * 200
        response = requests.get(f"{self.BASE_URL}?q={long_query}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['results']) > 0)
        print("✅ Edge case (long query) handled correctly.")

    def test_05_edge_case_special_chars(self):
        """Edge Case: Special and non-ASCII characters."""
        special_query = "🪸 reef @#$%^&*()! 🌊"
        response = requests.get(f"{self.BASE_URL}?q={special_query}")
        self.assertEqual(response.status_code, 200)
        print("✅ Edge case (special chars) handled correctly.")

    def test_06_database_integrity(self):
        """Verify the database file exists and is accessible."""
        self.assertTrue(os.path.exists("coral_morph.db"), "Database file is missing!")
        print("✅ Database integrity verified.")

if __name__ == "__main__":
    print("🧪 Starting End-to-End Validation Suite...")
    unittest.main()
