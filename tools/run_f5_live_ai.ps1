# Credentials stay in memory and the child environment, never in arguments/files.
function Read-LiveDemoSecureKey {
    param([scriptblock]$Prompt = { Read-Host 'OpenRouter API key' -AsSecureString })
    $promptFinished = $false
    try {
        $value = & $Prompt
        $promptFinished = $true
        return $value
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        $promptFinished = $true
        # A stopped pipeline cannot reliably carry Write-Host/return output.
        [Console]::Error.WriteLine('[AI_KEY_REQUIRED] OpenRouter API key is required for the F5 Live AI demo.')
        exit 1
    }
    catch { $promptFinished = $true; return $null }
    finally {
        # Ctrl+C can bypass catch when PowerShell stops the entire pipeline.
        if (-not $promptFinished) {
            [Console]::Error.WriteLine('[AI_KEY_REQUIRED] OpenRouter API key is required for the F5 Live AI demo.')
        }
    }
}

function New-LiveDemoStartInfo {
    param([scriptblock]$Prompt = { Read-Host 'OpenRouter API key' -AsSecureString })
    $key = [Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY', 'Process')
    $secureKey = $null
    $pointer = [IntPtr]::Zero
    try {
        if ([string]::IsNullOrWhiteSpace($key)) {
            $secureKey = Read-LiveDemoSecureKey -Prompt $Prompt
            if ($null -eq $secureKey) { return $null }
            $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
            $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
        }
        if ([string]::IsNullOrWhiteSpace($key)) { return $null }
        $info = New-Object System.Diagnostics.ProcessStartInfo
        $info.FileName = Join-Path (Split-Path $PSScriptRoot -Parent) 'DEMO_PORTABLE\DEMO.exe'
        $info.WorkingDirectory = Split-Path $info.FileName -Parent
        $info.UseShellExecute = $false
        $info.EnvironmentVariables['AI_PROVIDER'] = 'openrouter'
        $info.EnvironmentVariables['OPENROUTER_API_KEY'] = $key
        $info.EnvironmentVariables['OPENROUTER_MODEL'] = 'nvidia/nemotron-3-ultra-550b-a55b:free'
        $info.EnvironmentVariables['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
        $info.EnvironmentVariables['OPENROUTER_MAX_RETRIES'] = '0'
        return $info
    }
    catch { return $null }
    finally {
        $key = $null
        if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        if ($null -ne $secureKey) { $secureKey.Dispose() }
    }
}

function Invoke-LiveDemo {
    param([scriptblock]$Prompt = { Read-Host 'OpenRouter API key' -AsSecureString })
    $info = New-LiveDemoStartInfo -Prompt $Prompt
    if ($null -eq $info) {
        Write-Host '[AI_KEY_REQUIRED] OpenRouter API key is required for the F5 Live AI demo.'
        return 1
    }
    $process = $null
    try {
        $process = [Diagnostics.Process]::Start($info)
        $info.EnvironmentVariables.Remove('OPENROUTER_API_KEY')
        $process.WaitForExit()
        return $process.ExitCode
    }
    catch {
        Write-Host '[DEMO_START_FAILED] Check that the complete DEMO_PORTABLE build is available.'
        return 1
    }
    finally {
        $info.EnvironmentVariables.Remove('OPENROUTER_API_KEY')
        if ($null -ne $process) { $process.Dispose() }
    }
}

# Dot-sourcing permits offline configuration tests without starting the EXE.
if ($MyInvocation.InvocationName -ne '.') { exit (Invoke-LiveDemo) }
