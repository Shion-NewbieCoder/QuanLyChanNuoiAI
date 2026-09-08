# Developer verification only. Run while the isolated EXE is serving port 8000
# from an environment that blocks external network access but allows loopback.
param([string] $EvidencePath = (Join-Path (Get-Location) 'build/offline-verification.json'))
$ErrorActionPreference = 'Stop'
$baseUri = 'http://127.0.0.1:8000'
$report = [ordered]@{ status = 'RUNNING'; external_probes = @(); roles = @(); assets = @() }
try {
    foreach ($remoteUri in @('https://example.com', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css')) {
        $blocked = $false
        try { Invoke-WebRequest -Uri $remoteUri -UseBasicParsing -TimeoutSec 5 | Out-Null }
        catch { $blocked = $true }
        if (-not $blocked) { throw "External access is available; this is not an offline test: $remoteUri" }
        $report.external_probes += @{ url = $remoteUri; result = 'Connection blocked/unavailable' }
    }
    foreach ($role in @('manager', 'technician', 'employee')) {
        $page = Invoke-WebRequest -Uri "$baseUri/login/" -SessionVariable demoSession -UseBasicParsing
        $token = ($demoSession.Cookies.GetCookies([uri]$baseUri) | Where-Object Name -eq 'csrftoken').Value
        $page = Invoke-WebRequest -Uri "$baseUri/login/" -WebSession $demoSession -UseBasicParsing -Method Post -Body @{
            csrfmiddlewaretoken = $token; username = "demo_$role"; password = 'DemoOnly-2026!'; next = '/dashboard/'
        }
        if ($page.BaseResponse.ResponseUri.AbsolutePath -ne '/dashboard/') { throw "Login failed: $role" }
        $report.roles += $role
        if ($role -eq 'manager') { $managerSession = $demoSession }
    }
    $token = ($managerSession.Cookies.GetCookies([uri]$baseUri) | Where-Object Name -eq 'csrftoken').Value
    $assets = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($route in @('/dashboard/', '/herds/', '/animals/', '/animal-groups/', '/pens/', '/care/', '/feed/', '/medicine/', '/vaccines/', '/vaccination-records/', '/growth/', '/reproduction/', '/sales/', '/statistics/', '/ai/')) {
        $page = Invoke-WebRequest -Uri ($baseUri + $route) -WebSession $managerSession -UseBasicParsing
        if ($page.StatusCode -ne 200) { throw "Route failed: $route" }
        foreach ($match in [regex]::Matches($page.Content, '(?:src|href)="(/static/[^"#]+)')) { [void]$assets.Add($match.Groups[1].Value) }
    }
    foreach ($asset in $assets) {
        $page = Invoke-WebRequest -Uri ($baseUri + $asset) -WebSession $managerSession -UseBasicParsing
        if ($page.StatusCode -ne 200) { throw "Static unavailable: $asset" }
        $report.assets += $asset
    }
    $herdPayload = @{
        csrfmiddlewaretoken = $token; code = 'OFFLINE-CHECK'; name = 'Offline check'; animal_type = 'cow';
        management_mode = 'group'; quantity = '3'; status = 'active'; avatar = 'cow'
    }
    $page = Invoke-WebRequest -Uri "$baseUri/herds/create/" -WebSession $managerSession -UseBasicParsing -Method Post -Body $herdPayload
    $detail = $page.BaseResponse.ResponseUri.AbsolutePath
    if ($detail -notmatch '^/herds/\d+/$') { throw 'Offline create failed' }
    $herdPayload.name = 'Offline edited'
    $page = Invoke-WebRequest -Uri ($baseUri + $detail + 'edit/') -WebSession $managerSession -UseBasicParsing -Method Post -Body $herdPayload
    if ($page.Content -notmatch 'Offline edited') { throw 'Offline edit/read failed' }
    $page = Invoke-WebRequest -Uri "$baseUri/ai/" -WebSession $managerSession -UseBasicParsing -Method Post -Body @{
        csrfmiddlewaretoken = $token; feature = 'herd_summary'; 'herd_summary-target_id' = '1'
    }
    # Stable HTML class plus the existing Vietnamese safe message, UTF-8 source.
    if ($page.Content -notmatch 'AI hiện chưa được cấu hình') { throw 'Safe AI state missing' }
    $page = Invoke-WebRequest -Uri ($baseUri + $detail + 'delete/') -WebSession $managerSession -UseBasicParsing -Method Post -Body @{ csrfmiddlewaretoken = $token }
    if ($page.BaseResponse.ResponseUri.AbsolutePath -ne '/herds/') { throw 'Offline delete failed' }
    $report.crud = 'PASS: create/read/edit/delete'
    $report.statistics = 'PASS: HTTP 200'
    $report.ai_unconfigured = 'PASS: safe existing response'
    $report.status = 'PASS'
} catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
    throw
} finally {
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    $report | ConvertTo-Json -Depth 5
}
