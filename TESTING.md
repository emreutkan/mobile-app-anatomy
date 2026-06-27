# Testing

Run the included smoke tests:

```bash
python -m unittest discover -s tests -v
```

The tests verify:

- Expo/React Native framework detection
- canonical filesystem/navigation route discovery
- screen, feature, and symbol seed entities
- exclusion of dependency directories
- forced inclusion of generated mobile source
- atomic batch claim and completion
- GOD_README compilation

A separate end-to-end smoke run was used during packaging to complete all generated units/entities, produce the required named indexes, document a runtime blocker, compile the atlas, and obtain `VALIDATION PASS`.
