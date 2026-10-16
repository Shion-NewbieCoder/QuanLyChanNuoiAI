"""Offline launcher checks: fake credentials, no EXE or provider invocation."""
import os
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LiveLauncherTests(unittest.TestCase):
    def run_ps(self, body, key=None, expected=0):
        env = os.environ.copy()
        for name in ('OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'AI_API_KEY'):
            env.pop(name, None)
        if key is not None:
            env['OPENROUTER_API_KEY'] = key
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
             '-Command', ". ./tools/run_f5_live_ai.ps1; " + body],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stderr)
        self.assertNotIn('offline-placeholder', result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_existing_key_reused_without_prompt_and_only_child_configured(self):
        self.run_ps("""
function Read-Host { throw 'must not prompt' }
$originalProvider = $env:AI_PROVIDER
$info = New-LiveDemoStartInfo
if ($null -eq $info) { exit 2 }
if ($info.EnvironmentVariables['OPENROUTER_API_KEY'] -ne $env:OPENROUTER_API_KEY) { exit 3 }
if ($info.EnvironmentVariables['AI_PROVIDER'] -ne 'openrouter') { exit 4 }
if ($info.EnvironmentVariables['OPENROUTER_MODEL'] -ne 'nvidia/nemotron-3-ultra-550b-a55b:free') { exit 5 }
if ($info.EnvironmentVariables['OPENROUTER_BASE_URL'] -ne 'https://openrouter.ai/api/v1') { exit 6 }
if ($info.EnvironmentVariables['OPENROUTER_MAX_RETRIES'] -ne '0') { exit 7 }
if ($info.Arguments -or $info.UseShellExecute) { exit 8 }
if ($env:AI_PROVIDER -ne $originalProvider) { exit 9 }
""", key='offline-placeholder')

    def test_secure_prompt_does_not_set_parent_key(self):
        self.run_ps("""
$prompt = {
    $value = [Security.SecureString]::new()
    foreach ($character in 'offline-placeholder'.ToCharArray()) { $value.AppendChar($character) }
    return $value
}
$info = New-LiveDemoStartInfo -Prompt $prompt
if ($null -eq $info -or $env:OPENROUTER_API_KEY) { exit 2 }
if ($info.EnvironmentVariables['OPENROUTER_API_KEY'] -ne 'offline-placeholder') { exit 3 }
""")

    def test_blank_key_exits_explicitly_before_start(self):
        output = self.run_ps("""
function Read-Host { New-Object Security.SecureString }
if ((Invoke-LiveDemo) -ne 1) { exit 2 }
""")
        self.assertIn('[AI_KEY_REQUIRED]', output)

    def test_cancelled_prompt_exits_explicitly(self):
        output = self.run_ps("""
Invoke-LiveDemo -Prompt { throw [System.Management.Automation.PipelineStoppedException]::new() }
exit 99
""", expected=1)
        self.assertIn('[AI_KEY_REQUIRED]', output)
        self.assertNotIn('At line:', output)

    def test_null_prompt_exits_before_start(self):
        self.assertIn('[AI_KEY_REQUIRED]', self.run_ps(
            'if ((Invoke-LiveDemo -Prompt { $null }) -ne 1) { exit 2 }'))

    def test_whitespace_prompt_exits_before_start(self):
        self.assertIn('[AI_KEY_REQUIRED]', self.run_ps("""
if ((Invoke-LiveDemo -Prompt {
    $value = [Security.SecureString]::new()
    $value.AppendChar(' ')
    $value
}) -ne 1) { exit 2 }
"""))

    def test_default_prompt_remains_masked(self):
        self.run_ps("""
function Read-Host { param($Prompt, [switch]$AsSecureString)
    if (-not $AsSecureString) { exit 2 }
    $value = [Security.SecureString]::new()
    $value.AppendChar('x')
    $value
}
$value = Read-LiveDemoSecureKey
if ($null -eq $value -or $value.Length -ne 1) { exit 3 }
$value.Dispose()
""")

    def test_f5_runs_source_bootstrap_in_interactive_terminal(self):
        config = json.loads((ROOT / '.vscode/launch.json').read_text())['configurations'][0]
        self.assertEqual(config['type'], 'node-terminal')
        self.assertEqual(config['request'], 'launch')
        self.assertEqual(config['cwd'], '${workspaceFolder}')
        self.assertEqual(config['command'], 'python .\\tools\\run_demo.py')
        self.assertNotIn('run_f5_live_ai.ps1', config['command'])
        self.assertNotIn('DEMO.exe', config['command'])

    def test_unavailable_noninteractive_prompt_exits_explicitly(self):
        self.assertIn('[AI_KEY_REQUIRED]', self.run_ps('if ((Invoke-LiveDemo) -ne 1) { exit 2 }'))

    def test_portable_does_not_remove_provider_configuration(self):
        source = (ROOT / 'tools/portable_demo.py').read_text(encoding='utf-8')
        for name in ('AI_PROVIDER', 'AI_API_KEY', 'OPENROUTER_API_KEY', 'OPENAI_API_KEY'):
            self.assertNotIn('os.environ.pop("' + name + '"', source)


if __name__ == '__main__':
    unittest.main()
