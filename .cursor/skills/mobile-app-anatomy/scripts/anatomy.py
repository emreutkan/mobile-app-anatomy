#!/usr/bin/env python3
"""
Deterministic census and coverage ledger for the mobile-app-anatomy skill.

Standard library only. This script does not claim semantic understanding; it
creates auditable work units and enforces completion evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

SCHEMA_VERSION = 1
STATUSES = {"not_tracked", "tracking", "tracked_fully"}

EXCLUDED_DIR_NAMES = {
    ".git", ".gitnexus", ".gradle", ".idea", ".vscode", ".dart_tool",
    ".expo", ".next", ".nuxt", ".turbo", ".cache", "__pycache__",
    "node_modules", "vendor", "Pods", "DerivedData", "dist", "build",
    "coverage", ".nyc_output", "target", "out", "tmp", "temp",
    # Agent/client installations and generated instruction state are tooling,
    # not mobile-product implementation. Project-owned CI and .github files
    # remain in scope. Any excluded subtree can be force-included explicitly.
    ".agents", ".claude", ".codex", ".cursor", ".cline", ".gemini",
    ".junie", ".goose", ".opencode", ".openhands", ".antigravity",
    ".mcpjam", ".windsurf",
}

LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
    "Podfile.lock", "Gemfile.lock", "gradle.lockfile", "pubspec.lock",
    "Cargo.lock", "go.sum", "poetry.lock", "Pipfile.lock",
}

TEXT_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".dart", ".kt", ".kts", ".java", ".swift", ".m", ".mm", ".h", ".hpp",
    ".c", ".cc", ".cpp", ".cs", ".rb", ".py", ".go", ".rs",
    ".xml", ".plist", ".json", ".json5", ".yaml", ".yml", ".toml",
    ".gradle", ".properties", ".pbxproj", ".storyboard", ".xib",
    ".graphql", ".gql", ".sql", ".sh", ".bash", ".zsh", ".ps1",
    ".html", ".css", ".scss", ".sass", ".less", ".md", ".txt",
    ".env", ".xcconfig", ".strings", ".entitlements", ".pro",
}

TEXT_FILENAMES = {
    "Podfile", "Gemfile", "Fastfile", "Appfile", "Makefile", "Dockerfile",
    "gradlew", "gradlew.bat", "settings.gradle", "build.gradle",
    "AndroidManifest.xml", "Info.plist", "PrivacyInfo.xcprivacy",
}

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico",
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".mp4", ".mov", ".webm",
    ".ttf", ".otf", ".woff", ".woff2", ".lottie", ".riv", ".pdf",
}

LANG_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript/React", ".js": "JavaScript",
    ".jsx": "JavaScript/React", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".dart": "Dart", ".kt": "Kotlin", ".kts": "Kotlin Script",
    ".java": "Java", ".swift": "Swift", ".m": "Objective-C",
    ".mm": "Objective-C++", ".h": "C/C++/Objective-C Header",
    ".hpp": "C++", ".c": "C", ".cc": "C++", ".cpp": "C++",
    ".cs": "C#", ".rb": "Ruby", ".py": "Python", ".go": "Go",
    ".rs": "Rust", ".xml": "XML", ".plist": "Property List",
    ".json": "JSON", ".json5": "JSON5", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".gradle": "Gradle", ".properties": "Properties",
    ".pbxproj": "Xcode Project", ".storyboard": "Storyboard", ".xib": "XIB",
    ".graphql": "GraphQL", ".gql": "GraphQL", ".sql": "SQL",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".ps1": "PowerShell",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".sass": "Sass",
    ".less": "Less", ".md": "Markdown", ".strings": "Apple Strings",
    ".entitlements": "Apple Entitlements", ".xcconfig": "Xcode Config",
}

SYMBOL_PATTERNS = [
    ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:public\s+|private\s+|internal\s+|open\s+|final\s+|abstract\s+)*class\s+([A-Za-z_]\w*)")),
    ("struct", re.compile(r"^\s*(?:public\s+|private\s+|internal\s+)*struct\s+([A-Za-z_]\w*)")),
    ("interface", re.compile(r"^\s*(?:export\s+)?(?:public\s+)?interface\s+([A-Za-z_]\w*)")),
    ("enum", re.compile(r"^\s*(?:export\s+)?(?:public\s+)?enum\s+(?:class\s+)?([A-Za-z_]\w*)")),
    ("protocol", re.compile(r"^\s*(?:public\s+|private\s+|internal\s+)*protocol\s+([A-Za-z_]\w*)")),
    ("type", re.compile(r"^\s*export\s+type\s+([A-Za-z_]\w*)")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w*)\s*(?::[^=]+)?=\s*(?:async\s*)?\(")),
    ("function", re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+|open\s+|override\s+|static\s+|suspend\s+)*fun\s+([A-Za-z_]\w*)\s*\(")),
    ("function", re.compile(r"^\s*(?:public\s+|private\s+|internal\s+|static\s+|class\s+)*func\s+([A-Za-z_]\w*)\s*\(")),
    ("function", re.compile(r"^\s*(?:Future<[^>]+>|Future|void|Widget|String|int|double|bool|dynamic|[A-Z]\w*(?:<[^>]+>)?)\s+([a-zA-Z_]\w*)\s*\([^;]*\)\s*(?:async\s*)?\{")),
    ("composable", re.compile(r"^\s*@Composable\b")),
]

ROUTE_PATTERNS = [
    ("react_navigation_screen", re.compile(r"<(?:Stack|Tabs|Tab|Drawer)\.Screen[^>]*\bname\s*=\s*[\"'{]([^\"'}]+)")),
    ("react_navigation_call", re.compile(r"\b(?:navigation|nav)\.(?:navigate|push|replace|reset)\s*\(\s*[\"'`]([^\"'`]+)")),
    ("expo_router_call", re.compile(r"\brouter\.(?:push|replace|navigate)\s*\(\s*[\"'`]([^\"'`]+)")),
    ("expo_link", re.compile(r"\bhref\s*=\s*[\"'{]([^\"'}]+)")),
    ("flutter_named_route", re.compile(r"\b(?:Navigator\.[A-Za-z]+Named|pushNamed)\s*\([^,]*,\s*[\"']([^\"']+)")),
    ("go_router", re.compile(r"\b(?:GoRoute|ShellRoute)\s*\([^)]*(?:path|name)\s*:\s*[\"']([^\"']+)")),
    ("compose_route", re.compile(r"\bcomposable\s*\(\s*(?:route\s*=\s*)?[\"']([^\"']+)")),
    ("android_intent", re.compile(r"\bIntent\s*\([^,]+,\s*([A-Za-z_]\w*)::class")),
    ("swift_navigation", re.compile(r"\bNavigationLink\s*\([^)]*(?:value|destination)\s*:")),
    ("uikit_push", re.compile(r"\bpushViewController\s*\(\s*([A-Za-z_]\w*)")),
    ("uikit_present", re.compile(r"\bpresent\s*\(\s*([A-Za-z_]\w*)")),
]

SIGNAL_PATTERNS = {
    "authentication": re.compile(r"\b(?:auth\w*|login|logout|signIn\w*|signOut\w*|register\w*|session|token|oauth|apple.*sign|google.*sign)\b", re.I),
    "onboarding": re.compile(r"\b(onboarding|welcome|profile_complete|profileComplete|first.?run)\b", re.I),
    "purchases": re.compile(r"\b(revenuecat|storekit|billingclient|purchase|subscription|entitlement|paywall|restore.?purchase)\b", re.I),
    "permissions": re.compile(r"\b(permission|requestAuthorization|requestPermissions|AVAudioSession|camera|microphone|location)\b", re.I),
    "notifications": re.compile(r"\b(notification|push token|expo-notifications|firebase.messaging|UNUserNotificationCenter)\b", re.I),
    "deep_links": re.compile(r"\b(deep.?link|universal.?link|app.?link|Linking\.|openURL|onNewIntent)\b", re.I),
    "analytics": re.compile(r"\b(analytics|trackEvent|logEvent|amplitude|mixpanel|segment|firebase.analytics)\b", re.I),
    "remote_config_flags": re.compile(r"\b(remote.?config|feature.?flag|experiment|variant|A/B)\b", re.I),
    "persistence": re.compile(r"\b(AsyncStorage|MMKV|SharedPreferences|DataStore|UserDefaults|Keychain|CoreData|SwiftData|Room|SQLite|Hive|Isar)\b", re.I),
    "networking": re.compile(r"\b(fetch\(|axios|URLSession|Retrofit|OkHttp|Dio\(|http\.|GraphQL|Apollo)\b", re.I),
    "background": re.compile(r"\b(WorkManager|BGTaskScheduler|background.?fetch|HeadlessJsTask|service|worker|widget|extension)\b", re.I),
    "health_fitness": re.compile(r"\b(HealthKit|Health Connect|Google Fit|workout|exercise|recovery|heart.?rate|steps)\b", re.I),
    "native_bridge": re.compile(r"\b(NativeModules|TurboModule|RCTBridge|MethodChannel|EventChannel|JNI|@ReactMethod)\b", re.I),
}

def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def stable_id(*parts: object) -> str:
    raw = "|".join(str(p) for p in parts)
    return "u_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)

def git_info(repo: Path) -> tuple[str | None, list[str]]:
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain"],
            text=True, stderr=subprocess.DEVNULL
        ).splitlines()
        return commit, dirty
    except Exception:
        return None, []

def is_probably_text(path: Path) -> bool:
    if path.name in TEXT_FILENAMES or path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in sample:
        return False
    if not sample:
        return True
    printable = sum((b in b"\t\n\r" or 32 <= b <= 126 or b >= 128) for b in sample)
    return printable / len(sample) > 0.95

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def language_for(path: Path) -> str:
    if path.name == "Podfile":
        return "Ruby/CocoaPods"
    if path.name.endswith(".gradle.kts"):
        return "Kotlin Script/Gradle"
    return LANG_BY_EXT.get(path.suffix.lower(), "Text" if is_probably_text(path) else "Binary")

def classify(path_rel: str, path: Path, text: str | None) -> str:
    p = path_rel.replace("\\", "/").lower()
    n = path.name.lower()
    if any(tok in p for tok in ("/test/", "/tests/", "__tests__", ".test.", ".spec.")) or n.startswith("test_") or n.endswith("_test.dart"):
        return "test"
    if n in {"package.json", "pubspec.yaml", "androidmanifest.xml", "info.plist", "eas.json", "app.json", ".env", ".env.local", ".env.development", ".env.production", ".npmrc", ".yarnrc", ".gitignore"} or \
       path.suffix.lower() in {".gradle", ".properties", ".pbxproj", ".xcconfig", ".entitlements", ".plist"}:
        return "config"
    if "navigation" in p or "navigator" in p or "router" in p or "routes" in p or n.startswith("_layout") or "nav_graph" in p:
        return "navigation"
    if any(tok in p for tok in ("/screens/", "/pages/", "/routes/", "/views/")) or \
       re.search(r"(screen|page|viewcontroller|activity|fragment)\.(tsx?|jsx?|dart|kt|java|swift)$", n):
        return "screen"
    if any(tok in p for tok in ("/components/", "/widgets/", "/ui/")) or \
       re.search(r"(component|widget|view)\.(tsx?|jsx?|dart|kt|swift)$", n):
        return "component"
    if any(tok in p for tok in ("/store/", "/state/", "/redux/", "/bloc/", "/viewmodel", "/providers/")) or \
       re.search(r"(store|slice|reducer|context|provider|bloc|cubit|viewmodel)\.", n):
        return "state"
    if any(tok in p for tok in ("/api/", "/services/", "/repositories/", "/network/", "/clients/")) or \
       re.search(r"(api|service|repository|client|gateway)\.", n):
        return "service"
    if any(tok in p for tok in ("/hooks/", "/utils/", "/helpers/", "/lib/")) or \
       re.search(r"(util|helper|hook)\.", n):
        return "helper"
    if any(tok in p for tok in ("/models/", "/types/", "/schema", "/entities/")) or \
       re.search(r"(model|types?|schema|entity)\.", n):
        return "model"
    if any(tok in p for tok in ("/ios/", "/android/", "/native/")):
        return "native"
    if path.suffix.lower() in ASSET_EXTENSIONS:
        return "asset"
    return "source"

def extract_symbols(lines: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    pending_composable = False
    for i, line in enumerate(lines, 1):
        if SYMBOL_PATTERNS[-1][1].search(line):
            pending_composable = True
            continue
        matched = False
        for kind, pattern in SYMBOL_PATTERNS[:-1]:
            m = pattern.search(line)
            if m:
                actual_kind = "composable" if pending_composable and kind == "function" else kind
                out.append({"name": m.group(1), "kind": actual_kind, "line": i})
                pending_composable = False
                matched = True
                break
        if not matched and line.strip() and not line.lstrip().startswith("@"):
            pending_composable = False
    return out

def expo_route_from_file(path_rel: str) -> str | None:
    normalized = path_rel.replace("\\", "/")
    match = re.search(r"(?:^|/)app/(.+)$", normalized)
    if not match:
        return None
    route_file = match.group(1)
    suffix = Path(route_file).suffix.lower()
    if suffix not in {".ts", ".tsx", ".js", ".jsx"}:
        return None
    route_file = route_file[: -len(suffix)]
    parts = route_file.split("/")
    name = parts[-1]
    if name in {"_layout", "+not-found", "+html", "+native-intent"}:
        return None
    if name == "index":
        parts = parts[:-1]
    # Expo route groups organize files but are omitted from the URL.
    parts = [part for part in parts if not (part.startswith("(") and part.endswith(")"))]
    return "/" + "/".join(parts) if parts else "/"


def extract_routes(path_rel: str, lines: list[str]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    normalized = path_rel.replace("\\", "/")
    filesystem_route = expo_route_from_file(normalized)
    if filesystem_route is not None:
        routes.append({
            "kind": "expo_filesystem_route",
            "target": filesystem_route,
            "file": normalized,
            "line": 1,
        })
    for i, line in enumerate(lines, 1):
        for kind, pattern in ROUTE_PATTERNS:
            for match in pattern.finditer(line):
                target = match.group(1) if match.groups() else match.group(0).strip()[:160]
                routes.append({"kind": kind, "target": target, "file": normalized, "line": i})
    return routes

def redact_excerpt(line: str) -> str:
    value = line.strip()[:500]
    value = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._~+\-/=]+", "Bearer <REDACTED>", value)
    value = re.sub(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|token)\b(\s*[:=]\s*)([\"'])(.*?)(\3)",
        lambda m: f"{m.group(1)}{m.group(2)}<REDACTED>",
        value,
    )
    if re.match(r"^(?:export\s+)?[A-Z0-9_]*(?:PASSWORD|PASSWD|SECRET|API_KEY|ACCESS_TOKEN|REFRESH_TOKEN|AUTHORIZATION|TOKEN)[A-Z0-9_]*\s*=", value):
        key = value.split("=", 1)[0].rstrip()
        value = f"{key}=<REDACTED>"
    if re.match(r"(?i)^Authorization\s*:", value):
        value = "Authorization: <REDACTED>"
    value = re.sub(r"-----BEGIN [^-]+ PRIVATE KEY-----.*", "<REDACTED PRIVATE KEY>", value)
    return value[:240]


def extract_signals(path_rel: str, lines: list[str]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for i, line in enumerate(lines, 1):
        for category, pattern in SIGNAL_PATTERNS.items():
            if pattern.search(line):
                found.append({
                    "category": category,
                    "file": path_rel.replace("\\", "/"),
                    "line": i,
                    "excerpt": redact_excerpt(line),
                })
    return found

def detect_frameworks(repo: Path, files_by_rel: dict[str, Path]) -> dict[str, Any]:
    signals: list[dict[str, str]] = []
    frameworks: set[str] = set()
    platforms: set[str] = set()

    def add(name: str, evidence: str) -> None:
        frameworks.add(name)
        signals.append({"framework": name, "evidence": evidence})

    package = files_by_rel.get("package.json")
    if package:
        try:
            data = json.loads(read_text(package))
            deps = {}
            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))
            if "react-native" in deps:
                add("React Native", "package.json: react-native")
                platforms.update({"iOS", "Android"})
            if "expo" in deps:
                add("Expo", "package.json: expo")
            if "expo-router" in deps:
                add("Expo Router", "package.json: expo-router")
            if "@react-navigation/native" in deps:
                add("React Navigation", "package.json: @react-navigation/native")
        except Exception:
            pass

    if "pubspec.yaml" in files_by_rel:
        add("Flutter/Dart", "pubspec.yaml")
        platforms.update({"iOS", "Android"})

    if any(rel.endswith((".gradle", ".gradle.kts")) for rel in files_by_rel) or "AndroidManifest.xml" in {Path(r).name for r in files_by_rel}:
        add("Android Native", "Gradle/AndroidManifest")
        platforms.add("Android")

    if any(rel.endswith(".swift") for rel in files_by_rel) or any(rel.endswith(".pbxproj") for rel in files_by_rel):
        add("iOS Native", "Swift/Xcode project")
        platforms.add("iOS")

    if any("shared/src/" in rel.replace("\\", "/") and rel.endswith((".kt", ".kts")) for rel in files_by_rel):
        add("Kotlin Multiplatform", "shared/src Kotlin source sets")

    return {
        "generated_at": now_iso(),
        "frameworks": sorted(frameworks),
        "platforms": sorted(platforms),
        "signals": signals,
    }

def normalized_include_dirs(values: Iterable[str] | None) -> list[str]:
    return sorted({str(value).replace("\\", "/").strip("/") for value in (values or []) if str(value).strip("/")})


def normalized_exclude_dirs(values: Iterable[str] | None) -> list[str]:
    return sorted({str(value).replace("\\", "/").strip("/") for value in (values or []) if str(value).strip("/")})


def path_is_under(rel: str, roots: Iterable[str]) -> bool:
    rel = rel.replace("\\", "/").strip("/")
    return any(rel == root or rel.startswith(root + "/") for root in roots)


def include_intersects(rel: str, include_dirs: Iterable[str]) -> bool:
    rel = rel.replace("\\", "/").strip("/")
    for included in include_dirs:
        included = included.replace("\\", "/").strip("/")
        if rel == included or rel.startswith(included + "/") or included.startswith(rel + "/"):
            return True
    return False


def file_is_forced_included(rel: str, include_dirs: Iterable[str]) -> bool:
    rel = rel.replace("\\", "/").strip("/")
    return any(rel == included or rel.startswith(included + "/") for included in include_dirs)


def exclusion_reason(
    rel: str,
    path: Path,
    output: Path,
    include_dirs: Iterable[str] = (),
    exclude_dirs: Iterable[str] = (),
) -> str | None:
    parts = set(Path(rel).parts)
    if file_is_forced_included(rel, include_dirs):
        return None
    if path_is_under(rel, exclude_dirs):
        return "explicitly excluded directory"
    if any(part in EXCLUDED_DIR_NAMES for part in parts):
        return "third-party dependency, cache, agent tooling, editor metadata, or build output directory"
    try:
        if output.resolve() in path.resolve().parents or path.resolve() == output.resolve():
            return "generated anatomy documentation output"
    except Exception:
        pass
    if path.name in LOCKFILES:
        return "dependency resolution lockfile; behavior is documented from manifests and used packages"
    if path.name.endswith((".min.js", ".map")):
        return "minified artifact or source map"
    return None

def scan_repo(
    repo: Path,
    output: Path,
    chunk_lines: int,
    previous: dict[str, Any] | None = None,
    include_dirs: Iterable[str] = (),
    exclude_dirs: Iterable[str] = (),
    runtime_mode: str = "auto",
) -> dict[str, Any]:
    include_dirs = normalized_include_dirs(include_dirs)
    exclude_dirs = normalized_exclude_dirs(exclude_dirs)
    files_by_rel: dict[str, Path] = {}
    for base, dirs, files in os.walk(repo):
        base_path = Path(base)
        kept_dirs = []
        for d in dirs:
            candidate = base_path / d
            try:
                if candidate.resolve().is_relative_to(output.resolve()):
                    continue
            except Exception:
                pass
            try:
                candidate_rel = candidate.relative_to(repo).as_posix()
            except ValueError:
                continue
            default_excluded = d in EXCLUDED_DIR_NAMES
            explicitly_excluded = path_is_under(candidate_rel, exclude_dirs)
            if (default_excluded or explicitly_excluded) and not include_intersects(candidate_rel, include_dirs):
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs
        for filename in files:
            p = base_path / filename
            try:
                rel = p.relative_to(repo).as_posix()
            except ValueError:
                continue
            files_by_rel[rel] = p

    commit, dirty = git_info(repo)
    old_files = (previous or {}).get("files", {})
    old_units = (previous or {}).get("units", {})
    new_files: dict[str, Any] = {}
    new_units: dict[str, Any] = {}
    routes: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []
    inventory_rows: list[dict[str, Any]] = []
    archived = list((previous or {}).get("archived_files", []))
    changed_files: list[str] = []
    removed_files: list[str] = []

    for rel in sorted(files_by_rel):
        path = files_by_rel[rel]
        reason = exclusion_reason(rel, path, output, include_dirs, exclude_dirs)
        size = path.stat().st_size
        digest = sha256_file(path)
        text_mode = is_probably_text(path)
        language = language_for(path)
        lines: list[str] = []
        if text_mode and reason is None:
            lines = read_text(path).splitlines()
        category = classify(rel, path, "\n".join(lines[:100]) if lines else None)
        scope = (
            "excluded" if reason else
            "project_asset" if path.suffix.lower() in ASSET_EXTENSIONS or not text_mode else
            "project_test" if category == "test" else
            "project_config" if category == "config" else
            "project_source"
        )
        record = {
            "path": rel,
            "sha256": digest,
            "size_bytes": size,
            "line_count": len(lines) if text_mode else None,
            "language": language,
            "category": category,
            "scope": scope,
            "excluded": reason is not None,
            "exclusion_reason": reason,
            "units": [],
            "symbols_seed": [],
        }

        unchanged = rel in old_files and old_files[rel].get("sha256") == digest
        if not unchanged:
            changed_files.append(rel)
        if reason is None and text_mode:
            record["symbols_seed"] = extract_symbols(lines)
            routes.extend(extract_routes(rel, lines))
            signals.extend(extract_signals(rel, lines))
            line_count = max(1, len(lines))
            shard_ids: list[str] = []
            for start in range(1, line_count + 1, chunk_lines):
                end = min(line_count, start + chunk_lines - 1)
                uid = stable_id("line_shard", rel, start, end)
                old = old_units.get(uid) if unchanged else None
                unit = {
                    "id": uid,
                    "type": "line_shard",
                    "path": rel,
                    "start_line": start,
                    "end_line": end,
                    "status": old.get("status", "not_tracked") if old else "not_tracked",
                    "agent": old.get("agent") if old else None,
                    "started_at": old.get("started_at") if old else None,
                    "completed_at": old.get("completed_at") if old else None,
                    "report": old.get("report") if old else None,
                    "evidence": old.get("evidence", []) if old else [],
                    "excluded": False,
                    "exclusion_reason": None,
                    "depends_on": [],
                }
                new_units[uid] = unit
                shard_ids.append(uid)
            synth_id = stable_id("file_synthesis", rel)
            old_synth = old_units.get(synth_id) if unchanged else None
            synth = {
                "id": synth_id,
                "type": "file_synthesis",
                "path": rel,
                "start_line": 1,
                "end_line": len(lines),
                "status": old_synth.get("status", "not_tracked") if old_synth else "not_tracked",
                "agent": old_synth.get("agent") if old_synth else None,
                "started_at": old_synth.get("started_at") if old_synth else None,
                "completed_at": old_synth.get("completed_at") if old_synth else None,
                "report": old_synth.get("report") if old_synth else None,
                "evidence": old_synth.get("evidence", []) if old_synth else [],
                "excluded": False,
                "exclusion_reason": None,
                "depends_on": shard_ids,
            }
            new_units[synth_id] = synth
            record["units"] = shard_ids + [synth_id]
        elif reason is None:
            uid = stable_id("asset_analysis", rel)
            old = old_units.get(uid) if unchanged else None
            new_units[uid] = {
                "id": uid,
                "type": "asset_analysis",
                "path": rel,
                "start_line": None,
                "end_line": None,
                "status": old.get("status", "not_tracked") if old else "not_tracked",
                "agent": old.get("agent") if old else None,
                "started_at": old.get("started_at") if old else None,
                "completed_at": old.get("completed_at") if old else None,
                "report": old.get("report") if old else None,
                "evidence": old.get("evidence", []) if old else [],
                "excluded": False,
                "exclusion_reason": None,
                "depends_on": [],
            }
            record["units"] = [uid]
        new_files[rel] = record
        inventory_rows.append(record)

    for rel, old in old_files.items():
        if rel not in new_files:
            removed_files.append(rel)
            archived.append({
                "path": rel,
                "sha256": old.get("sha256"),
                "removed_at": now_iso(),
                "previous_record": old,
            })

    ledger = {
        "schema_version": SCHEMA_VERSION,
        "repo_root": str(repo.resolve()),
        "output_root": str(output.resolve()),
        "git_commit": commit,
        "dirty_worktree": dirty,
        "chunk_lines": chunk_lines,
        "include_dirs": include_dirs,
        "exclude_dirs": exclude_dirs,
        "runtime_mode": runtime_mode,
        "created_at": (previous or {}).get("created_at", now_iso()),
        "updated_at": now_iso(),
        "frameworks": detect_frameworks(repo, files_by_rel),
        "excluded_directory_patterns": [
            {
                "pattern": name,
                "reason": "third-party dependency, cache, agent tooling, editor metadata, or build output directory",
            }
            for name in sorted(EXCLUDED_DIR_NAMES)
        ] + [
            {"pattern": name, "reason": "explicitly excluded directory"}
            for name in exclude_dirs
        ],
        "files": new_files,
        "units": new_units,
        "archived_files": archived,
    }
    return {
        "ledger": ledger,
        "inventory": inventory_rows,
        "routes": routes,
        "signals": signals,
        "framework": ledger["frameworks"],
        "changed_files": changed_files,
        "removed_files": removed_files,
    }

def ensure_structure(output: Path) -> None:
    dirs = [
        "00-product", "01-launch-auth-onboarding", "02-navigation", "03-screens",
        "04-features", "05-flows", "06-state-data", "07-platform", "08-runtime",
        "09-code-atlas", "evidence/chunks", "evidence/files", "evidence/runtime",
        "machine",
    ]
    for d in dirs:
        (output / d).mkdir(parents=True, exist_ok=True)
    starter_files = {
        "DISCOVERY_JOURNAL.md": "# Discovery Journal\n\n",
        "UNKNOWNS.md": "# Unknowns\n\n",
        "CONTRADICTIONS.md": "# Contradictions\n\n",
    }
    for name, content in starter_files.items():
        p = output / name
        if not p.exists():
            p.write_text(content, encoding="utf-8")

def canonical_route_target(target: str) -> tuple[str, str]:
    value = str(target).strip()
    if value.startswith("(") and value.endswith(")"):
        return value, "navigator_candidate"
    if value.startswith("/"):
        value = re.sub(r"/+", "/", value)
        return value or "/", "screen_candidate"
    if re.fullmatch(r"[A-Za-z0-9_.\-\[\]]+", value):
        if value.endswith(("Activity", "Fragment", "ViewController", "Controller")):
            return value, "screen_candidate"
        return "/" + value, "screen_candidate"
    return value, "screen_candidate"


def upsert_seed_entity(
    entities: dict[str, Any],
    entity_id: str,
    kind: str,
    title: str,
    sources: list[str],
    metadata: dict[str, Any] | None = None,
) -> None:
    existing = entities.get(entity_id)
    if existing:
        for source in sources:
            if source not in existing.setdefault("sources", []):
                existing["sources"].append(source)
        target_metadata = existing.setdefault("metadata", {})
        for key, value in (metadata or {}).items():
            if isinstance(value, list) and isinstance(target_metadata.get(key), list):
                for item in value:
                    if item not in target_metadata[key]:
                        target_metadata[key].append(item)
            else:
                target_metadata[key] = value
        existing["updated_at"] = now_iso()
        return
    entities[entity_id] = {
        "id": entity_id,
        "kind": kind,
        "title": title,
        "status": "not_tracked",
        "sources": sources,
        "metadata": metadata or {},
        "report": None,
        "evidence": [],
        "excluded": False,
        "exclusion_reason": None,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def create_seed_entities(
    output: Path,
    routes: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
    previous: dict[str, Any] | None = None,
    changed_files: list[str] | None = None,
    removed_files: list[str] | None = None,
) -> None:
    state = previous or {"schema_version": 1, "entities": {}}
    entities = state.setdefault("entities", {})
    invalidated = set(changed_files or []) | set(removed_files or [])

    # Merge route evidence by canonical destination so static declarations and
    # navigation calls converge on the same screen candidate.
    for route in routes:
        canonical, kind = canonical_route_target(str(route["target"]))
        eid = f"{kind}." + hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:14]
        upsert_seed_entity(
            entities,
            eid,
            kind,
            canonical,
            [f"{route['file']}:{route['line']}"],
            {"route_kinds": [route["kind"]]},
        )
        route_kinds = entities[eid].setdefault("metadata", {}).setdefault("route_kinds", [])
        if route["kind"] not in route_kinds:
            route_kinds.append(route["kind"])

    # Seed a single candidate for each detected cross-cutting mobile feature.
    grouped_signals: dict[str, list[str]] = {}
    for signal in signals:
        grouped_signals.setdefault(signal["category"], []).append(
            f"{signal['file']}:{signal['line']}"
        )
    for category, sources in grouped_signals.items():
        eid = "feature_candidate." + re.sub(r"[^a-z0-9_]+", "_", category.lower())
        upsert_seed_entity(
            entities,
            eid,
            "feature_candidate",
            category.replace("_", " ").title(),
            sorted(set(sources)),
            {"signal_category": category},
        )

    # Seed file-level UI entities even when navigation is dynamic or generated.
    for record in inventory:
        if record.get("excluded"):
            continue
        path = record["path"]
        category = record.get("category")
        if category in {"screen", "component", "navigation"}:
            kind = {
                "screen": "screen_candidate",
                "component": "component_candidate",
                "navigation": "navigation_candidate",
            }[category]
            eid = f"{kind}.file." + hashlib.sha1(path.encode("utf-8")).hexdigest()[:14]
            upsert_seed_entity(
                entities,
                eid,
                kind,
                Path(path).stem,
                [f"{path}:1"],
                {"source_file": path, "file_category": category},
            )

        # Every deterministically discovered top-level symbol is a semantic
        # obligation. File dossiers may satisfy many symbols, but each symbol
        # must still be represented and completed or explicitly excluded.
        for symbol in record.get("symbols_seed", []):
            symbol_key = f"{path}|{symbol['line']}|{symbol['kind']}|{symbol['name']}"
            eid = "symbol_candidate." + hashlib.sha1(symbol_key.encode("utf-8")).hexdigest()[:16]
            upsert_seed_entity(
                entities,
                eid,
                "symbol_candidate",
                f"{symbol['kind']} {symbol['name']}",
                [f"{path}:{symbol['line']}"],
                {
                    "source_file": path,
                    "line": symbol["line"],
                    "symbol_kind": symbol["kind"],
                    "symbol_name": symbol["name"],
                },
            )

    # Invalidate after new seed evidence has been merged. This catches both
    # entities that previously referenced a changed file and entities that gain
    # a newly discovered source in that changed file.
    if invalidated:
        for entity in entities.values():
            source_paths = set()
            for source in entity.get("sources", []):
                if source.startswith(("runtime:", "gitnexus:", "test:")):
                    continue
                raw = source[5:] if source.startswith("repo:") else source
                source_paths.add(raw.rsplit(":", 1)[0])
            touched = sorted(source_paths & invalidated)
            if touched:
                entity["status"] = "not_tracked"
                entity["report"] = None
                entity["evidence"] = []
                entity["completed_at"] = None
                entity["excluded"] = False
                entity["exclusion_reason"] = None
                entity.setdefault("metadata", {})["reverification_required_for"] = touched
                entity["updated_at"] = now_iso()

    state["updated_at"] = now_iso()
    save_json(output / "machine" / "entities.json", state)

def write_scan(output: Path, scan: dict[str, Any], previous_entities: dict[str, Any] | None = None) -> None:
    ensure_structure(output)
    save_json(output / "machine" / "ledger.json", scan["ledger"])
    save_json(output / "machine" / "framework.json", scan["framework"])
    save_json(output / "machine" / "routes_seed.json", {"routes": scan["routes"]})
    save_json(output / "machine" / "signals.json", {"signals": scan["signals"]})
    with (output / "machine" / "inventory.jsonl").open("w", encoding="utf-8") as f:
        for row in scan["inventory"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    create_seed_entities(
        output,
        scan["routes"],
        scan["signals"],
        scan["inventory"],
        previous_entities,
        scan.get("changed_files", []),
        scan.get("removed_files", []),
    )
    write_coverage(output)

def aggregate_status(ledger: dict[str, Any]) -> dict[str, int]:
    counts = {"not_tracked": 0, "tracking": 0, "tracked_fully": 0, "excluded": 0}
    for unit in ledger.get("units", {}).values():
        if unit.get("excluded"):
            counts["excluded"] += 1
        else:
            counts[unit.get("status", "not_tracked")] += 1
    return counts

def entity_status(output: Path) -> dict[str, int]:
    data = load_json(output / "machine" / "entities.json", {"entities": {}})
    counts = {"not_tracked": 0, "tracking": 0, "tracked_fully": 0, "excluded": 0}
    for e in data.get("entities", {}).values():
        if e.get("excluded"):
            counts["excluded"] += 1
        else:
            counts[e.get("status", "not_tracked")] += 1
    return counts

def write_coverage(output: Path) -> None:
    ledger = load_json(output / "machine" / "ledger.json", {})
    units = ledger.get("units", {})
    files = ledger.get("files", {})
    u = aggregate_status(ledger)
    e = entity_status(output)
    total_required = sum(u[k] for k in STATUSES)
    complete = u["tracked_fully"]
    pct = (complete / total_required * 100.0) if total_required else 100.0
    text_lines = sum((f.get("line_count") or 0) for f in files.values() if not f.get("excluded"))
    excluded_files = sum(1 for f in files.values() if f.get("excluded"))
    by_type: dict[str, dict[str, int]] = {}
    for unit in units.values():
        typ = unit.get("type", "unknown")
        bucket = by_type.setdefault(typ, {s: 0 for s in sorted(STATUSES)} | {"excluded": 0})
        if unit.get("excluded"):
            bucket["excluded"] += 1
        else:
            bucket[unit.get("status", "not_tracked")] += 1

    lines = [
        "# Coverage",
        "",
        f"- Repository: `{ledger.get('repo_root', '')}`",
        f"- Commit: `{ledger.get('git_commit')}`",
        f"- Updated: `{ledger.get('updated_at', '')}`",
        f"- Relevant text lines assigned: **{text_lines:,}**",
        f"- Files inventoried: **{len(files):,}**",
        f"- Files excluded with reason: **{excluded_files:,}**",
        f"- Required work units: **{total_required:,}**",
        f"- Tracked fully: **{complete:,} ({pct:.2f}%)**",
        f"- Tracking: **{u['tracking']:,}**",
        f"- Not tracked: **{u['not_tracked']:,}**",
        "",
        "## Work units by type",
        "",
        "| Type | Not tracked | Tracking | Tracked fully | Excluded |",
        "|---|---:|---:|---:|---:|",
    ]
    for typ in sorted(by_type):
        b = by_type[typ]
        lines.append(f"| {typ} | {b['not_tracked']} | {b['tracking']} | {b['tracked_fully']} | {b['excluded']} |")
    lines += [
        "",
        "## Semantic entities",
        "",
        f"- Not tracked: **{e['not_tracked']}**",
        f"- Tracking: **{e['tracking']}**",
        f"- Tracked fully: **{e['tracked_fully']}**",
        f"- Excluded candidates: **{e['excluded']}**",
        "",
        "Static and runtime coverage must be reported separately in the final atlas.",
    ]
    (output / "COVERAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def resolve_report(output: Path, report: str) -> Path:
    p = Path(report)
    return p if p.is_absolute() else output / p

def command_init(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    output = Path(args.out).resolve()
    if (output / "machine" / "ledger.json").exists() and not args.force:
        print("Ledger already exists. Use refresh or init --force.", file=sys.stderr)
        return 2
    scan = scan_repo(repo, output, args.chunk_lines, None, args.include_dir, args.exclude_dir, args.runtime_mode)
    write_scan(output, scan)
    print(f"Initialized {output}")
    print(json.dumps(aggregate_status(scan["ledger"]), indent=2))
    return 0

def command_refresh(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    output = Path(args.out).resolve()
    previous = load_json(output / "machine" / "ledger.json")
    if not previous:
        print("No existing ledger; running init.", file=sys.stderr)
        args.force = True
        return command_init(args)
    entities = load_json(output / "machine" / "entities.json", {"schema_version": 1, "entities": {}})
    include_dirs = normalized_include_dirs(list(previous.get("include_dirs", [])) + list(args.include_dir or []))
    exclude_dirs = normalized_exclude_dirs(list(previous.get("exclude_dirs", [])) + list(args.exclude_dir or []))
    scan = scan_repo(
        repo,
        output,
        int(previous.get("chunk_lines", args.chunk_lines)),
        previous,
        include_dirs,
        exclude_dirs,
        args.runtime_mode or previous.get("runtime_mode", "auto"),
    )
    write_scan(output, scan, entities)
    print(f"Refreshed {output}")
    print(json.dumps(aggregate_status(scan["ledger"]), indent=2))
    return 0

def command_status(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    ledger = load_json(output / "machine" / "ledger.json")
    if not ledger:
        print("No ledger found.", file=sys.stderr)
        return 2
    write_coverage(output)
    print(json.dumps({
        "repo": ledger.get("repo_root"),
        "commit": ledger.get("git_commit"),
        "units": aggregate_status(ledger),
        "entities": entity_status(output),
    }, indent=2))
    return 0

def print_unknown_unit(ledger: dict[str, Any] | None, query: str) -> None:
    print(f"Unknown unit: {query}", file=sys.stderr)
    if not ledger:
        print("No current ledger is loaded.", file=sys.stderr)
        return
    units = ledger.get("units", {})
    query_l = str(query).lower()
    matches = [
        unit for uid, unit in units.items()
        if uid.startswith(str(query))
        or query_l in str(unit.get("path", "")).lower()
    ][:10]
    if matches:
        print("Current-ledger candidates:", file=sys.stderr)
        for unit in matches:
            print(
                f"  {unit.get('id')}  {unit.get('type')}  {unit.get('path')}"
                f":{unit.get('start_line') or ''}-{unit.get('end_line') or ''}",
                file=sys.stderr,
            )
    else:
        print(
            "The ID may be stale after init --force/refresh or may have been copied incorrectly. "
            "Claim from the current ledger with claim-next instead of deriving IDs manually.",
            file=sys.stderr,
        )


def command_claim(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "ledger.json"
    ledger = load_json(path)
    unit = ledger.get("units", {}).get(args.unit) if ledger else None
    if not unit:
        print_unknown_unit(ledger, args.unit)
        return 2
    if unit.get("excluded"):
        print("Unit is excluded.", file=sys.stderr)
        return 2
    if unit["status"] == "tracked_fully":
        print("Unit is already tracked_fully.", file=sys.stderr)
        return 2
    if unit["status"] == "tracking" and unit.get("agent") not in {None, args.agent}:
        print(f"Unit is already claimed by {unit.get('agent')}.", file=sys.stderr)
        return 3
    unit["status"] = "tracking"
    unit["agent"] = args.agent
    unit["started_at"] = unit.get("started_at") or now_iso()
    ledger["updated_at"] = now_iso()
    save_json(path, ledger)
    write_coverage(output)
    print(json.dumps(unit, indent=2))
    return 0

def command_complete(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "ledger.json"
    ledger = load_json(path)
    unit = ledger.get("units", {}).get(args.unit) if ledger else None
    if not unit:
        print_unknown_unit(ledger, args.unit)
        return 2
    if unit.get("excluded"):
        print("Excluded unit cannot be completed.", file=sys.stderr)
        return 2
    missing_deps = [
        dep for dep in unit.get("depends_on", [])
        if ledger["units"].get(dep, {}).get("status") != "tracked_fully"
        and not ledger["units"].get(dep, {}).get("excluded")
    ]
    if missing_deps:
        print(f"Dependencies incomplete: {missing_deps[:10]}", file=sys.stderr)
        return 3
    report_path = resolve_report(output, args.report)
    if not report_path.exists():
        print(f"Report does not exist: {report_path}", file=sys.stderr)
        return 4
    if not args.evidence:
        print("At least one --evidence value is required.", file=sys.stderr)
        return 4
    unit["status"] = "tracked_fully"
    unit["report"] = os.path.relpath(report_path, output).replace("\\", "/")
    unit["evidence"] = args.evidence
    unit["completed_at"] = now_iso()
    unit["agent"] = args.agent or unit.get("agent")
    ledger["updated_at"] = now_iso()
    save_json(path, ledger)
    write_coverage(output)
    print(json.dumps(unit, indent=2))
    return 0

def read_manifest(path: str) -> list[dict[str, Any]]:
    manifest_path = Path(path).resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    text = manifest_path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("items", data.get("updates", []))
        if not isinstance(data, list):
            raise ValueError("JSON manifest must be an array or contain items/updates")
        return [item for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        items: list[dict[str, Any]] = []
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"JSONL line {line_no} is not an object")
            items.append(item)
        return items


def command_claim_next(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "ledger.json"
    ledger = load_json(path)
    if not ledger:
        print("No ledger found.", file=sys.stderr)
        return 2
    allowed_types = set(args.type or [])
    candidates = []
    for unit in ledger.get("units", {}).values():
        if unit.get("excluded") or unit.get("status") != "not_tracked":
            continue
        if allowed_types and unit.get("type") not in allowed_types:
            continue
        if args.path_prefix and not str(unit.get("path", "")).startswith(args.path_prefix):
            continue
        # Do not claim synthesis work before all dependencies are complete.
        if any(
            not ledger["units"].get(dep, {}).get("excluded")
            and ledger["units"].get(dep, {}).get("status") != "tracked_fully"
            for dep in unit.get("depends_on", [])
        ):
            continue
        candidates.append(unit)
    candidates.sort(key=lambda u: (u.get("path", ""), u.get("start_line") or 0, u.get("type", "")))
    selected = candidates[: args.count]
    for unit in selected:
        unit["status"] = "tracking"
        unit["agent"] = args.agent
        unit["started_at"] = unit.get("started_at") or now_iso()
    if selected:
        ledger["updated_at"] = now_iso()
        save_json(path, ledger)
        write_coverage(output)
    print(json.dumps(selected, indent=2))
    return 0


def command_complete_batch(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    ledger_path = output / "machine" / "ledger.json"
    ledger = load_json(ledger_path)
    if not ledger:
        print("No ledger found.", file=sys.stderr)
        return 2
    try:
        items = read_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    completed: list[str] = []
    for index, item in enumerate(items, 1):
        uid = item.get("unit") or item.get("id")
        unit = ledger.get("units", {}).get(uid)
        if not unit:
            print(f"Manifest item {index}: unknown unit {uid}", file=sys.stderr)
            return 3
        if unit.get("excluded"):
            print(f"Manifest item {index}: unit is excluded: {uid}", file=sys.stderr)
            return 3
        report = item.get("report")
        evidence = item.get("evidence") or []
        if isinstance(evidence, str):
            evidence = [evidence]
        if not report or not resolve_report(output, report).exists():
            print(f"Manifest item {index}: missing report {report}", file=sys.stderr)
            return 4
        if not evidence:
            print(f"Manifest item {index}: evidence is required", file=sys.stderr)
            return 4
        for ev in evidence:
            error = validate_evidence(output, ledger, str(ev))
            if error:
                print(f"Manifest item {index}: {error}", file=sys.stderr)
                return 4
        missing_deps = [
            dep for dep in unit.get("depends_on", [])
            if ledger["units"].get(dep, {}).get("status") != "tracked_fully"
            and not ledger["units"].get(dep, {}).get("excluded")
        ]
        if missing_deps:
            print(f"Manifest item {index}: dependencies incomplete: {missing_deps[:10]}", file=sys.stderr)
            return 5
        unit["status"] = "tracked_fully"
        unit["report"] = os.path.relpath(resolve_report(output, report), output).replace("\\", "/")
        unit["evidence"] = [str(ev) for ev in evidence]
        unit["completed_at"] = now_iso()
        unit["agent"] = item.get("agent") or args.agent or unit.get("agent")
        completed.append(uid)
    if completed:
        ledger["updated_at"] = now_iso()
        save_json(ledger_path, ledger)
        write_coverage(output)
    print(json.dumps({"completed": completed, "count": len(completed)}, indent=2))
    return 0


def command_entity_claim_next(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path)
    if not data:
        print("No entity ledger found.", file=sys.stderr)
        return 2
    allowed_kinds = set(args.kind or [])
    candidates = []
    for entity in data.get("entities", {}).values():
        if entity.get("excluded") or entity.get("status") != "not_tracked":
            continue
        if allowed_kinds and entity.get("kind") not in allowed_kinds:
            continue
        candidates.append(entity)
    candidates.sort(key=lambda e: (e.get("kind", ""), e.get("title", ""), e.get("id", "")))
    selected = candidates[: args.count]
    for entity in selected:
        entity["status"] = "tracking"
        entity["agent"] = args.agent
        entity["started_at"] = entity.get("started_at") or now_iso()
        entity["updated_at"] = now_iso()
    if selected:
        data["updated_at"] = now_iso()
        save_json(path, data)
        write_coverage(output)
    print(json.dumps(selected, indent=2))
    return 0


def command_entity_complete_batch(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path)
    ledger = load_json(output / "machine" / "ledger.json", {})
    if not data:
        print("No entity ledger found.", file=sys.stderr)
        return 2
    try:
        items = read_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    completed: list[str] = []
    for index, item in enumerate(items, 1):
        eid = item.get("id") or item.get("entity")
        entity = data.get("entities", {}).get(eid)
        if not entity:
            print(f"Manifest item {index}: unknown entity {eid}", file=sys.stderr)
            return 3
        report = item.get("report")
        evidence = item.get("evidence") or []
        if isinstance(evidence, str):
            evidence = [evidence]
        if not report or not resolve_report(output, report).exists():
            print(f"Manifest item {index}: missing report {report}", file=sys.stderr)
            return 4
        if not evidence:
            print(f"Manifest item {index}: evidence is required", file=sys.stderr)
            return 4
        for ev in evidence:
            error = validate_evidence(output, ledger, str(ev))
            if error:
                print(f"Manifest item {index}: {error}", file=sys.stderr)
                return 4
        entity["status"] = "tracked_fully"
        entity["report"] = os.path.relpath(resolve_report(output, report), output).replace("\\", "/")
        entity["evidence"] = [str(ev) for ev in evidence]
        entity["completed_at"] = now_iso()
        entity["agent"] = item.get("agent") or args.agent or entity.get("agent")
        entity["updated_at"] = now_iso()
        completed.append(eid)
    if completed:
        data["updated_at"] = now_iso()
        save_json(path, data)
        write_coverage(output)
    print(json.dumps({"completed": completed, "count": len(completed)}, indent=2))
    return 0


def command_entity_import(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path, {"schema_version": 1, "entities": {}})
    try:
        items = read_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    entities = data.setdefault("entities", {})
    imported: list[str] = []
    for index, item in enumerate(items, 1):
        eid = item.get("id")
        kind = item.get("kind")
        title = item.get("title")
        if not eid or not kind or not title:
            print(f"Manifest item {index}: id, kind, and title are required", file=sys.stderr)
            return 3
        sources = item.get("sources") or item.get("source") or []
        if isinstance(sources, str):
            sources = [sources]
        upsert_seed_entity(
            entities,
            str(eid),
            str(kind),
            str(title),
            [str(source) for source in sources],
            item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
        )
        imported.append(str(eid))
    data["updated_at"] = now_iso()
    save_json(path, data)
    write_coverage(output)
    print(json.dumps({"imported": imported, "count": len(imported)}, indent=2))
    return 0

def command_exclude_unit(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "ledger.json"
    ledger = load_json(path)
    unit = ledger.get("units", {}).get(args.unit) if ledger else None
    if not unit:
        print_unknown_unit(ledger, args.unit)
        return 2
    unit["excluded"] = True
    unit["exclusion_reason"] = args.reason
    unit["status"] = "not_tracked"
    ledger["updated_at"] = now_iso()
    save_json(path, ledger)
    write_coverage(output)
    return 0

def command_exclude_file(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "ledger.json"
    ledger = load_json(path)
    file_rec = ledger.get("files", {}).get(args.path) if ledger else None
    if not file_rec:
        print("Unknown file path.", file=sys.stderr)
        return 2
    file_rec["excluded"] = True
    file_rec["exclusion_reason"] = args.reason
    for uid in file_rec.get("units", []):
        unit = ledger["units"].get(uid)
        if unit:
            unit["excluded"] = True
            unit["exclusion_reason"] = args.reason
            unit["status"] = "not_tracked"
    ledger["updated_at"] = now_iso()
    save_json(path, ledger)
    write_coverage(output)
    return 0

def command_entity_add(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path, {"schema_version": 1, "entities": {}})
    entities = data.setdefault("entities", {})
    existing = entities.get(args.id)
    if existing:
        existing["kind"] = args.kind
        existing["title"] = args.title
        for source in args.source or []:
            if source not in existing.setdefault("sources", []):
                existing["sources"].append(source)
        existing["updated_at"] = now_iso()
    else:
        entities[args.id] = {
            "id": args.id,
            "kind": args.kind,
            "title": args.title,
            "status": "not_tracked",
            "sources": args.source or [],
            "report": None,
            "evidence": [],
            "excluded": False,
            "exclusion_reason": None,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
    data["updated_at"] = now_iso()
    save_json(path, data)
    write_coverage(output)
    print(json.dumps(entities[args.id], indent=2))
    return 0

def command_entity_claim(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path)
    entity = data.get("entities", {}).get(args.id) if data else None
    if not entity:
        print("Unknown entity.", file=sys.stderr)
        return 2
    if entity.get("excluded") or entity.get("status") == "tracked_fully":
        print("Entity cannot be claimed.", file=sys.stderr)
        return 2
    entity["status"] = "tracking"
    entity["agent"] = args.agent
    entity["started_at"] = entity.get("started_at") or now_iso()
    entity["updated_at"] = now_iso()
    save_json(path, data)
    write_coverage(output)
    return 0

def command_entity_complete(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path)
    entity = data.get("entities", {}).get(args.id) if data else None
    if not entity:
        print("Unknown entity.", file=sys.stderr)
        return 2
    report_path = resolve_report(output, args.report)
    if not report_path.exists():
        print(f"Report does not exist: {report_path}", file=sys.stderr)
        return 3
    if not args.evidence:
        print("At least one --evidence value is required.", file=sys.stderr)
        return 3
    entity["status"] = "tracked_fully"
    entity["report"] = os.path.relpath(report_path, output).replace("\\", "/")
    entity["evidence"] = args.evidence
    entity["completed_at"] = now_iso()
    entity["updated_at"] = now_iso()
    save_json(path, data)
    write_coverage(output)
    return 0

def command_entity_exclude(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    path = output / "machine" / "entities.json"
    data = load_json(path)
    entity = data.get("entities", {}).get(args.id) if data else None
    if not entity:
        print("Unknown entity.", file=sys.stderr)
        return 2
    entity["excluded"] = True
    entity["exclusion_reason"] = args.reason
    entity["status"] = "not_tracked"
    entity["updated_at"] = now_iso()
    save_json(path, data)
    write_coverage(output)
    return 0

EVIDENCE_RE = re.compile(r"^(?P<path>.+):(?P<start>\d+)(?:-(?P<end>\d+))?$")

def validate_evidence(output: Path, ledger: dict[str, Any], evidence: str) -> str | None:
    evidence = str(evidence).strip()
    if not evidence:
        return "empty evidence"
    if evidence.startswith("gitnexus:"):
        return None if len(evidence) > len("gitnexus:") else "empty GitNexus evidence"
    if evidence.startswith("runtime:"):
        raw = evidence[len("runtime:"):]
        if not raw:
            return "empty runtime evidence"
        candidates = [output / raw, output / "evidence" / "runtime" / raw]
        if any(candidate.exists() for candidate in candidates):
            return None
        return f"runtime evidence file does not exist: {raw}"
    if evidence.startswith("test:"):
        evidence = evidence[len("test:"):]
    if evidence.startswith("repo:"):
        evidence = evidence[len("repo:"):]

    # Allow non-line evidence for inventoried binary assets/config artifacts.
    if evidence in ledger.get("files", {}):
        return None
    m = EVIDENCE_RE.match(evidence)
    if not m:
        return f"unrecognized evidence format: {evidence}"
    rel = m.group("path").replace("\\", "/")
    rec = ledger.get("files", {}).get(rel)
    if not rec:
        return f"evidence file is not inventoried: {rel}"
    count = rec.get("line_count")
    if count is None:
        return f"line evidence points to non-text file: {rel}"
    start = int(m.group("start"))
    end = int(m.group("end") or start)
    if start < 1 or end < start or end > max(1, count):
        return f"evidence range out of bounds: {evidence} (file has {count} lines)"
    return None

def command_validate(args: argparse.Namespace) -> int:
    output = Path(args.out).resolve()
    ledger = load_json(output / "machine" / "ledger.json")
    entities_data = load_json(output / "machine" / "entities.json", {"entities": {}})
    if not ledger:
        print("FAIL: no ledger found.", file=sys.stderr)
        return 2

    errors: list[str] = []
    for uid, unit in ledger.get("units", {}).items():
        if unit.get("excluded"):
            if not unit.get("exclusion_reason"):
                errors.append(f"{uid}: excluded without reason")
            continue
        if unit.get("status") != "tracked_fully":
            errors.append(f"{uid}: status={unit.get('status')}")
            continue
        report = unit.get("report")
        if not report or not resolve_report(output, report).exists():
            errors.append(f"{uid}: missing report {report}")
        if not unit.get("evidence"):
            errors.append(f"{uid}: no evidence")
        for ev in unit.get("evidence", []):
            err = validate_evidence(output, ledger, ev)
            if err:
                errors.append(f"{uid}: {err}")

    for eid, entity in entities_data.get("entities", {}).items():
        if entity.get("excluded"):
            if not entity.get("exclusion_reason"):
                errors.append(f"{eid}: entity excluded without reason")
            continue
        if entity.get("status") != "tracked_fully":
            errors.append(f"{eid}: entity status={entity.get('status')}")
            continue
        report = entity.get("report")
        if not report or not resolve_report(output, report).exists():
            errors.append(f"{eid}: missing entity report {report}")
        if not entity.get("evidence"):
            errors.append(f"{eid}: no entity evidence")

    required = [
        "COVERAGE.md", "DISCOVERY_JOURNAL.md", "UNKNOWNS.md",
        "CONTRADICTIONS.md", "GOD_README.md",
        "00-product/PRODUCT_MODEL.md",
        "01-launch-auth-onboarding/LAUNCH_MAP.md",
        "02-navigation/NAVIGATION_GRAPH.md",
        "03-screens/SCREEN_INDEX.md",
        "04-features/FEATURE_INDEX.md",
        "05-flows/FLOW_INDEX.md",
        "06-state-data/STATE_DATA_MAP.md",
        "07-platform/PLATFORM_MAP.md",
        "09-code-atlas/CODE_INDEX.md",
    ]
    for rel in required:
        required_path = output / rel
        if not required_path.exists():
            errors.append(f"missing required deliverable: {rel}")
        elif required_path.suffix.lower() == ".md" and len(required_path.read_text(encoding="utf-8", errors="replace").strip()) < 40:
            errors.append(f"required deliverable is effectively empty: {rel}")

    runtime_mode = ledger.get("runtime_mode", "auto")
    state_matrix = output / "08-runtime" / "STATE_MATRIX.md"
    blocker = output / "08-runtime" / "BLOCKER.md"
    runtime_files = [p for p in (output / "evidence" / "runtime").rglob("*") if p.is_file()]
    if runtime_mode == "on":
        if not state_matrix.exists() or len(state_matrix.read_text(encoding="utf-8", errors="replace").strip()) < 40:
            errors.append("runtime-mode=on requires 08-runtime/STATE_MATRIX.md")
        if not runtime_files:
            errors.append("runtime-mode=on requires at least one runtime evidence file")
    elif runtime_mode == "off":
        if not blocker.exists() or len(blocker.read_text(encoding="utf-8", errors="replace").strip()) < 40:
            errors.append("runtime-mode=off requires 08-runtime/BLOCKER.md with the exact reason")
    else:
        runtime_documented = state_matrix.exists() and len(state_matrix.read_text(encoding="utf-8", errors="replace").strip()) >= 40 and bool(runtime_files)
        blocked_documented = blocker.exists() and len(blocker.read_text(encoding="utf-8", errors="replace").strip()) >= 40
        if not runtime_documented and not blocked_documented:
            errors.append("runtime-mode=auto requires either a populated STATE_MATRIX plus evidence or a populated BLOCKER.md")

    write_coverage(output)
    if errors:
        print(f"VALIDATION FAIL — {len(errors)} issue(s)")
        for error in errors[:500]:
            print(f"- {error}")
        if len(errors) > 500:
            print(f"... {len(errors) - 500} more")
        return 1
    print("VALIDATION PASS")
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Mobile App Anatomy coverage ledger")
    sub = p.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--repo", default=".")
    init.add_argument("--out", default="./docs/mobile-app-anatomy")
    init.add_argument("--chunk-lines", type=int, default=300)
    init.add_argument("--force", action="store_true")
    init.add_argument("--include-dir", action="append", default=[], help="Force traversal of an otherwise excluded generated/build subtree")
    init.add_argument("--exclude-dir", action="append", default=[], help="Exclude a repository-relative tooling or non-product subtree")
    init.add_argument("--runtime-mode", choices=["auto", "on", "off"], default="auto")
    init.set_defaults(func=command_init)

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--repo", default=".")
    refresh.add_argument("--out", default="./docs/mobile-app-anatomy")
    refresh.add_argument("--chunk-lines", type=int, default=300)
    refresh.add_argument("--force", action="store_true")
    refresh.add_argument("--include-dir", action="append", default=[], help="Add an otherwise excluded generated/build subtree")
    refresh.add_argument("--exclude-dir", action="append", default=[], help="Add a repository-relative tooling or non-product subtree exclusion")
    refresh.add_argument("--runtime-mode", choices=["auto", "on", "off"], default=None)
    refresh.set_defaults(func=command_refresh)

    status = sub.add_parser("status")
    status.add_argument("--out", default="./docs/mobile-app-anatomy")
    status.set_defaults(func=command_status)

    claim = sub.add_parser("claim")
    claim.add_argument("--out", default="./docs/mobile-app-anatomy")
    claim.add_argument("--unit", required=True)
    claim.add_argument("--agent", default="agent")
    claim.set_defaults(func=command_claim)

    complete = sub.add_parser("complete")
    complete.add_argument("--out", default="./docs/mobile-app-anatomy")
    complete.add_argument("--unit", required=True)
    complete.add_argument("--report", required=True)
    complete.add_argument("--evidence", action="append", default=[])
    complete.add_argument("--agent")
    complete.set_defaults(func=command_complete)

    cn = sub.add_parser("claim-next")
    cn.add_argument("--out", default="./docs/mobile-app-anatomy")
    cn.add_argument("--type", action="append", default=[])
    cn.add_argument("--path-prefix")
    cn.add_argument("--count", type=int, default=25)
    cn.add_argument("--agent", default="agent")
    cn.set_defaults(func=command_claim_next)

    cb = sub.add_parser("complete-batch")
    cb.add_argument("--out", default="./docs/mobile-app-anatomy")
    cb.add_argument("--manifest", required=True)
    cb.add_argument("--agent")
    cb.set_defaults(func=command_complete_batch)

    ecn = sub.add_parser("entity-claim-next")
    ecn.add_argument("--out", default="./docs/mobile-app-anatomy")
    ecn.add_argument("--kind", action="append", default=[])
    ecn.add_argument("--count", type=int, default=100)
    ecn.add_argument("--agent", default="agent")
    ecn.set_defaults(func=command_entity_claim_next)

    ecb = sub.add_parser("entity-complete-batch")
    ecb.add_argument("--out", default="./docs/mobile-app-anatomy")
    ecb.add_argument("--manifest", required=True)
    ecb.add_argument("--agent")
    ecb.set_defaults(func=command_entity_complete_batch)

    eimp = sub.add_parser("entity-import")
    eimp.add_argument("--out", default="./docs/mobile-app-anatomy")
    eimp.add_argument("--manifest", required=True)
    eimp.set_defaults(func=command_entity_import)

    exu = sub.add_parser("exclude-unit")
    exu.add_argument("--out", default="./docs/mobile-app-anatomy")
    exu.add_argument("--unit", required=True)
    exu.add_argument("--reason", required=True)
    exu.set_defaults(func=command_exclude_unit)

    exf = sub.add_parser("exclude-file")
    exf.add_argument("--out", default="./docs/mobile-app-anatomy")
    exf.add_argument("--path", required=True)
    exf.add_argument("--reason", required=True)
    exf.set_defaults(func=command_exclude_file)

    ea = sub.add_parser("entity-add")
    ea.add_argument("--out", default="./docs/mobile-app-anatomy")
    ea.add_argument("--kind", required=True)
    ea.add_argument("--id", required=True)
    ea.add_argument("--title", required=True)
    ea.add_argument("--source", action="append", default=[])
    ea.set_defaults(func=command_entity_add)

    ec = sub.add_parser("entity-claim")
    ec.add_argument("--out", default="./docs/mobile-app-anatomy")
    ec.add_argument("--id", required=True)
    ec.add_argument("--agent", default="agent")
    ec.set_defaults(func=command_entity_claim)

    ed = sub.add_parser("entity-complete")
    ed.add_argument("--out", default="./docs/mobile-app-anatomy")
    ed.add_argument("--id", required=True)
    ed.add_argument("--report", required=True)
    ed.add_argument("--evidence", action="append", default=[])
    ed.set_defaults(func=command_entity_complete)

    ee = sub.add_parser("entity-exclude")
    ee.add_argument("--out", default="./docs/mobile-app-anatomy")
    ee.add_argument("--id", required=True)
    ee.add_argument("--reason", required=True)
    ee.set_defaults(func=command_entity_exclude)

    val = sub.add_parser("validate")
    val.add_argument("--out", default="./docs/mobile-app-anatomy")
    val.set_defaults(func=command_validate)

    return p

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "chunk_lines", 300) < 25:
        parser.error("--chunk-lines must be at least 25")
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
