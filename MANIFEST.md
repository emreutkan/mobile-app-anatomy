# Release manifest

Version: `1.0.1`

Primary components:

- Agent Skill: `skills/mobile-app-anatomy/SKILL.md`
- Deterministic census/coverage engine: `scripts/anatomy.py`
- Monolithic atlas compiler: `scripts/render_readme.py`
- Ten mobile-analysis reference protocols
- Five dossier templates and batch-manifest examples
- Claude plugin metadata
- Codex plugin and marketplace metadata
- Cursor project rule
- Windows and Unix installers
- Automated smoke tests

Packaging checks:

- Python compilation: PASS
- JSON manifest parsing: PASS
- Shell syntax: PASS
- Unit smoke tests: PASS
- End-to-end validator smoke test: PASS

## 1.0.1 fixes

- Added Windows PowerShell 5.1 command discipline; agents must not use `&&`/`||`.
- Excluded common repo-local agent/client directories before census creation.
- Added repeatable `--exclude-dir` to `init` and `refresh`.
- Added actionable diagnostics for stale or malformed unit IDs.
- Added regression tests for default agent-directory exclusions and custom exclusion persistence.
