$linuxIp = "192.168.3.113"
$port = 8080
$targetDir = "D:\Omega_frames\v63_subset_l1_shadow_w1\host=windows1"

Write-Output "Starting High-Speed HTTP Download from $linuxIp..."

# List of all files we want to ensure are downloaded
$filesToDownload = @(
    "20250106_fbd5c8b.parquet", "20250107_fbd5c8b.parquet", "20250108_fbd5c8b.parquet", "20250109_fbd5c8b.parquet",
    "20250110_fbd5c8b.parquet", "20250113_fbd5c8b.parquet", "20250114_fbd5c8b.parquet", "20250115_fbd5c8b.parquet",
    "20250116_fbd5c8b.parquet", "20250117_fbd5c8b.parquet", "20250120_fbd5c8b.parquet", "20250121_fbd5c8b.parquet",
    "20250122_fbd5c8b.parquet", "20250123_fbd5c8b.parquet", "20250124_fbd5c8b.parquet", "20250127_fbd5c8b.parquet",
    "20250205_fbd5c8b.parquet", "20250206_fbd5c8b.parquet", "20250207_fbd5c8b.parquet", "20250210_fbd5c8b.parquet",
    "20250211_fbd5c8b.parquet", "20250212_fbd5c8b.parquet", "20250213_fbd5c8b.parquet", "20250214_fbd5c8b.parquet",
    "20250217_fbd5c8b.parquet", "20250218_fbd5c8b.parquet", "20250219_fbd5c8b.parquet", "20250220_fbd5c8b.parquet",
    "20250221_fbd5c8b.parquet", "20250224_fbd5c8b.parquet", "20250225_fbd5c8b.parquet", "20250226_fbd5c8b.parquet",
    "20250227_fbd5c8b.parquet", "20250228_fbd5c8b.parquet", "20250303_fbd5c8b.parquet", "20250304_fbd5c8b.parquet",
    "20250305_fbd5c8b.parquet", "20250306_fbd5c8b.parquet", "20250307_fbd5c8b.parquet", "20250310_fbd5c8b.parquet",
    "20250311_fbd5c8b.parquet", "20250312_fbd5c8b.parquet", "20250313_fbd5c8b.parquet", "20250314_fbd5c8b.parquet",
    "20250630_fbd5c8b.parquet", "20250701_fbd5c8b.parquet", "20250702_fbd5c8b.parquet", "20250703_fbd5c8b.parquet",
    "20250704_fbd5c8b.parquet", "20250707_fbd5c8b.parquet", "20250708_fbd5c8b.parquet", "20250709_fbd5c8b.parquet",
    "20250710_fbd5c8b.parquet", "20250711_fbd5c8b.parquet", "20250714_fbd5c8b.parquet", "20250715_fbd5c8b.parquet",
    "20250716_fbd5c8b.parquet", "20250717_fbd5c8b.parquet", "20250718_fbd5c8b.parquet", "20250723_fbd5c8b.parquet",
    "20251029_fbd5c8b.parquet"
)

# Skip files that are already fully transferred (based on our previous observation of the first few successful files)
$skipFiles = @("20250106_fbd5c8b.parquet", "20250107_fbd5c8b.parquet", "20250108_fbd5c8b.parquet", "20250109_fbd5c8b.parquet", "20250110_fbd5c8b.parquet", "20250113_fbd5c8b.parquet")

foreach ($file in $filesToDownload) {
    if ($skipFiles -contains $file) {
        Write-Output "Skipping $file (already verified)"
        continue
    }

    $url = "http://${linuxIp}:${port}/$file"
    $dest = Join-Path -Path $targetDir -ChildPath $file
    
    Write-Output "Downloading $file..."
    # We use Invoke-WebRequest which is native and generally fast on modern PS, 
    # but we will wrap it to catch any 404s if a file isn't ready on Linux yet
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        Write-Output "Successfully downloaded $file"
    } catch {
        Write-Output "Failed to download $file - $_"
    }
}
Write-Output "All downloads completed."
