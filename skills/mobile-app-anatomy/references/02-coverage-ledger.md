# Coverage Ledger

## Purpose

The ledger is the authority for completeness. Conversation memory, a task list, and a prose statement such as “I reviewed the app” are not evidence.

## Work states

Every work unit uses exactly:

- `not_tracked`
- `tracking`
- `tracked_fully`

An item may also have a separate `excluded` record. `blocked` is recorded as a blocker field, but a blocked item remains `not_tracked` or `tracking`; it does not count as complete.

## Unit hierarchy

The inventory script creates:

### Line shards

Text files are divided into contiguous shards, normally 300 lines. Every line belongs to exactly one primary shard. Agents may read overlap around shard boundaries, but completion evidence must identify the primary interval.

### File synthesis units

A file-synthesis unit depends on every shard of that file. It reconciles split functions, symbols, imports, exports, behavior, and feature/flow relationships.

### Asset/config units

Binary assets or non-line-oriented project artifacts get a single unit. Completion requires metadata, usage references, and visual/behavioral interpretation when relevant.

### Semantic entities

Agents create and track:

- screens
- overlays/modals/sheets
- navigators
- features
- user flows
- state machines
- services
- persisted stores
- APIs
- permissions
- notifications
- deep links
- subscriptions/entitlements
- background tasks
- native bridges
- app targets/extensions

## Claiming

Before work:

```bash
python scripts/anatomy.py claim --out <output> --unit <unit-id> --agent <name>
```

A claimed unit records agent, timestamp, and previous state. Do not claim a unit already marked `tracking` by another active agent.

## Completing

Completion requires:

- a report path that exists
- evidence references
- no unresolved contradiction inside the unit
- all discovered dependencies added to the frontier
- all discovered screens/features/flows registered as entities
- status changed to `tracked_fully`

```bash
python scripts/anatomy.py complete \
  --out <output> \
  --unit <unit-id> \
  --report evidence/chunks/example.md \
  --evidence "src/example.ts:1-300"
```

## Adding entities

```bash
python scripts/anatomy.py entity-add \
  --out <output> \
  --kind screen \
  --id screen.home \
  --title "Home" \
  --source "src/screens/Home.tsx:1-240"
```

Complete them only after their required documentation exists:

```bash
python scripts/anatomy.py entity-complete \
  --out <output> \
  --id screen.home \
  --report "03-screens/Home.md" \
  --evidence "src/screens/Home.tsx:1-240"
```

## Refresh behavior

`refresh` compares file hashes.

- unchanged completed files preserve status
- modified files reset their shards and file synthesis to `not_tracked`
- new files create units
- removed files are archived with removal metadata
- changed line counts regenerate shard boundaries
- semantic entities linked only to changed files are marked for re-verification

## Coverage dimensions

`COVERAGE.md` must report separately:

- relevant files inventoried
- text lines assigned to shards
- line shards complete
- file synthesis units complete
- assets/config units complete
- screens complete
- features complete
- flows complete
- state systems complete
- platform/native surfaces complete
- static evidence coverage
- runtime state-matrix coverage
- contradictions
- unknowns
- exclusions

Never combine static and runtime coverage into one misleading number.

## Evidence quality

Strong evidence:

- exact file and line range
- GitNexus symbol UID and context/process result
- runtime screenshot with state description
- device log tied to an action
- test case and result
- network trace tied to the flow

Weak evidence:

- filename only
- directory-level assumption
- README claim not verified against code
- package presence without usage evidence
- model inference without a source

A weak source can create a hypothesis but cannot close an entity.

## Large-repository batch operations

For repositories with thousands of shards or symbols, do not perform one ledger rewrite per item. Claim and complete work in batches:

```bash
python scripts/anatomy.py claim-next \
  --out <output> \
  --type line_shard \
  --count 25 \
  --agent worker-1
```

A completion manifest may be JSON or JSONL:

```json
[
  {
    "unit": "u_123",
    "report": "evidence/chunks/u_123.md",
    "evidence": ["src/file.ts:1-300"],
    "agent": "worker-1"
  }
]
```

```bash
python scripts/anatomy.py complete-batch \
  --out <output> \
  --manifest batch.json
```

Use equivalent entity commands:

```bash
python scripts/anatomy.py entity-claim-next \
  --out <output> \
  --kind symbol_candidate \
  --count 250 \
  --agent symbol-worker

python scripts/anatomy.py entity-complete-batch \
  --out <output> \
  --manifest entity-batch.json
```

Newly discovered entities can be imported in one operation:

```bash
python scripts/anatomy.py entity-import \
  --out <output> \
  --manifest discovered-entities.jsonl
```

Each imported object requires `id`, `kind`, and `title`; it may include `sources` and `metadata`.

## Symbol obligations

The deterministic census seeds every top-level symbol it can recognize. This is a lower bound, not a complete parser for every language construct. During shard and file synthesis, agents must add missed methods, closures, generated route handlers, extension methods, reducers, selectors, callbacks, native bridge methods, and dynamic registrations to the entity ledger.

A symbol may share a file dossier with other symbols, but it cannot remain absent or untracked. Every symbol entity must be `tracked_fully` or explicitly excluded with a reason.
