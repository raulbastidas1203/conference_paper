# Skill: /track-claims

## Invocation

```
/track-claims
/track-claims --stage A
/track-claims --stage B
/track-claims --file <path-to-draft-section>
/track-claims --update
```

**Examples:**
- `/track-claims` — auto-detect stage: Stage A if no draft, Stage B if draft exists
- `/track-claims --stage A` — force pre-writing mode (plan validation)
- `/track-claims --stage B --file drafts/paper.tex` — audit a specific draft file
- `/track-claims --update` — update existing map in `outputs/claim-evidence-map-<date>.md`

---

## What this skill does

`/track-claims` maintains the living claim-evidence map that links every research claim
to its supporting evidence. It runs in two modes:

**Stage A (pre-writing):** Reads the experiment plan and contribution statement.
Builds a forward-looking register: what will be claimed, what experiment will support it,
and what is currently unplanned. Flags BLOCKING gaps before any experiments run.

**Stage B (during/after drafting):** Reads the draft and extracts every explicit and
implicit claim. Cross-references each against tables, figures, and citations. Flags
CRITICAL number mismatches (INV-9), MISSING evidence, WEAK ablation coverage, and
SPECULATIVE novelty claims (INV-17).

This skill should be run:
- Once at Phase 0 after `/plan-experiments` (Stage A)
- After each major section is drafted (Stage B)
- Before any submission gate check

---

## Prerequisites

**For Stage A:**
- `templates/paper-outline.md` with contribution list
- `outputs/experiment-plan-<date>.md` (run `/plan-experiments` first)

**For Stage B:**
- At least one draft section in `drafts/`
- `outputs/claim-evidence-map-<date>.md` from Stage A (for traceability)

---

## Agent dispatch

**Claim-Tracker (main)**
Runs the full claim extraction and evidence-mapping protocol described in
`.claude/agents/claim-tracker.md`. Handles both Stage A and Stage B.

**Librarian (on demand)**
If Claim-Tracker identifies SPECULATIVE claims (INV-17 needed), it routes those
to the Librarian for literature verification before flagging them as resolved.

**Writer-Critic (on demand — Stage B only)**
If CRITICAL number mismatches (INV-9) are found, the issue is escalated to the user
directly. Writer-Critic is notified to include the mismatch in its next report.

---

## Output

Primary output: `outputs/claim-evidence-map-<date>.md`

The map contains:
- Summary table (counts by status: SUPPORTED / PLANNED / MISSING / CRITICAL / WEAK)
- Full claim register (ID, section, claim text, type, evidence source, status)
- CRITICAL section: INV-9 number mismatches (escalated to user)
- MISSING section: claims with no evidence (must fix before gate)
- WEAK section: claims needing stronger ablation support
- SPECULATIVE section: novelty claims needing INV-17 literature verification
- Contribution-to-hypothesis traceability table
- Next actions list (prioritized by severity)

---

## Severity of findings

| Status | Severity | Action required |
|--------|---------|----------------|
| CRITICAL (INV-9 mismatch) | Blocks submission | User must resolve; may indicate data error |
| MISSING (no evidence) | Blocks submission | Add experiment OR remove claim |
| WEAK (ablation needed) | MAJOR | Strengthen ablation before final gate |
| SPECULATIVE (INV-17) | MAJOR | Route to Librarian for literature search |
| PLANNED (experiment designed, not run) | INFO | No action needed until experiments complete |
| SUPPORTED | INFO | No action needed |

---

## Integration with workflow phases

```
PHASE 0  — /track-claims --stage A   (after /plan-experiments)
PHASE 4  — /track-claims --stage B   (after each drafted section)
PHASE 5  — /track-claims --stage B   (before /review-draft)
PHASE 6  — /track-claims --update    (final audit before /simulate-review)
```

The claim-evidence map from Stage A and Stage B are linked: Stage B updates
the original register, marking PLANNED claims as SUPPORTED or MISSING based
on what actually appears in the draft.
