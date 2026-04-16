# Skill: /plan-experiments

## Invocation

```
/plan-experiments
/plan-experiments --venue <venue>
/plan-experiments --outline <path-to-outline>
```

**Examples:**
- `/plan-experiments` — reads `templates/paper-outline.md` and infers venue from it
- `/plan-experiments --venue CoRL` — force venue-specific calibration
- `/plan-experiments --outline drafts/outline-v2.md` — use a specific outline file

---

## What this skill does

`/plan-experiments` runs before any paper draft exists. It transforms a contribution
statement (from the paper outline) into a concrete, venue-calibrated experiment plan.

This skill is the entry point to Phase 0 of the research workflow. Running it produces:
1. A structured experiment plan (`outputs/experiment-plan-<date>.md`)
2. An initial claim register with PLANNED/MISSING status for each contribution
3. A list of papers that need full-text reading before experiments begin (NEED-PDF)

The experiment plan becomes the contract: every table and figure in the final paper should
trace back to an entry in this plan.

---

## Prerequisites

Before running this skill:
- Fill `templates/paper-outline.md` with at least: target venue, contribution list (2–4 items),
  and the problem statement
- Run `/search-lit <topic>` at least once so candidate baselines and benchmarks are known

If the outline is empty or contributions are generic ("we improve performance"), the
Experiment-Planner will ask clarifying questions before proceeding.

---

## Agent dispatch

**Step 1 — Librarian (baseline verification)**
Before planning, the Librarian verifies that the baselines and benchmarks referenced in the
outline exist and are real. Marks each as VERIFIED or CANDIDATE.

**Step 2 — Experiment-Planner (main)**
Reads the outline, domain profile, venue profile, and benchmark notes.
Produces the experiment plan following the Experiment-Planner protocol.

**Step 3 — Claim-Tracker (forward validation)**
Runs Stage A using the experiment plan as input. Builds the initial claim register.
Flags any contributions that have no planned experiment.

---

## Output

Primary output: `outputs/experiment-plan-<date>.md`
Secondary output: `outputs/claim-evidence-map-<date>.md` (Stage A, forward-looking)

The experiment plan includes:
- Contribution → hypothesis mapping table
- Benchmark and task selection with justification
- Baseline roster with fairness checks
- Evaluation protocol (success criterion, metrics, N, seeds, train/test split)
- Results table structure (what tables and figures will contain which results)
- Ablation schedule (one row per key design choice)
- Papers to retrieve (NEED-PDF)
- Open questions for the user

---

## After running this skill

1. Review the plan and answer the open questions listed at the end
2. Retrieve any NEED-PDF papers and place them in `/papers/`
3. Update `references/tracker.md` with VERIFIED baselines
4. When user approves, change plan status from DRAFT → APPROVED
5. Use the approved plan to guide actual experiments
6. When results exist, run `/track-claims` to map results to claims

---

## Integration with workflow phases

```
PHASE 0 — PRE-WRITING
  Trigger: /plan-experiments
  Input:   templates/paper-outline.md (contribution statement + venue)
  Output:  outputs/experiment-plan-<date>.md
           outputs/claim-evidence-map-<date>.md (Stage A)
  Gate:    All contributions map to planned experiments; user approves plan

PHASE 2 — DISCOVERY
  /search-lit feeds verified baselines into the plan

PHASE 4 — DRAFTING
  Experiment plan is the source of truth for tables/figures
  Run /track-claims (Stage B) after each section

PHASE 5 — REVIEW
  Methods-Referee uses experiment plan as evaluation standard
```
