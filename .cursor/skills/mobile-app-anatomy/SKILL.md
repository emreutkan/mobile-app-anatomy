---
name: mobile-app-anatomy
description: Exhaustively reverse-engineer and document an entire mobile application codebase. Use when asked to understand everything, map every screen/component/function/helper/flow/state, create a complete app atlas or GOD_README, audit a large React Native/Expo, Flutter/Dart, Android/Kotlin/Java, iOS/Swift/Objective-C, or Kotlin Multiplatform app, or prove that no relevant source file or user journey was skipped. Not for quick code questions or ordinary README generation.
---

# Mobile App Anatomy

Build a complete, evidence-backed anatomy atlas of a mobile application. Treat the repository as an unknown organism: inventory every relevant source unit, reconstruct cold launch and every reachable user path, trace each feature through UI → state → service → native/platform behavior, validate runtime behavior where possible, and compile the result into both modular documentation and a monolithic `GOD_README.md`.

Cost and token minimization are not objectives. Completeness, traceability, and resumability are.

## Invocation

Interpret arguments as:

```text
<repo-path> [--output <path>] [--runtime-mode auto|on|off] [--chunk-lines <n>] [--resume]
```

Defaults:

```text
repo-path: current working directory
output: <repo>/docs/mobile-app-anatomy
runtime-mode: auto
chunk-lines: 300
```

Supported primary targets:

- React Native and Expo, including Expo Router and React Navigation
- Flutter and Dart
- Android with Kotlin/Java, XML navigation, Fragments, Activities, and Jetpack Compose
- iOS with Swift/Objective-C, SwiftUI, UIKit, storyboards, and coordinators
- Kotlin Multiplatform and hybrid repositories with native modules

## Non-negotiable operating rules

1. Never conclude from sampling. Every relevant project-owned file must appear in the ledger.
2. Never mark a text file complete from a summary alone. Every generated line shard must reach `tracked_fully`.
3. Maintain exactly these work states: `not_tracked`, `tracking`, `tracked_fully`. Exclusions are separate records with explicit reasons.
4. Persist findings to disk continuously. Do not rely on conversation memory.
5. Every factual claim in final documentation must cite repository evidence: file path plus line range, runtime evidence, or both.
6. Start user-flow reconstruction at process launch, not at an arbitrary feature folder.
7. Follow discoveries recursively. A screen that references auth, storage, analytics, permissions, subscriptions, deep links, background work, or native modules creates new frontier items.
8. Do not stop because the repository is large, repetitive, expensive, or slow.
9. Do not silently skip generated source, native projects, tests, config, migrations, localization, assets, or platform manifests. Track them or exclude each with a specific justification.
10. Unknown behavior must be recorded as an unknown; never infer it as fact.
11. Runtime-unreachable paths remain documentation obligations. Explain guards, flags, or missing prerequisites.
12. Completion is determined only by the validation gates in `references/10-completion-gates.md`.
13. Never copy secret values, access tokens, private keys, signing credentials, or production personal data into reports. Record the key name, storage mechanism, and behavioral purpose with the value redacted.

## Shell and platform discipline

Detect the active shell before composing commands. The workflow must run correctly on Windows PowerShell 5.1, PowerShell 7+, cmd.exe, and POSIX shells.

On Windows PowerShell 5.1:

- Never use `&&` or `||`; they are not valid statement separators.
- Never use POSIX `\` line continuation or `VAR=value command` environment syntax.
- Prefer one command per tool invocation. If commands must be grouped, use separate lines and inspect `$LASTEXITCODE` before continuing.
- Use native argument arrays or quoted paths; do not interpolate untrusted repository paths into shell fragments.

Portable Phase 0 Git inspection should be executed as separate commands:

```powershell
git -C "<repo-path>" rev-parse HEAD
git -C "<repo-path>" status --short
git -C "<repo-path>" branch --show-current
git -C "<repo-path>" remote get-url origin
```

Do not treat a shell syntax error as repository evidence. Correct the command and rerun it.

## Required setup

Read these references before beginning:

1. `references/01-intake-and-framework-detection.md`
2. `references/02-coverage-ledger.md`
3. `references/03-route-first-exploration.md`
4. `references/08-gitnexus-integration.md`
5. `references/10-completion-gates.md`

Initialize deterministic state:

```bash
python <skill-dir>/scripts/anatomy.py init \
  --repo "<repo-path>" \
  --out "<output-path>" \
  --chunk-lines <n> \
  --runtime-mode auto
```

When project-owned generated behavior lives under a normally excluded build directory, explicitly include its source subtree:

```bash
python <skill-dir>/scripts/anatomy.py init \
  --repo "<repo-path>" \
  --out "<output-path>" \
  --include-dir "android/app/build/generated" \
  --include-dir "ios/Generated"
```

Never include an entire dependency/build tree without first identifying which generated subtrees are project-owned and behaviorally relevant.

Agent/client installation directories such as `.agents`, `.claude`, `.codex`, `.cursor`, `.cline`, and `.gemini` are excluded by default. Add repository-specific non-product tooling with repeatable `--exclude-dir` arguments:

```powershell
python <skill-dir>/scripts/anatomy.py init `
  --repo "<repo-path>" `
  --out "<output-path>" `
  --exclude-dir "tools/generated-fixtures" `
  --exclude-dir "vendor-internal-snapshots"
```

An explicit `--include-dir` overrides a default or custom directory exclusion for the included subtree. Never exclude application source merely to reduce workload.

If `--resume` was requested or the output already exists:

```bash
python <skill-dir>/scripts/anatomy.py refresh \
  --repo "<repo-path>" \
  --out "<output-path>"
python <skill-dir>/scripts/anatomy.py status --out "<output-path>"
```

If GitNexus is available, index before semantic analysis. Do not set `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` for Swift, Kotlin, or Dart repositories.

```bash
npx gitnexus analyze --force --embeddings --skills
npx gitnexus setup -c cursor,codex
```

Use `--pdg` additionally for TypeScript/JavaScript when control/data-dependence analysis is useful and supported by the installed version.

## Phase 0 — Freeze the specimen

Record:

- repository root
- current commit and dirty working-tree state
- detected frameworks and package managers
- app identifiers and platform targets
- build variants/flavors/schemes
- environment/config sources
- whether the app can currently build and launch
- available simulator/emulator/runtime-control tools

Do not modify product code during documentation unless the user explicitly asks.

## Phase 1 — Deterministic census

Run the inventory script. Inspect:

```text
<output>/machine/framework.json
<output>/machine/inventory.jsonl
<output>/machine/ledger.json
<output>/machine/routes_seed.json
<output>/machine/signals.json
<output>/COVERAGE.md
```

Correct classification errors before deep analysis. The script is a census, not semantic truth.

The ledger creates:

- line-shard units for every relevant text file
- one file-synthesis unit per file
- asset/config units where line sharding is not applicable
- merged screen/navigator candidates from filesystem routes, route declarations, and navigation calls
- feature candidates from auth, onboarding, storage, networking, analytics, purchases, permissions, notifications, deep links, background tasks, and native bridges
- file-level screen/component/navigation candidates
- symbol candidates for every deterministically discovered top-level function, class, type, protocol, component, or composable

## Phase 2 — Build the launch-to-frontier map

Read `references/03-route-first-exploration.md`.

Begin at actual process launch:

1. Native entry point and application delegate/activity/application class
2. JavaScript/Dart/Swift/Kotlin app entry
3. provider/container initialization
4. splash/loading gates
5. persisted auth/session restoration
6. remote config and feature-flag initialization
7. first rendered route for every possible initial state

Maintain `DISCOVERY_JOURNAL.md` as an observable research log, not private chain-of-thought. For every discovery, record:

```text
Observation
Evidence
Interpretation
New frontier items
Open questions
```

Example progression:

```text
Cold launch → Welcome
Welcome exposes Apple, Google, and custom account auth
Auth success → onboarding when profile_complete=false
Onboarding collects X/Y/Z
X/Y/Z are consumed by recommendation and recovery functions
Completion routes to Home or Plan Builder depending on generated_plan state
Home contains a context-sensitive header navigator and bottom navigator
Each navigator branch becomes a new screen and flow frontier
```

Continue until the screen/action frontier is empty.

## Phase 3 — Exhaust every source shard

Read:

- `references/05-symbol-and-file-dossiers.md`
- `references/09-agent-prompts.md`

For small batches, claim a specific `line_shard` work unit. Use only an ID read from the current `machine/ledger.json` or returned by `claim-next`; never derive or reuse IDs from before `init --force` or a refresh that changed file boundaries:

```bash
python <skill-dir>/scripts/anatomy.py claim --out "<output>" --unit "<unit-id>"
```

If a command reports `Unknown unit`, stop using that ID, reload the current ledger, and claim again. Do not continue as if the unit were covered.

For large repositories, claim work in one atomic batch to avoid rewriting a large ledger for every shard:

```bash
python <skill-dir>/scripts/anatomy.py claim-next \
  --out "<output>" \
  --type line_shard \
  --count 25 \
  --agent "<worker-name>"
```

For every claimed shard:

1. Read the exact line interval plus enough overlap/context to understand split symbols.
2. Write a shard evidence report under `evidence/chunks/`.
3. Record symbols, responsibilities, state reads/writes, side effects, callers/callees, feature links, navigation links, platform APIs, failure paths, and unresolved questions.
4. Add every newly discovered semantic entity to the entity ledger. Never leave a discovered helper/function/component only in prose.

Complete individual units with `complete`, or preferably create a JSON/JSONL manifest and commit a large batch atomically:

```json
[
  {
    "unit": "u_example",
    "report": "evidence/chunks/u_example.md",
    "evidence": ["src/example.ts:1-300"],
    "agent": "worker-1"
  }
]
```

```bash
python <skill-dir>/scripts/anatomy.py complete-batch \
  --out "<output>" \
  --manifest "<batch-manifest.json>"
```

After all shards of a file complete, claim and perform its `file_synthesis` unit. A file is not understood until its shards are reconciled into one dossier and connected to all symbol, feature, flow, state, and platform entities.

Claim semantic entities in large batches:

```bash
python <skill-dir>/scripts/anatomy.py entity-claim-next \
  --out "<output>" \
  --kind symbol_candidate \
  --count 250 \
  --agent "<worker-name>"
```

Complete them with `entity-complete-batch`. Multiple symbols may cite the same complete file dossier, but each symbol must be explicitly accounted for. Import discoveries in bulk with `entity-import`.

Use the strongest available reasoning model for semantic passes. Parallelize independent units, but never allow multiple agents to write the same report or ledger record simultaneously.

## Phase 4 — Reconstruct mobile-specific systems

Read `references/04-mobile-feature-taxonomy.md`.

Map at minimum:

- launch/bootstrap
- authentication and account lifecycle
- onboarding and profile derivation
- navigation graphs, nested navigators, tabs, drawers, sheets, modals, overlays
- screen and component hierarchy
- UI state, domain state, server state, persistence, caches
- networking and request/response transforms
- offline behavior and synchronization
- permissions and privacy prompts
- notifications and deep links
- subscriptions, purchases, restore, entitlement state
- analytics, experiments, remote config, feature flags
- background tasks, widgets, extensions, watch modules, services
- native bridges and platform divergence
- accessibility, localization, theming, responsive behavior
- error, loading, empty, partial, stale, and recovery states
- tests and what behavior they prove or fail to cover
- build, signing, release, and store-facing configuration insofar as it changes app behavior

For every feature, trace:

```text
entry conditions
→ user-visible surface
→ interactions
→ validation
→ state transitions
→ services/network/native calls
→ persistence
→ analytics
→ success/failure/interrupt paths
→ downstream feature effects
```

## Phase 5 — Runtime validation

Read `references/06-runtime-validation.md`.

When a runnable build and control tool exist, operate the app as a user. Static findings are hypotheses until runtime confirms them.

Exercise a state matrix including:

- fresh install
- logged out
- logged in
- partially onboarded
- fully onboarded
- free/subscribed/expired entitlement
- no data/some data/large data
- loading/timeout/error/offline/stale cache
- permissions undecided/allowed/denied/revoked
- foreground/background/terminated/restored
- deep-link and notification entry
- smallest/largest supported screens
- keyboard and accessibility settings
- platform-specific iOS/Android branches

Store screenshots, logs, test flows, and observed state transitions under `08-runtime/` and `evidence/runtime/`.

If runtime is unavailable, document the exact blocker. Do not mark runtime entities verified.

## Phase 6 — Cross-system synthesis

Read `references/07-synthesis-and-output.md`.

Produce modular authoritative documents and then compile:

```bash
python <skill-dir>/scripts/render_readme.py \
  --out "<output-path>" \
  --title "<App Name> — Complete Mobile Application Anatomy"
```

Required principal outputs:

```text
GOD_README.md
COVERAGE.md
DISCOVERY_JOURNAL.md
UNKNOWNS.md
CONTRADICTIONS.md
00-product/PRODUCT_MODEL.md
01-launch-auth-onboarding/LAUNCH_MAP.md
02-navigation/NAVIGATION_GRAPH.md
03-screens/SCREEN_INDEX.md
04-features/FEATURE_INDEX.md
05-flows/FLOW_INDEX.md
06-state-data/STATE_DATA_MAP.md
07-platform/PLATFORM_MAP.md
08-runtime/STATE_MATRIX.md        # when runtime is executed
08-runtime/BLOCKER.md             # when runtime cannot be executed
09-code-atlas/CODE_INDEX.md
evidence/
machine/
```

`GOD_README.md` is a compiled monolith. Modular files remain the maintainable source of truth.

## Phase 7 — Adversarial verification

Assign independent verifier agents that did not write the original sections. They must search for:

- files with incomplete shards
- symbols absent from dossiers
- routes without screen docs
- screens without incoming or outgoing transitions
- navigation calls to undocumented destinations
- features with UI but no state/service trace
- state/services with no feature owner
- orphaned native modules
- unreferenced assets and localization keys
- dynamic routes and reflection/registration patterns
- feature flags and build-variant-only behavior
- deep links, notifications, background tasks, widgets, extensions
- contradictory documentation claims
- evidence paths or line ranges that no longer exist
- runtime observations that disagree with static analysis

Run:

```bash
python <skill-dir>/scripts/anatomy.py validate --out "<output-path>"
```

Do not declare completion unless it exits successfully.

## Resume and change handling

The analysis must survive context resets and multiple sessions.

At each session start:

```bash
python <skill-dir>/scripts/anatomy.py refresh --repo "<repo>" --out "<output>"
python <skill-dir>/scripts/anatomy.py status --out "<output>"
```

Changed files are reset to `not_tracked`; unchanged completed units remain complete. New files create new units. Removed files are archived in state rather than silently deleted.

## Final response contract

Report:

- repository commit analyzed
- detected frameworks/platforms
- file, line-shard, file-synthesis, screen, feature, and flow counts
- static coverage percentage
- runtime coverage percentage
- unresolved unknowns and blockers
- validation result
- locations of `GOD_README.md`, `COVERAGE.md`, and the machine ledger

Never say “complete” when validation is failing.
