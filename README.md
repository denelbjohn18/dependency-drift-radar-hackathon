# Dependency Drift Radar
A local evidence dashboard for Python dependency migrations, deprecations and security investigation. Paste up to five package names or exact pins. SerpApi Google Search supplies two focused evidence searches per package. Links, search snippets, queries and retrieval timestamps stay together; Markdown export makes the research portable. A person can save a review decision for each lead and download a next-check brief.

This is NOT a vulnerability scanner. It never claims a safe upgrade version, full-page verification, actual CVE applicability or semver compatibility. Snippet-only findings are always marked UNVERIFIED. Synthetic fixtures are prominently labeled and are not evidence of live API functionality.

## Start on macOS (Python 3.10+)
```sh
unzip dependency-drift-radar.zip
cd dependency-drift-radar
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py
```
Open http://127.0.0.1:8501. Try the synthetic fixtures first. No paid API, model, hosting or deployment is needed. Alternatively `uv sync --frozen`, `uv run python app.py` uses the included lockfile.

## Live mode
Create a free SerpApi account with helpdenel@gmail.com. The official pricing page currently lists $0,250searches/month,50/hour. Never upgrade, add a payment card or buy credits for this project.
Enter the key without writing it to shell history:
```sh
read -s SERPAPI_API_KEY
export SERPAPI_API_KEY
python app.py
```
Paste the API key when the terminal waits, then press Enter. Restarting the app loads the key. Do not write the key into source, a README, screenshots, video or chat. Use the secure vault link provided separately for any handoff.
Choose Live SerpApi and scan ONE package first. Expect roughly80seconds for the second uncached query: the server paces calls below50/hour. Cached searches do not spend another request and show original retrieval time.

## Honest free-tier controls
- Max5packages/scan,2queries/package (10 searches max).
- Max20live request attempts per server process, including failures.
- Server runs single-threaded and spaces uncached request attempts80seconds apart. During a live scan its page can wait, up to~12min for5packages. Start with1package for the demo.
- Cache uses query hashes and stores allowlisted result fields only. It never stores keys or provider metadata.
- Restarting resets process budget. It does not reset SerpApi monthly/hourly quota. Check your real account dashboard before live runs.
- .cache persists older evidence, not current truth. Delete .cache only intentionally; this spends searches again. Cached retrieval timestamps remain visible.
- If requests fail or quota ends, stop. No retries, paid fallback or additional LLM is used.

## Scope and limitations
Python simple exact pins and names only. No requirements includes, URLs, editables, ranges or environment markers. First pin wins for duplicate package names. Known documentation domains supported for FastAPI,Pydantic,Django,Flask,Requests,NumPy,Pandas,SQLAlchemy; other packages use a PyPI-scoped first search and a broader second search. Search snippets may be truncated, stale, misleading or irrelevant. Domain labels are navigation aids, not verified publisher identities. Evidence is research for a human to verify, not upgrade advice.

The app searches source references; it does not fetch or execute package code, crawl linked pages or install user requirements. It binds localhost only, uses CSRF form tokens and escapes displayed text. Do not expose the development server publicly. Cached queries may reveal dependency names; do not include confidential/private package names. Export is plain Markdown, not executable content.

## Case study: finding a Pydantic migration lead
Input pin: `pydantic==1.10.0`. That pin is investigation context only.

This lead comes from one cached targeted search, not from the default two-query package scan. Query: `Pydantic official Migration Guide V1 V2 model_dump dict`. Retrieved: `2026-10-10T10:13:33.575558+00:00`.

Organic result used here:
- Title: Automated migration tool for Pydantic v1 to v2 #12772
- Link: https://github.com/pydantic/pydantic/discussions/12772
- Snippet, UNVERIFIED search snippet only: First off, I want to thank the Pydantic team for the excellent migration guide. It is thorough and covers virtually every breaking change between v1 and v2.

PyPI lists both Homepage and Source for pydantic as https://github.com/pydantic/pydantic. The result URL is a discussion in that repository. That locates the page. It does not make the post official Pydantic advice, and the author's role was not checked.

Page-checked finding: the discussion post says, "First off, I want to thank the Pydantic team for the excellent migration guide. It is thorough and covers virtually every breaking change between v1 and v2." The words "migration guide" link to https://docs.pydantic.dev/latest/migration/. The same post says the author built a tool named Codeshift and lists `.dict()` to `.model_dump()` among mechanical V1-to-V2 renames. The post does not mention bump-pydantic. The narrow conclusion is that this official-repository discussion is a lead to migration documentation and to an automated migration tool described by the discussion author.

Follow-on page research, not a SerpApi organic result: opening that guide link resolved to https://pydantic.dev/docs/validation/latest/get-started/migration/ ("Migration Guide | Pydantic Docs"). Its rename table has columns Pydantic V1 and Pydantic V2, with the row `dict()` | `model_dump()`. That guide URL is not in the cached organic results for this query.

Discovery limitation: generic package queries produced third-party noise, and this targeted query returned a translated mirror and other third-party pages before this official-repository discussion. Retrieval labels do not mean verified facts.

Pin applicability: not established. This does not show that a tool supports exactly 1.10.0, that this pin is vulnerable or deprecated, that an upgrade is required, or that it is incompatible with FastAPI 0.95.0. No automated migration was run.

Practical next step: read the linked guide and inspect any tool on its own project page, then test a migration on a separate branch. This research app does not perform that migration.

## Review queue
Each deduped lead starts unreviewed. Saving Keep, Dismiss, or Unsure is a human decision. Keep means the lead is worth investigating. It is not an upgrade approval and it is not proof of a vulnerability. Dismiss means deprioritized. It is not fixed or resolved. Unsure stays unresolved. A snippet is never promoted to a verified claim.

Version applicability stays "not established" until a person saves "reviewer says applicable" or "reviewer says not applicable" with a source URL and a rationale. That pair is a reviewer-entered assessment, not automatic verification. The fields are not filled from the pin, query, or snippet. Search snippets stay UNVERIFIED. Synthetic fixtures stay SYNTHETIC.

Reviews are stored in `.reviews/` on this machine, separate from `.cache/`. They are gitignored and not synced. Restarting the app and rerunning a cached search keeps the decision. The card shows the retrieval time that decision was saved against. If a later result changes that lead's title or snippet, the saved decision and note remain, the card shows "needs re-review: evidence changed", and the lead returns to Unresolved until a person saves it again. A lead missing from a later search is not dismissed.

The next-check brief is a Markdown download of those decisions beside the original source, queries, snippets, and retrieval times. It is a work list, not a vulnerability report.

TODO: capture a real screenshot from the app of this cached result, including the source, the exact query, the retrieval timestamp, and the UNVERIFIED label. No screenshot is included. The targeted search was a manual investigation check, not output from the default two-query package scan, and the current screen has no custom-query control that would show this cache entry.

## Before submitting
Run a live scan with your real key, verify links and screenshots, record<3min screen demo with local app working. Synthetic fixture runs alone do NOT prove meaningful SerpApi functionality. Review docs/SUBMISSION.md, replace placeholders, verify repo+demo links in incognito, and only publish or submit after explicit approval.

## Original work and AI disclosure
Prepared for the SerpApi India Hackathon 2026 on October9. New project. AI assisted implementation, tests, docs and demo script. The participant must review, run and stand behind it. See docs/AI_DISCLOSURE.md and docs/DEMO.md.

Official sources:
https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html
https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html
https://serpapi.com/pricing
