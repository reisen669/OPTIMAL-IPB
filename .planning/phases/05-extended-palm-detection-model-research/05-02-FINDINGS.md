# Phase 5 Plan 02 — Findings: ModelScope (P), MDPI/ISPRS 2024-2025 (O), CVPR/ICCV 2024 (R)

**Probe date:** 2026-06-19
**Plan:** 05-02-PLAN.md
**Sources:** P (ModelScope/Alibaba), O (MDPI Remote Sensing + ISPRS 2024–2025), R (CVPR/ICCV 2024)

---

## Source P: ModelScope (Alibaba)

- Probe date: 2026-06-19
- Queries run:
  1. modelscope.cn task=image-object-detection keyword=棕榈 (palm) → Site header only — no model listings returned
  2. modelscope.cn task=image-object-detection keyword=油棕榈 (oil palm) → Site header only — no model listings returned
  3. modelscope.cn task=image-object-detection keyword=palm tree → Site header only — no model listings returned
  4. modelscope.cn task=image-object-detection keyword=tree crown detection → Site header only — no model listings returned
- Candidates found: None
- Result: Probed — ModelScope full model catalog requires authenticated browsing. All four queries (Chinese and English) returned only the site header ("ModelScope - 模型列表页") without model listings. Access to model search results requires a registered ModelScope account. Cannot confirm presence or absence of palm/tree-crown detection models via unauthenticated WebFetch.
- Status: Excluded (inconclusive — authenticated access required; cannot confirm no models exist)
- Probe notes: This matches RESEARCH.md Source P assessment (Priority LOW; authentication barrier expected). A logged-in Chinese-language ModelScope browse by a team member could complete this probe if deemed necessary.

---

## Source O: MDPI Remote Sensing / ISPRS 2024–2025

- Probe date: 2026-06-19
- MDPI Remote Sensing queries:
  1. q=oil+palm+detection, journal=remotesensing, 2024–2025 → HTTP 403 Forbidden (MDPI blocks automated fetches)
  2. q=tree+crown+detection, journal=remotesensing, 2024–2025 → HTTP 403 Forbidden
  3. q=palm+tree+detection, journal=forests, 2024–2025 → HTTP 403 Forbidden
- ISPRS query: oil palm detection 2024–2025 → Not accessible via WebFetch
- WebSearch fallback results:
  - No 2024–2025 MDPI Remote Sensing oil palm detection papers with GitHub link + pretrained checkpoint found in search results
  - MDPI Forests 2025: Ceroxylon palm detection paper (Ceroxylon palms, Peru/Amazonas NW) — no GitHub checkpoint link found in search results
  - No ISPRS 2024–2025 oil palm papers with pretrained checkpoints found
- Papers with GitHub link and downloadable checkpoint: None confirmed
- Papers with GitHub code but no checkpoint (Watch List nominations):
  - Ceroxylon palm detection (MDPI Forests 2025, NW Peru) — GitHub code status unknown; geographic mismatch (SE Asia exclusion applies regardless)
- Candidates for main table: None
- Result: Probed — no 2024–2025 MDPI/ISPRS palm/tree-crown papers with confirmed pretrained checkpoint + GitHub link found via accessible queries. MDPI search API blocked unauthenticated access; WebSearch fallback used. No new main-table candidates from Source O.

---

## Source R: CVPR 2024 / ICCV 2024

- Probe date: 2026-06-19
- CVPR 2024 papers page checked: YES (via DmitryRyumin/CVPR-2023-24-Papers GitHub repo)
- DmitryRyumin tracking repo checked: YES — https://github.com/DmitryRyumin/CVPR-2023-24-Papers
- Search terms: palm, tree crown, canopy, aerial detection, forest detection, remote sensing detection
- CVPR 2024 Photogrammetry and Remote Sensing section: 19 papers noted but individual titles not extracted from the tracking repo index
- Papers found with palm/tree-crown content: None confirmed in accessible content
- Papers with downloadable checkpoint: None
- ICCV 2024: arXiv search for ICCV 2024 tree/palm papers rate-limited; no dedicated ICCV 2024 proceedings page accessible
- Result: Probed — no palm/tree-crown detection papers with public code confirmed at CVPR/ICCV 2024. Consistent with RESEARCH.md assessment that top vision conferences focus on general remote sensing tasks, not palm-specific detection with public checkpoints.
- Probe notes: DmitryRyumin tracking repo shows category headers with paper counts but individual titles were not expanded in the fetched content. A manual search of the Photogrammetry section (19 papers) could be done but is unlikely to yield palm-specific results per RESEARCH.md priority assessment.
