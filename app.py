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
PAGE = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dependency Drift Radar</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--text:#111827;--muted:#475569;--line:#d5dae1;--line-soft:#e6e9ee;--control:#7b8494;--accent:#1e3a8a;--accent-hover:#172e6e;--warn-text:#7a3a00;--warn-bg:#fff8e8;--warn-line:#b45309;--err-text:#7f1d1d;--err-bg:#fdf2f2;--err-line:#b91c1c;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:32px 24px}
p,h1,h2,h3,blockquote{margin:0}
a{color:var(--accent);text-underline-offset:2px}
a:hover{color:var(--accent-hover)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.site-header{padding-bottom:24px;margin-bottom:24px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:14px;color:var(--muted);margin-bottom:4px}
h1{font-size:24px;line-height:1.3;font-weight:650;margin-bottom:8px}
h2{font-size:18px;line-height:1.4;font-weight:650}
.lede{max-width:72ch;color:var(--muted)}
.stack>*+*{margin-top:12px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:24px}
.meta{font-size:14px;color:var(--muted)}
.mono{font-family:var(--mono);font-size:14px}
.notice{padding:12px 16px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--muted);border-radius:4px}
.warn{color:var(--warn-text);background:var(--warn-bg);border-color:#ecd7b0;border-left-color:var(--warn-line)}
.err{color:var(--err-text);background:var(--err-bg);border-color:#efc9c9;border-left-color:var(--err-line)}
.saved{border-left-color:var(--accent)}
label{display:block;margin-bottom:4px;font-size:14px;font-weight:600}
textarea,input[type=url],select{display:block;width:100%;min-height:40px;padding:8px 12px;font:inherit;color:var(--text);background:#fff;border:1px solid var(--control);border-radius:4px}
textarea{resize:vertical;line-height:1.5}
#req{font-family:var(--mono);font-size:14px}
button,.btn{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 16px;font:inherit;font-weight:600;line-height:1.3;text-align:center;text-decoration:none;color:#fff;background:var(--accent);border:1px solid var(--accent);border-radius:4px;cursor:pointer}
button:hover{background:var(--accent-hover);border-color:var(--accent-hover)}
.btn-secondary{color:var(--accent);background:#fff;border-color:var(--control)}
.btn-secondary:hover{color:var(--accent-hover);background:#f1f4f9}
.scan-row{display:flex;flex-wrap:wrap;align-items:flex-end;gap:16px;margin-top:16px}
.scan-row .field{flex:1 1 280px;max-width:420px}
.notices{margin-top:16px}
.results{margin-top:32px;padding-top:24px;border-top:1px solid var(--line)}
.filters{display:flex;flex-wrap:wrap;gap:8px}
.filters button{color:var(--text);background:#fff;border-color:var(--control);font-weight:500}
.filters button:hover{background:#f1f4f9;color:var(--text)}
.filters button.on{color:#fff;background:var(--accent);border-color:var(--accent);font-weight:650}
.section-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-top:32px}
.exports{display:flex;flex-wrap:wrap;gap:8px}
.leads{margin-top:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:24px;margin-bottom:16px;overflow-wrap:anywhere}
.card-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:12px}
.pin{font-family:var(--mono);font-size:14px;font-weight:650;margin-right:4px}
.tag{display:inline-block;padding:2px 8px;font-size:14px;line-height:1.5;color:var(--muted);background:#f8fafc;border:1px solid var(--line);border-radius:4px}
.tag-status{color:var(--warn-text);background:var(--warn-bg);border-color:var(--warn-line);font-weight:650}
.card h3{font-size:17px;line-height:1.4;font-weight:650}
.url{margin-top:4px;font-family:var(--mono);font-size:14px;color:var(--muted)}
.facts{margin:16px 0 0;padding:0;list-style:none;border-top:1px solid var(--line-soft)}
.facts li{padding:8px 0;border-bottom:1px solid var(--line-soft)}
.flag{color:var(--warn-text);font-weight:650}
.sub{margin:16px 0 8px;font-size:14px;font-weight:650;color:var(--muted)}
.prov{padding:12px 16px;background:#fafbfc;border:1px solid var(--line-soft);border-radius:4px}
.prov+.prov{margin-top:8px}
blockquote{padding-left:12px;margin-bottom:8px;border-left:3px solid #94a3b8}
.review-state{margin-top:16px}
fieldset{min-width:0;margin:16px 0 0;padding:16px 24px 24px;border:1px solid var(--line);border-radius:6px}
legend{padding:0 8px;font-weight:650}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px}
.wide{grid-column:1/-1}
.actions{margin-top:16px}
.mt4{margin-top:4px}.mt8{margin-top:8px}.mt12{margin-top:12px}.mt16{margin-top:16px}
footer{margin-top:32px;padding-top:16px;border-top:1px solid var(--line)}
@media (max-width:640px){.wrap{padding:24px 16px}.panel,.card{padding:16px}fieldset{padding:12px 16px 16px}.grid{grid-template-columns:minmax(0,1fr)}.scan-row .field{max-width:none}button,.btn,select,input[type=url]{min-height:44px}.scan-row button,.actions button{width:100%}}
</style></head><body><div class="wrap">
<header class="site-header"><p class="eyebrow">Local Python dependency research</p><h1>Dependency Drift Radar</h1><p class="lede">Find migration, deprecation and security leads for your pinned packages. Every lead keeps its source and search context. No invented CVEs. No automatic upgrades.</p></header>
<main>
<div class="stack"><p class="notice warn">Search snippets are not proof. Verify the linked source and whether it applies to your installed version before acting.</p>
<form class="panel" method="post"><input type="hidden" name="token" value="{{token}}"><label for="req">Python requirements (up to 5 packages)</label><textarea id="req" name="requirements" rows="5">{{text}}</textarea><div class="scan-row"><div class="field"><label for="mode">Run mode</label><select name="mode" id="mode"><option value="fixture" {% if mode=='fixture' %}selected{% endif %}>Synthetic fixtures (no API / no spend)</option><option value="cache" {% if mode=='cache' %}selected{% endif %}>Saved cache only (no network call)</option><option value="live" {% if mode=='live' %}selected{% endif %}>Live SerpApi (uses free searches)</option></select></div><button>Find evidence leads</button></div>
<p class="meta mt16">Process live attempts: {{used}} / 20. Max 10 per scan. Same queries use local cache. Server spaces requests 80 seconds apart for the free 50/hour throughput. Demo fixtures do not demonstrate live SerpApi use. Requested mode is not the evidence origin.</p></form></div>
<div class="notices stack">{% if not key_set %}<p class="notice warn">This process has no search key. Live mode will not run, and this page will not present a completed live search.</p>{% endif %}
{% if error %}<p class="notice err" role="alert">{{error}}</p>{% endif %}
{% if saved_title %}<p class="notice saved" role="status">Review saved for {{saved_title}}.</p>{% endif %}
{% for warning in warnings %}<p class="notice warn" role="alert">{{warning}}</p>{% endfor %}</div>
{% macro card(r, token, report_id, queue) %}<article class="card"><div class="card-top"><span class="pin">{{r.package}} / {{r.installed_pin}}</span><span class="tag tag-status">{{r.status}}</span><span class="tag">{{r.relevance}}</span><span class="tag">{{r.source_category}}</span></div><h3><a href="{{r.url}}" target="_blank" rel="noopener noreferrer">{{r.title}}</a></h3><p class="url">{{r.url}}</p>
<ul class="facts"><li>{{r.evidence_origin_label}}</li><li>{{r.version_note}}</li><li class="flag">{{r.applicability}}</li><li class="meta">{{r.freshness_note}}</li><li>Heuristic cues: {{r.signals}}</li></ul>
<div class="sub">Provenance</div>{% for item in r.provenance %}<div class="prov"><blockquote>{{item.snippet}}</blockquote><p class="meta"><span class="mono">{{item.query}}</span><br>Retrieved {{item.retrieved_at}} | Retrieval time: {{item.retrieval_label}} | Cached: {{item.cached}} | Origin: {{item.origin}}</p></div>{% endfor %}
<div class="review-state stack">{% if r.review.saved %}<div class="notice saved"><p>Saved {{r.review.decision_label}} at {{r.review.updated_at}}. {% if r.review.needs_rereview %}Version applicability for this evidence: not established until you save again. Previous assessment retained: {{r.review.applicability_label}}.{% else %}Version applicability: {{r.review.applicability_label}}. Reviewer-entered assessment, not automatic verification.{% endif %}</p><p class="meta mt4">Reviewed against pin {{r.review.evidence_pin or "not stored"}}. Evidence status when saved: {{r.review.evidence_status or "not stored"}}. Reviewed against retrieval {% for t in r.review.reviewed_against %}{{t}}{% if not loop.last %}; {% endif %}{% endfor %}</p></div>{% else %}<p class="meta">Not saved yet.</p>{% endif %}
{% if r.review.needs_rereview %}<div class="notice warn"><p class="flag">needs re-review: evidence changed</p><p class="mt4">Previous decision retained: {{r.review.decision_label}}. The previous note stays in the form until you save this review again. Applicability for this evidence is not established until you save again.</p></div>{% endif %}</div>
<form method="post" action="/review"><input type="hidden" name="token" value="{{token}}"><input type="hidden" name="report" value="{{report_id}}"><input type="hidden" name="queue" value="{{queue}}"><input type="hidden" name="evidence_id" value="{{r.review.id}}"><fieldset><legend>Review this lead</legend><p class="meta">Saving Keep promotes this lead into the kept queue. Keep means worth investigating, not safe to upgrade or proven vulnerable. Dismiss means deprioritized, not fixed or resolved. Unsure stays unresolved. This save does not verify the snippet.</p>
<div class="grid"><div><label for="decision-{{r.review.id}}">Decision</label><select name="decision" id="decision-{{r.review.id}}"><option value="unreviewed" {% if r.review.decision=='unreviewed' %}selected{% endif %}>Unreviewed</option><option value="keep" {% if r.review.decision=='keep' %}selected{% endif %}>Keep — worth investigating</option><option value="dismiss" {% if r.review.decision=='dismiss' %}selected{% endif %}>Dismiss — deprioritized</option><option value="unsure" {% if r.review.decision=='unsure' %}selected{% endif %}>Unsure — unresolved</option></select></div>
<div class="wide"><label for="note-{{r.review.id}}">Reviewer note</label><textarea id="note-{{r.review.id}}" name="note" rows="3" maxlength="2000">{{r.review.note}}</textarea></div>
<p class="meta wide">Reviewer-entered assessment, not automatic verification. Applicable or not applicable needs a source URL and a rationale. These fields are not filled from the pin, query, or snippet.</p>
<div><label for="applicability-{{r.review.id}}">Version applicability</label><select name="version_applicability" id="applicability-{{r.review.id}}"><option value="not_established" {% if r.review.version_applicability=='not_established' %}selected{% endif %}>not established</option><option value="reviewer_says_applicable" {% if r.review.version_applicability=='reviewer_says_applicable' %}selected{% endif %}>reviewer says applicable</option><option value="reviewer_says_not_applicable" {% if r.review.version_applicability=='reviewer_says_not_applicable' %}selected{% endif %}>reviewer says not applicable</option></select></div>
<div><label for="url-{{r.review.id}}">Applicability source URL</label><input id="url-{{r.review.id}}" type="url" name="applicability_url" value="{{r.review.applicability_url}}"></div>
<div class="wide"><label for="rationale-{{r.review.id}}">Applicability rationale</label><textarea id="rationale-{{r.review.id}}" name="applicability_rationale" rows="2" maxlength="500">{{r.review.applicability_rationale}}</textarea></div></div>
<div class="actions"><button>Save review</button></div></fieldset></form></article>{% endmacro %}
{% if ran %}<section class="results"><form class="filters" method="get" action="/"><input type="hidden" name="report" value="{{report_id}}"><button name="queue" value="all" {% if queue=='all' %}class="on" aria-pressed="true"{% else %}aria-pressed="false"{% endif %}>All ({{counts.all}})</button><button name="queue" value="unresolved" {% if queue=='unresolved' %}class="on" aria-pressed="true"{% else %}aria-pressed="false"{% endif %}>Unresolved ({{counts.unresolved}})</button><button name="queue" value="kept" {% if queue=='kept' %}class="on" aria-pressed="true"{% else %}aria-pressed="false"{% endif %}>Kept ({{counts.kept}})</button><button name="queue" value="dismissed" {% if queue=='dismissed' %}class="on" aria-pressed="true"{% else %}aria-pressed="false"{% endif %}>Dismissed ({{counts.dismissed}})</button></form><p class="meta mt12">Unresolved includes unreviewed leads, unsure decisions, and saved reviews whose evidence changed. A filter does not dismiss a lead. Unmatched leads stay in All until a person saves a decision.</p>
<div class="section-head"><h2>{{ranked|length}} ranked leads</h2><p class="exports">{% if report_id %}<a class="export btn btn-secondary" href="/export/{{report_id}}">Download Markdown</a> <a class="export btn btn-secondary" href="/brief/{{report_id}}">Download next-check brief</a>{% endif %}</p></div><p class="notice mt12">{{summary}}</p><div class="leads">{% for r in ranked %}{{card(r, token, report_id, queue)}}{% endfor %}</div>
<div class="section-head"><h2>{{unmatched|length}} unmatched leads</h2></div><p class="meta mt8">These stay visible so source ranking cannot hide weak retrievals. Relevance labels use name, title, snippet and domain cues. They are not verification, compatibility, or pin-applicability scores.</p><div class="leads">{% for r in unmatched %}{{card(r, token, report_id, queue)}}{% endfor %}</div></section>{% endif %}
</main>
<footer><p class="meta">Scope: package names and exact pins. A name without == is not an exact installed version, and a version range is rejected. This tool searches evidence; it does not verify full pages, compare semver or decide safe versions. Review decisions stay in local .reviews/ and are not synced.</p></footer></div></body></html>'''

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
