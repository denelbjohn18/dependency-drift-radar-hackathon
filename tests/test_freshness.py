import hashlib, json, os, re, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

from app import app
from radar import (
    RadarError, evidence_rows, export_markdown, fetch_search, finalize_evidence,
    parse_requirements, queries, version_note,
)
from reviews import attach_reviews, build_review, next_check_brief, present_review, save_review


def _fields(**overrides):
    base = {
        "decision": "keep", "note": "Look at the source.", "version_applicability": "reviewer_says_applicable",
        "applicability_url": "https://example.com/src", "applicability_rationale": "Reviewer-entered only.",
    }
    base.update(overrides)
    return base


class FreshnessTests(unittest.TestCase):
    def test_exact_pin_unpinned_input_and_range_rejection(self):
        with self.assertRaises(RadarError) as caught:
            parse_requirements("requests>=1")
        self.assertIn("not an exact installed version", str(caught.exception))
        self.assertIn("not established", str(caught.exception))
        self.assertIn("unknown", version_note(parse_requirements("requests")[0][1]))
        exact = evidence_rows(
            {"query": "q", "retrieved_at": "2020-01-01T00:00:00+00:00", "results": [{"title": "A", "link": "https://example.com/a", "snippet": "pydantic"}]},
            "pydantic", "1.10.0",
        )[0]
        self.assertIn("exact pin 1.10.0", exact["version_note"])
        self.assertEqual(exact["applicability"], "Pin applicability: not established")
        self.assertEqual(exact["status"], "UNVERIFIED: search snippet only")

    def test_cache_hit_does_not_replace_retrieval_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            query = "saved-query"
            path = Path(directory) / (hashlib.sha256(query.encode()).hexdigest() + ".json")
            path.write_text(json.dumps({
                "query": query, "retrieved_at": "2020-01-01T00:00:00+00:00",
                "results": [{"title": "T", "link": "https://example.com/t", "snippet": "ok"}],
            }))
            before = path.read_text()
            with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
                payload, cached = fetch_search(query, "DO_NOT_STORE", directory, {"used": 0})
            self.assertTrue(cached)
            self.assertEqual(payload["retrieved_at"], "2020-01-01T00:00:00+00:00")
            self.assertEqual(path.read_text(), before)
            self.assertNotIn("DO_NOT_STORE", before)

    def test_missing_and_invalid_timestamps_stay_unknown(self):
        missing = evidence_rows(
            {"query": "q", "results": [{"title": "A", "link": "https://example.com/a", "snippet": "pydantic"}]},
            "pydantic", "1.10.0",
        )[0]
        self.assertEqual(missing["provenance"][0]["retrieved_at"], "")
        self.assertEqual(missing["provenance"][0]["retrieval_label"], "unknown")
        self.assertEqual(missing["evidence_origin"], "unknown")
        self.assertEqual(missing["status"], "UNVERIFIED: search snippet only")
        invalid = evidence_rows(
            {"query": "q", "retrieved_at": "yesterday", "results": [{"title": "A", "link": "https://example.com/a", "snippet": "pydantic"}]},
            "pydantic", "1.10.0",
        )[0]
        self.assertEqual(invalid["provenance"][0]["retrieved_at"], "yesterday")
        self.assertEqual(invalid["provenance"][0]["retrieval_label"], "unknown")
        self.assertIn("Retrieval time: unknown", invalid["freshness_note"])
        self.assertNotIn("expiry", invalid["freshness_note"].lower().split("no expiry")[0])

    def test_mixed_provenance_export_is_not_one_origin(self):
        link = "https://example.com/mix"
        old = evidence_rows(
            {"query": "old-q", "retrieved_at": "2020-01-01T00:00:00+00:00", "results": [{"title": "M", "link": link, "snippet": "pydantic one"}]},
            "pydantic", "1.10.0", cached=True,
        )
        new = evidence_rows(
            {"query": "new-q", "retrieved_at": "2024-06-01T00:00:00+00:00", "results": [{"title": "M", "link": link, "snippet": "pydantic two"}]},
            "pydantic", "1.10.0", cached=False,
        )
        rows = finalize_evidence(old + new)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["evidence_origin"], "mixed")
        rows[0]["requested_mode"] = "live"
        text = export_markdown(rows)
        self.assertIn("Actual evidence origin: mixed", text)
        self.assertIn("2020-01-01T00:00:00+00:00", text)
        self.assertIn("2024-06-01T00:00:00+00:00", text)
        self.assertIn("old-q", text)
        self.assertIn("new-q", text)
        self.assertIn("UNVERIFIED: search snippet only", text)
        with tempfile.TemporaryDirectory() as directory:
            brief = next_check_brief(attach_reviews(rows, Path(directory))[0])
        self.assertIn("Actual evidence origin: mixed", brief)
        self.assertIn("Origin: cached search result", brief)
        self.assertIn("Origin: network retrieval", brief)

    def test_live_cache_hit_presentation_uses_sanitized_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            for query in queries("pydantic", "1.10.0"):
                path = cache / (hashlib.sha256(query.encode()).hexdigest() + ".json")
                path.write_text(json.dumps({
                    "query": query, "retrieved_at": "2020-01-01T00:00:00+00:00",
                    "results": [{"title": "Cached lead", "link": "https://example.com/cached-lead", "snippet": "pydantic migration"}],
                }))
            client = app.test_client()
            token = re.search(r'name="token" value="([^"]+)"', client.get("/").text)[1]
            with patch.dict(os.environ, {"SERPAPI_API_KEY": "fixture-key-not-a-real-secret"}), patch("app.CACHE", cache), patch("urllib.request.urlopen", side_effect=AssertionError("network")):
                page = client.post("/", data={"token": token, "requirements": "pydantic==1.10.0", "mode": "live"}).text
            self.assertIn("Requested mode: Live search", page)
            self.assertIn("Selecting Live is not proof a network call happened", page)
            self.assertIn("Actual evidence origin: cached search result", page)
            self.assertIn("2020-01-01T00:00:00+00:00", page)
            self.assertIn("UNVERIFIED: search snippet only", page)
            self.assertNotIn("Actual evidence origin: network retrieval", page)
            self.assertNotIn("fixture-key-not-a-real-secret", page)

    def test_live_without_key_is_not_a_completed_search(self):
        client = app.test_client()
        token = re.search(r'name="token" value="([^"]+)"', client.get("/").text)[1]
        with patch.dict(os.environ, {"SERPAPI_API_KEY": ""}):
            page = client.post("/", data={"token": token, "requirements": "pydantic==1.10.0", "mode": "live"}).text
        self.assertIn("Live mode was not run", page)
        self.assertNotIn("Actual evidence origin", page)

    def test_changed_pin_invalidates_saved_applicability(self):
        row = evidence_rows(
            {"query": "q", "retrieved_at": "2020-01-01T00:00:00+00:00", "results": [{"title": "A", "link": "https://example.com/pin", "snippet": "pydantic"}]},
            "pydantic", "1.10.0",
        )[0]
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            record = build_review(row, _fields(), now="2026-10-11T12:00:00+00:00")
            save_review(folder, record)
            stored = json.loads((folder / f"{record['id']}.json").read_text())
            other = evidence_rows(
                {"query": "q", "retrieved_at": "2020-01-01T00:00:00+00:00", "results": [{"title": "A", "link": "https://example.com/pin", "snippet": "pydantic"}]},
                "pydantic", "not pinned",
            )[0]
            view = present_review(other, stored)
            self.assertTrue(view["needs_rereview"])
            self.assertEqual(view["applicability_for_current_evidence"], "not established")
            self.assertIn("unknown", other["version_note"])
            self.assertEqual(other["status"], "UNVERIFIED: search snippet only")
