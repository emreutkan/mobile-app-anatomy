# Intake and Framework Detection

## Objective

Freeze the exact repository state and identify every mobile application surface before semantic analysis begins.

## Specimen record

Create `<output>/00-product/SPECIMEN.md` with:

- repository root and remote
- HEAD commit
- dirty files and untracked files
- default branch
- monorepo workspaces
- application names and bundle/application IDs
- supported iOS and Android versions
- build variants, flavors, schemes, targets, extensions, widgets, watch apps
- package manager and lockfiles
- environment files and configuration resolution order
- build commands and launch commands
- detected simulator/emulator tooling
- whether runtime testing is possible

Never switch commits or clean the working tree without explicit permission.

## Detection order

### React Native / Expo

Inspect:

- `package.json`
- `app.json`, `app.config.js`, `app.config.ts`
- `eas.json`
- `metro.config.*`, `babel.config.*`
- `ios/Podfile`, `ios/*.xcodeproj`, `ios/*.xcworkspace`
- `android/settings.gradle*`, `android/build.gradle*`, `android/app/build.gradle*`
- `app/` for Expo Router
- navigation packages and root navigation containers
- state packages: Redux, Zustand, Jotai, MobX, XState, React Query/TanStack Query
- native modules and config plugins

Framework signals:

- Expo Router: `expo-router`, `app/_layout.*`, route groups such as `(tabs)`
- React Navigation: `NavigationContainer`, `createNativeStackNavigator`, `createBottomTabNavigator`, `createDrawerNavigator`
- bare React Native: `AppRegistry.registerComponent`
- Expo entry: `registerRootComponent`, `expo-router/entry`

### Flutter

Inspect:

- `pubspec.yaml`
- `lib/main.dart`
- `MaterialApp`, `CupertinoApp`, `WidgetsApp`
- `Navigator`, named routes
- `go_router`, `auto_route`, `beamer`, `routemaster`
- Bloc/Cubit, Riverpod, Provider, GetX, MobX
- Android and iOS host projects
- flavors and generated plugin registrants

### Android

Inspect:

- `settings.gradle*`, root and app `build.gradle*`
- `AndroidManifest.xml`
- `Application` subclasses
- launcher Activities
- XML navigation graphs
- `NavHost`, `composable(...)`, Fragments, Activities, Intents
- Hilt/Dagger/Koin modules
- Room, DataStore, SharedPreferences
- WorkManager, Services, BroadcastReceivers, App Widgets
- product flavors and build types

### iOS

Inspect:

- Xcode projects/workspaces and `project.pbxproj`
- `Info.plist`, entitlements, privacy manifests
- `App`, `AppDelegate`, `SceneDelegate`
- SwiftUI `WindowGroup`, `NavigationStack`, `NavigationLink`, sheets, full-screen covers
- UIKit storyboards, coordinators, navigation controllers, tab controllers
- Core Data, SwiftData, UserDefaults, Keychain
- extensions, widgets, notification services, watch targets
- schemes and build configurations

### Kotlin Multiplatform

Identify:

- shared source sets
- platform-specific `actual` implementations
- Compose Multiplatform navigation
- Swift/iOS wrappers
- shared networking, persistence, and domain modules
- platform-specific lifecycle and permission handling

## Scope classification

Every path must be placed in one of these scope classes:

1. `project_source` — authored behavior; analyze every line.
2. `project_test` — tests, fixtures, mocks; analyze because they reveal intended behavior.
3. `project_config` — manifests, build scripts, schemas, localization, feature flags; analyze.
4. `project_asset` — images, animations, fonts, sounds; inventory, inspect metadata/usage, and visually inspect when relevant.
5. `generated_source` — do not silently exclude. Track the generator/source of truth and behavior surface. Analyze generated source line-by-line unless a documented deterministic source makes that redundant.
6. `third_party` — exclude only when genuinely external and unmodified.
7. `build_output` — exclude with a concrete reason and source-of-truth pointer.

Exclusion is not a work status. The exclusion record must include path pattern, reason, source of truth, and who/what verified it.

## Initial architecture questions

Record answers or unknowns:

- What code executes first on each platform?
- What determines the first visible screen?
- Where is session/auth state restored?
- Where are migrations run?
- Which initialization tasks block rendering?
- Which features are platform-specific?
- Which behavior is server-driven?
- Which features are build-variant or feature-flag gated?
- What can run without a visible screen?
- Which app targets can be launched independently?

Do not begin final documentation until these questions exist in the research backlog.

## Generated-source inclusion

The census excludes common dependency/cache/build directories by default and records those patterns in the ledger. This is not permission to ignore project-owned generated behavior.

Identify generators and relevant generated subtrees from Gradle tasks, React Native codegen, Expo prebuild/config plugins, SwiftGen/Sourcery, Flutter build runners, protobuf/GraphQL generation, Room/Core Data generation, and native bridge codegen. Re-run initialization or refresh with one or more forced includes:

```bash
python scripts/anatomy.py refresh \
  --repo <repo> \
  --out <output> \
  --include-dir android/app/build/generated/source \
  --include-dir ios/Generated
```

Include the smallest source subtree that contains behavior. Record the generator, input/source of truth, determinism, and why generated lines are analyzed or excluded.

## Agent and editor tooling exclusions

Installed agent skills and client metadata are not part of the mobile product. The census excludes common directories including `.agents`, `.claude`, `.codex`, `.cursor`, `.cline`, `.gemini`, `.junie`, `.goose`, `.opencode`, `.openhands`, `.antigravity`, `.mcpjam`, and `.windsurf`. Do not exclude `.github` wholesale because workflows, release automation, and platform metadata may affect the shipped app.

Use repeatable `--exclude-dir` values for repository-specific non-product trees. Use `--include-dir` for a narrow subtree when a default exclusion contains project-owned generated behavior.

## Shell compatibility

Before running shell commands, identify whether the host is Windows PowerShell 5.1, PowerShell 7+, cmd.exe, or a POSIX shell. PowerShell 5.1 does not accept `&&` or `||`. Run Phase 0 Git commands separately and treat parser errors as failed commands, not evidence.
