# Lab Meeting Report v1.2 Quality Evaluation Design

**Date:** 2026-07-13

**Status:** User-approved design, pending written-spec review

**Target release:** `v1.2.0`

## Context

`v1.1.0` validates repository structure, packaging, examples, and release artifacts, but it does not measure whether the skill produces more faithful research-progress reports. The current tests can detect a missing file or stale package name; they cannot detect an invented metric, an omitted failed experiment, a silently reconciled source conflict, or destructive edits to an existing report.

`v1.2.0` will make report quality measurable before changing the prompt. The work starts by freezing `v1.1.0` as the behavioral baseline, building an adversarial public evaluation corpus, and grading the baseline. Skill instructions or templates change only in response to observed, generalizable failures.

## Goals

1. Measure evidence fidelity and numeric accuracy for research-progress reports.
2. Treat invented critical facts, unsupported conclusions, missing negative results, and silently resolved conflicts as release-blocking failures.
3. Test both report composition from supplied evidence and end-to-end local-file workflows.
4. Compare `v1.1.0` and the `v1.2.0` candidate under isolated, repeatable conditions.
5. Keep the final report readable; internal evidence controls should not become visible boilerplate unless evidence shows that visible attribution is necessary.
6. Publish evaluation inputs, grading rules, representative outputs, and an evidence-bounded benchmark summary.

## Non-Goals

- Change Lark/Feishu ingestion or publishing behavior.
- Expand paper-review or mixed-report modes.
- Optimize skill triggering or the frontmatter description.
- Run model-backed evaluations in GitHub Actions.
- Add telemetry, private research data, adoption claims, or unsupported quality claims.
- Force a prompt change when the baseline already satisfies the accepted quality bar.

## Evaluation Architecture

The evaluation has two layers. Both use only synthetic public data.

### Layer A: Evidence-to-report composition

These cases isolate reasoning and writing by supplying a bounded evidence packet.

| Case ID | Adversarial condition | Primary failure being tested |
|---|---|---|
| `clean-multiseed` | Baseline, three new-model seeds, latency, and an explicit success criterion | Numeric transcription and allowed derived calculations |
| `conflicting-results` | Two source files report different values for the same metric | Silent reconciliation or unsupported source preference |
| `buried-negative-result` | A failed experiment appears in a low-salience note after positive results | Omission or minimization of negative evidence |
| `missing-evidence-causal-lure` | Notes suggest a cause but provide no isolating experiment | Turning interpretation into fact or causality |
| `duplicated-multilingual-notes` | Chinese and English notes repeat some facts with different wording | Double counting, language drift, and duplicate conclusions |

### Layer B: End-to-end local workflow

These cases test file selection, provenance, report creation, and safe updates.

| Case ID | Adversarial condition | Primary failure being tested |
|---|---|---|
| `scoped-directory-selection` | Relevant results coexist with caches, unrelated notes, and generated output | Reading outside scope or citing irrelevant files |
| `safe-existing-report-update` | An existing dated report contains manual sections and one superseded result | Deleting manual content or failing to record supersession |
| `partial-source-failure` | One source is unreadable and a referenced figure is missing | Inventing replacement evidence or hiding skipped sources |

## Case Contract

Each case lives under `evals/research-progress/cases/<case-id>/` and contains a `manifest.json`, a task prompt, and an `inputs/` tree. End-to-end cases may also include an existing report fixture.

The manifest records:

- case ID, evaluation layer, requested language, and report mode;
- input paths and the expected report path;
- required facts and their source IDs;
- allowed numeric values, metadata numbers, units, and declared derived calculations;
- required negative results, blockers, and uncertainty statements;
- known conflicts, including every value and its source;
- fixture-specific forbidden claims;
- sources that must be used, skipped, or reported as unreadable;
- preservation markers for existing-report updates;
- human-review notes that explain semantic risks without prescribing prose.

The manifest is the grading contract, not a model prompt. The agent sees the source materials and user task, not the expected assertions.

## Isolated Runner

`scripts/run_behavior_evals.py` runs one skill version at a time.

1. Resolve the baseline from Git tag `v1.1.0` or the candidate from an explicit directory.
2. Hash the complete skill package and copy it into a fresh case workspace.
3. Copy the case inputs into that workspace without exposing the manifest assertions to the agent.
4. Require an explicit model ID, then invoke `codex exec --ephemeral --ignore-user-config --sandbox workspace-write --model <model-id>` with the skill path explicitly named in the task.
5. Require the run to read that exact copied `SKILL.md`, ignore any same-named global installation, use only the supplied local sources, and not perform network research.
6. Require the report at the case's expected relative path.
7. Save output, exit status, duration, model, Codex CLI version, Git commit, prompt hash, run number, and skill hash.
8. Grade only after the process exits and the expected output can be read as UTF-8 Markdown.

The global installed skill is never edited by the runner. Each run receives an independent directory and cannot overwrite fixtures, baselines, or another run.

Development runs execute each case once per version. The final release benchmark executes every case three times for `v1.1.0` and three times for the candidate. Frozen baseline results may be reused only when the skill hash, model ID, Codex CLI version, runner hash, grader hash, prompt hash, and case hash all match the candidate comparison environment; otherwise the baseline is rerun.

## Deterministic Hard Gates

`scripts/grade_report.py` evaluates each report against its manifest and emits structured grading JSON.

### Numeric closed-world check

- Normalize decimal forms, percentages, units, signs, and ranges.
- Classify dates, seed IDs, sample counts, and priority labels separately from experimental measurements.
- Require every critical source number listed by the manifest.
- Reject undeclared experimental numbers.
- Permit a derived number only when the manifest declares the operation and operands; require the report to present it as a calculation rather than a directly observed source value.

### Evidence completeness check

- Require all critical facts and negative results.
- Require blockers and uncertainty when the manifest marks them as decision-relevant.
- Require every known conflict to retain all conflicting values and source attribution.
- Require missing or unreadable sources to remain visible.

### Forbidden-claim check

- Reject fixture-specific unsupported causal claims, significance claims, citations, metadata, configurations, and explanations.
- Reject claims that a missing figure or unreadable file contained a result.
- Reject language that promotes a hypothesis or interpretation to a verified fact when the evidence contract does not support it.

### Update-safety check

- Require every manual-content preservation marker.
- Require unchanged claims that were not superseded.
- Require superseded claims to remain historically visible with the new source and change recorded.
- Reject whole-report replacement when the fixture requires a merge.

### Scope and provenance check

- Require all used sources in the report's source inventory.
- Reject citations to files outside the provided case workspace.
- Require mandated skipped and unreadable sources to be reported.

Any invented critical number, unsupported critical conclusion, omitted negative result, hidden source conflict, or destructive update fails the entire run. Hard-gate failures are not averaged away by soft scores.

## Human Review

Deterministic grading is followed by claim-level human review because semantic fabrication cannot be completely detected with string and numeric checks.

The reviewer checks:

1. whether each key conclusion is supported by a supplied source;
2. whether facts, interpretations, hypotheses, and derived calculations remain distinct;
3. whether wording exaggerates evidence strength;
4. whether the report is clear, proportionate, concise, and useful for deciding the next experiment.

A static review page presents randomized A/B outputs without identifying the skill version. It includes the case prompt, source material, hard-gate results, and fields for semantic-fidelity findings and qualitative feedback. The soft rubric uses the same scale for evidence clarity, information selection, decision usefulness, and readability. A semantic fabrication found during review is promoted to a hard-gate failure.

## Iteration Loop

1. Implement and test the corpus, manifest schema, runner, and grader without changing the skill.
2. Run and grade the frozen `v1.1.0` baseline.
3. Group failures by root cause rather than by case wording.
4. Modify only the smallest skill instruction or research-progress template needed to address a general failure.
5. Run the candidate against all cases.
6. Generate the static review page before interpreting qualitative results.
7. Record feedback and repeat until the release gate passes or further prompt changes stop producing meaningful improvement.

Potential improvements include an internal pre-draft evidence ledger, explicit separation of source facts and derived calculations, a pre-write preservation inventory for report updates, and a post-draft numeric/conflict/negative-result audit. These are candidates, not predetermined requirements. Evaluation evidence decides which are added.

## Failure Handling

Failures are classified before scoring:

- **Quality failure:** the process produced a readable report that violates a hard gate or human semantic audit. It counts as a failed run.
- **Infrastructure failure:** timeout, abnormal process exit, missing output, invalid UTF-8, or grader crash. Retry once with the identical configuration. A second failure marks the run invalid and blocks release; it does not count as a quality pass or failure.

Runner and grader errors include the case ID, run ID, stage, and actionable reason. They must not print credentials or persist raw authentication material. Partial output remains inside the isolated workspace for diagnosis.

## Testing Strategy

The grader is developed with red-green-refactor tests. Required mutation tests start from a valid fixture report and verify that grading fails after each mutation:

- insert an invented experimental value;
- remove a failed experiment;
- collapse conflicting values into one conclusion;
- promote an unsupported causal explanation to fact;
- delete a manual preservation marker;
- cite an unprovided source.

Positive tests verify a complete valid report, declared derived calculations, correct supersession, visible missing sources, and harmless differences in Markdown formatting.

The repository validator will require the case inventory, manifest schema, runner, grader, test files, benchmark summary, and synthetic-data labels. Existing repository and official skill validation remain release gates.

GitHub Actions runs deterministic grader tests and repository validation only. It does not invoke Codex or require model credentials.

## Repository Artifacts

The planned repository additions are:

```text
evals/
  research-progress/
    schema/
    cases/
      <case-id>/
scripts/
  grade_report.py
  run_behavior_evals.py
tests/
  test_grade_report.py
  test_run_behavior_evals.py
benchmarks/
  v1.1-v1.2/
    benchmark.json
    benchmark.md
    representative-outputs/
```

Raw repeated-run workspaces and transient review files remain outside the committed repository. The repository contains the public corpus, scoring implementation, aggregate results, and representative outputs needed to inspect the claims without committing session logs or authentication material. Representative outputs are selected mechanically as run 1 for each case and version; they are never hand-picked after scoring.

## Release Gate

`v1.2.0` may be published only when:

1. all 24 candidate runs pass deterministic hard gates;
2. no candidate run is invalid or has an unexplained infrastructure failure;
3. claim-level human review finds no unsupported critical conclusion;
4. the candidate's median blinded soft score is at least the baseline median, and no case-level median drops by more than one point on the five-point rubric;
5. at least one predefined adversarial case shows a measurable improvement: the baseline has one or more hard-gate failures while all three candidate runs pass, or, when both versions pass all hard gates for that case, the candidate wins at least two of three paired blinded reviews without a hard-gate regression;
6. unit tests, repository validation, official skill validation, sensitive-data scans, and fresh-clone verification pass.

If `v1.1.0` passes every accepted case, strengthen the adversarial suite before changing the prompt. If no defensible behavioral difference emerges, retain the current skill instructions and publish only the evaluation infrastructure without claiming improved report quality.

## Release Communication

Release notes will report the corpus, grading method, model and CLI metadata, baseline comparison, hard-gate outcomes, limitations, and representative failures. They will not generalize beyond the synthetic research-progress cases or claim universal hallucination prevention.
