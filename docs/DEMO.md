# Demo recording, 90–120 seconds

Record the local Flask app at http://127.0.0.1:8501. Keep the recording between 90 and 120 seconds, and strictly under 3 minutes. Narration is optional. Use the polished local UI.

Use Saved cache only and a real stored response. The card on screen needs to show cached, the original query, and the original retrieval time. Leave synthetic fixtures off this recording. Do not start a live search while filming. A key is not required for a cache-only recording. Playback uses the private `.cache/` already on the machine. A fresh clone does not include that cache, so film on the machine that already has these stored responses.

Do not make a new SerpApi call for the recording. Do not show the API key, an account page, or a private review note.

## Shot list: shipped default case

This path is the default two-query form. It is the case in `docs/OUTCOME_PROOF.md`. It does not use the manually cached query `Pydantic official Migration Guide V1 V2 model_dump dict`.

0:00–0:15. The form shows `pydantic==1.10.0` and `fastapi==0.95.0`. Run mode is Saved cache only. Leave the notice visible: this request does not call a search API.

0:15–0:40. Open the card for [pydantic issue 9768](https://github.com/pydantic/pydantic/issues/9768). Show `UNVERIFIED: search snippet only`, cached, query `site:docs.pydantic.dev pydantic 1.10.0 migration deprecation`, and retrieval time `2026-10-10T09:29:23.321816+00:00`. The origin line stays "cached search result".

0:40–1:05. Open that GitHub URL and compare it with the snippet. The page's v1 sample prints pydantic 1.10.13 and accepts an extra field; the v2 sample prints pydantic 2.7.2 and rejects one inheritance order. Say that applicability to installed pin 1.10.0 is not established. The reply author's role was not independently verified.

1:05–1:25. Save the review as Keep. Leave version applicability on "not established". Leave the note, applicability URL, and rationale empty so no private note is on screen. Keep means worth investigating. The save writes `.reviews/` on this machine and does not call SerpApi.

1:25–1:50. Download the next-check brief. Show the kept section: source URL, query, retrieval time, origin cached search result, and applicability not established.

1:50–2:00. One sentence on the same page: the other leads stay unresolved. The FastAPI release-date discussion is still listed and was not a useful migration lead in the nine-lead sample. Stop.

## If the default cache card is not what you can open

Say on screen that you are leaving the default scan. The manual cache entry `Pydantic official Migration Guide V1 V2 model_dump dict`, retrieved `2026-10-10T10:13:33.575558+00:00`, is a targeted query, not the default form. The shot list above does not need it.

## After the recording

Upload a new video, public or unlisted, under 3 minutes. The link has to open in an incognito window without an access request. Until that check is done, the demo field in `docs/SUBMISSION.md` stays:

[replace with the NEW under-3-minute public/unlisted video URL after upload and incognito access check]

This documentation pass did not film or upload that video.
