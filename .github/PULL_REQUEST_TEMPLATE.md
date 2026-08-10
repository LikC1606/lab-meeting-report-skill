## Summary

Describe the user-visible problem and the change that addresses it.

## Evidence And Safety Impact

Explain whether the change affects numeric fidelity, source provenance, negative results, file scope, existing-report updates, or Feishu/Lark operations.

## Verification

List the checks you ran and their results.

```text
python -m unittest discover -s tests -v
python scripts/validate_repo.py .
```

## Checklist

- [ ] The change is focused and contains no private research data or secrets.
- [ ] Public examples use only synthetic or thoroughly anonymized material.
- [ ] New source files referenced by examples are included.
- [ ] English and Chinese documentation remain behaviorally consistent.
- [ ] Tests and repository validation pass, or skipped checks are explained.
- [ ] Behavioral claims are supported by versioned evaluation evidence.
