"""Human review state for evidence leads. Never a verification verdict."""
import hashlib, json, os, re, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from radar import scan_summary

DECISIONS = ("unreviewed", "keep", "dismiss", "unsure")
APPLICABILITY_VALUES = ("not_established", "reviewer_says_applicable", "reviewer_says_not_applicable")
QUEUES = ("all", "unresolved", "kept", "dismissed")
NOTE_LIMIT = 2000
RATIONALE_LIMIT = 500
URL_LIMIT = 2000
DECISION_LABEL = {"unreviewed": "Unreviewed", "keep": "Keep", "dismiss": "Dismiss", "unsure": "Unsure"}
APPLICABILITY_LABEL = {
    "not_established": "not established",
    "reviewer_says_applicable": "reviewer says applicable",
    "reviewer_says_not_applicable": "reviewer says not applicable",
}
_HEX_ID = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_KEYS = {
    "id", "package", "canonical", "decision", "note", "version_applicability",
    "applicability_url", "applicability_rationale", "updated_at", "fingerprint",
    "evidence_retrieved_at",
}
_CONTEXT_KEYS = {"evidence_pin", "evidence_status"}
_EVIDENCE_STATUSES = {"SYNTHETIC FIXTURE", "UNVERIFIED: search snippet only"}

class ReviewError(ValueError):
    pass

class ReviewCorrupt(ValueError):
    pass

def evidence_id(package, canonical):
    return hashlib.sha256(f"{package}\n{canonical}".encode()).hexdigest()

def evidence_fingerprint(row):
    # Snippet order is not identity. Tracking parameters stay out; canonical is the source.
    snippets = sorted((item.get("snippet") or "") for item in (row.get("provenance") or []))
    parts = [
        row.get("title") or "",
        row.get("canonical") or "",
        row.get("installed_pin") or "",
        row.get("status") or "",
        *snippets,
    ]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()

def retrieval_times(row):
    return [str(item.get("retrieved_at") or "") for item in (row.get("provenance") or [])]

def valid_http_url(url, allow_userinfo=False):
    if not isinstance(url, str) or not url or len(url) > URL_LIMIT or any(ch.isspace() for ch in url):
        return False
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return False
    if not allow_userinfo and (parts.username or parts.password):
        return False
    return True

def _plain(value, limit, label):
    if not isinstance(value, str):
        raise ReviewError(f"{label} must be plain text.")
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in text:
        raise ReviewError(f"{label} must be plain text.")
    if len(text) > limit:
        raise ReviewError(f"{label} is limited to {limit} characters.")
    return text

def build_review(row, fields, now=None):
    decision = fields.get("decision", "")
    if decision not in DECISIONS:
        raise ReviewError("Decision must be unreviewed, keep, dismiss, or unsure.")
    note = _plain(fields.get("note", ""), NOTE_LIMIT, "Reviewer note")
    applicability = fields.get("version_applicability", "")
    if applicability not in APPLICABILITY_VALUES:
        raise ReviewError("Version applicability must be not established, reviewer says applicable, or reviewer says not applicable.")
    rationale = _plain(fields.get("applicability_rationale", ""), RATIONALE_LIMIT, "Applicability rationale").strip()
    url = fields.get("applicability_url", "")
    if not isinstance(url, str):
        raise ReviewError("Applicability source URL must be an http or https URL.")
    url = url.strip()
    if len(url) > URL_LIMIT:
        raise ReviewError("Applicability source URL is too long.")
    if url and not valid_http_url(url):
        raise ReviewError("Applicability source URL must be an http or https URL.")
    if applicability != "not_established":
        if not rationale:
            raise ReviewError("Reviewer says applicable or not applicable requires a rationale.")
        if not url:
            raise ReviewError("Reviewer says applicable or not applicable requires an http or https source URL.")
    times = retrieval_times(row)
    if not times or len(times) > 20 or any(not isinstance(item, str) or len(item) > 80 for item in times):
        raise ReviewError("This lead has no usable retrieval time to review against.")
    pin = row.get("installed_pin") or ""
    status = row.get("status") or ""
    if not isinstance(pin, str) or not pin or len(pin) > 80:
        raise ReviewError("This lead has no usable installed pin to review against.")
    if status not in _EVIDENCE_STATUSES:
        raise ReviewError("This lead has no usable evidence status to review against.")
    record = {
        "id": evidence_id(row["package"], row["canonical"]),
        "package": row["package"],
        "canonical": row["canonical"],
        "decision": decision,
        "note": note,
        "version_applicability": applicability,
        "applicability_url": url,
        "applicability_rationale": rationale,
        "updated_at": now or datetime.now(timezone.utc).isoformat(),
        "fingerprint": evidence_fingerprint(row),
        "evidence_retrieved_at": times,
        "evidence_pin": pin,
        "evidence_status": status,
    }
    _check_record(record)
    return record

def review_bucket(view):
    if view.get("needs_rereview") or view.get("decision") in ("unreviewed", "unsure"):
        return "unresolved"
    if view.get("decision") == "keep":
        return "kept"
    if view.get("decision") == "dismiss":
        return "dismissed"
    return "unresolved"

def present_review(row, stored=None):
    view = {
        "id": evidence_id(row["package"], row["canonical"]),
        "decision": "unreviewed",
        "decision_label": "Unreviewed",
        "note": "",
        "version_applicability": "not_established",
        "applicability_label": "not established",
        "applicability_url": "",
        "applicability_rationale": "",
        "updated_at": "",
        "saved": False,
        "needs_rereview": False,
        "reviewed_against": [],
        "evidence_pin": "",
        "evidence_status": "",
        "applicability_for_current_evidence": "not established",
    }
    if stored:
        context_missing = "evidence_pin" not in stored or "evidence_status" not in stored
        changed = stored["fingerprint"] != evidence_fingerprint(row) or context_missing
        view.update({
            "decision": stored["decision"],
            "decision_label": DECISION_LABEL[stored["decision"]],
            "note": stored["note"],
            "version_applicability": stored["version_applicability"],
            "applicability_label": APPLICABILITY_LABEL[stored["version_applicability"]],
            "applicability_url": stored["applicability_url"],
            "applicability_rationale": stored["applicability_rationale"],
            "updated_at": stored["updated_at"],
            "saved": True,
            "needs_rereview": changed,
            "reviewed_against": list(stored["evidence_retrieved_at"]),
            "evidence_pin": stored.get("evidence_pin", ""),
            "evidence_status": stored.get("evidence_status", ""),
            "applicability_for_current_evidence": "not established" if changed else APPLICABILITY_LABEL[stored["version_applicability"]],
        })
    view["bucket"] = review_bucket(view)
    return view

def queue_counts(rows):
    counts = {"all": len(rows), "unresolved": 0, "kept": 0, "dismissed": 0}
    for row in rows:
        counts[row["review"]["bucket"]] += 1
    return counts

def _check_record(data, filename_stem=None):
    if not isinstance(data, dict):
        return False
    keys = set(data)
    if not _REQUIRED_KEYS <= keys <= _REQUIRED_KEYS | _CONTEXT_KEYS:
        return False
    if ("evidence_pin" in data) != ("evidence_status" in data):
        return False
    if not isinstance(data["id"], str) or not _HEX_ID.fullmatch(data["id"]):
        return False
    if filename_stem is not None and filename_stem != data["id"]:
        return False
    package, canonical = data["package"], data["canonical"]
    if not isinstance(package, str) or not package or len(package) > 200:
        return False
    if not isinstance(canonical, str) or not valid_http_url(canonical, allow_userinfo=True):
        return False
    if evidence_id(package, canonical) != data["id"]:
        return False
    if data["decision"] not in DECISIONS or data["version_applicability"] not in APPLICABILITY_VALUES:
        return False
    if not isinstance(data["note"], str) or len(data["note"]) > NOTE_LIMIT or "\x00" in data["note"]:
        return False
    if not isinstance(data["applicability_rationale"], str) or len(data["applicability_rationale"]) > RATIONALE_LIMIT:
        return False
    if "\x00" in data["applicability_rationale"]:
        return False
    url = data["applicability_url"]
    if not isinstance(url, str) or len(url) > URL_LIMIT or (url and not valid_http_url(url)):
        return False
    if data["version_applicability"] != "not_established":
        if not data["applicability_rationale"].strip() or not url:
            return False
    if not isinstance(data["updated_at"], str) or not data["updated_at"] or len(data["updated_at"]) > 80:
        return False
    try:
        datetime.fromisoformat(data["updated_at"])
    except ValueError:
        return False
    if not isinstance(data["fingerprint"], str) or not _HEX_ID.fullmatch(data["fingerprint"]):
        return False
    times = data["evidence_retrieved_at"]
    if not isinstance(times, list) or not 1 <= len(times) <= 20:
        return False
    if any(not isinstance(item, str) or len(item) > 80 for item in times):
        return False
    if "evidence_pin" in data:
        pin, status = data["evidence_pin"], data["evidence_status"]
        if not isinstance(pin, str) or not pin or len(pin) > 80:
            return False
        if status not in _EVIDENCE_STATUSES:
            return False
    return True

def _corrupt(path):
    return ReviewCorrupt(
        f"Review file {path.name} could not be read and was left unchanged. Fix or remove that file before saving a new review for it."
    )

def read_review_file(path):
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise _corrupt(path) from None
    if not _check_record(data, path.stem):
        raise _corrupt(path)
    return data

def load_reviews(directory):
    directory = Path(directory)
    records, warnings = {}, []
    if not directory.exists():
        return records, warnings
    if not directory.is_dir():
        warnings.append("Review directory .reviews could not be read and was left unchanged.")
        return records, warnings
    try:
        paths = sorted(directory.glob("*.json"))
    except OSError:
        warnings.append("Review directory .reviews could not be read and was left unchanged.")
        return records, warnings
    for path in paths:
        if not path.is_file():
            continue
        try:
            records[path.stem] = read_review_file(path)
        except ReviewCorrupt as exc:
            warnings.append(str(exc))
    return records, warnings

def attach_reviews(rows, directory):
    stored, warnings = load_reviews(directory)
    annotated = []
    for row in rows:
        eid = evidence_id(row["package"], row["canonical"])
        record = stored.get(eid)
        if record and (record["package"] != row["package"] or record["canonical"] != row["canonical"]):
            warnings.append(
                f"Review file {eid}.json does not match this lead and was left unchanged."
            )
            record = None
        annotated.append({**row, "review": present_review(row, record)})
    return annotated, warnings

def save_review(directory, record):
    if not _check_record(record):
        raise ReviewError("Review could not be saved because its fields are not valid.")
    directory = Path(directory)
    path = directory / f"{record['id']}.json"
    if path.exists():
        read_review_file(path)
    text = json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise ReviewError("Could not save the review. Any previous review file was left unchanged.") from None
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        raise ReviewError("Could not save the review. Any previous review file was left unchanged.") from None
    finally:
        tmp.unlink(missing_ok=True)

def apply_attempt(rows, attempt):
    if not attempt:
        return
    form = attempt["form"]
    for row in rows:
        view = row["review"]
        if view["id"] != attempt["id"]:
            continue
        decision = form.get("decision", "")
        if isinstance(decision, str) and decision in DECISIONS:
            view["decision"] = decision
        applicability = form.get("version_applicability", "")
        if isinstance(applicability, str) and applicability in APPLICABILITY_VALUES:
            view["version_applicability"] = applicability
        note = form.get("note", "")
        rationale = form.get("applicability_rationale", "")
        url = form.get("applicability_url", "")
        if isinstance(note, str):
            view["note"] = note[:NOTE_LIMIT]
        if isinstance(rationale, str):
            view["applicability_rationale"] = rationale[:RATIONALE_LIMIT]
        if isinstance(url, str):
            view["applicability_url"] = url[:URL_LIMIT]
        view["bucket"] = review_bucket(view)

def _md_literal(value):
    lines = []
    for line in (value or "").split("\n"):
        if re.match(r"^(#{1,6} |[->] |\* |\+ |\d+\. )", line):
            line = "\\" + line
        lines.append(line)
    return "\n".join(lines)

def _md_field(label, value):
    text = _md_literal(value)
    parts = text.split("\n")
    if len(parts) == 1:
        return f"{label}: {parts[0]}"
    return "\n".join([f"{label}:", *[f"    {line}" for line in parts]])

def _meaning(decision):
    if decision == "keep":
        return "Meaning: worth investigating. This is not an upgrade approval and not proof of a vulnerability."
    if decision == "dismiss":
        return "Meaning: deprioritized. This is not fixed or resolved."
    if decision == "unsure":
        return "Meaning: unresolved."
    return "Meaning: unreviewed. This stays unresolved until a person saves a decision."

def _brief_card(row):
    review = row["review"]
    lines = [
        f"### {row['package']} ({row['installed_pin']})",
        "Installed pin is investigation context only.",
    ]
    if row.get("version_note"):
        lines.append(row["version_note"])
    lines.append(f"Decision: {review['decision_label']}")
    lines.append(_meaning(review["decision"]))
    if review["needs_rereview"]:
        lines += [
            "needs re-review: evidence changed",
            "The previous decision and note are retained. This lead stays unresolved until a person saves the review again.",
        ]
    if review["saved"]:
        lines.append(f"Review updated: {review['updated_at']}")
        lines.append("Reviewed against pin: " + (review["evidence_pin"] or "not stored"))
        lines.append("Evidence status when saved: " + (review["evidence_status"] or "not stored"))
        lines.append("Reviewed against retrieval: " + "; ".join(review["reviewed_against"]))
        if review["needs_rereview"]:
            lines.append("Version applicability for this evidence: not established until a person saves again.")
    else:
        lines.append("No saved review.")
    lines += [
        _md_field("Reviewer note", review["note"]),
        f"Version applicability: {review['applicability_for_current_evidence'] if review['needs_rereview'] else review['applicability_label']}",
        "Version applicability is a reviewer-entered assessment, not automatic verification.",
    ]
    if review["applicability_url"]:
        lines.append(f"Applicability source: {review['applicability_url']}")
    if review["applicability_rationale"]:
        lines.append(_md_field("Applicability rationale", review["applicability_rationale"]))
    lines += [
        f"Status: {row['status']}",
    ]
    if row.get("evidence_origin_label"):
        lines.append(row["evidence_origin_label"])
    if row.get("freshness_note"):
        lines.append(row["freshness_note"])
    lines += [
        f"Relevance: {row['relevance']}",
        f"Source category: {row['source_category']}",
        row["applicability"],
        f"Heuristic cues: {row['signals']}",
        f"Source: {row['url']}",
        "Provenance:",
    ]
    for item in row["provenance"]:
        lines += [
            f"- Query: {item['query']}",
            f"  Retrieved: {item['retrieved_at']}; cached={item['cached']}",
            f"  Retrieval time: {item.get('retrieval_label') or item.get('retrieved_at') or 'unknown'}",
            f"  Origin: {item.get('origin') or 'unknown'}",
            f"  Snippet: {item['snippet']}",
        ]
    if review["bucket"] == "kept":
        lines.append("Next check: open the source and any reviewer-entered applicability URL, then compare the page with the installed pin. The search snippet is not that check.")
    else:
        lines.append("Next check: not in the kept queue.")
    lines.append("")
    return lines

def next_check_brief(rows, warnings=None):
    counts = queue_counts(rows) if rows else {"all": 0, "unresolved": 0, "kept": 0, "dismissed": 0}
    lines = [
        "# Next-check brief",
        "",
        "This brief is a maintainer work list. Human decisions sit beside the search leads they refer to.",
        "A saved decision does not verify a snippet, establish CVE applicability, or choose a safe upgrade.",
        "Search snippets remain UNVERIFIED. Synthetic fixtures remain SYNTHETIC.",
        "A Live request is not proof a network call happened. A cache hit stays cached evidence.",
        "A missing or invalid retrieval timestamp is unknown. Freshness is the age of retrieved evidence, not proof a page or claim is current. There is no expiry cutoff.",
        "Keep means worth investigating. Dismiss means deprioritized, not fixed or resolved.",
        "Unresolved includes unreviewed leads, unsure decisions, and reviews marked needs re-review: evidence changed.",
        "A lead absent from a later search is not resolved and is not automatically dismissed.",
        "",
        f"All: {counts['all']}. Unresolved: {counts['unresolved']}. Kept: {counts['kept']}. Dismissed: {counts['dismissed']}.",
        "",
    ]
    requested = next((row.get("requested_mode") for row in rows if row.get("requested_mode")), None)
    if requested:
        lines += [scan_summary(requested, rows), ""]
    if warnings:
        lines.append("Store warnings:")
        lines += [f"- {warning}" for warning in warnings]
        lines.append("")
    sections = (
        ("kept", "Kept for a next check", "reviewed-kept"),
        ("unresolved", "Unresolved", "unresolved"),
        ("dismissed", "Dismissed — deprioritized, not resolved", "reviewed-dismissed"),
    )
    for bucket, title, section_id in sections:
        chosen = [row for row in rows if row["review"]["bucket"] == bucket]
        lines += [f"## {title} ({len(chosen)})", "", f"Export section: {section_id}", ""]
        if not chosen:
            lines += ["None.", ""]
            continue
        for row in chosen:
            lines += _brief_card(row)
    return "\n".join(lines)
