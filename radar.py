"""Search-result evidence only: never a vulnerability verdict."""
import hashlib, json, re, ssl, urllib.parse, urllib.request, certifi
from datetime import datetime, timezone
from pathlib import Path

# First-search site: scopes. These strings are part of the cache key.
DOMAINS = {"fastapi": "fastapi.tiangolo.com", "pydantic": "docs.pydantic.dev", "django": "docs.djangoproject.com", "flask": "flask.palletsprojects.com", "requests": "requests.readthedocs.io", "numpy": "numpy.org", "pandas": "pandas.pydata.org", "sqlalchemy": "docs.sqlalchemy.org"}
# Documentation hosts checked against each project's PyPI project_urls.
# pydantic.dev is included because docs.pydantic.dev answers with a 301 to pydantic.dev/docs/.
DOC_HOSTS = {"fastapi": ("fastapi.tiangolo.com",), "pydantic": ("docs.pydantic.dev", "pydantic.dev"), "django": ("docs.djangoproject.com",), "flask": ("flask.palletsprojects.com",), "requests": ("requests.readthedocs.io",), "numpy": ("numpy.org",), "pandas": ("pandas.pydata.org",), "sqlalchemy": ("docs.sqlalchemy.org",)}
# Repository host is exact: gist.github.com and other subdomains are different sites.
# Owner/repo values are the Source or Repository URLs published on PyPI.
REPOS = {"fastapi": ("github.com", "fastapi", "fastapi"), "pydantic": ("github.com", "pydantic", "pydantic"), "django": ("github.com", "django", "django"), "flask": ("github.com", "pallets", "flask"), "requests": ("github.com", "psf", "requests"), "numpy": ("github.com", "numpy", "numpy"), "pandas": ("github.com", "pandas-dev", "pandas"), "sqlalchemy": ("github.com", "sqlalchemy", "sqlalchemy")}
SOURCE_TIER = {"Package documentation": 0, "Package repository": 1, "Other source": 2}
APPLICABILITY = "Pin applicability: not established"
_TRACKING = {"gclid", "fbclid", "msclkid"}
class RadarError(ValueError): pass

def parse_requirements(text):
    if len(text)>10000: raise RadarError("Input exceeds 10,000 characters.")
    packages=[]
    for raw in text.splitlines():
        line=raw.split("#",1)[0].strip()
        if not line: continue
        if line.startswith(("-", "git+", "http")) or "@" in line: raise RadarError("Use simple package pins, not URLs, flags or editable installs.")
        m=re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[A-Za-z0-9,._-]+\])?(?:\s*==\s*([0-9][A-Za-z0-9.+_-]*))?",line)
        if not m:
            if re.search(r"(>=|<=|~=|!=|>|<)", line):
                raise RadarError("A version range is not an exact installed version. Pin applicability is not established. Enter an exact pin such as pydantic==1.10.0, or a package name with no version.")
            raise RadarError("Use package names or exact pins such as pydantic==1.10.0. No ranges or markers in this MVP.")
        name=re.sub(r"[-_.]+","-",m.group(1)).lower()
        if name not in [p[0] for p in packages]: packages.append((name,m.group(2) or "not pinned"))
    if not packages: raise RadarError("Enter at least one Python package.")
    if len(packages)>5: raise RadarError("Maximum five packages per run to conserve searches.")
    return packages

def version_note(version):
    if version == "not pinned":
        return "Installed version: unknown. The input is a package name, not an exact pin."
    if re.fullmatch(r"[0-9][A-Za-z0-9.+_-]*", version or ""):
        return f"Installed version: exact pin {version}."
    return f"Installed version: not exact. Input kept: {version}."

def queries(name,version):
    scope="site:"+DOMAINS.get(name,"pypi.org/project/"+name)
    v="" if version=="not pinned" else version
    return [f'{scope} {name} {v} migration deprecation',f'{name} {v} security advisory release notes']

def fetch_search(query,key,cache_dir,quota,limit=20):
    cache_dir=Path(cache_dir);cache_dir.mkdir(parents=True,exist_ok=True)
    path=cache_dir/(hashlib.sha256(query.encode()).hexdigest()+".json")
    if path.exists():
        try: return json.loads(path.read_text()),True
        except (json.JSONDecodeError,OSError): path.unlink(missing_ok=True)
    # Counts attempts, including network/API errors, conservatively.
    if quota["used"]>=limit: raise RadarError("Local live-search budget reached. Use fixtures or cached queries; do not buy credits.")
    quota["used"]+=1
    params=urllib.parse.urlencode({"engine":"google","q":query,"api_key":key,"num":5})
    try:
        with urllib.request.urlopen("https://serpapi.com/search.json?"+params,timeout=25,context=ssl.create_default_context(cafile=certifi.where())) as r: data=json.load(r)
    except Exception: raise RadarError("SerpApi request failed. Check key/quota/connectivity. No automatic retries or paid fallback.") from None
    if data.get("error"): raise RadarError("SerpApi returned an error. Check account quota/key; no paid fallback.")
    payload={"query":query,"retrieved_at":datetime.now(timezone.utc).isoformat(),"results":data.get("organic_results",[])[:5]}
    # Store only allowlisted fields, never API keys, metadata URLs or account data.
    payload["results"]=[{k:x[k] for k in ("title","link","snippet","date") if k in x} for x in payload["results"]]
    path.write_text(json.dumps(payload));return payload,False

def read_cached_search(query, cache_dir):
    """Return a stored response without calling the network or rewriting its timestamp."""
    path = Path(cache_dir) / (hashlib.sha256(query.encode()).hexdigest() + ".json")
    if not path.exists():
        raise RadarError("No saved response for this query. Saved-cache mode does not call the network.")
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        raise RadarError("Saved response for this query is unreadable. The file was not replaced and no network call was made.")
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise RadarError("Saved response for this query is unreadable. The file was not replaced and no network call was made.")
    return payload, True

def _hostname(host):
    return (host or "").lower().rstrip(".")

def documentation_host(name, host):
    host=_hostname(host)
    for domain in DOC_HOSTS.get(name, ()):
        domain=_hostname(domain)
        if host==domain or host.endswith("."+domain): return True
    return False

def repository_url(name, host, path):
    spec=REPOS.get(name)
    if not spec: return False
    repo_host, owner, repo = spec
    if _hostname(host)!=repo_host: return False
    parts=[p for p in path.split("/") if p]
    return len(parts)>=2 and parts[0]==owner and parts[1]==repo

def source_category(name, url):
    parts=urllib.parse.urlsplit(url)
    if documentation_host(name, parts.hostname): return "Package documentation"
    if repository_url(name, parts.hostname, parts.path): return "Package repository"
    return "Other source"

def _name_re(name):
    body=re.escape(name.lower()).replace(r"\-","[-_ ]")
    return re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])")

def _compact(text):
    return re.sub(r"[^a-z0-9]","",(text or "").lower())

def relevance_label(name, version, title, snippets, host, category):
    text="\n".join([title or "", *snippets])
    if category in ("Package documentation", "Package repository") or _name_re(name).search(text.lower()):
        return "package-matched lead"
    labels=_hostname(host).split(".") if host else []
    forms={name.lower(), name.lower().replace("-","_")}
    weak_domain=any(label in forms for label in labels) or _compact(name) in _compact(f"{text} {host or ''}")
    pin=version not in ("", "not pinned") and re.search(rf"(?<![0-9]){re.escape(version)}(?![0-9])", text) is not None
    if weak_domain or pin: return "needs relevance review"
    return "unmatched lead"

def signal_labels(snippets):
    text=" ".join(snippets).lower()
    labels=[x for x,term in (("migration","migrat"),("deprecation","deprecat"),("security mention","security")) if term in text]
    return ", ".join(labels) or "general lead"

def _tracking_param(name):
    lowered=name.lower()
    return lowered.startswith("utm_") or lowered in _TRACKING

def canonical_url(url):
    parts=urllib.parse.urlsplit(url)
    kept=[(k,v) for k,v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True) if not _tracking_param(k)]
    kept.sort()
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(kept), ""))

def _timestamp_recorded(value):
    text = "" if value is None else str(value).strip()
    if not text or text.startswith("SYNTHETIC"):
        return False
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True

def retrieval_label(value):
    text = "" if value is None else str(value).strip()
    if text.startswith("SYNTHETIC"):
        return text
    if _timestamp_recorded(text):
        return text
    return "unknown"

def _item_origin(item):
    retrieved = "" if item.get("retrieved_at") is None else str(item.get("retrieved_at")).strip()
    if retrieved.startswith("SYNTHETIC"):
        return "synthetic fixture"
    if item.get("cached") is True:
        return "cached search result"
    if item.get("cached") is False and _timestamp_recorded(retrieved):
        return "network retrieval"
    return "unknown"

_ORIGIN_LABEL = {
    "synthetic fixture": "Evidence origin: synthetic fixture. Not a live search result.",
    "cached search result": "Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.",
    "network retrieval": "Evidence origin: network retrieval of this search result. The snippet stays UNVERIFIED.",
    "mixed": "Evidence origin: mixed. This lead has more than one retrieval origin.",
    "unknown": "Evidence origin: unknown.",
}

def _annotate_origin(row):
    kinds = []
    unknown = False
    recorded = False
    for item in row.get("provenance") or []:
        item["origin"] = _item_origin(item)
        item["retrieval_label"] = retrieval_label(item.get("retrieved_at"))
        if item["origin"] not in kinds:
            kinds.append(item["origin"])
        if item["retrieval_label"] == "unknown":
            unknown = True
        elif _timestamp_recorded(item.get("retrieved_at")):
            recorded = True
    origin = kinds[0] if len(kinds) == 1 else ("mixed" if kinds else "unknown")
    row["evidence_origin"] = origin
    row["evidence_origin_label"] = _ORIGIN_LABEL[origin]
    row["version_note"] = version_note(row.get("installed_pin") or "")
    base = "Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff."
    if origin == "synthetic fixture":
        row["freshness_note"] = "Freshness does not apply to a synthetic fixture. There is no real retrieval time. " + base
    elif unknown and recorded:
        row["freshness_note"] = "Retrieval time: mixed, including at least one unknown timestamp. " + base
    elif unknown or not recorded:
        row["freshness_note"] = "Retrieval time: unknown. " + base
    else:
        row["freshness_note"] = "Retrieval time is the stored search timestamp. " + base
    return row

def _provenance(payload, snippet, cached):
    return {"query": payload.get("query",""), "snippet": snippet, "retrieved_at": payload.get("retrieved_at",""), "cached": cached}

def _same_provenance(a,b):
    return (a["query"], a["snippet"], a["retrieved_at"], a["cached"])==(b["query"], b["snippet"], b["retrieved_at"], b["cached"])

def _refresh(row):
    snippets=[p["snippet"] for p in row["provenance"]]
    parts=urllib.parse.urlsplit(row["url"])
    row["source_category"]=source_category(row["package"], row["url"])
    row["relevance"]=relevance_label(row["package"], row["installed_pin"], row["title"], snippets, parts.hostname, row["source_category"])
    row["signals"]=signal_labels(snippets)
    row["applicability"]=APPLICABILITY
    return _annotate_origin(row)

def evidence_rows(payload,name,version,cached=False,synthetic=False):
    rows=[]; index={}
    for result in payload.get("results",[]):
        link=result.get("link","")
        parts=urllib.parse.urlsplit(link)
        if parts.scheme not in ("http","https") or not parts.hostname: continue
        canon=canonical_url(link)
        snippet=result.get("snippet","")
        item=_provenance(payload, snippet, cached)
        if canon in index:
            dest=rows[index[canon]]
            if not any(_same_provenance(item, have) for have in dest["provenance"]): dest["provenance"].append(item)
            _refresh(dest)
            continue
        row={"package":name,"installed_pin":version,"title":result.get("title") or "Untitled","url":link,"canonical":canon,"status":"SYNTHETIC FIXTURE" if synthetic else "UNVERIFIED: search snippet only","provenance":[item]}
        rows.append(_refresh(row)); index[canon]=len(rows)-1
    return rows

def finalize_evidence(rows):
    merged=[]; index={}
    for row in rows:
        key=(row["package"], row["canonical"])
        if key not in index:
            copy={**row, "provenance": list(row["provenance"])}
            index[key]=len(merged); merged.append(_refresh(copy)); continue
        dest=merged[index[key]]
        for item in row["provenance"]:
            if not any(_same_provenance(item, have) for have in dest["provenance"]): dest["provenance"].append(item)
        _refresh(dest)
    merged.sort(key=lambda row: (row["relevance"]=="unmatched lead", SOURCE_TIER[row["source_category"]]))
    return merged

def scan_summary(requested_mode, rows):
    labels = {
        "fixture": "Requested mode: synthetic fixtures. This request does not call a search API.",
        "live": "Requested mode: Live search. Selecting Live is not proof a network call happened.",
        "cache": "Requested mode: saved cache only. This request does not call a search API.",
    }
    head = labels.get(requested_mode, "Requested mode: not recorded.")
    origins = []
    for row in rows:
        origin = row.get("evidence_origin") or "unknown"
        if origin not in origins:
            origins.append(origin)
    if not rows:
        body = "No leads were returned."
    elif origins == ["synthetic fixture"]:
        body = "Actual evidence origin: synthetic fixture. These are not current facts and not a live search."
    elif origins == ["cached search result"]:
        body = "Actual evidence origin: cached search result. Retrieval timestamps stay the stored times."
    elif origins == ["network retrieval"]:
        body = "Actual evidence origin: network retrieval for these search results. Snippets stay UNVERIFIED."
    elif len(origins) > 1 or "mixed" in origins:
        body = "Actual evidence origin: mixed. This scan combines more than one origin. There is no single live or cached badge."
    else:
        body = "Actual evidence origin: unknown."
    return head + " " + body

def _export_card(r):
    lines=[f"## {r['package']} ({r['installed_pin']})",f"Status: {r['status']}"]
    if r.get("version_note"): lines.append(r["version_note"])
    if r.get("evidence_origin_label"): lines.append(r["evidence_origin_label"])
    if r.get("freshness_note"): lines.append(r["freshness_note"])
    lines += [f"Relevance: {r['relevance']}",f"Source category: {r['source_category']}",r["applicability"],f"Heuristic cues: {r['signals']}",f"Source: {r['url']}","Provenance:"]
    for item in r["provenance"]:
        lines += [f"- Query: {item['query']}",f"  Retrieved: {item['retrieved_at']}; cached={item['cached']}"]
        if item.get("retrieval_label"): lines.append(f"  Retrieval time: {item['retrieval_label']}")
        if item.get("origin"): lines.append(f"  Origin: {item['origin']}")
        lines.append(f"  Snippet: {item['snippet']}")
    lines.append("")
    return lines

def export_markdown(rows):
    ranked=[r for r in rows if r["relevance"]!="unmatched lead"]
    unmatched=[r for r in rows if r["relevance"]=="unmatched lead"]
    requested = next((r.get("requested_mode") for r in rows if r.get("requested_mode")), None)
    out=["# Dependency Drift Radar evidence","","Search-result leads, not verified vulnerabilities or upgrade advice. Open source links and verify applicability before changing code.","Relevance labels are retrieval heuristics. An official host is still an unverified snippet.","A Live request is not proof a network call happened. A cache hit stays cached evidence. A missing or invalid retrieval timestamp is unknown.",""]
    if requested: out += [scan_summary(requested, rows), ""]
    out += [f"## Ranked leads ({len(ranked)})",""]
    for r in ranked: out += _export_card(r)
    out += [f"## Unmatched leads ({len(unmatched)})","","Shown so ranking cannot hide weak retrievals.","",]
    for r in unmatched: out += _export_card(r)
    return "\n".join(out)
