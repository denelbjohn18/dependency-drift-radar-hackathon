import hashlib, json, os, secrets, time
from pathlib import Path
from flask import Flask, render_template_string, request, session, Response, redirect
from radar import *
from reviews import (
    QUEUES, ReviewError, ReviewCorrupt, evidence_id, attach_reviews, save_review,
    build_review, apply_attempt, queue_counts, next_check_brief,
)
app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
ROOT = Path(__file__).parent
CACHE = ROOT / ".cache"
REVIEWS = ROOT / ".reviews"
# Process-wide ceiling protects repeated browser sessions. Restarting resets it.
quota = {"used": 0}
last_request = [0.0]
reports = {}
scans = {}
PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dependency Drift Radar</title>
<style>body{background:#111827;color:#e5e7eb;font:16px system-ui;max-width:1050px;margin:40px auto;padding:0 22px}h1{font-size:36px;margin-bottom:8px}p{line-height:1.6;color:#b9c7d9}.chip{background:#273549;padding:6px 12px;border-radius:15px;display:inline-block;font-size:13px}textarea,input[type=url]{width:100%;box-sizing:border-box;background:#1e293b;color:white;padding:16px;border:1px solid #46556b;border-radius:8px;font:15px monospace}button,.export{background:#84cc16;color:#122100;padding:12px 18px;border:0;border-radius:7px;font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block}select{padding:10px;margin:12px 12px 12px 0;color:white;background:#263348;border-radius:6px}article{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:18px;margin:16px 0}a{color:#a3e635;overflow-wrap:anywhere}blockquote{border-left:3px solid #64748b;padding-left:15px;margin-left:0;line-height:1.6}.warn{color:#fde68a}.meta{font-size:13px;color:#94a3b8}.err{border:1px solid #f87171;padding:14px}.saved{color:#bbf7d0}label{display:block;margin:22px 0 10px}fieldset{border:1px solid #334155;border-radius:8px;margin-top:14px}legend{padding:0 8px}.filters{margin:18px 0}.filters button{background:#273549;color:#e5e7eb}.filters button.on{outline:2px solid #a3e635}.exports a{margin-right:10px}</style>
<header><span class="chip">Local Python dependency research</span><h1>Dependency Drift Radar</h1><p>Find migration, deprecation and security leads for your pinned packages. Every lead keeps its source and search context. No invented CVEs. No automatic upgrades.</p></header>
<p class="warn">Search snippets are not proof. Verify the linked source and whether it applies to your installed version before acting.</p>
<form method="post"><input type="hidden" name="token" value="{{token}}"><label for="req">Python requirements (up to 5 packages)</label><textarea id="req" name="requirements" rows="5">{{text}}</textarea><label for="mode">Run mode</label><select name="mode" id="mode"><option value="fixture" {% if mode=='fixture' %}selected{% endif %}>Synthetic fixtures (no API / no spend)</option><option value="cache" {% if mode=='cache' %}selected{% endif %}>Saved cache only (no network call)</option><option value="live" {% if mode=='live' %}selected{% endif %}>Live SerpApi (uses free searches)</option></select><button>Find evidence leads</button></form>
<p class="meta">Process live attempts: {{used}} / 20. Max 10 per scan. Same queries use local cache. Server spaces requests 80 seconds apart for the free 50/hour throughput. Demo fixtures do not demonstrate live SerpApi use. Requested mode is not the evidence origin.</p>
{% if not key_set %}<p class="warn">This process has no search key. Live mode will not run, and this page will not present a completed live search.</p>{% endif %}
{% if error %}<p class="err" role="alert">{{error}}</p>{% endif %}
{% if saved_title %}<p class="saved" role="status">Review saved for {{saved_title}}.</p>{% endif %}
{% for warning in warnings %}<p class="warn" role="alert">{{warning}}</p>{% endfor %}
{% macro card(r, token, report_id, queue) %}<article><span class="chip">{{r.package}} / {{r.installed_pin}}</span><h3><a href="{{r.url}}" target="_blank" rel="noopener noreferrer">{{r.title}}</a></h3><p>{{r.version_note}}</p><p class="warn">{{r.status}}</p><p>{{r.evidence_origin_label}}</p><p class="meta">{{r.freshness_note}}</p><p>{{r.relevance}} | {{r.source_category}}</p><p class="warn">{{r.applicability}}</p><p>Heuristic cues: {{r.signals}}</p>{% for item in r.provenance %}<blockquote>{{item.snippet}}</blockquote><p class="meta">{{item.query}}<br>Retrieved {{item.retrieved_at}} | Retrieval time: {{item.retrieval_label}} | Cached: {{item.cached}} | Origin: {{item.origin}}</p>{% endfor %}
{% if r.review.saved %}<p class="saved">Saved {{r.review.decision_label}} at {{r.review.updated_at}}. {% if r.review.needs_rereview %}Version applicability for this evidence: not established until you save again. Previous assessment retained: {{r.review.applicability_label}}.{% else %}Version applicability: {{r.review.applicability_label}}. Reviewer-entered assessment, not automatic verification.{% endif %}</p><p class="meta">Reviewed against pin {{r.review.evidence_pin or "not stored"}}. Evidence status when saved: {{r.review.evidence_status or "not stored"}}. Reviewed against retrieval {% for t in r.review.reviewed_against %}{{t}}{% if not loop.last %}; {% endif %}{% endfor %}</p>{% else %}<p class="meta">Not saved yet.</p>{% endif %}
{% if r.review.needs_rereview %}<p class="warn">needs re-review: evidence changed</p><p>Previous decision retained: {{r.review.decision_label}}. The previous note stays in the form until you save this review again. Applicability for this evidence is not established until you save again.</p>{% endif %}
<form method="post" action="/review"><input type="hidden" name="token" value="{{token}}"><input type="hidden" name="report" value="{{report_id}}"><input type="hidden" name="queue" value="{{queue}}"><input type="hidden" name="evidence_id" value="{{r.review.id}}"><fieldset><legend>Review this lead</legend><p>Saving Keep promotes this lead into the kept queue. Keep means worth investigating, not safe to upgrade or proven vulnerable. Dismiss means deprioritized, not fixed or resolved. Unsure stays unresolved. This save does not verify the snippet.</p><label for="decision-{{r.review.id}}">Decision</label><select name="decision" id="decision-{{r.review.id}}"><option value="unreviewed" {% if r.review.decision=='unreviewed' %}selected{% endif %}>Unreviewed</option><option value="keep" {% if r.review.decision=='keep' %}selected{% endif %}>Keep — worth investigating</option><option value="dismiss" {% if r.review.decision=='dismiss' %}selected{% endif %}>Dismiss — deprioritized</option><option value="unsure" {% if r.review.decision=='unsure' %}selected{% endif %}>Unsure — unresolved</option></select><label for="note-{{r.review.id}}">Reviewer note</label><textarea id="note-{{r.review.id}}" name="note" rows="3" maxlength="2000">{{r.review.note}}</textarea><label for="applicability-{{r.review.id}}">Version applicability</label><select name="version_applicability" id="applicability-{{r.review.id}}"><option value="not_established" {% if r.review.version_applicability=='not_established' %}selected{% endif %}>not established</option><option value="reviewer_says_applicable" {% if r.review.version_applicability=='reviewer_says_applicable' %}selected{% endif %}>reviewer says applicable</option><option value="reviewer_says_not_applicable" {% if r.review.version_applicability=='reviewer_says_not_applicable' %}selected{% endif %}>reviewer says not applicable</option></select><p>Reviewer-entered assessment, not automatic verification. Applicable or not applicable needs a source URL and a rationale. These fields are not filled from the pin, query, or snippet.</p><label for="url-{{r.review.id}}">Applicability source URL</label><input id="url-{{r.review.id}}" type="url" name="applicability_url" value="{{r.review.applicability_url}}"><label for="rationale-{{r.review.id}}">Applicability rationale</label><textarea id="rationale-{{r.review.id}}" name="applicability_rationale" rows="2" maxlength="500">{{r.review.applicability_rationale}}</textarea><button>Save review</button></fieldset></form></article>{% endmacro %}
{% if ran %}<form class="filters" method="get" action="/"><input type="hidden" name="report" value="{{report_id}}"><button name="queue" value="all" {% if queue=='all' %}class="on"{% endif %}>All ({{counts.all}})</button><button name="queue" value="unresolved" {% if queue=='unresolved' %}class="on"{% endif %}>Unresolved ({{counts.unresolved}})</button><button name="queue" value="kept" {% if queue=='kept' %}class="on"{% endif %}>Kept ({{counts.kept}})</button><button name="queue" value="dismissed" {% if queue=='dismissed' %}class="on"{% endif %}>Dismissed ({{counts.dismissed}})</button></form><p>Unresolved includes unreviewed leads, unsure decisions, and saved reviews whose evidence changed. A filter does not dismiss a lead. Unmatched leads stay in All until a person saves a decision.</p><h2>{{ranked|length}} ranked leads</h2><p>{{summary}}</p><p class="exports">{% if report_id %}<a class="export" href="/export/{{report_id}}">Download Markdown</a> <a class="export" href="/brief/{{report_id}}">Download next-check brief</a>{% endif %}</p>{% for r in ranked %}{{card(r, token, report_id, queue)}}{% endfor %}<h2>{{unmatched|length}} unmatched leads</h2><p>These stay visible so source ranking cannot hide weak retrievals. Relevance labels use name, title, snippet and domain cues. They are not verification, compatibility, or pin-applicability scores.</p>{% for r in unmatched %}{{card(r, token, report_id, queue)}}{% endfor %}{% endif %}
<footer><p class="meta">Scope: package names and exact pins. A name without == is not an exact installed version, and a version range is rejected. This tool searches evidence; it does not verify full pages, compare semver or decide safe versions. Review decisions stay in local .reviews/ and are not synced.</p></footer></html>'''

def remember(report_id, rows, text, mode, summary):
    reports[report_id] = export_markdown(rows)
    scans[report_id] = {"rows": rows, "text": text, "mode": mode, "summary": summary}
    while len(reports) > 30:
        old = next(iter(reports))
        reports.pop(old, None)
        scans.pop(old, None)

def render_scan(report_id, queue, error, saved_id, text, mode, attempt=None):
    if queue not in QUEUES:
        queue = "all"
    ranked, unmatched, warnings = [], [], []
    counts = {"all": 0, "unresolved": 0, "kept": 0, "dismissed": 0}
    summary, saved_title, ran = "", "", False
    scan = scans.get(report_id) if report_id else None
    if scan:
        ran = True
        text, mode, summary = scan["text"], scan["mode"], scan["summary"]
        annotated, warnings = attach_reviews(scan["rows"], REVIEWS)
        counts = queue_counts(annotated)
        apply_attempt(annotated, attempt)
        if saved_id:
            for row in annotated:
                if row["review"]["id"] == saved_id and row["review"]["saved"]:
                    saved_title = row["title"]
        visible = annotated if queue == "all" else [row for row in annotated if row["review"]["bucket"] == queue]
        ranked = [row for row in visible if row["relevance"] != "unmatched lead"]
        unmatched = [row for row in visible if row["relevance"] == "unmatched lead"]
    return render_template_string(
        PAGE, ranked=ranked, unmatched=unmatched, error=error, ran=ran, text=text, mode=mode,
        token=session["token"], used=quota["used"], report_id=report_id if scan else "",
        summary=summary, queue=queue, counts=counts, warnings=warnings, saved_title=saved_title,
        key_set=bool(os.environ.get("SERPAPI_API_KEY")),
    )

@app.route("/", methods=["GET", "POST"])
def index():
    session.setdefault("token", secrets.token_urlsafe(24))
    error, text, mode = "", "pydantic==1.10.0\nfastapi==0.95.0", "fixture"
    report_id = request.args.get("report", "") if request.method == "GET" else ""
    queue = request.args.get("queue", "all") if request.method == "GET" else "all"
    saved_id = request.args.get("saved", "") if request.method == "GET" else ""
    if request.method == "POST":
        text = request.form.get("requirements", "")
        mode = request.form.get("mode", "fixture")
        report_id, saved_id, queue = "", "", "all"
        try:
            if request.form.get("token") != session["token"]:
                raise RadarError("Invalid form token. Refresh the page.")
            packages = parse_requirements(text)
            if mode not in ("fixture", "live", "cache"):
                raise RadarError("Unknown run mode.")
            key = os.environ.get("SERPAPI_API_KEY", "")
            if mode == "live" and not key:
                raise RadarError("Set SERPAPI_API_KEY in your terminal. Live mode was not run. Never paste the key into a project file or chat.")
            fixture = json.loads((ROOT / "fixtures/search.json").read_text())
            rows = []
            for name, version in packages:
                for q in queries(name, version):
                    if mode == "fixture":
                        payload = {**fixture, "query": q}
                        cached = False
                    elif mode == "cache":
                        payload, cached = read_cached_search(q, CACHE)
                    else:
                        # Check cache first to avoid imposing a wait on cache hits.
                        cached_path = CACHE / (hashlib.sha256(q.encode()).hexdigest() + ".json")
                        if not cached_path.exists() and last_request[0]:
                            time.sleep(max(0, 80 - (time.monotonic() - last_request[0])))
                        try:
                            payload, cached = fetch_search(q, key, CACHE, quota)
                        finally:
                            if not cached_path.exists():
                                last_request[0] = time.monotonic()
                        if not cached:
                            last_request[0] = time.monotonic()
                    rows.extend(evidence_rows(payload, name, version, cached, mode == "fixture"))
            rows = finalize_evidence(rows)
            for row in rows:
                row["requested_mode"] = mode
            summary = scan_summary(mode, rows)
            report_id = secrets.token_urlsafe(16)
            remember(report_id, rows, text, mode, summary)
        except RadarError as exc:
            error = str(exc)
            report_id = ""
    if report_id and report_id not in scans:
        error = error or "This scan is no longer in memory. Run the search again. Saved reviews remain on disk and are not dismissed."
        report_id = ""
    return render_scan(report_id, queue, error, saved_id, text, mode)

@app.post("/review")
def review():
    session.setdefault("token", secrets.token_urlsafe(24))
    report_id = request.form.get("report", "")
    queue = request.form.get("queue", "all")
    if queue not in QUEUES:
        queue = "all"
    text, mode = "pydantic==1.10.0\nfastapi==0.95.0", "fixture"
    if request.form.get("token") != session.get("token"):
        return render_scan(report_id, queue, "Invalid form token. Refresh the page.", "", text, mode)
    if report_id not in scans:
        return render_scan("", "all", "This scan is no longer in memory. Run the search again. Saved reviews remain on disk and are not dismissed.", "", text, mode)
    eid = request.form.get("evidence_id", "")
    row = next((item for item in scans[report_id]["rows"] if evidence_id(item["package"], item["canonical"]) == eid), None)
    if row is None:
        return render_scan(report_id, queue, "That lead is not in this scan. A lead absent from search results is not dismissed.", "", text, mode)
    try:
        save_review(REVIEWS, build_review(row, request.form))
    except ReviewCorrupt as exc:
        return render_scan(report_id, queue, str(exc), "", text, mode)
    except ReviewError as exc:
        return render_scan(report_id, "all", str(exc), "", text, mode, {"id": eid, "form": request.form})
    return redirect(f"/?report={report_id}&queue={queue}&saved={eid}")

@app.get("/export/<report_id>")
def export(report_id):
    if report_id not in reports:
        return "Report expired or not found", 404
    return Response(reports[report_id], mimetype="text/markdown", headers={"Content-Disposition": 'attachment; filename="drift-evidence.md"'})

@app.get("/brief/<report_id>")
def brief(report_id):
    scan = scans.get(report_id)
    if not scan:
        return "This scan is no longer in memory. Run the search again. Saved reviews remain on disk and are not dismissed.", 404
    annotated, warnings = attach_reviews(scan["rows"], REVIEWS)
    body = next_check_brief(annotated, warnings)
    return Response(body, mimetype="text/markdown", headers={"Content-Disposition": 'attachment; filename="next-check-brief.md"'})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8501, threaded=False)
