param(
    [string]$Compiler = "g++"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

$commonFlags = @(
    "-std=c++17",
    "-O3",
    "-g",
    "-fno-omit-frame-pointer",
    "-march=native",
    "-DNDEBUG",
    "-Wall",
    "-Wextra"
)

$targets = @(
    @{ Source = "matrix_vector_dot_naive.cpp"; Output = "matrix_vector_dot_naive.exe" },
    @{ Source = "matrix_vector_dot_optimized.cpp"; Output = "matrix_vector_dot_optimized.exe" },
    @{ Source = "matrix_vector_dot_optimized_unrolled.cpp"; Output = "matrix_vector_dot_optimized_unrolled.exe" },
    @{ Source = "n_number_sum_naive.cpp"; Output = "n_number_sum_naive.exe" },
    @{ Source = "n_number_sum_two_way.cpp"; Output = "n_number_sum_two_way.exe" },
    @{ Source = "n_number_sum_unrolled.cpp"; Output = "n_number_sum_unrolled.exe" },
    @{ Source = "n_number_sum_pairwise.cpp"; Output = "n_number_sum_pairwise.exe" }
)

foreach ($target in $targets) {
    Write-Host "Building $($target.Output)..."
    & $Compiler @commonFlags $target.Source "-o" $target.Output
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed for $($target.Source)"
    }
}

Write-Host "Build finished with profiling-friendly flags:"
Write-Host ($commonFlags -join " ")
