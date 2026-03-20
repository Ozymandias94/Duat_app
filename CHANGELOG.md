# CHANGELOG.md
## Egyptian Astrology App — Session Log

Newest entries at the top. One entry per session in which code was written
or changed. This file is the only memory between sessions — maintain it
carefully.

---

## [2026-03-20] — Codebase audit: full inventory of what exists, what is missing, and what conflicts with spec

### Built or changed
- No code written this session.
- Comprehensive audit of every file and directory completed.
- Feature status cross-referenced against the full Launch list in docs/features.md.
- Calculation layer, API integration, and hemerological calendar all verified.

### Files created or modified
- CHANGELOG.md — added this entry

### Feature plan items advanced
- None advanced. Audit only.
- Feature #3 (Natal Birth Reading) confirmed as the correct starting point.

### Decisions made not covered by the spec
- None. Audit only.

### Left open for next session
- **LOCKED RULE VIOLATION — fix first:** `app/systems/western.py` line 12 says
  "Placidus houses" in the system prompt string. Must change to "Whole Sign
  houses" before writing any other code.
- **Swiss Ephemeris not integrated:** `pyswisseph` is in requirements.txt but
  never imported or called anywhere. kerykeion is used instead for Western and
  Vedic. Egyptian system has no calculation at all. Must implement pyswisseph
  before any reading data is trustworthy.
- **36-decan lookup not implemented:** Egyptian system maps 12 calendar date
  ranges to deity signs only — no degree-level decan placement exists. The
  36-decan system requires pyswisseph for degree accuracy.
- **Lots not calculated:** Lot of Fortune and Lot of the Daimon are fully
  specified in engine.md Sections 7 and 12.5 but have zero code.
- **Natal chart not cached:** `cache.py` caches reading output text only.
  Engine Section 12.5 requires persistent natal chart data cached per user.
  Currently the full chart recalculates on every API call.
- **Transit detection layer missing:** No retrograde, eclipse, Saturn return,
  Jupiter return, planetary station, or Sothis detection exists. Engine
  Section 12.6 defines the full requirement. Daily readings currently pass
  only static natal data — no transits.
- **Hemerological calendar not implemented:** No lookup table, no date
  matching, no Khoiak standing layer (Oct 22–Nov 19). Engine Section 11.6.1
  defines 17 charged dates. None are implemented.
- **Duplicate engine file:** `app/systems/egyptian_astrology_engine.md` is a
  copy of `docs/engine.md`. The copy may drift. Remove or symlink; the
  canonical file is `docs/engine.md`.
- **No UI code exists:** Features #7–#15 (Sky Map, Explorer, Oracle Chamber,
  Ka Reading, Circle of Ka, Temple Library, Shareable Cards, Partial Profile)
  have no frontend implementation. No mobile app code at all.
- **Reading request format (Section 12.4):** Current user prompt is simpler
  than the full spec likely requires. Verify against Section 12.4 when
  implementing natal chart pipeline.

### Audit findings: what exists
- FastAPI scaffolding: endpoints at /horoscope/systems and /horoscope/daily
- Anthropic API integration: claude-sonnet-4-6, fallback to haiku, caching
- engine.md correctly loaded as system prompt for Egyptian system
- Egyptian zodiac: 12 signs mapped to deities by calendar date range (not
  36-decan, not degree-level)
- Reading output cache: per-day, keyed by birth data + system

### Audit findings: Launch feature status
- Feature #1 (Daily Reading): PARTIAL — endpoint and Claude call exist, but
  input data is only a static sign lookup. No transits, no decans, no Lots.
- Feature #2 (Push Notification): NOT STARTED
- Feature #3 (Natal Birth Reading): NOT STARTED
- Feature #4 (Transit Readings): NOT STARTED
- Feature #5 (Hemerological Calendar): NOT STARTED
- Feature #6 (Sothis Annual Reading): NOT STARTED
- Feature #7 (Egyptian Sky Map): NOT STARTED
- Feature #8 (Decan & House Explorer): NOT STARTED
- Feature #9 (The Ka Reading): NOT STARTED
- Feature #10 (Circle of Ka): NOT STARTED
- Feature #11 (The Oracle Chamber): NOT STARTED
- Feature #12 (Temple Library — Deity Glossary): NOT STARTED
- Feature #13 (Temple Library — Sacred Calendar): NOT STARTED
- Feature #14 (Shareable Reading Cards): NOT STARTED
- Feature #15 (Partial Profile for Non-Users): NOT STARTED

### Recommended sequence for next session
1. Fix western.py:12 (Placidus → Whole Sign) — locked rule violation
2. Implement pyswisseph planetary position calculation (replace kerykeion)
3. Implement 36-decan lookup by degree (Sun, Moon, Ascendant, all planets)
4. Implement Whole Sign house assignment
5. Implement Lot of Fortune and Lot of the Daimon (engine Section 7)
6. Implement natal data caching (engine Section 12.5 full field list)
7. Wire natal data into reading request format (engine Section 12.4)
8. Implement hemerological calendar module (engine Section 11.6.1)
9. Implement transit detection layer (engine Section 12.6)
10. Then Feature #1 (Daily Reading) becomes real; Feature #3 (Natal Birth
    Reading) follows immediately after

### Engine sections referenced
- Section 7 — Lots (Lot of Fortune, Lot of the Daimon): verified no code
- Section 11.6.1 — hemerological dates: verified no code
- Section 12.4 — reading request format: partial match only
- Section 12.5 — natal data fields and caching: verified no code
- Section 12.6 — transit detection: verified no code

---

## [2026-03-19] — Project initialization

### Built or changed
- Created project file structure
- Wrote CLAUDE.md (session orientation and locked rules)
- Wrote docs/engine.md (reading engine v1.3 — dual-purpose: project
  documentation and Anthropic API system prompt)
- Wrote docs/features.md (full feature plan, Launch through V3)
- Wrote docs/design.md (color schemes, typography, layout, motion)

### Files created or modified
- CLAUDE.md — created
- CHANGELOG.md — created
- docs/engine.md — created (engine v1.3, 13 sections)
- docs/features.md — created (22 features across 4 release versions)
- docs/design.md — created (4 color schemes, typography, layout, sky map,
  animation, anti-patterns)

### Feature plan items advanced
- None — this session was project setup only. No application code written.

### Decisions made not covered by the spec
- docs/ directory chosen over flat file structure to keep CLAUDE.md concise
  and allow situational reading of supporting files
- engine.md marked as DUAL PURPOSE at top of file — serves as both project
  documentation and the literal system prompt passed to the Anthropic API
  on every reading generation call. This distinction must be preserved.

### Left open for next session
- No application code exists yet. Start with the calculation layer:
  Swiss Ephemeris integration and the natal chart generation pipeline.
  Feature #3 (Natal Birth Reading) is the correct first build target —
  everything else depends on having natal data.
- Recommended first session scope: ephemeris setup → birth data input →
  position calculation → decan lookup → natal field caching (engine
  Section 12.5). Do not start the AI reading call until the calculation
  layer is verified accurate.

### Engine sections referenced
- Section 12 (Implementation instructions) — reviewed for project setup
- Section 12.2 (Ephemeris and calculation stack) — Swiss Ephemeris confirmed
- Section 12.5 (Natal chart caching) — field list confirmed for first build

---
