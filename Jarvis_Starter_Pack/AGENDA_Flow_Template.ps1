param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("append", "finalize", "status", "reset")]
  [string]$Action,

  [string]$Workspace = ".",
  [string]$Who = "",
  [string]$Text = "",
  [string]$Title = "Agreement",
  [string]$Decision = "",
  [string]$Next = ""
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path $Workspace
$agendaDir = Join-Path $root "AGENTS\Agenda"
$archiveDir = Join-Path $agendaDir "archive"
$logPath = Join-Path $agendaDir "AGENDA_LOG.md"

function Ensure-Agenda {
  if (-not (Test-Path $agendaDir)) {
    New-Item -ItemType Directory -Path $agendaDir -Force | Out-Null
  }
  if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
  }
  if (-not (Test-Path $logPath)) {
    $header = @(
      "# Agenda Log"
      ""
      "- Single-file decision board"
      "- Format: ## YYYY-MM-DD HH:mm:ss - [speaker]"
      ""
    ) -join "`r`n"
    Set-Content -Path $logPath -Value $header -Encoding UTF8
  }
}

function Append-Entry {
  if ([string]::IsNullOrWhiteSpace($Who)) { throw "append requires -Who" }
  if ([string]::IsNullOrWhiteSpace($Text)) { throw "append requires -Text" }
  Ensure-Agenda
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $block = @(
    "## $ts - $Who"
    "$Text"
    ""
  ) -join "`r`n"
  Add-Content -Path $logPath -Value $block -Encoding UTF8
  Write-Output "[ok] appended: $ts - $Who"
}

function Finalize-Board {
  Ensure-Agenda
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $agreement = Join-Path $agendaDir "AGREEMENT_$stamp.md"
  $backup = Join-Path $archiveDir "AGENDA_LOG_BACKUP_$stamp.md"
  $logBody = Get-Content -Path $logPath -Raw -Encoding UTF8

  if ([string]::IsNullOrWhiteSpace($Decision)) { $Decision = "(not specified)" }
  if ([string]::IsNullOrWhiteSpace($Next)) { $Next = "(not specified)" }

  $doc = @(
    "# $Title"
    ""
    "- finalized_at: $ts"
    ""
    "## Decision"
    "$Decision"
    ""
    "## Next Action"
    "$Next"
    ""
    "## Agenda Log Snapshot"
    $logBody
    ""
  ) -join "`r`n"

  Set-Content -Path $agreement -Value $doc -Encoding UTF8
  Copy-Item -Path $logPath -Destination $backup -Force
  Clear-Content -Path $logPath -Encoding UTF8
  Write-Output "[ok] agreement: $agreement"
  Write-Output "[ok] backup: $backup"
  Write-Output "[ok] board cleared: $logPath"
}

function Show-Status {
  Ensure-Agenda
  Write-Output "[agenda_dir] $agendaDir"
  Get-ChildItem -Path $agendaDir -Force | Select-Object Name,Length,LastWriteTime | Format-Table -Auto
}

function Reset-Board {
  Ensure-Agenda
  Get-ChildItem -Path $agendaDir -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne "AGENDA_LOG.md" } |
    Remove-Item -Force
  Set-Content -Path $logPath -Value "# Agenda Log`r`n" -Encoding UTF8
  Write-Output "[ok] reset completed"
}

switch ($Action) {
  "append"   { Append-Entry; break }
  "finalize" { Finalize-Board; break }
  "status"   { Show-Status; break }
  "reset"    { Reset-Board; break }
  default    { throw "unknown action: $Action" }
}
