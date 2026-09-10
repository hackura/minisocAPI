param(
    [string]$ApiUrl = "http://127.0.0.1:8000/api/v1/events",
    [string]$ApiKey = $env:MINISOC_API_KEY,
    [int]$MaxEvents = 20,
    [int]$HoursBack = 1
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Error "MINISOC_API_KEY is not set. Example: `$env:MINISOC_API_KEY='dev-minisoc-key'"
}

$headers = @{ "X-API-Key" = $ApiKey }
$startTime = (Get-Date).AddHours(-1 * $HoursBack)

function Convert-WindowsEventToMiniSOC {
    param([System.Diagnostics.Eventing.Reader.EventRecord]$Event)

    $message = try { $Event.FormatDescription() } catch { "Windows Event ID $($Event.Id)" }
    $username = $null
    $sourceIp = $null

    # Security Event ID 4625 = failed logon.
    if ($Event.Id -eq 4625) {
        $eventType = "failed_login"
        $severityHint = "high"

        if ($message -match "Account Name:\s*([^\r\n]+)") {
            $username = $matches[1].Trim()
        }
        if ($message -match "Source Network Address:\s*([^\r\n]+)") {
            $sourceIp = $matches[1].Trim()
        }
    }
    elseif ($Event.Id -eq 4624) {
        $eventType = "successful_login"
        $severityHint = "low"
    }
    else {
        $eventType = "windows_security_event"
        $severityHint = "low"
    }

    return @{
        event_type = $eventType
        username   = $username
        source_ip  = $sourceIp
        message    = $message
    }
}

Write-Host "MiniSOC Windows Collector"
Write-Host "Reading Security log since $startTime"
Write-Host "Sending up to $MaxEvents events to $ApiUrl"

$events = Get-WinEvent -FilterHashtable @{ LogName = "Security"; StartTime = $startTime } -MaxEvents $MaxEvents

$sent = 0
foreach ($event in $events) {
    $payload = Convert-WindowsEventToMiniSOC -Event $event | ConvertTo-Json -Depth 5

    try {
        $response = Invoke-RestMethod -Uri $ApiUrl -Method Post -Headers $headers -ContentType "application/json" -Body $payload
        Write-Host "[OK] Windows Event $($event.Id) -> MiniSOC event #$($response.id) ($($response.severity))"
        $sent++
    }
    catch {
        Write-Warning "[FAILED] Windows Event $($event.Id): $($_.Exception.Message)"
    }
}

Write-Host "Collection complete. Sent $sent event(s)."
