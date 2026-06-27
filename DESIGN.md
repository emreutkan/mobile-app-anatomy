# Design lineage

This package combines useful architectural patterns from `code-to-docs` and GitNexus, but changes their stopping rules for exhaustive mobile-app reverse engineering.

## Patterns retained from code-to-docs

Source reviewed: `RCellar/code-to-docs-skill`.

The source system uses a staged documentation pipeline:

1. survey the repository and identify modules;
2. run a first semantic extraction pass;
3. run a second analysis/health pass;
4. synthesize cross-module documentation;
5. persist state for incremental updates;
6. verify generated documentation.

Those are sound orchestration patterns and are retained here as census, shard analysis, file synthesis, cross-system synthesis, refresh, and adversarial verification.

## Constraints intentionally removed

The source prompts contain cost- and context-saving behavior such as bounded call-chain depth, large-file search shortcuts, and tiered model use. Those choices are appropriate for ordinary documentation but conflict with the requested completeness contract.

`mobile-app-anatomy` therefore:

- does not stop at a fixed call depth;
- does not treat large files as sampled evidence;
- does not allow a module summary to close unread line ranges;
- does not optimize token spend as an objective;
- makes completion depend on a machine ledger rather than an agent's confidence.

## How GitNexus is used

Source reviewed: `abhigyanpatwari/GitNexus`.

GitNexus builds a persistent local knowledge graph from parsed repository structure. It contributes symbol lookup, imports, callers/callees, functional clusters, execution processes, graph queries, and repository-specific generated skills. This package uses that graph as an accelerator for relationship discovery and cross-checking.

GitNexus is not the completeness authority because dynamic routes, runtime injection, server-driven behavior, platform configuration, assets, flags, generated registration, and runtime state may not be fully resolved statically. The line ledger and semantic entity ledger remain authoritative.

For mobile repositories, optional Swift, Kotlin, and Dart grammars must remain enabled. Program-dependence analysis is treated as an additional TypeScript/JavaScript signal when available, not as a universal mobile-language guarantee.

## Mobile-first inversion

Ordinary code documentation often starts from folders and modules. This skill starts from operating-system and user entry points:

```text
process launch
→ native host entry
→ framework entry
→ initialization gates
→ first visible destination
→ every action and branch
→ discovered feature/state/service/native frontier
```

The repository census runs in parallel so route-first discovery cannot overlook hidden/background/non-UI behavior.

## Completion model

The system uses two interlocking obligations:

1. Structural coverage: every relevant file and line shard is completed or explicitly excluded.
2. Semantic coverage: every discovered screen, component, symbol, feature, flow, state system, service, API, permission, purchase, background target, and native bridge is completed or explicitly excluded.

Runtime evidence is tracked separately from static evidence. Static completion never silently implies runtime verification.

## Source projects

- code-to-docs: https://github.com/RCellar/code-to-docs-skill
- GitNexus: https://github.com/abhigyanpatwari/GitNexus
