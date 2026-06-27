param(
  [ValidateSet("claude", "codex", "cursor", "all")]
  [string]$Target = "all",
  [string]$ProjectPath = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillSource = Join-Path $Root "skills/mobile-app-anatomy"

function Copy-FreshDirectory([string]$Source, [string]$Destination) {
  if (Test-Path $Destination) {
    Remove-Item -Recurse -Force $Destination
  }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
  Copy-Item -Recurse -Force $Source $Destination
}

if ($Target -in @("claude", "all")) {
  $Destination = Join-Path $HOME ".claude/skills/mobile-app-anatomy"
  Copy-FreshDirectory $SkillSource $Destination
  Write-Host "Installed Claude skill: $Destination"
}

if ($Target -in @("codex", "all")) {
  $Destination = Join-Path $HOME ".agents/skills/mobile-app-anatomy"
  Copy-FreshDirectory $SkillSource $Destination
  Write-Host "Installed Codex skill: $Destination"
}

if ($Target -in @("cursor", "all")) {
  $CursorRoot = Join-Path $ProjectPath ".cursor"
  $Destination = Join-Path $CursorRoot "skills/mobile-app-anatomy"
  Copy-FreshDirectory $SkillSource $Destination
  New-Item -ItemType Directory -Force -Path (Join-Path $CursorRoot "rules") | Out-Null
  Copy-Item -Force (Join-Path $Root "cursor/mobile-app-anatomy.mdc") (Join-Path $CursorRoot "rules/mobile-app-anatomy.mdc")
  Write-Host "Installed Cursor skill and rule under: $CursorRoot"
}
