import json, re, tempfile, unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import app as app_module
from app import app
from radar import canonical_url, evidence_rows, finalize_evidence, export_markdown
from reviews import (
    ReviewCorrupt, ReviewError, evidence_id, evidence_fingerprint, build_review,
    present_review, save_review, load_reviews, attach_reviews, next_check_brief, review_bucket,
)

def lead(url="https://docs.pydantic.dev/migration", title="Guide", snippet="alpha", query="q-one", retrieved="2026-01-01T00:00:00+00:00", package="pydantic", pin="1.10.0", cached=False):
    rows = evidence_rows({"query": query, "retrieved_at": retrieved, "results": [{"title": title, "link": url, "snippet": snippet}]}, package, pin, cached=cached)
    return finalize_evidence(rows)[0]

def fields(**overrides):
    base = {"decision": "keep", "note": "Read the guide.", "version_applicability": "not_established", "applicability_url": "", "applicability_rationale": ""}
    base.update(overrides)
    return base

class IdentityTests(unittest.TestCase):
    def test_id_uses_package_and_canonical_not_order(self):
        payload = {"query": "q", "retrieved_at": "t", "results": [
            {"title": "Docs", "link": "https://docs.pydantic.dev/a?version=1&utm_source=ad", "snippet": "one"},
            {"title": "Other", "link": "https://docs.pydantic.dev/a?version=2", "snippet": "two"},
        ]}
        rows = finalize_evidence(evidence_rows(payload, "pydantic", "1"))
        first, second = rows[0]["canonical"], rows[1]["canonical"]
        self.assertNotEqual(evidence_id("pydantic", first), evidence_id("pydantic", second))
        self.assertEqual(evidence_id("pydantic", canonical_url("https://docs.pydantic.dev/a?version=1&utm_source=ad")), evidence_id("pydantic", first))
        self.assertNotEqual(evidence_id("pydantic", first), evidence_id("fastapi", first))
        by_url = {row["url"]: evidence_id(row["package"], row["canonical"]) for row in rows}
        by_url_reversed = {row["url"]: evidence_id(row["package"], row["canonical"]) for row in reversed(rows)}
        self.assertEqual(by_url, by_url_reversed)

    def test_fingerprint_tracks_title_snippet_and_source_only(self):
        row = lead()
        same = lead(query="other-query", retrieved="2026-02-02T00:00:00+00:00", cached=True, url="https://docs.pydantic.dev/migration?utm_source=x")
        self.assertEqual(evidence_fingerprint(row), evidence_fingerprint(same))
        changed = lead(snippet="beta")
        self.assertNotEqual(evidence_fingerprint(row), evidence_fingerprint(changed))
        retitled = lead(title="Renamed")
        self.assertNotEqual(evidence_fingerprint(row), evidence_fingerprint(retitled))

    def test_reorder_and_tracking_do_not_rereview_but_snippet_pin_and_status_do(self):
        from radar import evidence_rows, finalize_evidence
        link = "https://docs.pydantic.dev/migration"
        merged = finalize_evidence(evidence_rows({"query": "q-one", "retrieved_at": "t1", "results": [{"title": "Guide", "link": link, "snippet": "beta"}]}, "pydantic", "1.10.0") + evidence_rows({"query": "q-two", "retrieved_at": "t2", "results": [{"title": "Guide", "link": link, "snippet": "alpha"}]}, "pydantic", "1.10.0"))[0]
        swapped = deepcopy(merged)
        swapped["provenance"] = list(reversed(swapped["provenance"]))
        self.assertEqual(evidence_fingerprint(merged), evidence_fingerprint(swapped))
        tracked = lead(url=link + "?utm_source=ad&gclid=1")
        plain = lead(url=link)
        self.assertEqual(evidence_id(plain["package"], plain["canonical"]), evidence_id(tracked["package"], tracked["canonical"]))
        record = build_review(plain, fields(version_applicability="reviewer_says_applicable", applicability_url="https://example.com/source", applicability_rationale="Checked the page."), now="2026-10-11T12:00:00+00:00")
        self.assertFalse(present_review(tracked, record)["needs_rereview"])
        self.assertEqual(record["updated_at"], "2026-10-11T12:00:00+00:00")
        self.assertEqual(record["evidence_pin"], "1.10.0")
        self.assertEqual(record["evidence_status"], "UNVERIFIED: search snippet only")
        changed = deepcopy(merged)
        changed["provenance"][0]["snippet"] = "gamma"
        self.assertTrue(present_review(changed, build_review(merged, fields(), now="2026-10-11T12:00:00+00:00"))["needs_rereview"])
        moved = lead(url="https://docs.pydantic.dev/other-page")
        self.assertNotEqual(evidence_id(plain["package"], plain["canonical"]), evidence_id(moved["package"], moved["canonical"]))
        synthetic = deepcopy(plain)
        synthetic["status"] = "SYNTHETIC FIXTURE"
        synthetic_record = build_review(synthetic, fields(version_applicability="reviewer_says_applicable", applicability_url="https://example.com/source", applicability_rationale="Fixture only."), now="2026-10-11T12:00:00+00:00")
        reused = present_review(plain, synthetic_record)
        self.assertTrue(reused["needs_rereview"])
        self.assertEqual(reused["bucket"], "unresolved")
        self.assertEqual(reused["applicability_for_current_evidence"], "not established")
        self.assertEqual(reused["evidence_status"], "SYNTHETIC FIXTURE")
        later_pin = lead(pin="2.0.0")
        pinned = present_review(later_pin, record)
        self.assertTrue(pinned["needs_rereview"])
        self.assertEqual(pinned["bucket"], "unresolved")
        self.assertEqual(pinned["applicability_for_current_evidence"], "not established")
        self.assertEqual(pinned["version_applicability"], "reviewer_says_applicable")
        with self.assertRaises(ReviewError):
            build_review(plain, fields(decision="resolved"))

    def test_keep_is_not_verification_and_defaults_are_unreviewed(self):
        row = lead(snippet="discussed 1.10.0 today", url="https://example.com/n")
        view = present_review(row, None)
        self.assertEqual(view["decision"], "unreviewed")
        self.assertEqual(view["version_applicability"], "not_established")
        self.assertEqual(view["note"], "")
        self.assertEqual(view["bucket"], "unresolved")
        self.assertFalse(view["saved"])
        record = build_review(row, fields(), now="2026-10-11T12:00:00+00:00")
        self.assertNotIn(row["provenance"][0]["snippet"], json.dumps(record))
        self.assertEqual(record["version_applicability"], "not_established")
        self.assertEqual(present_review(row, record)["bucket"], "kept")
        unsure = build_review(row, fields(decision="unsure"), now="2026-10-11T12:00:00+00:00")
        self.assertEqual(review_bucket(present_review(row, unsure)), "unresolved")

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.row = lead()

    def test_round_trip_and_missing_file_is_quiet(self):
        record = build_review(self.row, fields(note="a" * 2000), now="2026-10-11T12:00:00+00:00")
        save_review(self.directory, record)
        loaded, warnings = load_reviews(self.directory)
        self.assertEqual(warnings, [])
        self.assertEqual(loaded[record["id"]]["note"], "a" * 2000)
        self.assertEqual(loaded[record["id"]]["evidence_retrieved_at"], ["2026-01-01T00:00:00+00:00"])
        self.assertFalse(list(self.directory.glob(".*.tmp")))
        empty, quiet = load_reviews(self.directory / "missing")
        self.assertEqual(empty, {})
        self.assertEqual(quiet, [])

    def test_note_cap_and_applicability_requirements(self):
        with self.assertRaises(ReviewError):
            build_review(self.row, fields(note="a" * 2001))
        with self.assertRaises(ReviewError):
            build_review(self.row, fields(version_applicability="reviewer_says_applicable", applicability_rationale="because"))
        with self.assertRaises(ReviewError):
            build_review(self.row, fields(version_applicability="reviewer_says_not_applicable", applicability_url="https://example.com/a", applicability_rationale="   "))
        for bad in ("javascript:alert(1)", "https://user:secret@example.com/a", "ftp://example.com/a", "https://"):
            with self.assertRaises(ReviewError):
                build_review(self.row, fields(version_applicability="reviewer_says_applicable", applicability_url=bad, applicability_rationale="checked the page"))
        saved = build_review(self.row, fields(version_applicability="reviewer_says_applicable", applicability_url="https://docs.pydantic.dev/latest/migration/", applicability_rationale="Guide row lists dict() to model_dump()."), now="2026-10-11T12:00:00+00:00")
        self.assertEqual(saved["applicability_url"], "https://docs.pydantic.dev/latest/migration/")
        self.assertNotIn("secret", json.dumps(saved))

    def test_corrupt_file_is_not_overwritten(self):
        record = build_review(self.row, fields(), now="2026-10-11T12:00:00+00:00")
        path = self.directory / f"{record['id']}.json"
        path.write_text("{", encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaises(ReviewCorrupt):
            save_review(self.directory, record)
        self.assertEqual(path.read_bytes(), before)
        loaded, warnings = load_reviews(self.directory)
        self.assertEqual(loaded, {})
        self.assertIn("left unchanged", warnings[0])
        self.assertEqual(path.read_bytes(), before)

    def test_evidence_change_retains_decision_and_absent_lead_stays(self):
        record = build_review(self.row, fields(note="check the table"), now="2026-10-11T12:00:00+00:00")
        save_review(self.directory, record)
        changed = lead(title="Guide revised")
        view = present_review(changed, record)
        self.assertTrue(view["needs_rereview"])
        self.assertEqual(view["decision"], "keep")
        self.assertEqual(view["note"], "check the table")
        self.assertEqual(view["reviewed_against"], ["2026-01-01T00:00:00+00:00"])
        self.assertEqual(view["bucket"], "unresolved")
        other = lead(url="https://example.com/other", title="Elsewhere", snippet="pydantic notes")
        attach_reviews([other], self.directory)
        self.assertEqual(json.loads((self.directory / f"{record['id']}.json").read_text())["decision"], "keep")
        again = build_review(changed, fields(note="check the table"), now="2026-10-11T13:00:00+00:00")
        save_review(self.directory, again)
        self.assertFalse(present_review(changed, again)["needs_rereview"])
        self.assertEqual(present_review(changed, again)["bucket"], "kept")

    def test_brief_keeps_human_decision_apart_from_snippets(self):
        record = build_review(self.row, fields(version_applicability="reviewer_says_not_applicable", applicability_url="https://example.com/source", applicability_rationale="Page is about v2 only."), now="2026-10-11T12:00:00+00:00")
        annotated, _ = attach_reviews([self.row], self.directory)
        annotated[0]["review"] = present_review(self.row, record)
        text = next_check_brief(annotated)
        self.assertIn("worth investigating", text)
        self.assertIn("reviewer says not applicable", text)
        self.assertIn("reviewer-entered assessment, not automatic verification", text)
        self.assertIn("UNVERIFIED: search snippet only", text)
        self.assertIn("q-one", text)
        self.assertIn("alpha", text)
        self.assertIn("2026-01-01T00:00:00+00:00", text)
        self.assertIn("Pin applicability: not established", text)
        stale = present_review(lead(title="Changed"), record)
        brief = next_check_brief([{**lead(title="Changed"), "review": stale}])
        self.assertIn("needs re-review: evidence changed", brief)
        self.assertIn("## Unresolved (1)", brief)
        self.assertIn("The previous decision and note are retained.", brief)
        self.assertIn("Next check:", text)
        self.assertIn("Export section: reviewed-kept", text)
        self.assertIn("q-one", text)
        escaped = deepcopy(self.row)
        escaped["review"] = present_review(self.row, build_review(self.row, fields(note="## injected\nWorth a look <note>"), now="2026-10-11T12:00:00+00:00"))
        literal = next_check_brief([escaped])
        self.assertNotRegex(literal, r"(?m)^## injected")
        self.assertIn("Worth a look <note>", literal)
        self.assertIn("\\## injected", literal)

    def test_failed_replace_and_source_change_do_not_overwrite_or_resolve(self):
        record = build_review(self.row, fields(), now="2026-10-11T12:00:00+00:00")
        save_review(self.directory, record)
        path = self.directory / f"{record['id']}.json"
        before = path.read_bytes()
        replacement = build_review(self.row, fields(decision="dismiss"), now="2026-10-11T13:00:00+00:00")
        with patch("reviews.os.replace", side_effect=OSError("disk")):
            with self.assertRaises(ReviewError):
                save_review(self.directory, replacement)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.directory.glob(".*.tmp")))
        other = lead(url="https://example.com/absent-source", title="Elsewhere", snippet="pydantic notes")
        annotated, _ = attach_reviews([other], self.directory)
        self.assertFalse(annotated[0]["review"]["saved"])
        self.assertEqual(json.loads(path.read_text())["decision"], "keep")
        self.assertIn(".reviews/", (Path(__file__).resolve().parents[1] / ".gitignore").read_text())

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_reviews = app_module.REVIEWS
        app_module.REVIEWS = Path(self.tmp.name)
        self.addCleanup(setattr, app_module, "REVIEWS", self.old_reviews)
        self.reports = dict(app_module.reports)
        self.scans = dict(app_module.scans)
        app_module.reports.clear()
        app_module.scans.clear()
        self.addCleanup(app_module.reports.update, self.reports)
        self.addCleanup(app_module.reports.clear)
        self.addCleanup(app_module.scans.update, self.scans)
        self.addCleanup(app_module.scans.clear)
        self.client = app.test_client()

    def scan(self):
        page = self.client.get("/")
        token = re.search(r'name="token" value="([^"]+)"', page.text)[1]
        result = self.client.post("/", data={"token": token, "requirements": "pydantic==1.10.0", "mode": "fixture"})
        self.assertEqual(result.status_code, 200)
        return token, result

    def test_fixture_queue_does_not_auto_keep_or_call_serpapi(self):
        with patch("urllib.request.urlopen") as call:
            token, result = self.scan()
        self.assertEqual(call.call_count, 0)
        self.assertIn("SYNTHETIC FIXTURE", result.text)
        self.assertIn("Pin applicability: not established", result.text)
        self.assertIn("unmatched leads", result.text)
        self.assertIn("Save review", result.text)
        self.assertIn('value="unreviewed" selected', result.text)
        self.assertNotIn('value="keep" selected', result.text)
        self.assertNotIn("onchange=", result.text)
        self.assertEqual(result.text.count("Save review"), 2)
        self.assertIn("All (2)", result.text)
        self.assertIn("Unresolved (2)", result.text)
        self.assertIn("Kept (0)", result.text)
        self.assertIn("Dismissed (0)", result.text)
        self.assertIn("Not saved yet.", result.text)
        self.assertEqual(list(Path(self.tmp.name).glob("*.json")), [])
        for query in ("site:docs.pydantic.dev pydantic 1.10.0 migration deprecation", "pydantic 1.10.0 security advisory release notes"):
            self.assertIn(query, result.text)
        self.assertNotIn("<script>", result.text)

    def test_save_persists_across_rerun_and_filters(self):
        token, result = self.scan()
        report = re.search(r'href="/export/([^"]+)"', result.text)[1]
        migration = evidence_id("pydantic", canonical_url("https://example.invalid/migration"))
        saved = self.client.post("/review", data={
            "token": token, "report": report, "queue": "all", "evidence_id": migration,
            "decision": "keep", "note": "Worth a look <note>", "version_applicability": "not_established",
            "applicability_url": "", "applicability_rationale": "",
        }, follow_redirects=True)
        self.assertIn("Review saved for Synthetic migration documentation lead.", saved.text)
        self.assertIn("Saved Keep", saved.text)
        self.assertIn("Reviewed against retrieval SYNTHETIC: no real retrieval", saved.text)
        self.assertIn("&lt;note&gt;", saved.text)
        self.assertNotIn("Worth a look <note>", saved.text)
        self.assertIn("Kept (1)", saved.text)
        self.assertIn("Unresolved (1)", saved.text)
        kept = self.client.get(f"/?report={report}&queue=kept")
        self.assertIn("Synthetic migration documentation lead", kept.text)
        self.assertNotIn("Synthetic security investigation lead", kept.text)
        evidence = self.client.get(f"/export/{report}").text
        self.assertNotIn("Worth a look", evidence)
        self.assertIn("SYNTHETIC FIXTURE", evidence)
        brief = self.client.get(f"/brief/{report}").text
        self.assertIn("Worth a look <note>", brief)
        self.assertIn("SYNTHETIC FIXTURE", brief)
        self.assertIn("worth investigating", brief)
        self.assertIn("## Kept for a next check (1)", brief)
        self.assertIn("## Unresolved (1)", brief)
        rerun_token = re.search(r'name="token" value="([^"]+)"', saved.text)[1]
        with patch("urllib.request.urlopen") as call:
            rerun = self.client.post("/", data={"token": rerun_token, "requirements": "pydantic==1.10.0", "mode": "fixture"})
        self.assertEqual(call.call_count, 0)
        self.assertIn("Saved Keep", rerun.text)
        self.assertIn("Reviewed against retrieval SYNTHETIC: no real retrieval", rerun.text)
        self.assertNotIn("needs re-review: evidence changed", rerun.text)

    def test_applicability_csrf_and_evidence_change(self):
        token, result = self.scan()
        report = re.search(r'href="/export/([^"]+)"', result.text)[1]
        migration = evidence_id("pydantic", canonical_url("https://example.invalid/migration"))
        denied = self.client.post("/review", data={"report": report, "evidence_id": migration, "decision": "keep"})
        self.assertIn("Invalid form token", denied.text)
        self.assertEqual(list(Path(self.tmp.name).glob("*.json")), [])
        missing = self.client.post("/review", data={
            "token": token, "report": report, "queue": "all", "evidence_id": migration,
            "decision": "keep", "note": "n", "version_applicability": "reviewer_says_applicable",
            "applicability_url": "", "applicability_rationale": "I read a page.",
        })
        self.assertIn("requires an http or https source URL", missing.text)
        self.assertEqual(list(Path(self.tmp.name).glob("*.json")), [])
        self.assertIn('value="keep" selected', missing.text)
        ok = self.client.post("/review", data={
            "token": token, "report": report, "queue": "all", "evidence_id": migration,
            "decision": "dismiss", "note": "Third-party page.", "version_applicability": "reviewer_says_not_applicable",
            "applicability_url": "https://example.com/checked?id=1&id=2", "applicability_rationale": "The page does not mention this pin.",
        }, follow_redirects=True)
        self.assertIn("Saved Dismiss", ok.text)
        self.assertIn("reviewer says not applicable", ok.text)
        self.assertIn("https://example.com/checked?id=1&amp;id=2", ok.text)
        body = json.loads((Path(self.tmp.name) / f"{migration}.json").read_text())
        body["fingerprint"] = "a" * 64
        (Path(self.tmp.name) / f"{migration}.json").write_text(json.dumps(body), encoding="utf-8")
        stale = self.client.get(f"/?report={report}&queue=unresolved")
        self.assertIn("needs re-review: evidence changed", stale.text)
        self.assertIn("Previous decision retained: Dismiss", stale.text)
        self.assertIn("Third-party page.", stale.text)
        self.assertIn("Unresolved (2)", stale.text)
        kept = self.client.get(f"/?report={report}&queue=kept")
        self.assertNotIn("Synthetic migration documentation lead", kept.text)
        dismissed = self.client.get(f"/?report={report}&queue=dismissed")
        self.assertIn("Dismissed (0)", dismissed.text)
        reconfirmed = self.client.post("/review", data={
            "token": token, "report": report, "queue": "dismissed", "evidence_id": migration,
            "decision": "dismiss", "note": "Third-party page.", "version_applicability": "reviewer_says_not_applicable",
            "applicability_url": "https://example.com/checked?id=1&id=2", "applicability_rationale": "The page does not mention this pin.",
        }, follow_redirects=True)
        self.assertNotIn("needs re-review: evidence changed", reconfirmed.text)
        self.assertIn("Synthetic migration documentation lead", reconfirmed.text)
        self.assertIn("Dismissed (1)", reconfirmed.text)

    def test_corrupt_review_blocks_save_and_stays_visible(self):
        token, result = self.scan()
        report = re.search(r'href="/export/([^"]+)"', result.text)[1]
        migration = evidence_id("pydantic", canonical_url("https://example.invalid/migration"))
        path = Path(self.tmp.name) / f"{migration}.json"
        path.write_text("{", encoding="utf-8")
        page = self.client.get(f"/?report={report}")
        self.assertIn("left unchanged", page.text)
        self.assertIn("Not saved yet.", page.text)
        failed = self.client.post("/review", data={
            "token": token, "report": report, "queue": "all", "evidence_id": migration,
            "decision": "keep", "note": "new", "version_applicability": "not_established",
            "applicability_url": "", "applicability_rationale": "",
        })
        self.assertIn("left unchanged", failed.text)
        self.assertEqual(path.read_text(), "{")

    def test_evidence_export_still_lists_queries_after_review_ui(self):
        token, result = self.scan()
        link = re.search(r'href="(/export/[^"]+)"', result.text)[1]
        body = self.client.get(link).text
        self.assertIn("SYNTHETIC FIXTURE", body)
        self.assertIn("Unmatched leads", body)
        from radar import queries
        for query in queries("pydantic", "1.10.0"):
            self.assertIn(query, body)
        rows = finalize_evidence(evidence_rows({"query": "q", "retrieved_at": "t", "results": [{"title": "A", "link": "https://example.com/a", "snippet": "one"}]}, "pydantic", "1"))
        self.assertNotIn("Reviewer note", export_markdown(rows))
