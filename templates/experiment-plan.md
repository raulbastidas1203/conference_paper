# Experiment Plan Template

<!-- Fill this template before running any experiments. Generated/updated by /plan-experiments. -->
<!-- Status: DRAFT → APPROVED (change after user review) -->

## Paper metadata

| Field | Value |
|-------|-------|
| Paper title (working) | |
| Target venue | |
| Submission deadline | |
| Page limit | |
| Real robot required by venue? | [Yes / No / Preferred] |
| Status | DRAFT |

---

## Contribution → Hypothesis mapping

<!-- One row per contribution. Each must map to at least one falsifiable hypothesis. -->

| # | Contribution (from outline) | Hypothesis | Falsification condition | Evidence type |
|---|----|----|----|----|
| C1 | | | | Table / Figure |
| C2 | | | | |
| C3 | | | | |

---

## Benchmarks and tasks

<!-- One row per benchmark. See .claude/references/benchmark-notes.md for reference. -->

| Benchmark | Tasks selected | Why selected | Community adoption | Sim / Real | Citation |
|-----------|---------------|-------------|-------------------|-----------|---------|
| | | | ≥3 papers in venue? | | |

**Sim-to-real scope:** [Sim-only / Real-robot / Both]
**Justification if sim-only:** [Required by INV-16]

---

## Baseline roster

<!-- One row per baseline. All must be cited before experiments run. -->

| Baseline | Full citation | Input modality | Version | Fairness status | Notes |
|---------|--------------|---------------|---------|----------------|-------|
| | | | Latest | FAIR / FLAG | |

**Fairness protocol:**
- Same input modality as proposed method: [Yes / No — list exceptions]
- Same observation space: [Yes / No]
- Hyperparameter tuning: [describe approach]
- Code source: [official repo / reimplemented — if reimplemented, explain]

---

## Evaluation protocol

| Field | Value |
|-------|-------|
| Task success criterion | [exact definition — binary? threshold?] |
| Primary metric | [success rate / SPL / path length / other] |
| Secondary metrics | |
| N trials per method per task | [N — minimum: 20 manipulation / 100 navigation] |
| N seeds (learning methods) | [N — minimum: 3, recommend: 5] |
| Train/test split | [describe object/scene split] |
| Statistical reporting | mean ± std across N trials |
| Evaluation conditions | [lab / varied lighting / real-world / etc.] |

---

## Results table structure

| Table | Section | What it shows | Rows | Columns |
|-------|---------|-------------|------|---------|
| TABLE I | Sec. V | Main comparison | Ours + baselines | Tasks × SR |
| TABLE II | Sec. VI | Ablation | Variants | Tasks × SR |

---

## Figure structure

| Figure | Section | Type | What it shows | Key takeaway |
|--------|---------|------|-------------|-------------|
| Fig. 1 | Sec. I/III | Diagram | System architecture | How the method works |
| Fig. 2 | Sec. V | Photo/render | Qualitative results | Visual success |

---

## Ablation schedule

<!-- One row per key design choice. Required by INV-12. -->

| # | Component | What it does | Ablated version | Hypothesis | Table row |
|---|-----------|-------------|----------------|-----------|---------|
| A1 | | | Remove / replace with [X] | SR drops by ≥X% | TABLE II row 1 |
| A2 | | | | | TABLE II row 2 |

---

## Papers to retrieve (NEED-PDF)

<!-- Baselines and benchmarks that require full-text reading. Fetch with university credentials. -->

| Paper | Reason | DOI / arXiv |
|-------|--------|-------------|
| | Baseline: need implementation details | |
| | Benchmark: need task definitions | |

---

## Open questions

<!-- List any decisions that require user input before experiments can be designed. -->

1. [ ] Is real-robot validation planned, or will this be sim-only?
2. [ ] How many GPU hours / demonstration collection hours are available?
3. [ ] Are there specific objects / tasks already collected data for?
4. [ ] What is the target N for main results?

---

## Plan validation checklist

Before changing status to APPROVED:

- [ ] Every contribution (C1, C2...) maps to at least one table row or figure
- [ ] Every hypothesis has a falsification condition
- [ ] All baselines are verified (VERIFIED in tracker.md)
- [ ] N trials meets domain minimum
- [ ] Ablation covers all key design choices
- [ ] Sim-to-real scope stated explicitly (INV-16)
- [ ] No NEED-PDF papers missing (or user has confirmed they will provide PDFs)
- [ ] Open questions answered or acknowledged
