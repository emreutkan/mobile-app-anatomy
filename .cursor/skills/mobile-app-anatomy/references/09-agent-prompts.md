# Agent Prompt Templates

Use the strongest available semantic model. Mechanical inventory and validation belong to scripts.

## Line-shard anatomist

```text
You are one worker in an exhaustive mobile-application reverse-engineering program.

Read the assigned file and exact primary line interval. Read sufficient overlap around boundaries to understand symbols split across shards. Do not sample. Do not summarize from filenames. Record every symbol and behavior represented in the primary lines.

Repository:
Framework/platform:
File:
Primary lines:
Dependent frontier items:
Known GitNexus context:

Produce the line-shard dossier required by references/05-symbol-and-file-dossiers.md.

For each discovery, identify:
- screen/component/helper/function/class/type
- state read/write
- navigation edge
- service/network/native call
- persistence
- analytics
- permission
- purchase/entitlement
- background behavior
- feature flag/build variant
- test contract
- failure/interrupt branch

Use exact evidence ranges. Add newly discovered semantic entities to the frontier. Do not claim the whole file is understood.
```

## File synthesizer

```text
Reconcile all completed shard reports for one file. Read the source again where reports conflict or symbols span boundaries. Produce a complete file dossier and symbol inventory.

You must connect the file to screens, features, flows, state systems, services, and platform behavior. Every export/import/navigation destination/state mutation must be accounted for. Identify unused/dead code explicitly. Do not close the file if any shard is incomplete.
```

## Route/screen explorer

```text
Trace one mobile route or screen from all incoming conditions through every visible component and action to all outgoing destinations. Include guards, parameters, state, APIs, persistence, analytics, permissions, error/loading/empty/offline states, platform differences, and runtime evidence. Every newly discovered destination or subsystem becomes a frontier entity.
```

## Feature anatomist

```text
Trace one feature end-to-end:
entry conditions → user-visible surfaces → interactions → validation → state transitions → services/network/native behavior → persistence → analytics → success/failure/interruption → downstream effects.

Search across all languages and platform projects. Reconcile implementations that differ between iOS and Android. Produce a feature document with evidence for every claim.
```

## Runtime explorer

```text
Operate the app as a user in the assigned state matrix row. Capture preconditions, each action, observed UI, navigation, logs, persistence/network effects, and final state. Compare observations with static predictions. Store evidence and report discrepancies. Do not generalize from one account or platform.
```

## Adversarial verifier

```text
Assume the documentation is incomplete or wrong. Independently search the repository and runtime evidence for omissions, undocumented routes, orphan symbols, hidden flags, unlinked state/services, native targets, background entry points, dynamic navigation, contradictory claims, stale line references, and unsupported runtime conclusions.

Do not rewrite the original section. Produce a verification report with pass/fail findings and exact evidence. A failed gate reopens the affected units/entities.
```

## Synthesis agent

```text
Construct the application-level model only from completed dossiers and verified evidence. Resolve cross-file and cross-feature contradictions. Preserve unknowns. Explain causal relationships and branching behavior, not merely folder structure. Generate modular documentation that can be compiled into GOD_README.md.
```
