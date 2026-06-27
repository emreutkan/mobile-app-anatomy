# Mobile App Anatomy

`mobile-app-anatomy` is an exhaustive reverse-engineering skill for large mobile applications. It is designed for React Native/Expo, Flutter, native Android, native iOS, Kotlin Multiplatform, and mixed repositories.

It does not produce a conventional repository summary. It creates a persistent census, divides every relevant text file into auditable line shards, reconstructs the application from cold launch outward, maps screens/components/features/flows/state/services/native behavior, validates runtime behavior where tooling is available, and refuses to finish until the coverage validator passes.

## Core behavior

- Inventories every project-owned file and records explicit exclusions.
- Maintains `not_tracked`, `tracking`, and `tracked_fully` statuses.
- Creates line-shard and file-synthesis work units.
- Seeds explicit obligations for discovered screens, navigators, features, components, and top-level symbols.
- Supports atomic batch claiming/completion so million-line repositories do not rewrite the full ledger for every individual shard.
- Starts from process launch, auth/session restoration, splash gates, onboarding, and initial routing.
- Recursively expands screens, actions, branches, business rules, services, persistence, permissions, purchases, analytics, deep links, notifications, and native integrations.
- Keeps all findings on disk so work can span many sessions and agents.
- Requires path-and-line evidence for implementation claims.
- Produces modular documentation plus a compiled `GOD_README.md`.
- Uses a machine-verifiable completion gate rather than trusting an agent's statement that it is done.

## Package layout

```text
mobile-app-anatomy/
├── skills/mobile-app-anatomy/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/anatomy.py
│   ├── scripts/render_readme.py
│   └── assets/
├── cursor/mobile-app-anatomy.mdc
├── .claude-plugin/
├── .codex-plugin/
├── install.ps1
└── install.sh
```

## Install

### Windows PowerShell

```powershell
# Install for Claude, Codex, and the current Cursor project
.\install.ps1 -Target all -ProjectPath "C:\path\to\your\mobile-app"

# Or one target only
.\install.ps1 -Target cursor -ProjectPath "C:\path\to\your\mobile-app"
.\install.ps1 -Target claude
.\install.ps1 -Target codex
```

### macOS/Linux

```bash
./install.sh all /path/to/your/mobile-app
# or: ./install.sh cursor /path/to/your/mobile-app
```

Manual locations:

```text
Claude: ~/.claude/skills/mobile-app-anatomy/
Codex:  ~/.agents/skills/mobile-app-anatomy/
Cursor: <project>/.cursor/skills/mobile-app-anatomy/
        <project>/.cursor/rules/mobile-app-anatomy.mdc
```


### Codex plugin marketplace

The package also includes a Codex plugin manifest and local marketplace definition. Add the package root as a marketplace:

```bash
codex plugin marketplace add /absolute/path/to/mobile-app-anatomy
```

Then install `mobile-app-anatomy` from the Codex plugin directory. Direct local-skill installation through `install.ps1` or `install.sh` remains the simplest setup for personal use.

## GitNexus setup

Install and index inside the application repository:

```bash
npm install -g gitnexus@latest
gitnexus setup -c cursor,codex
gitnexus analyze --force --embeddings --skills
```

For TypeScript/JavaScript repositories, add `--pdg` when supported and useful:

```bash
gitnexus analyze --force --embeddings --skills --pdg
```

Do not set `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` for repositories containing Swift, Kotlin, or Dart, because those grammars are needed for mobile-language indexing.

GitNexus is an accelerator and graph source, not the completion authority. The deterministic anatomy ledger remains authoritative.

## Invoke

Use a direct instruction such as:

```text
Use the mobile-app-anatomy skill on this repository in exhaustive mode. Start from cold launch, resume until every relevant work unit and entity is tracked fully, compile GOD_README.md, and do not claim completion until validation passes.
```

The skill initializes:

```bash
python <skill-dir>/scripts/anatomy.py init \
  --repo . \
  --out ./docs/mobile-app-anatomy \
  --chunk-lines 300 \
  --runtime-mode auto
```

Force inclusion of behaviorally relevant generated subtrees that would otherwise be excluded as build output:

```bash
python <skill-dir>/scripts/anatomy.py init \
  --repo . \
  --out ./docs/mobile-app-anatomy \
  --include-dir android/app/build/generated
```

Resume later with:

```bash
python <skill-dir>/scripts/anatomy.py refresh --repo . --out ./docs/mobile-app-anatomy
python <skill-dir>/scripts/anatomy.py status --out ./docs/mobile-app-anatomy
```


For large repositories, use batch operations:

```bash
python <skill-dir>/scripts/anatomy.py claim-next \
  --out ./docs/mobile-app-anatomy \
  --type line_shard \
  --count 25 \
  --agent worker-1

python <skill-dir>/scripts/anatomy.py complete-batch \
  --out ./docs/mobile-app-anatomy \
  --manifest ./batch.json

python <skill-dir>/scripts/anatomy.py entity-claim-next \
  --out ./docs/mobile-app-anatomy \
  --kind symbol_candidate \
  --count 250 \
  --agent symbol-worker
```

Example manifests are included under `skills/mobile-app-anatomy/assets/`.

Compile the atlas:

```bash
python <skill-dir>/scripts/render_readme.py \
  --out ./docs/mobile-app-anatomy \
  --title "Application Anatomy Atlas"
```

Final gate:

```bash
python <skill-dir>/scripts/anatomy.py validate --out ./docs/mobile-app-anatomy
```

Completion is valid only when the command prints:

```text
VALIDATION PASS
```

## Output

The generated atlas includes product structure, launch/auth/onboarding, navigation, every screen, feature and flow dossiers, state/data lifecycle, platform/native behavior, runtime observations or an explicit runtime blocker, code dossiers, unknowns, contradictions, evidence, coverage metrics, and a compiled `GOD_README.md`. Validation requires the named product, launch, navigation, screen, feature, flow, state/data, platform, and code index files rather than accepting empty directories.

The machine-readable ledger under `docs/mobile-app-anatomy/machine/` makes the process resumable and auditable even for repositories that require thousands of analysis calls.
