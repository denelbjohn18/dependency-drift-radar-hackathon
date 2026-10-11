# Draft entry, not submitted

This file is a draft. It has not been submitted.

Project: Dependency Drift Radar
Track: Open Innovation
Deadline: October 12, 2026, 23:59 IST
Public repository: https://github.com/denelbjohn18/dependency-drift-radar-hackathon

Description: Dependency Drift Radar is a local Flask app. A person enters up to five Python package names or exact pins. The app plans two SerpApi Google searches per package: a documentation-scoped migration and deprecation query, and a broader security-advisory and release-notes query. Each lead keeps its source link, snippet, query, and retrieval time. A person saves Keep, Dismiss, or Unsure. Keep means worth investigating. Dismiss means deprioritized. Unsure stays unresolved. The next-check brief downloads those decisions beside the original provenance. Snippets stay unverified. The app does not apply an upgrade.

Three modes ship. Synthetic fixtures run after clone with no key and are labeled synthetic. Saved cache only reads privately stored responses and makes no network call; a clone does not include that cache. Live uses `SERPAPI_API_KEY` from the local environment and that account's free quota, never a key file in the repository. The requested mode is recorded separately from the evidence origin. Selecting Live does not turn a cache hit into a new network call.

The recorded default case is `pydantic==1.10.0` and `fastapi==0.95.0` in saved-cache mode. The kept lead was pydantic issue 9768. Applicability to pin 1.10.0 was left not established. The FastAPI default top 3 in that sample still had no relevant lead. Details: `docs/OUTCOME_PROOF.md` and `docs/EVALUATION.md` (nine leads: relevant 3, irrelevant 2, uncertain 4; Cursor-assisted labels, not an independent owner review).

Meaningful SerpApi use: SerpApi Google Search is the live evidence source, two queries per package, with local caching so a repeated query does not spend another search. The real responses in the private cache were originally retrieved using SerpApi. This documentation pass spends no searches and does not use a key. Synthetic fixtures are not that use.

Lead: Denel John
Email: helpdenel@gmail.com
Phone: [verify participant phone before submission]
Occupation: [verify participant occupation before submission]
Professional experience: [verify actual value before submission]
Existing project: No. This repository's history begins on 2026-10-11 with the commit "Add the Dependency Drift Radar hackathon app." No earlier project is recorded in this tree.
How learned / community source: [inspect form choices; no unsupported community affiliation]
Demo: [replace with the NEW under-3-minute public/unlisted video URL after upload and incognito access check]
AI tools: Draft in `docs/AI_DISCLOSURE.md`. That draft names Instinct and Cursor for implementation, tests, documentation, and the demo script, and it still asks the participant to replace the review sentence if that review has not happened. This documentation pass was done in Cursor. That draft is not marked here as the participant's final confirmation.

Still open before anyone submits: phone, occupation, professional experience, and community source; the new demo URL after an incognito check; participant confirmation of the AI disclosure; and an explicit decision to submit. This draft is not an entry.
