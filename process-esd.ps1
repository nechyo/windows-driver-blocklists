# process-esd.ps1
param (
    [string]$WorkingDir = ".",
    [string]$EsdFile = "metadata.esd"
)

$ErrorActionPreference = "Stop"

# Create directories
$outputDir = Join-Path $WorkingDir "output"
$tempDir = Join-Path $WorkingDir "temp"
New-Item -ItemType Directory -Force -Path $outputDir, $tempDir | Out-Null

$esdPath = Join-Path $tempDir $EsdFile
$targetFile = "3\Windows\System32\CodeIntegrity\driversipolicy.p7b"

try {
    Write-Host "Extracting driversipolicy.p7b using 7-Zip..."
    $sevenZipPath = "${env:ProgramFiles}\7-Zip\7z.exe"
    
    if (-not (Test-Path $sevenZipPath)) {
        throw "7-Zip is not installed in the default location"
    }

    $extractCmd = "& `"$sevenZipPath`" e `"$esdPath`" `"$targetFile`" -o`"$outputDir`" -y"
    Invoke-Expression $extractCmd
    if ($LASTEXITCODE -ne 0) { throw "7-Zip extraction failed" }

    # Cleanup
    Write-Host "Cleaning up..."
    Remove-Item -Path $esdPath -Force
    
    Write-Host "Process completed successfully!"
}
catch {
    Write-Error "Error: $_"
    exit 1
}