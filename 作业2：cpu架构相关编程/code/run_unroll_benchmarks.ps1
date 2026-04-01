param(
    [switch]$MatrixOnly,
    [switch]$SumOnly
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
$resultsRoot = Join-Path $projectRoot "results\unroll_compare_series"

New-Item -ItemType Directory -Force -Path $resultsRoot | Out-Null
Set-Location $scriptRoot

$runMatrix = -not $SumOnly
$runSum = -not $MatrixOnly

if ($runMatrix) {
    $matrixCases = @(
        @{ N = 256; Repeats = 4000 },
        @{ N = 1024; Repeats = 500 },
        @{ N = 1536; Repeats = 250 },
        @{ N = 1792; Repeats = 150 },
        @{ N = 2048; Repeats = 100 }
    )

    foreach ($case in $matrixCases) {
        $baseCsv = Join-Path $resultsRoot ("matrix_vector_dot_n{0}.csv" -f $case.N)
        Write-Host "Running matrix optimized baseline n=$($case.N)..."
        & ".\matrix_vector_dot_optimized.exe" $case.N $case.Repeats $baseCsv
        if ($LASTEXITCODE -ne 0) {
            throw "Matrix optimized baseline failed for n=$($case.N)"
        }

        Write-Host "Running matrix unrolled n=$($case.N)..."
        & ".\matrix_vector_dot_optimized_unrolled.exe" $case.N $case.Repeats $baseCsv
        if ($LASTEXITCODE -ne 0) {
            throw "Matrix unrolled failed for n=$($case.N)"
        }
    }
}

if ($runSum) {
    $sumSizes = @(1024, 2048, 4096, 8192, 16384)
    foreach ($n in $sumSizes) {
        $csvPath = Join-Path $resultsRoot ("n_number_sum_n{0}.csv" -f $n)
        Write-Host "Running sum two-way baseline n=$n..."
        & ".\n_number_sum_two_way.exe" $n 1000 $csvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Two-way sum failed for n=$n"
        }

        Write-Host "Running sum unrolled n=$n..."
        & ".\n_number_sum_unrolled.exe" $n 1000 $csvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Unrolled sum failed for n=$n"
        }
    }
}

Write-Host "Benchmark run finished. Results saved to $resultsRoot"
