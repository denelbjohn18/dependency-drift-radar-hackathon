# Manual evaluation of cached leads

This file records a manual look at ranked leads already stored in `.cache`. It is not an overall search-accuracy score, a time-savings claim, or a statistical benchmark. The sample is the top 3 ranked leads in each case below. Uncertain stays its own label.

Evaluator: Cursor-assisted manual labels recorded in this workspace on 2026-10-11. These are not an independent review by the project owner.

Page text was used only as reference for the label. Pin applicability stays "not established" on every row. A relevant page is not proof the installed pin is affected. Search snippets stay UNVERIFIED. Synthetic fixtures in `fixtures/search.json` are not in these counts.

## Sample

Nine leads: three cases, top 3 after the app's existing ranking.

| Label | Count |
| --- | ---: |
| relevant lead | 3 |
| irrelevant lead | 2 |
| uncertain | 4 |

Default package scans and the manual targeted search are separate. Combining them still only describes these nine leads.

## What was counted from cache files

Six stored response files. Thirty organic results. Six distinct queries. Retrieval timestamps in those files: `2026-10-10T09:29:23.321816+00:00`, `2026-10-10T09:30:44.213886+00:00`, `2026-10-10T09:32:05.434840+00:00`, `2026-10-10T09:33:26.421452+00:00`, `2026-10-10T10:13:33.575558+00:00`, `2026-10-10T10:15:18.166715+00:00`.

Upstream call count, latency, and cost were not recorded. Two queries in a package scan are the app's plan, not proof that two calls happened. This file was built by reading `.cache`. No new search was spent.

One extra cached query, `"Pydantic" "Migration Guide" "model_dump" "dict"`, is included in the file and result totals above and is not one of the labeled cases.

## Case: pydantic==1.10.0 default package scan

Procedure: default two-query scan. Queries and retrieval times:

- `site:docs.pydantic.dev pydantic 1.10.0 migration deprecation`, retrieved `2026-10-10T09:29:23.321816+00:00`
- `pydantic 1.10.0 security advisory release notes`, retrieved `2026-10-10T09:30:44.213886+00:00`

Deduped leads: 10. Ranked: 10. Unmatched: 0. Raw results in the two stored responses: 10. The `site:` query's stored results are not on `docs.pydantic.dev`.

1. Relevant lead. [Inconsistent behavior with extra configuration when inheriting from multiple models](https://github.com/pydantic/pydantic/issues/9768). Package repository. The page describes a v1-to-v2 difference for `extra` configuration and a reply says a migration-guide note could be added. The reply author's role was not verified. The page does not establish that pin 1.10.0 must change.
2. Uncertain. [Drop support for deprecated pydantic <2](https://github.com/linkml/linkml/issues/2681). The page is about LinkML dropping Pydantic v1 for LinkML's own 1.10.0 release. That version text is not the pydantic pin.
3. Relevant lead. [Migrate to pydantic v2](https://github.com/gabrieldemarmiesse/python-on-whales/issues/452). The page is a third-party project's v2 migration, including renames and deprecation warnings. It is not Pydantic's own guide and does not establish pin applicability.

## Case: fastapi==0.95.0 default package scan

Procedure: default two-query scan. This case is noisy. Queries and retrieval times:

- `site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation`, retrieved `2026-10-10T09:32:05.434840+00:00`
- `fastapi 0.95.0 security advisory release notes`, retrieved `2026-10-10T09:33:26.421452+00:00`

Deduped leads: 10. Ranked: 10. Unmatched: 0. Raw results: 10. The stored `site:` results are not on `fastapi.tiangolo.com`.

1. Irrelevant lead. [how can I know when each version of fastapi release was out](https://github.com/fastapi/fastapi/discussions/6119). The page asks when releases such as 0.78.0 were published. It does not discuss migration, deprecation, or pin 0.95.0.
2. Uncertain. [full-stack-fastapi-template release notes](https://github.com/fastapi/full-stack-fastapi-template/blob/master/release-notes.md). The page fetch returned an empty document, so it was not judged from page text.
3. Uncertain. [fastapi repository URL with a ref parameter](https://github.com/tiangolo/fastapi?ref=blog.kiwifarm.it). The page fetch returned a short repository stub, not the README body, so the cached snippet was not confirmed.

## Case: targeted Pydantic migration query

Procedure: manual targeted search, not the default package scan. Query: `Pydantic official Migration Guide V1 V2 model_dump dict`. Retrieved: `2026-10-10T10:13:33.575558+00:00`. Deduped leads: 5. Ranked: 5. Unmatched: 0. Raw results: 5.

1. Irrelevant lead. [Types | Pydantic Docs](https://pydantic.dev/docs/validation/latest/concepts/types/). The page documents types and validation. The portion read does not present the V1-to-V2 migration guide. Documentation-host rank is why it is first.
2. Relevant lead. [Automated migration tool for Pydantic v1 to v2 #12772](https://github.com/pydantic/pydantic/discussions/12772). This is the lead already described in the README case study. The discussion is in the pydantic/pydantic repository. The post points at a migration guide and the discussion author describes a tool named Codeshift. The author's role was not checked, so this does not call that author a maintainer. Pin applicability is not established.
3. Uncertain. [Russian migration page on pydantic.com.cn](https://pydantic.com.cn/ru/migration/). The page is a V1-to-V2 migration text and mentions bump-pydantic. This pass did not verify the mirror as an official Pydantic publication. It is not the docs host the app treats as package documentation.

Machine-readable copies: `docs/evaluation.json` and `docs/evaluation.csv`.
