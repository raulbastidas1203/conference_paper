# conference-Darin

Research workflow for IEEE conference papers in robotics, humanoids, and embodied AI.
Modeled on the worker-critic architecture of clo-author, specialized for robotics research.

---

## System Identity

conference-Darin is a multi-agent Claude Code workflow for producing high-quality IEEE robotics
conference papers. It has two layers:

1. **Intellectual layer** — literature synthesis, argument structure, experimental design critique,
   claim verification, IEEE-style writing, revision support.
2. **Quality enforcement layer** — worker-critic agent pairs, content invariants, venue-calibrated
   peer review simulation.

The system works exclusively with real literature and verifiable citations. It never invents papers,
results, or metrics. If a reference cannot be confirmed from a primary source, it is marked
`[UNVERIFIED]` and the user is notified immediately.

---

## Worker-Critic Architecture

Every creative role has a paired critic. Critics cannot edit files; creators cannot score their
own work. This separation is enforced throughout all workflows.

| Worker | Critic | Domain |
|--------|--------|--------|
| Librarian | Librarian-Critic | Literature search & coverage |
| Writer | Writer-Critic | Paper drafting & IEEE compliance |
| — | Domain-Referee | Robotics expertise & novelty |
| — | Methods-Referee | Experimental rigor & reproducibility |
| — | Editor | Venue simulation & desk review |

**Pre-writing planning agents** (no worker-critic pair; produce plans, not paper text):

| Agent | Domain |
|-------|--------|
| Benchmark-Mapper | Benchmark/task selection, evaluation scope, venue-calibrated gap analysis |
| Experiment-Planner | Experiment design, baseline roster, evaluation protocol, ablation schedule |
| Claim-Tracker | Claim-to-evidence mapping, gap detection, INV-9 audit |

**Separation of powers:** Critics produce reports and scores, never artifacts. Workers produce
artifacts, never self-scores. Planning agents produce structured plans and maps, never paper text.

**Escalation protocol:** Worker-critic deadlock after 3 cycles → escalate to user with full
context. User decision is final.

See `.claude/agents/` for complete agent specifications.

---

## Quality Gates

| Gate | Threshold | Condition for passing |
|------|-----------|----------------------|
| Draft-ready | ≥ 70 | Safe to share with co-authors |
| Revision-ready | ≥ 80 | All CRITICAL issues resolved |
| Submission-ready | ≥ 90 | No blocking issues remain |

**Weighted scoring components:**

| Component | Weight | Assessed by |
|-----------|--------|-------------|
| Literature coverage | 15 % | Librarian-Critic |
| Related work positioning | 20 % | Domain-Referee |
| Methodology clarity | 20 % | Methods-Referee |
| Experimental rigor | 30 % | Methods-Referee |
| Writing & IEEE format | 15 % | Writer-Critic |

No submission gate override. If score < 90, the blocking issues must be resolved.

---

## Available Commands

**Pre-writing (Phase 0 — before any draft exists):**

| Command | Purpose | Agent dispatch |
|---------|---------|---------------|
| `/map-benchmarks [--venue]` | Recommend benchmarks, tasks, metrics, and gap analysis | Benchmark-Mapper |
| `/plan-experiments [--venue]` | Design experiment plan from contribution statement | Librarian + Experiment-Planner + Claim-Tracker |
| `/track-claims [--stage A\|B]` | Build/update claim-to-evidence map | Claim-Tracker (+ Librarian for INV-17) |
| `/plan-figures [--venue]` | Plan figure/table structure and visual narrative | Writer + Writer-Critic |

**Literature & synthesis (Phases 2–3):**

| Command | Purpose | Agent dispatch |
|---------|---------|---------------|
| `/search-lit` | Systematic literature search | Librarian → Librarian-Critic |
| `/related-work` | Synthesis + comparison table | Librarian + Writer |

**Drafting & review (Phases 4–6):**

| Command | Purpose | Agent dispatch |
|---------|---------|---------------|
| `/review-draft` | Full critical review | Domain-Referee + Methods-Referee + Writer-Critic |
| `/check-claims` | Claims-evidence audit (draft) | Writer-Critic |
| `/simulate-review [venue]` | Venue peer review simulation | Editor → Referees |
| `/revision-letter` | Response to reviewers | Writer |
| `/ieee-checklist [--venue]` | Pre-submission verification | Writer-Critic |

---

## Workflow Phases

```
Phase 0 — PRE-WRITING (before any manuscript text)
  See: workflows/pre-writing.md for full protocol

  0.1 PROBLEM DEFINITION
    Fill: templates/paper-outline.md (contribution list, venue, problem statement)
    Gate: contribution is falsifiable and specific

  0.2 LITERATURE, BENCHMARKS, AND BASELINES
    Run: /search-lit <topic> (2–3 queries)
    Run: /map-benchmarks --venue <venue>
    Build: references/tracker.md; benchmark-map output feeds into experiment plan
    Gate: ≥5 Central papers verified; benchmarks mapped; no BLOCKING gaps

  0.3 EXPERIMENT DESIGN
    Run: /plan-experiments --venue <venue>
    Output: outputs/experiment-plan-<date>.md
    Gate: ALL contributions map to experiments; N meets domain minimum; ablation complete

  0.4 CLAIM REGISTER (Stage A)
    Run: /track-claims --stage A
    Output: outputs/claim-evidence-map-<date>.md
    Gate: no MISSING claims; SPECULATIVE claims routed to literature check

  0.5 FIGURE/TABLE BLUEPRINT
    Run: /plan-figures --venue <venue>
    Output: outputs/figures-plan-<date>.md
    Gate: every claim has a planned table/figure; fits page limit

Phase 1 — SCOPING
  Define: contribution, venue, deadline, co-authors
  Output: research spec (see templates/paper-outline.md)
  Gate: contribution must be falsifiable and specific before Phase 2
  Note: if Phase 0 was completed, scoping is already done

Phase 2 — DISCOVERY
  Run: /search-lit <tema principal>
  Classify each paper: Central / Related / Marginal
  Build: references/tracker.md entries
  Gate: ≥ 5 central papers with at least 1 from ICRA/IROS/CoRL/RSS/RA-L/T-RO

Phase 3 — SYNTHESIS
  Run: /related-work
  Output: draft related work section + comparison table
  Gate: gap is clearly stated and no competitor is misrepresented

Phase 4 — DRAFTING
  Order: Methodology → Experiments → Results → Related Work → Introduction → Abstract → Conclusion
  Run: /check-claims after each section
  Run: /track-claims --stage B after each major section
  Gate: no [TODO: cite] remaining; all claims have evidence; claim map shows no MISSING

Phase 5 — REVIEW
  Run: /review-draft
  Iterate until score ≥ 80
  Gate: no CRITICAL issues in Methods-Referee report

Phase 6 — PRE-SUBMISSION
  Run: /simulate-review --venue <venue>
  Run: /ieee-checklist --venue <venue>
  Run: /track-claims --update  (final evidence audit)
  Gate: aggregate score ≥ 90; claim map fully SUPPORTED

Phase 7 — POST-REVIEW (if revised)
  Run: /revision-letter
  Apply changes, re-run /review-draft
  Gate: all reviewer comments addressed point-by-point
```

---

## Reference Handling Protocol

### Access tiers

**CANDIDATE** — found in search; only title, authors, venue, year, abstract confirmed.
Add to `references/tracker.md` as CANDIDATE.

**VERIFIED** — title, authors, venue, year confirmed from a primary source (IEEE Xplore, arXiv,
DBLP, publisher page). Safe to cite in paper.

**FULL-TEXT** — complete paper read; PDF in `/papers/` or accessed from open arXiv link.
Required for papers used as baselines, benchmarks, or central methodological references.

**UNVERIFIED** — cannot confirm existence or key details from any primary source.
Mark as `[UNVERIFIED]` inline; notify user explicitly; do not include in references.bib.

**NEED-PDF** — paper is confirmed and important (FULL-TEXT required) but not freely accessible.
List under "Papers to retrieve" at the end of every relevant skill output so user can fetch
with university credentials.

### Source priority

1. **Top robotics venues** (primary, peer-reviewed): ICRA, IROS, CoRL, RSS, RA-L, T-RO, Humanoids
2. **Adjacent top venues**: CVPR, ICCV, NeurIPS, ICML (robotics/embodied AI tracks), HRI
3. **Recent work 2023+** from any venue with strong relevance
4. **arXiv preprints**: mark explicitly as `[PREPRINT: arXiv:XXXX.XXXXX]`; verify before treating
   as primary source; do not cite arXiv if a published version exists.

**Important:** In robotics research, top conferences (ICRA, IROS, CoRL, RSS) are primary venues,
not second-tier publications. Do not deprioritize them relative to journals.

---

## Domain Specialization

Full domain calibration in `.claude/references/domain-profile.md`.

**Core research areas:**
- Robot learning: imitation learning (BC, DAgger, Diffusion Policy, ACT), RL, offline RL
- Humanoids: whole-body control, loco-manipulation, bipedal locomotion, teleoperation
- Manipulation: grasping, bimanual, dexterous, contact-rich, deformable objects
- Sim2real: domain randomization, system identification, adaptation
- Perception: visual affordance, object pose estimation, 3D scene understanding
- Control: MPC, WBC, impedance control, force control, trajectory optimization
- Navigation: visual navigation, SLAM, motion planning, exploration

**Target venues:** ICRA · IROS · CoRL · RSS · RA-L · T-RO · Humanoids · HRI

Venue-specific profiles: `.claude/references/venue-profiles.md`
Method-specific guides: `.claude/references/method-guides.md`
Benchmark reference: `.claude/references/benchmark-notes.md`

---

## Content Invariants

Non-negotiable standards applied to all output. Full list: `.claude/rules/content-invariants.md`.

Key invariants (abbreviated):
- **INV-1** Tables use booktabs only. No `\hline`, no vertical rules.
- **INV-2** All quantitative results report mean ± std over N trials.
- **INV-4** Hardware described completely: robot, controllers, sensors, environment.
- **INV-5** All baselines cited with direct reference to their published paper.
- **INV-9** Numbers in text match tables exactly. No exceptions.
- **INV-12** Ablation study required for each key design choice.
- **INV-14** Abstract: problem + approach + quantitative result.

---

## Git & PR Convention

**Siempre que se complete trabajo en este repo:**
1. Commitear los cambios con mensaje descriptivo
2. Pushear al branch de trabajo (`claude/...` o feature branch)
3. Crear un PR a `main` usando el GitHub MCP tool (`mcp__github__create_pull_request`)
   - `owner`: `raulbastidas1203`, `repo`: `conference-darin`, `base`: `main`
   - Incluir en el body: qué cambió, por qué, y test plan
4. No hacer merge sin aprobación explícita del usuario

Esta convención aplica a toda sesión donde se pusheen cambios, sin excepción.

---

## Limitations

**conference-Darin does NOT:**
- Execute simulations (Gazebo, MuJoCo, IsaacSim, PyBullet, Isaac Lab)
- Run robot hardware or access sensor data
- Generate experimental data, metrics, or results
- Claim contributions or results the user has not obtained
- Download PDFs from paywalled sources

**conference-Darin does:**
- Design experiment plans: benchmark selection, baseline roster, evaluation protocol, ablation schedule
- Build claim-to-evidence maps before and during drafting
- Plan figure/table structure with INV compliance assignments
- Search literature via open APIs (Semantic Scholar, arXiv, DBLP, OpenAlex, Crossref)
- Verify citations and flag unverifiable ones
- Synthesize related work with gap identification and comparison tables
- Simulate peer review at target venue with calibrated referee dispositions
- Review writing for IEEE standards and robotics conventions
- Audit claims against evidence present in the paper
- Write revision letters with point-by-point responses

---

## Workspace Layout

```
/papers/            PDFs provided by user (gitignored)
/drafts/            Active paper (LaTeX or Markdown)
/lit-notes/         Per-paper reading notes (one file per paper)
/references/        references.bib + tracker.md (classification table)
/outputs/           Skill outputs, quality reports, review logs
                    (experiment plans, claim maps, figure blueprints, reviews)
/templates/         IEEE paper outline, comparison table, revision response,
                    experiment plan, claim-evidence map
/workflows/         Process guides (pre-writing, new-paper, lit-review, submission-prep)
/.claude/
  /agents/          10 agent role specifications
                    (Librarian, Librarian-Critic, Writer, Writer-Critic,
                     Domain-Referee, Methods-Referee, Editor,
                     Benchmark-Mapper, Experiment-Planner, Claim-Tracker)
  /references/      Domain knowledge (profile, venues, methods, benchmarks)
  /rules/           Content invariants (20 standards, CRITICAL/MAJOR severity)
  /skills/          11 skill implementations
                    (search-lit, related-work, map-benchmarks, plan-experiments,
                     track-claims, plan-figures, check-claims, review-draft,
                     simulate-review, revision-letter, ieee-checklist)
```
