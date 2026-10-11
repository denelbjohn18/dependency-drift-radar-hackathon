# Outcome proof, 2026-10-11

This is one cache-only investigation through the default form. It is not a benchmark and not a claim that the project won anything. No Targeted follow-up control was added. The default scan already returned a lead that survived a source-page read.

Reviewer: Cursor-assisted. This is not an independent decision by Denel.

## What was run

Saved cache only. Requirements left as the form default:

```
pydantic==1.10.0
fastapi==0.95.0
```

The process had no search key. The server log for this run shows only `127.0.0.1` requests: the page, one `POST /`, one `POST /review`, and `GET /brief/...`. No SerpApi host appears in that log.

Cached responses on disk: 6 files, 30 organic results, 6 queries. Timestamps: `2026-10-10T09:29:23.321816+00:00`, `2026-10-10T09:30:44.213886+00:00`, `2026-10-10T09:32:05.434840+00:00`, `2026-10-10T09:33:26.421452+00:00`, `2026-10-10T10:13:33.575558+00:00`, `2026-10-10T10:15:18.166715+00:00`. Those files stayed in `.cache` and are not in the source archive.

## Default scan

The app queries for this form are:

- `site:docs.pydantic.dev pydantic 1.10.0 migration deprecation`, retrieved `2026-10-10T09:29:23.321816+00:00`, 5 stored results. None of those stored links are on `docs.pydantic.dev`.
- `pydantic 1.10.0 security advisory release notes`, retrieved `2026-10-10T09:30:44.213886+00:00`, 5 stored results.
- `site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation`, retrieved `2026-10-10T09:32:05.434840+00:00`, 5 stored results. None of those stored links are on `fastapi.tiangolo.com`.
- `fastapi 0.95.0 security advisory release notes`, retrieved `2026-10-10T09:33:26.421452+00:00`, 5 stored results.

The screen showed 20 ranked leads and 0 unmatched. All 20 stayed listed. The FastAPI release-date discussion was still on the page after the review.

Lead used: [Inconsistent behavior with extra configuration when inheriting from multiple models](https://github.com/pydantic/pydantic/issues/9768). Package `pydantic`, exact pin `1.10.0`. Source category: Package repository. Status on the card: `UNVERIFIED: search snippet only`. The card's query and retrieval time are the first query above. Origin: cached search result.

The page is an issue in `pydantic/pydantic`. That is the package repository, not package documentation and not a third-party project.

What the page supports: the report compares multiple-parent inheritance with `extra` configuration. The v1 sample prints pydantic 1.10.13 and accepts an extra field in both inheritance orders. The v2 sample prints pydantic 2.7.2 and rejects one order with `extra_forbidden`. The assigned account sydney-runkle replies that the last parent config overrides earlier parents and that a migration-guide note could be added.

What remains unknown: whether pin 1.10.0 behaves like the page's 1.10.13 sample. The account's role was not independently verified. The page does not say this pin must change. Applicability was left **not established**. No target version, severity, or upgrade safety is claimed.

Next check: inspect this project's model inheritance and extra configuration against that difference on the issue URL above.

Saved from the lead form: Keep, at `2026-10-11T13:44:14.386514+00:00`, reviewed against pin 1.10.0 and retrieval `2026-10-10T09:29:23.321816+00:00`. The note says Cursor-assisted and is not an independent decision by Denel.

Export: `docs/outcome-next-check-brief.md`. It keeps the source, query, snippet, original retrieval time, the reviewer note, applicability not established, and the other 19 unresolved leads.

Screenshots:

- `docs/outcome-screenshots/01-default-scan-lead.png`
- `docs/outcome-screenshots/04-fastapi-noise-still-listed.png`
- `docs/outcome-screenshots/06-review-saved-detail.png`
- `docs/outcome-screenshots/08-brief-kept-section.png`
- `docs/outcome-screenshots/10-brief-next-check.png`

`09-brief-provenance.png` is the same brief, scrolled to the query line. The brief download from the app is an attachment. The readable shots are that file shown with line wrapping. A raw text view of the same file crowded the long note onto one line.

## FastAPI default scan

Held out of the ranking rule, then checked again. Its own top 3 did not change:

1. `https://github.com/fastapi/fastapi/discussions/6119` — irrelevant lead. Release dates, not migration or pin 0.95.0.
2. `https://github.com/fastapi/full-stack-fastapi-template/blob/master/release-notes.md` — uncertain. The earlier page fetch was empty.
3. `https://github.com/tiangolo/fastapi?ref=blog.kiwifarm.it` — uncertain. The earlier fetch was a short repository stub.

This top 3 still has no relevant lead. Ranking did not create one. That failure stands.

On the combined default form, source tier used to place that FastAPI discussion second, ahead of the LinkML and python-on-whales leads. After the change it is sixth. It is still listed. Pydantic's own top 3, scanned alone, stays issue 9768, LinkML issue 2681, python-on-whales issue 452.

## Ranking, and what it is not

Before this pass, source tier could put generic documentation above a migration lead. On the cached query `Pydantic official Migration Guide V1 V2 model_dump dict` (retrieved `2026-10-10T10:13:33.575558+00:00`, not a default-scan query), the first result was the Types docs page and the migration discussion was second.

After: discussion 12772, then the pydantic.com.cn page, then a LangChain forum result. The Types page is fifth. The historical nine-lead labels are unchanged in `docs/EVALUATION.md`. A separate note there covers this new order. The LangChain reply that was fetched is uncertain, not a pin finding.

An unlabeled cached query, `"Pydantic" "Migration Guide" "model_dump" "dict"` (retrieved `2026-10-10T10:15:18.166715+00:00`), moved a third-party page with migration wording ahead of two pydantic repository issues whose snippets did not contain that wording. That page was not read for a new label. Heuristic order is not verification.

## Follow-up

Not used. The default scan supported the investigation above, so no Targeted follow-up field was added and no extra cache lookup was presented as the default query.

## Gaps

Pin 1.10.0 applicability is not established. The `site:` queries did not return pages on those documentation hosts. The FastAPI default top 3 is still not a useful migration case. No live search was run. A local extract of the backup archive is not a hosted download check.
