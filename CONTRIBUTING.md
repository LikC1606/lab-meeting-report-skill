# Contributing

Contributions that make research reporting more accurate, auditable, portable, or easier to use are welcome.

## Before You Start

- Search existing issues and discussions for related work.
- Open a feature request before making a broad behavioral or format change.
- Do not include unpublished research, personal data, credentials, private Feishu/Lark links, or copied proprietary material.
- Use synthetic or thoroughly anonymized examples.
- Keep changes focused. A pull request should solve one coherent problem.

Questions about usage and report design belong in [Discussions](https://github.com/LikC1606/lab-meeting-report-skill/discussions). Reproducible defects belong in the [bug form](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=bug_report.yml).

## Development Setup

The repository validation suite targets Python 3.12 and requires PyYAML.

```bash
python -m pip install "PyYAML>=6.0,<7"
python -m unittest discover -s tests -v
python scripts/validate_repo.py .
```

To regenerate the deterministic README preview after changing its example content:

```bash
python -m pip install reportlab pymupdf
python scripts/render_preview.py
```

The validator checks the portable skill layout, metadata, public examples, evaluation assets, release benchmark, UTF-8 safety, and blocked secret patterns.

Do not run the behavior benchmark unless your change requires a new model-based evaluation. The checked-in unit tests and repository validator do not call external model APIs.

## Change Guidelines

### Skill behavior

- Preserve the separation between source facts, derived calculations, interpretations, and hypotheses.
- Keep negative results, blockers, missing evidence, and unresolved conflicts visible.
- Do not weaken scoped file access, safe report updates, or Feishu/Lark authorization boundaries.
- Update or add a synthetic evaluation case when behavior changes.
- Do not revise published benchmark claims without a versioned evaluation artifact that supports the new claim.

### Documentation and examples

- Keep the English and Chinese README files behaviorally consistent.
- Prefer a complete input/output example over a promotional claim.
- Include every local source referenced by a public example.
- Label synthetic data prominently and never present it as real research.
- Use relative links so examples remain usable in forks and offline clones.

### Feishu/Lark integration

- Use user identity and minimum required scopes.
- Read only resources the user explicitly selected.
- Validate the local Markdown before any remote write.
- Never add destructive remote operations or silent bot fallback behavior.

## Pull Requests

Before opening a pull request:

1. Run the unit tests and repository validator.
2. Review the diff for private data, secrets, generated noise, and unrelated changes.
3. Explain the user-visible problem and why the proposed behavior is evidence-safe.
4. State which checks you ran and any checks you could not run.
5. Update documentation and examples when the public workflow changes.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
