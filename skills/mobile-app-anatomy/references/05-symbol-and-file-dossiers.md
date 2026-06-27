# Symbol and File Dossiers

## Line-shard report

Each shard report must include:

```markdown
# <path> — lines <start>-<end>

## Exact coverage
Primary lines:
Context overlap:

## Symbols encountered
- symbol, kind, declaration range, visibility/export status

## Responsibilities

## Inputs and outputs

## State read

## State written

## Side effects

## Calls and dependencies

## Navigation and UI effects

## Feature and flow links

## Platform/native behavior

## Error and interruption behavior

## Tests and contracts

## Discoveries added to frontier

## Contradictions or ambiguities

## Evidence
```

Do not quote large implementations. Use precise references and short signatures.

## File synthesis dossier

After all shards are complete, create one file dossier:

```markdown
# <path>

## Role in the application

## Complete symbol inventory

## Public surface

## Internal control flow

## Data flow and state transitions

## Callers and consumers

## Callees and dependencies

## Screens/components rendered

## Features implemented or supported

## User flows participated in

## Persistence/network/native effects

## Failure modes and recovery

## Platform/build-variant behavior

## Tests

## Known dead/unreachable code

## Open questions

## Source-shard evidence
```

The complete symbol inventory must reconcile regex/static parser findings, GitNexus graph results, and manual reading. Missing or anonymous callbacks should still be described by location and responsibility.

## Component dossier

For UI components include:

- props and defaults
- controlled/uncontrolled behavior
- local state
- context/store dependencies
- hooks/effects
- render branches
- event handlers
- accessibility labels/roles
- animation/gesture behavior
- error/loading/empty states
- reuse sites
- visual asset and localization dependencies

## Helper/function dossier

For significant helpers and functions include:

- signature
- semantic purpose
- preconditions
- postconditions
- pure/impure classification
- state and side effects
- callers
- callees
- edge cases
- failure behavior
- business rule encoded
- tests
- feature consequences

## Cross-file verification

A file synthesis cannot close until:

- every exported symbol has at least one documented consumer or is marked unused
- every import is classified
- every navigation destination is registered
- every state read/write is connected to an owning state system
- every network/native call is connected to a feature/flow
- every TODO/FIXME/disabled branch is recorded
- all shard contradictions are resolved or moved to `CONTRADICTIONS.md`

## Secret handling

Configuration and source may contain credentials or tokens. Document the existence, resolution order, consumers, storage mechanism, and security implications, but replace values with `<REDACTED>`. Do not place secrets in evidence reports, `DISCOVERY_JOURNAL.md`, machine manifests, screenshots, logs, or `GOD_README.md`.
