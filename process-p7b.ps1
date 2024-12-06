git clone https://github.com/nechyo/WDACTools
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Unrestricted
Import-Module .\WDACTools\WDACTools.psm1
# output/*.p7b 파일을 blacklists/*.xml로 변환하는 스크립트
$inputDirectory = "output"
$outputDirectory = "blacklists"

if (!(Test-Path $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory
}

$p7bFiles = Get-ChildItem -Path $inputDirectory -Filter "*.p7b"

foreach ($file in $p7bFiles) {
    $outputFileName = [System.IO.Path]::ChangeExtension($file.Name, ".xml")
    $outputFilePath = Join-Path -Path $outputDirectory -ChildPath $outputFileName

    try {
        ConvertTo-WDACCodeIntegrityPolicy -BinaryFilePath $file.FullName -XmlFilePath $outputFilePath
        Write-Host "Converted: $($file.FullName) -> $outputFilePath"
    } catch {
        Write-Error "Error converting file: $($file.FullName). $_"
    }
}
