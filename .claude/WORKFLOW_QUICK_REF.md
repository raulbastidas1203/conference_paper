# Workflow Quick Reference — conference-Darin

---

## Commands

### Pre-writing (Phase 0 — before any draft)

| Command | When to use | Agents dispatched |
|---------|-------------|------------------|
| `/plan-experiments [--venue]` | After filling outline, before running experiments | Librarian + Experiment-Planner + Claim-Tracker |
| `/track-claims --stage A` | After /plan-experiments, to audit coverage | Claim-Tracker (+ Librarian for INV-17) |
| `/plan-figures [--venue]` | After experiment plan approved | Writer + Writer-Critic |

### Literature & synthesis (Phases 2–3)

| Command | When to use | Agents dispatched |
|---------|-------------|------------------|
| `/search-lit <topic>` | Start of paper, before related work | Librarian → Librarian-Critic |
| `/related-work` | After ≥5 Central papers verified | Librarian + Writer → Writer-Critic |

### Drafting & review (Phases 4–6)

| Command | When to use | Agents dispatched |
|---------|-------------|------------------|
| `/track-claims --stage B` | After each major section drafted | Claim-Tracker |
| `/check-claims` | Before each section is finalized | Writer-Critic (claim mode) |
| `/review-draft` | After completing any major section | Domain-Referee + Methods-Referee + Writer-Critic |
| `/simulate-review --venue <v>` | Before submission | Editor → Domain-Referee + Methods-Referee |
| `/revision-letter` | After receiving reviewer comments | Writer |
| `/ieee-checklist --venue <v>` | Final pre-submission check | Writer-Critic (format mode) |

---

## Quality gates

| Score | Meaning | Gate |
|-------|---------|------|
| ≥ 90 | No blocking issues | Submission-ready |
| 80–89 | All CRITICAL resolved | Revision-ready |
| 70–79 | Safe to share | Draft-ready |
| < 70 | Fundamental issues | Blocked |

---

## Workflow by phase

```
PHASE 0 — PRE-WRITING (before experiments run)
  Fill:    templates/paper-outline.md
  Run:     /search-lit (baselines + benchmarks)
  Run:     /plan-experiments --venue <v>
  Run:     /track-claims --stage A
  Run:     /plan-figures --venue <v>
  Gate:    All contributions have experiments; no MISSING claims; blueprint complete

PHASE 1 — SCOPING
  Fill:    templates/paper-outline.md (if not done in Phase 0)
  Define:  contribution (specific + falsifiable), venue, deadline

PHASE 2 — DISCOVERY
  Run:     /search-lit <topic>
  Build:   references/tracker.md
  Read:    papers flagged as Central

PHASE 3 — SYNTHESIS
  Run:     /related-work
  Identify: gap + positioning

PHASE 4 — DRAFTING
  Order:   Methodology → Experiments → Results → Related Work → Intro → Abstract → Conclusion
  After each section: /check-claims  +  /track-claims --stage B

PHASE 5 — REVIEW
  Run:     /review-draft
  Target:  score ≥ 80
  Fix:     all CRITICAL issues

PHASE 6 — PRE-SUBMISSION
  Run:     /simulate-review --venue <v>
  Run:     /ieee-checklist --venue <v>
  Run:     /track-claims --update
  Target:  score ≥ 90, zero CRITICAL, claim map fully SUPPORTED

PHASE 7 — REVISION
  Run:     /revision-letter
  Re-run:  /review-draft
  Gate:    all reviewer concerns addressed point-by-point
```

---

## Agent roles (one-line summary)

| Agent | Role | Creates? |
|-------|------|---------|
| Librarian | Finds papers, updates tracker | Tracker entries, lit-notes |
| Librarian-Critic | Verifies coverage, flags fabrications | Review reports only |
| Writer | Drafts sections, writes revision letters | Paper content |
| Writer-Critic | Audits IEEE compliance, claims, numbers | Review reports only |
| Domain-Referee | Simulates robotics reviewer | Review reports only |
| Methods-Referee | Audits experimental rigor | Review reports only |
| Editor | Simulates AC/PC, synthesizes reviews | Editorial report only |
| Experiment-Planner | Designs experiments before writing | Experiment plan |
| Claim-Tracker | Maps claims to evidence, flags gaps | Claim-evidence map |

**Golden rule:** Critics never edit. Workers never score themselves.
Planning agents produce plans and maps, never paper text.

---

## Pre-writing outputs (Phase 0)

| Output file | Created by | Purpose |
|-------------|-----------|---------|
| `outputs/experiment-plan-<date>.md` | `/plan-experiments` | Contract: what experiments prove what |
| `outputs/claim-evidence-map-<date>.md` | `/track-claims` | Living map of claim → evidence |
| `outputs/figures-plan-<date>.md` | `/plan-figures` | Blueprint of tables and figures |

---

## Reference status flow

```
CANDIDATE → VERIFIED → FULL-TEXT
                ↓
           NEED-PDF (tell user) → FULL-TEXT (after user provides PDF)
                ↓
          UNVERIFIED (remove from .bib, tell user)
```

---

## Content invariant quick-check

Before any section is finalized, verify:

| # | Check | Severity |
|---|-------|---------|
| INV-1 | Tables: booktabs only, no \hline | CRITICAL |
| INV-2 | Results: mean ± std everywhere | CRITICAL |
| INV-3 | N trials stated in all tables | MAJOR |
| INV-4 | Hardware fully described | MAJOR |
| INV-5 | All baselines cited | CRITICAL |
| INV-6 | Figures legible in grayscale | MAJOR |
| INV-7/8 | Captions autocontained | MAJOR |
| INV-9 | Numbers in text = numbers in tables | CRITICAL |
| INV-10 | Acronyms defined on first use | MAJOR |
| INV-12 | Ablation covers key components | CRITICAL |
| INV-14 | Abstract has quantitative result | CRITICAL |
| INV-15 | Intro has numbered contribution list | CRITICAL |
| INV-16 | Sim/real scope explicitly stated | CRITICAL |
| INV-18 | Causal claims have ablation support | CRITICAL |

Full list with rationale: `.claude/rules/content-invariants.md`

---

## Workspace layout

```
/papers/           User-provided PDFs (gitignored)
/drafts/           Active LaTeX/Markdown draft
/lit-notes/        Per-paper reading notes
/references/       references.bib + tracker.md
/outputs/          Skill outputs: experiment plans, claim maps, figure blueprints,
                   review reports, quality logs
/templates/        Paper outline, experiment plan, claim-evidence map,
                   comparison tables, revision template
/workflows/        Process guides: pre-writing, new-paper, lit-review, submission-prep
/.claude/
  /agents/         9 agent role specs
  /references/     Domain knowledge (profile, venues, methods, benchmarks)
  /rules/          Content invariants (20 standards, severity-tagged)
  /skills/         10 skill implementations
```
