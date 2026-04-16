# Claim-Evidence Map Template

<!-- Living document. Updated by /track-claims at each phase. -->
<!-- Stage A: pre-writing (forward-looking). Stage B: draft review (backward-looking). -->

## Header

| Field | Value |
|-------|-------|
| Paper | |
| Date (last updated) | |
| Stage | A — pre-writing / B — draft review |
| Draft file reviewed | [path, or "none — pre-writing"] |

---

## Summary

| Status | Count | Meaning |
|--------|-------|---------|
| SUPPORTED | 0 | Claim has direct evidence in draft |
| PLANNED | 0 | Evidence designed in experiment plan, not yet in draft |
| MISSING | 0 | No evidence designed or found — BLOCKING |
| CRITICAL | 0 | INV-9 number mismatch — escalate to user |
| WEAK | 0 | Ablation/evidence exists but insufficient scope |
| SPECULATIVE | 0 | INV-17 novelty claim — needs literature verification |

---

## Claim register

<!-- Add one row per claim extracted from the contribution list or draft. -->
<!-- Claim types: Quantitative | Comparative | Sample-efficiency | Generalization | Causal | Qualitative | Novelty | About-prior-work -->

| ID | Section | Claim | Type | Evidence source | Status | Notes |
|----|---------|-------|------|----------------|--------|-------|
| C-001 | Abstract | | Quantitative | TABLE I col X | PLANNED | |
| C-002 | Sec. I | | Novelty | — | SPECULATIVE | INV-17 needed |
| C-003 | Sec. I | | Causal | TABLE II row X | PLANNED | |

---

## CRITICAL — Number mismatches (INV-9)

<!-- Any entry here blocks submission and is escalated to the user. -->

| Claim in text | Location | Table/Figure value | Discrepancy |
|--------------|---------|-------------------|-------------|
| | | | ❌ ESCALATE |

---

## MISSING claims (no evidence)

<!-- Each entry here is a BLOCKING issue: add an experiment or remove the claim. -->

| Claim ID | Claim | Recommended action |
|---------|-------|-------------------|
| | | Add experiment / Remove claim |

---

## WEAK claims (insufficient evidence)

<!-- Evidence exists but is weak (small N, narrow scope, single task). -->

| Claim ID | Claim | Current evidence | What would strengthen it |
|---------|-------|-----------------|-------------------------|
| | | | |

---

## SPECULATIVE claims (INV-17 needed)

<!-- Novelty claims that require literature confirmation before they can be asserted. -->

| Claim ID | Claim | Search needed | Librarian status |
|---------|-------|--------------|-----------------|
| | "first to do X" | Search [ICRA/IROS/CoRL 20XX–20XX] for [query] | PENDING |

---

## Contribution → hypothesis traceability

<!-- Connects the paper's stated contributions to planned experiments and results. -->

| Contribution | Hypothesis | Planned result | Draft location | Status |
|-------------|-----------|---------------|---------------|--------|
| | | TABLE I | — | PLANNED |
| | | TABLE II | Sec. VI | SUPPORTED |

---

## Hypothesis → result traceability

<!-- Reverse direction: for every experiment, which claim does it support? -->

| Experiment / Table row | Hypothesis supported | Claim ID | Draft citation |
|------------------------|--------------------|---------|----|
| TABLE I — main comparison | "Ours > baselines on task X" | C-001 | Sec. V para 2 |

---

## Next actions (prioritized)

| Priority | Claim ID | Action |
|---------|---------|--------|
| CRITICAL | | Resolve INV-9 mismatch — check whether [X.X] or [X.Y] is the correct value |
| BLOCKING | | Add experiment for [claim] OR remove from contributions |
| MAJOR | | Strengthen ablation: run on ≥3 tasks |
| MAJOR | | Route to Librarian: INV-17 literature check for [claim] |
