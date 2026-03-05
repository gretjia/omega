param(
    [int]$SampleCount = 20
)

$7z = "C:\Program Files\7-Zip\7z.exe"
$Root = "E:\data\level2"

Write-Host "Scanning archives in $Root..."
$files = Get-ChildItem -Path $Root -Recurse -Filter *.7z
$total = $files.Count

if ($total -eq 0) {
    Write-Error "No archives found!"
    exit 1
}

Write-Host "Found $total archives. Sampling $SampleCount..."

# Random Sample
$sample = $files | Get-Random -Count $SampleCount

$passed = 0
$failed = 0

foreach ($f in $sample) {
    Write-Host -NoNewline "Testing $($f.Name)... "
    $proc = Start-Process -FilePath $7z -ArgumentList "t", "`"$($f.FullName)`"" -Wait -NoNewWindow -PassThru
    
    if ($proc.ExitCode -eq 0) {
        Write-Host "OK" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "FAIL (Code: $($proc.ExitCode))" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n--- Integrity Summary ---"
Write-Host "Total Tested: $SampleCount"
Write-Host "Passed:       $passed"
Write-Host "Failed:       $failed"

if ($failed -gt 0) {
    exit 1
}
exit 0
