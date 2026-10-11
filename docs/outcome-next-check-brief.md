# Next-check brief

This brief is a maintainer work list. Human decisions sit beside the search leads they refer to.
A saved decision does not verify a snippet, establish CVE applicability, or choose a safe upgrade.
Search snippets remain UNVERIFIED. Synthetic fixtures remain SYNTHETIC.
A Live request is not proof a network call happened. A cache hit stays cached evidence.
A missing or invalid retrieval timestamp is unknown. Freshness is the age of retrieved evidence, not proof a page or claim is current. There is no expiry cutoff.
Keep means worth investigating. Dismiss means deprioritized, not fixed or resolved.
Unresolved includes unreviewed leads, unsure decisions, and reviews marked needs re-review: evidence changed.
A lead absent from a later search is not resolved and is not automatically dismissed.

All: 20. Unresolved: 19. Kept: 1. Dismissed: 0.

Requested mode: saved cache only. This request does not call a search API. Actual evidence origin: cached search result. Retrieval timestamps stay the stored times.

## Kept for a next check (1)

Export section: reviewed-kept

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Keep
Meaning: worth investigating. This is not an upgrade approval and not proof of a vulnerability.
Review updated: 2026-10-11T13:44:14.386514+00:00
Reviewed against pin: 1.10.0
Evidence status when saved: UNVERIFIED: search snippet only
Reviewed against retrieval: 2026-10-10T09:29:23.321816+00:00
Reviewer note: Cursor-assisted review, not an independent decision by Denel. Kept as a useful investigation. Source category Package repository matches the URL: this is an issue in pydantic/pydantic, not package documentation and not a third-party project. The page compares multiple-parent model inheritance with extra configuration. Its v1 sample prints pydantic 1.10.13 and accepts an extra field in both inheritance orders. Its v2 sample prints pydantic 2.7.2 and rejects one order with extra_forbidden. The assigned account sydney-runkle replies that the last parent config overrides earlier parents and that a migration-guide note could be added. That account's role was not independently verified. Applicability to installed pin 1.10.0 is not established: the page's v1 sample is 1.10.13, not this pin. Next check: inspect this project's model inheritance and extra configuration against that difference on https://github.com/pydantic/pydantic/issues/9768. No target version, severity, or upgrade claim.
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Package repository
Pin applicability: not established
Heuristic cues: migration
Source: https://github.com/pydantic/pydantic/issues/9768
Provenance:
- Query: site:docs.pydantic.dev pydantic 1.10.0 migration deprecation
  Retrieved: 2026-10-10T09:29:23.321816+00:00; cached=True
  Retrieval time: 2026-10-10T09:29:23.321816+00:00
  Origin: cached search result
  Snippet: I am migrating from Pydantic v1 to v2 and have encountered some inconsistencies and validation issues, particularly with the extra configuration ...
Next check: open the source and any reviewer-entered applicability URL, then compare the page with the installed pin. The search snippet is not that check.

## Unresolved (19)

Export section: unresolved

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: deprecation
Source: https://github.com/linkml/linkml/issues/2681
Provenance:
- Query: site:docs.pydantic.dev pydantic 1.10.0 migration deprecation
  Retrieved: 2026-10-10T09:29:23.321816+00:00; cached=True
  Retrieval time: 2026-10-10T09:29:23.321816+00:00
  Origin: cached search result
  Snippet: We have deprecated Pydantic <2 support for a little while now. It is time to drop support for our 1.10.0 release.
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: deprecation
Source: https://github.com/gabrieldemarmiesse/python-on-whales/issues/452
Provenance:
- Query: site:docs.pydantic.dev pydantic 1.10.0 migration deprecation
  Retrieved: 2026-10-10T09:29:23.321816+00:00; cached=True
  Retrieval time: 2026-10-10T09:29:23.321816+00:00
  Origin: cached search result
  Snippet: Most changes from pydantic v1 to v2 involves renames, which will work but give DeprecationWarnings when using v2.
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: migration
Source: https://github.com/permitio/fastapi_websocket_rpc/discussions/23
Provenance:
- Query: site:docs.pydantic.dev pydantic 1.10.0 migration deprecation
  Retrieved: 2026-10-10T09:29:23.321816+00:00; cached=True
  Retrieval time: 2026-10-10T09:29:23.321816+00:00
  Origin: cached search result
  Snippet: Pydantic enourages to migrate to 2.x version, pydantic dependency for both rpc and pubsub packages is limited to versions between 1.9.1 and 2. https://docs. ...
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: migration
Source: https://github.com/sabre-coder/pydantic-validator-migration-samples
Provenance:
- Query: site:docs.pydantic.dev pydantic 1.10.0 migration deprecation
  Retrieved: 2026-10-10T09:29:23.321816+00:00; cached=True
  Retrieval time: 2026-10-10T09:29:23.321816+00:00
  Origin: cached search result
  Snippet: This preview contains exactly three original migration rules for coding agents and developers. V1 does not support Python 3.14 or later.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Package repository
Pin applicability: not established
Heuristic cues: general lead
Source: https://github.com/fastapi/fastapi/discussions/6119
Provenance:
- Query: site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation
  Retrieved: 2026-10-10T09:32:05.434840+00:00; cached=True
  Retrieval time: 2026-10-10T09:32:05.434840+00:00
  Origin: cached search result
  Snippet: The release notes do not include when each version was out. I would really like to know when 0.78.0 was released? and when the other releases were out?
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://secure.software/pypi/packages/pydantic/dependencies/2.11.10
Provenance:
- Query: pydantic 1.10.0 security advisory release notes
  Retrieved: 2026-10-10T09:30:44.213886+00:00; cached=True
  Retrieval time: 2026-10-10T09:30:44.213886+00:00
  Origin: cached search result
  Snippet: Supply chain risk analysis for pydantic@2.11.10. Learn more about package security, deployment risks, vulnerabilities, popularity, versions, and more with ...
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://cve.imfht.com/product/pydantic?lang=en
Provenance:
- Query: pydantic 1.10.0 security advisory release notes
  Retrieved: 2026-10-10T09:30:44.213886+00:00; cached=True
  Retrieval time: 2026-10-10T09:30:44.213886+00:00
  Origin: cached search result
  Snippet: pydantic — Vulnerabilities & Security Advisories 2. All 2 CVE vulnerabilities found in pydantic, with AI-generated Chinese analysis, references, and POCs.
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://anaconda.org/conda-forge/pydantic/files/manage?type=&version=1.10.9
Provenance:
- Query: pydantic 1.10.0 security advisory release notes
  Retrieved: 2026-10-10T09:30:44.213886+00:00; cached=True
  Retrieval time: 2026-10-10T09:30:44.213886+00:00
  Origin: cached search result
  Snippet: A new user experience is coming soon! These rolling changes are ongoing … pydantic 4 Data validation and settings management using python type hinting
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://www.cybersecurity-help.cz/vdb/soft/fedoraproject/python-pydantic/
Provenance:
- Query: pydantic 1.10.0 security advisory release notes
  Retrieved: 2026-10-10T09:30:44.213886+00:00; cached=True
  Retrieval time: 2026-10-10T09:30:44.213886+00:00
  Origin: cached search result
  Snippet: List of all known security vulnerabilities in python-pydantic, including CVE and CWE identifiers, severity, exploit and KEV status, first fixed releases, ...
Next check: not in the kept queue.

### pydantic (1.10.0)
Installed pin is investigation context only.
Installed version: exact pin 1.10.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://nvd.nist.gov/vuln/search?resultType=records&cpeFilterMode=cpe&cpeName=cpe:2.3:a:pydantic:pydantic:0.11.1:*:*:*:*:*:*:*
Provenance:
- Query: pydantic 1.10.0 security advisory release notes
  Retrieved: 2026-10-10T09:30:44.213886+00:00; cached=True
  Retrieval time: 2026-10-10T09:30:44.213886+00:00
  Origin: cached search result
  Snippet: Pydantic is a data validation and settings management using Python type hinting. causes validation to run forever with 100% CPU usage (on one CPU). 1-888-282- ...
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://github.com/fastapi/full-stack-fastapi-template/blob/master/release-notes.md
Provenance:
- Query: site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation
  Retrieved: 2026-10-10T09:32:05.434840+00:00; cached=True
  Retrieval time: 2026-10-10T09:32:05.434840+00:00
  Origin: cached search result
  Snippet: Full-stack web application template with FastAPI, React, SQLModel, PostgreSQL, Vite, Tailwind CSS, shadcn/ui, FastAPI Cloud, and Docker Compose.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://github.com/tiangolo/fastapi?ref=blog.kiwifarm.it
Provenance:
- Query: site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation
  Retrieved: 2026-10-10T09:32:05.434840+00:00; cached=True
  Retrieval time: 2026-10-10T09:32:05.434840+00:00
  Origin: cached search result
  Snippet: The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). One of the fastest Python frameworks available.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://news.ycombinator.com/item?id=36635523
Provenance:
- Query: site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation
  Retrieved: 2026-10-10T09:32:05.434840+00:00; cached=True
  Retrieval time: 2026-10-10T09:32:05.434840+00:00
  Origin: cached search result
  Snippet: FastAPI is already being used in production in many applications and systems. And the test coverage is kept at 100%.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://github.com/tiangolo/fastapi?ref=hackernoon.com
Provenance:
- Query: site:fastapi.tiangolo.com fastapi 0.95.0 migration deprecation
  Retrieved: 2026-10-10T09:32:05.434840+00:00; cached=True
  Retrieval time: 2026-10-10T09:32:05.434840+00:00
  Origin: cached search result
  Snippet: The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). One of the fastest Python frameworks available.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://getsafety.com/packages/pypi/fastapi-health
Provenance:
- Query: fastapi 0.95.0 security advisory release notes
  Retrieved: 2026-10-10T09:33:26.421452+00:00; cached=True
  Retrieval time: 2026-10-10T09:33:26.421452+00:00
  Origin: cached search result
  Snippet: Known vulnerabilities and security issues detected in the extension's dependencies and code. No vulnerabilities found for this package. Safety Discovered ...
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://data.safetycli.com/packages/pypi/tempest-fastapi-sdk/changelog?page=4&
Provenance:
- Query: fastapi 0.95.0 security advisory release notes
  Retrieved: 2026-10-10T09:33:26.421452+00:00; cached=True
  Retrieval time: 2026-10-10T09:33:26.421452+00:00
  Origin: cached search result
  Snippet: Safety actively analyzes 1028474 Python packages for vulnerabilities to keep your Python projects secure. Releases Has known vulnerabilities 69.0
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://insights.linuxfoundation.org/project/fastapi/security?timeRange=past365days&start=2025-08-16&end=2026-08-16
Provenance:
- Query: fastapi 0.95.0 security advisory release notes
  Retrieved: 2026-10-10T09:33:26.421452+00:00; cached=True
  Retrieval time: 2026-10-10T09:33:26.421452+00:00
  Origin: cached search result
  Snippet: Check FastAPI security and best practices, including vulnerabilities, dependencies, licensing, and governance compliance.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: general lead
Source: https://data.safetycli.com/packages/pypi/tempest-fastapi-sdk/changelog?page=69&
Provenance:
- Query: fastapi 0.95.0 security advisory release notes
  Retrieved: 2026-10-10T09:33:26.421452+00:00; cached=True
  Retrieval time: 2026-10-10T09:33:26.421452+00:00
  Origin: cached search result
  Snippet: Safety actively analyzes 1029146 Python packages for vulnerabilities to keep your Python projects secure. Scan your dependencies. Page 69 of 70. 0.6.0.
Next check: not in the kept queue.

### fastapi (0.95.0)
Installed pin is investigation context only.
Installed version: exact pin 0.95.0.
Decision: Unreviewed
Meaning: unreviewed. This stays unresolved until a person saves a decision.
No saved review.
Reviewer note: 
Version applicability: not established
Version applicability is a reviewer-entered assessment, not automatic verification.
Status: UNVERIFIED: search snippet only
Evidence origin: cached search result. A Live request does not turn a cache hit into a new network call.
Retrieval time is the stored search timestamp. Freshness is the age of this retrieved evidence, not proof the webpage or the technical claim is current. This tool has no expiry cutoff.
Relevance: package-matched lead
Source category: Other source
Pin applicability: not established
Heuristic cues: security mention
Source: https://blog.stackademic.com/guide-to-building-secure-backends-in-fastapi-in-2024-dcbccc0bfab0
Provenance:
- Query: fastapi 0.95.0 security advisory release notes
  Retrieved: 2026-10-10T09:33:26.421452+00:00; cached=True
  Retrieval time: 2026-10-10T09:33:26.421452+00:00
  Origin: cached search result
  Snippet: – Subscribe to security advisories for the dependencies you use. This can often be done through version control platforms like GitHub or GitLab.
Next check: not in the kept queue.

## Dismissed — deprioritized, not resolved (0)

Export section: reviewed-dismissed

None.
