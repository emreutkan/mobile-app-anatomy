# Route-First Exploration

## Goal

Reconstruct the application in the same order a user and the operating system encounter it, while recursively expanding every discovered dependency.

## Frontier algorithm

Maintain three lists in `DISCOVERY_JOURNAL.md` and `machine/entities.json`:

- `frontier` — discovered but not yet fully traced
- `active` — currently being investigated
- `closed` — fully traced with evidence

Start with:

- each platform process entry
- every launcher activity/scene/window
- deep-link entry
- push-notification entry
- widget/extension entry
- background execution entry

For each frontier item:

1. Identify entry conditions and guards.
2. Find the exact implementation.
3. Enumerate visible UI and interactive actions.
4. Enumerate state reads and writes.
5. Enumerate navigation destinations.
6. Enumerate services, storage, native APIs, analytics, permissions, flags, and side effects.
7. Add every new concept to the correct frontier.
8. Trace success, cancellation, failure, interruption, and retry paths.
9. Close only after all outgoing edges are documented or explicitly classified as dead/unreachable.

## Cold launch branches

At minimum evaluate:

- first install
- returning user
- authenticated session
- expired/revoked session
- incomplete onboarding
- migrations pending
- remote config unavailable
- cached data available/unavailable
- app opened from icon
- app opened from deep link
- app opened from notification
- restored background state

## Screen dossier requirements

Each screen/overlay document must contain:

- stable ID and route name/path
- platform availability
- source files
- navigator/container hierarchy
- all incoming transitions and their conditions
- all outgoing transitions and their conditions
- guards and redirects
- parameters and validation
- component tree
- visible copy and localization keys
- interactive controls and handlers
- state dependencies
- service/API dependencies
- persisted state reads/writes
- analytics events
- permissions and native APIs
- loading/empty/error/offline/stale states
- accessibility behavior
- screenshots/runtime evidence
- tests
- unresolved questions

## Navigation patterns to search

### React Native / Expo

- route files and `_layout`
- `Stack.Screen`, `Tabs.Screen`, `Drawer.Screen`
- `navigation.navigate`, `push`, `replace`, `reset`, `goBack`
- `router.push`, `replace`, `back`, `Link`
- conditional navigator rendering
- navigation refs and deep-link config
- modal presentation options

### Flutter

- `MaterialApp.routes`, `onGenerateRoute`
- `Navigator.push*`, `pop*`
- `GoRoute`, `ShellRoute`, redirects
- `AutoRoute`, guards
- nested navigators and tab shells
- modal bottom sheets and dialogs

### Android

- manifest launcher and exported components
- XML navigation destinations/actions
- Compose `NavHost`, `composable`, `navigation`, `dialog`
- Intents, activity results, fragments
- bottom navigation and drawers
- conditional graph start destinations

### iOS

- SwiftUI `WindowGroup`, `NavigationStack`, `navigationDestination`
- `NavigationLink`, sheets, full-screen covers, popovers
- UIKit coordinators, `pushViewController`, `present`
- storyboards, segues, tab controllers
- URL/openURL handlers and scene restoration

## Dynamic and hidden paths

Search specifically for:

- computed route names
- route registries
- reflection/annotation registration
- server-driven navigation
- remote-config destinations
- feature-flagged screens
- debug/admin/developer menus
- build-flavor-only routes
- experiment variants
- notification payload route mapping
- deep-link wildcard handlers

## Observable research log

Use concise entries:

```markdown
## 2026-06-28T12:00:00Z — Auth gate

**Observation:** Root layout waits for persisted session and profile status.
**Evidence:** `app/_layout.tsx:40-118`, `src/auth/session.ts:12-94`.
**Interpretation:** Initial destination has three branches: welcome, onboarding, tabs.
**New frontier:** `screen.welcome`, `flow.oauth.apple`, `flow.oauth.google`,
`flow.email_auth`, `flow.onboarding`, `navigator.main_tabs`.
**Open questions:** How is revoked-token recovery handled?
```

This is an auditable decision log. Do not write hidden/private chain-of-thought.
