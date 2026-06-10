$baseUrl = "http://localhost:8010/api/digital-buddy"

$tests = @(
    @{
        question = "Можно ли передавать проксим-карту другому лицу?"
        expected_code = "KMG-PR-1186"
        expected_section_contains = "пропуск"
    },
    @{
        question = "Что делать сотруднику при потере пропуска?"
        expected_code = "KMG-PR-1186"
        expected_section_contains = "Обязанности"
    },
    @{
        question = "Что такое конфликт интересов и что должен сделать работник?"
        expected_code = "KMG-VND-6677"
        expected_section_contains = "5.3.1"
    },
    @{
        question = "Что делать при предложении взятки?"
        expected_code = "KMG-VND-6677"
        expected_section_contains = "5.1.5"
    },
    @{
        question = "Куда обращаться по коррупционным правонарушениям?"
        expected_code = "KMG-VND-6677"
        expected_section_contains = "доверия"
    },
    @{
        question = "Какие требования к деловой переписке в KMG?"
        expected_code = "KMG-VND-4071"
        expected_section_contains = "переписк"
    },
    @{
        question = "Как вести себя на совещаниях согласно кодексу этики?"
        expected_code = "KMG-VND-4071"
        expected_section_contains = "Совещания"
    },
    @{
        question = "Как формулировать SMART-цели на испытательный срок?"
        expected_code = "KMG-DI-6241"
        expected_section_contains = "SMART"
    },
    @{
        question = "Какой курс доллара сегодня?"
        expected_code = $null
        expected_mode = "no_context"
    }
)

Write-Host "=== Digital Buddy E2E tests (questions from VND instructions) ===" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

foreach ($test in $tests) {
    $body = @{ employee_id = 1; question = $test.question } | ConvertTo-Json -Compress
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/ask" -Method Post -Body $body -ContentType "application/json; charset=utf-8" -TimeoutSec 120
    } catch {
        Write-Host "FAIL: $($test.question)" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        $failed++
        continue
    }

    $codeOk = $true
    $sectionOk = $true
    $modeOk = $true

    if ($test.expected_code) {
        $codeOk = $response.document_code -eq $test.expected_code
    } elseif ($test.expected_mode -eq "no_context") {
        $modeOk = $response.mode -eq "no_context"
        $codeOk = -not $response.document_code
    }

    if ($test.expected_section_contains) {
        $sectionOk = $response.section -like "*$($test.expected_section_contains)*"
    }

    $ok = $codeOk -and $sectionOk -and $modeOk

    if ($ok) {
        $passed++
        Write-Host "PASS: $($test.question)" -ForegroundColor Green
    } else {
        $failed++
        Write-Host "FAIL: $($test.question)" -ForegroundColor Red
    }

    Write-Host "  mode=$($response.mode) code=$($response.document_code)"
    Write-Host "  source=$($response.source)"
    Write-Host "  section=$($response.section)"
    Write-Host "  answer=$($response.answer.Substring(0, [Math]::Min(180, $response.answer.Length)))..."
    Write-Host ""
}

Write-Host "=== Results: $passed passed, $failed failed ===" -ForegroundColor Cyan
if ($failed -gt 0) { exit 1 }
