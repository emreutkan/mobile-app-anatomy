# Synthesis and Output

## Output hierarchy

```text
docs/mobile-app-anatomy/
├── GOD_README.md
├── COVERAGE.md
├── DISCOVERY_JOURNAL.md
├── UNKNOWNS.md
├── CONTRADICTIONS.md
├── 00-product/
│   └── PRODUCT_MODEL.md
├── 01-launch-auth-onboarding/
│   └── LAUNCH_MAP.md
├── 02-navigation/
│   └── NAVIGATION_GRAPH.md
├── 03-screens/
│   └── SCREEN_INDEX.md
├── 04-features/
│   └── FEATURE_INDEX.md
├── 05-flows/
│   └── FLOW_INDEX.md
├── 06-state-data/
│   └── STATE_DATA_MAP.md
├── 07-platform/
│   └── PLATFORM_MAP.md
├── 08-runtime/
│   ├── STATE_MATRIX.md
│   └── BLOCKER.md
├── 09-code-atlas/
│   └── CODE_INDEX.md
├── evidence/
│   ├── chunks/
│   ├── files/
│   └── runtime/
└── machine/
```

## GOD_README order

1. Executive application model
2. Product purpose and user types
3. Platform/framework architecture
4. Complete launch sequence
5. Authentication/account lifecycle
6. Onboarding and personalization
7. Navigation architecture
8. Screen atlas
9. Feature encyclopedia
10. User-flow encyclopedia
11. State, persistence, and data lifecycle
12. Networking and service integration
13. Permissions, notifications, deep links
14. Purchases and entitlements
15. Native/platform-specific behavior
16. Background targets/extensions/widgets/watch
17. Analytics, experiments, remote config
18. Error, offline, and recovery behavior
19. Accessibility, localization, appearance
20. Build/release behavior
21. Test and observability map
22. Complete code atlas
23. Unknowns, contradictions, dead code
24. Coverage and verification report

## Evidence notation

Use a stable notation:

```text
[repo:path/to/file.ts:L40-L118]
[runtime:ios/fresh-install/welcome.png]
[gitnexus:Function:path/to/file.ts:symbolName]
[test:path/to/test.ts:L12-L88]
```

Every paragraph making implementation claims should contain evidence or link to a lower-level document that does.

## Screen index

Generate tables for:

- route ID
- screen name
- platform
- incoming paths
- outgoing paths
- guards
- source files
- static status
- runtime status

## Feature index

Generate tables for:

- feature ID
- user value
- entry points
- screens
- flows
- state/services
- persistence/API/native effects
- flags/variants
- tests
- status

## Flow index

A flow document must show:

- trigger and preconditions
- happy path
- branch graph
- cancellation/back behavior
- errors and retries
- persistence points
- analytics
- terminal states
- source evidence
- runtime evidence

Use Mermaid for readable graphs but also include text/tables so the documentation remains searchable.

## Monolithic compilation

`render_readme.py` concatenates modular markdown in lexical directory/file order, strips repeated YAML frontmatter, adds source-file boundaries, and creates a table of contents. The monolith is derived output; edit modular files, then regenerate.
