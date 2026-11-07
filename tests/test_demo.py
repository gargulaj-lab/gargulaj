"""Integration checks against isolated accounts and synthetic railway data."""
import os
from pathlib import Path
import tempfile
import unittest

_temporary = tempfile.TemporaryDirectory()
os.environ["DATABASE_FILE"] = str(Path(_temporary.name) / "test.db")
os.environ["SESSION_SECRET"] = "isolated-integration-test-secret"
os.environ.pop("RAIL_GRAPH_FILE", None)
os.environ.pop("STATION_GRAPH_FILE", None)
os.environ.pop("RAIL_STATIC_DIR", None)

from fastapi.testclient import TestClient
from app.main import app


class DemoFlowTest(unittest.TestCase):
    def test_journey_statistics_and_account_isolation(self):
        with TestClient(app) as first, TestClient(app) as second:
            self.assertEqual(first.get("/").status_code, 200)
            self.assertEqual(first.get("/register").status_code, 200)
            self.assertIn("error", first.get("/api/journeys").json())
            for client, email in [(first, "first@example.test"), (second, "second@example.test")]:
                registered = client.post("/register", data={"email": email, "password": "Demo-test-123!", "password_confirm": "Demo-test-123!"})
                self.assertEqual(registered.status_code, 200)
                logged_in = client.post("/login", data={"email": email, "password": "Demo-test-123!"})
                self.assertEqual(logged_in.status_code, 200)
                self.assertIn("Ukázková síť", logged_in.text)
            network = first.get("/static/railway_network_multi.geojson")
            self.assertEqual(network.status_code, 200)
            self.assertEqual(network.json()["type"], "FeatureCollection")
            route = first.get("/api/route", params=[("start", "Demo Západ"), ("end", "Demo Východ"), ("via", "Demo Střed")]).json()
            self.assertEqual(route["distance_km"], 5.0)
            self.assertEqual(route["edge_ids"], [0, 1])
            journey = {"journey_date": "2026-01-01", "start": "Demo Západ", "end": "Demo Východ", "via": ["Demo Střed"]}
            ids = []
            for _ in range(2):
                saved = first.post("/api/journeys", json=journey).json()
                self.assertTrue(saved["success"])
                ids.append(saved["journey_id"])
            stats = first.get("/api/stats").json()
            self.assertEqual(stats["total_km"], 10.0)
            self.assertEqual(stats["unique_km"], 5.0)
            travelled = first.get("/api/network/travelled").json()
            self.assertEqual([e["journey_count"] for e in travelled["edges"]], [2, 2])
            self.assertEqual(second.get("/api/journeys").json()["count"], 0)
            self.assertIn("error", second.delete(f"/api/journeys/{ids[0]}").json())
            for identifier in ids:
                self.assertTrue(first.delete(f"/api/journeys/{identifier}").json()["success"])
            self.assertEqual(first.get("/api/stats").json()["unique_km"], 0)
            self.assertIn("error", first.get("/api/route", params={"start": "Missing", "end": "Demo Východ"}).json())


if __name__ == "__main__":
    unittest.main()
