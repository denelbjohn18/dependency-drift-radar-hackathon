import re, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import app as app_module
from app import app
from radar import queries

class PageStructureTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(setattr, app_module, "REVIEWS", app_module.REVIEWS)
        app_module.REVIEWS = Path(tmp.name)
        self.client = app.test_client()

    def test_every_card_keeps_labelled_review_fields_and_caveats(self):
        page = self.client.get("/")
        token = re.search(r'name="token" value="([^"]+)"', page.text)[1]
        with patch("urllib.request.urlopen") as call:
            html = self.client.post("/", data={"token": token, "requirements": "pydantic==1.10.0", "mode": "fixture"}).text
        self.assertEqual(call.call_count, 0)
        for text in ('<label for="req">Python requirements (up to 5 packages)</label>', '<label for="mode">Run mode</label>',
                     "Search snippets are not proof.", "Requested mode: synthetic fixtures.",
                     "Actual evidence origin: synthetic fixture.", "Download Markdown", "Download next-check brief",
                     "Unresolved includes unreviewed leads", "Scope: package names and exact pins."):
            self.assertIn(text, html)
        for queue in ("all", "unresolved", "kept", "dismissed"):
            self.assertIn(f'name="queue" value="{queue}"', html)
        cards = html.split("<article")[1:]
        self.assertEqual(len(cards), 2)
        for card in cards:
            eid = re.search(r'name="evidence_id" value="([0-9a-f]{64})"', card)[1]
            for prefix, name, label in (("decision", "decision", "Decision"), ("note", "note", "Reviewer note"),
                                        ("applicability", "version_applicability", "Version applicability"),
                                        ("url", "applicability_url", "Applicability source URL"),
                                        ("rationale", "applicability_rationale", "Applicability rationale")):
                self.assertIn(f'<label for="{prefix}-{eid}">{label}</label>', card)
                self.assertRegex(card, rf'(id="{prefix}-{eid}"[^>]*name="{name}"|name="{name}"[^>]*id="{prefix}-{eid}")')
            for text in ("SYNTHETIC FIXTURE", "pydantic / 1.10.0", "Evidence origin: synthetic fixture.", "Installed version: exact pin 1.10.0.",
                         "Pin applicability: not established", "Freshness does not apply to a synthetic fixture.", "Heuristic cues:",
                         "Retrieved SYNTHETIC: no real retrieval", "Origin: synthetic fixture", "Not saved yet.", "<legend>Review this lead</legend>",
                         "Keep means worth investigating, not safe to upgrade or proven vulnerable.",
                         "Reviewer-entered assessment, not automatic verification.", "Save review"):
                self.assertIn(text, card)
            for q in queries("pydantic", "1.10.0"):
                self.assertIn(q, card)
