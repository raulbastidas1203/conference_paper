# Skill: /plan-figures

## Invocation

```
/plan-figures
/plan-figures --venue <venue>
/plan-figures --file <path-to-experiment-plan>
```

**Examples:**
- `/plan-figures` — reads experiment plan and outline, infers venue
- `/plan-figures --venue ICRA` — use ICRA page/figure constraints
- `/plan-figures --file outputs/experiment-plan-2024-09.md` — use a specific plan file

---

## What this skill does

`/plan-figures` plans the complete set of figures and tables the paper needs before any
LaTeX is written. It answers: what visual artifacts are required, in what order do they
appear, what does each one show, and which content invariants apply.

Running this skill prevents the most common structural problem in robotics papers: a draft
where tables and figures are added incrementally without a coherent visual narrative, leading
to redundant figures, missing ablation tables, and captions that don't connect to the claims.

The output is a figure/table blueprint (`outputs/figures-plan-<date>.md`) that:
- Lists every table and figure with its purpose and content specification
- Assigns each to a paper section
- Maps each to the claims it supports (traceability to claim-evidence map)
- Specifies which content invariants apply and how to satisfy them
- Flags venue-specific constraints (page limit, figure count, double-column layout)

---

## Prerequisites

- `outputs/experiment-plan-<date>.md` (run `/plan-experiments` first)
- `templates/paper-outline.md` with section structure

---

## Agent dispatch

**Writer (figure planning mode)**
The Writer reads the experiment plan and outline, then proposes the figure/table structure
following IEEE robotics conventions for the target venue.

**Writer-Critic (blueprint review)**
Reviews the proposed blueprint for: INV compliance assignments, missing visual elements,
duplicate information across figures, and venue-specific format constraints.

---

## Output

Primary output: `outputs/figures-plan-<date>.md`

---

## Output format (what the figures plan looks like)

```markdown
## Figures and Tables Plan
Paper: [title or contribution ID]
Target venue: [venue]
Page limit: [N] pages (double-column IEEE)
Date: <date>

---

### Tables

#### TABLE I — Main comparison results
Section: Results (Sec. V)
Caption above table (IEEE convention)
Content: Success rate (mean ± std) across [N tasks] for [proposed method + N baselines]
Rows: Ours, Diffusion Policy [1], BC [2], ACT [3], [Baseline 4]
Columns: Task-1 SR, Task-2 SR, Task-3 SR, Avg SR, Demo Count
INV checks: INV-1 (booktabs), INV-2 (mean±std), INV-3 (N=20 in caption), INV-5 (all baselines cited)
Claim supported: C-001 (main performance claim), C-003 (sample efficiency)
Notes: Bold the best number per column. Report N=20 trials in caption.

#### TABLE II — Ablation study
Section: Analysis (Sec. VI)
Content: Proposed method with components removed one at a time
Rows: Full model, w/o attention, w/o diffusion head, w/o contact sensing, BC (lower bound)
Columns: SR on Task-1, SR on Task-3, Avg SR
INV checks: INV-1, INV-2, INV-3, INV-12 (must cover all key components)
Claim supported: C-005 (causal claim about attention), C-006 (causal claim about diffusion head)

---

### Figures

#### Fig. 1 — System overview
Section: Introduction or Method (Sec. I or III)
Type: Architecture diagram
Content: Input (RGB-D observation) → components → output (action sequence)
Caption below figure (IEEE convention)
INV checks: INV-6 (grayscale legible: use distinct shapes not only colors), INV-7 (autocontained)
INV-19: all labels in LaTeX, not embedded in image
Notes: Key design choices should be visually highlighted. No embedded text titles.

#### Fig. 2 — Qualitative results
Section: Results (Sec. V)
Type: Photo strip or rendered sequence
Content: [N=3] task demonstrations showing success/failure comparison vs. best baseline
Caption: must state task name, method, success/failure label, N shown
INV checks: INV-7 (autocontained), INV-6 (legible in grayscale — use markers)
Claim supported: C-002 (qualitative robustness)

#### Fig. 3 — Learning curves (if RL/IL method)
Section: Results or Analysis
Type: Line plot with shaded ± std region
Content: Success rate vs. number of demonstrations for Ours + top 2 baselines
Axes: x = demonstrations (log scale if needed), y = success rate [0,1]
INV checks: INV-2 (shaded ±std), INV-6 (grayscale: use distinct line styles), INV-7
Claim supported: C-003 (sample efficiency claim)
Notes: Show final performance at the same demonstration budget for all methods.

---

### Visual narrative summary

The reader's journey through figures and tables:
1. Fig 1 — understand what the method does (architecture)
2. Table I — see that it outperforms baselines quantitatively
3. Fig 2 — see qualitative evidence of what the improvement looks like
4. Fig 3 — see that it is more sample-efficient
5. Table II — understand WHY it works (ablation isolates components)

---

### Venue constraints

| Constraint | Value | Status |
|-----------|-------|--------|
| Page limit | [N] pages | CHECK before finalizing figure count |
| Max figures | — | [N] figures planned |
| Double-column | Yes | All tables in two-column format |
| Blind review | [Yes/No] | [Action if yes: anonymize acknowledgments] |
| Supplementary allowed | [Yes/No] | [List what goes there if yes] |

---

### Content invariant assignment

| INV | Applies to | Check |
|-----|-----------|-------|
| INV-1 | All tables | Booktabs only |
| INV-2 | Table I, Table II, Fig 3 | Mean ± std |
| INV-3 | Table I, Table II | N stated in caption |
| INV-5 | Table I | All baselines cited in caption or main text |
| INV-6 | Fig 2, Fig 3 | Grayscale legible |
| INV-7 | All figures | Autocontained captions |
| INV-8 | All tables | Autocontained captions |
| INV-12 | Table II | Covers all key design choices |
| INV-19 | All figures | Labels in LaTeX, not embedded |

---

### Missing visuals (flagged by Writer-Critic review)

[List any claims in the claim-evidence map that lack a planned figure or table]
```

---

## Integration with workflow phases

```
PHASE 0 — After /plan-experiments and /track-claims --stage A
  Run: /plan-figures
  Output: outputs/figures-plan-<date>.md
  Gate: every claim in claim register maps to a planned table/figure

PHASE 4 — During drafting
  Each table/figure follows the blueprint from this plan
  Run /check-claims after each section to verify alignment

PHASE 5 — /review-draft checks actual tables/figures against this plan
```
