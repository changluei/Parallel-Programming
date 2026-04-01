#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <vector>

#include "csv_utils.h"

using namespace std;

using Clock = chrono::steady_clock;

const int DEFAULT_REPEATS = 100;

volatile double g_sink = 0.0;

vector<double> buildInputVector(int n) {
    vector<double> a(n);
    for (int i = 0; i < n; ++i) {
        a[i] = 1.0 + (i % 97) * 0.125;
    }
    return a;
}

vector<double> buildMatrix(int n) {
    vector<double> b(static_cast<size_t>(n) * n);
    for (int row = 0; row < n; ++row) {
        size_t offset = static_cast<size_t>(row) * n;
        for (int col = 0; col < n; ++col) {
            b[offset + col] = 0.5 * (row + 1) + 0.25 * ((col % 31) + 1);
        }
    }
    return b;
}

void matrixVectorDotOptimizedUnrolled(const vector<double> &a,
                                      const vector<double> &b,
                                      vector<double> &sum,
                                      int n) {
    fill(sum.begin(), sum.end(), 0.0);
    double *out = sum.data();
    const double *matrix = b.data();

    for (int row = 0; row < n; ++row) {
        const double factor = a[row];
        const double *rowPtr = matrix + static_cast<size_t>(row) * n;

        int col = 0;
        for (; col + 7 < n; col += 8) {
            out[col] += rowPtr[col] * factor;
            out[col + 1] += rowPtr[col + 1] * factor;
            out[col + 2] += rowPtr[col + 2] * factor;
            out[col + 3] += rowPtr[col + 3] * factor;
            out[col + 4] += rowPtr[col + 4] * factor;
            out[col + 5] += rowPtr[col + 5] * factor;
            out[col + 6] += rowPtr[col + 6] * factor;
            out[col + 7] += rowPtr[col + 7] * factor;
        }
        for (; col < n; ++col) {
            out[col] += rowPtr[col] * factor;
        }
    }
}

double checksum(const vector<double> &values) {
    return accumulate(values.begin(), values.end(), 0.0);
}

double matrixMiB(int n) {
    const double bytes = static_cast<double>(n) * n * sizeof(double);
    return bytes / (1024.0 * 1024.0);
}

template <class Func>
double benchmark(Func func, int repeats, vector<double> &input, const vector<double> &output) {
    auto begin = Clock::now();
    double local = 0.0;
    for (int r = 0; r < repeats; ++r) {
        const size_t index = static_cast<size_t>(r) % input.size();
        const double delta = (r & 1) ? 0.0625 : -0.0625;
        input[index] += delta;
        func();
        input[index] -= delta;
        local += output[r % output.size()];
    }
    auto end = Clock::now();
    g_sink += local;
    chrono::duration<double, milli> elapsed = end - begin;
    return elapsed.count() / repeats;
}

int main(int argc, char *argv[]) {
    const int n = argc >= 2 ? max(1, atoi(argv[1])) : 1024;
    const int repeats = argc >= 3 ? max(1, atoi(argv[2])) : DEFAULT_REPEATS;
    const string csvPath = argc >= 4 ? argv[3] : buildDefaultCsvPath("matrix_vector_dot_unrolled", n);

    vector<double> a = buildInputVector(n);
    vector<double> b = buildMatrix(n);
    vector<double> result(n, 0.0);

    matrixVectorDotOptimizedUnrolled(a, b, result, n);
    const double avgMs = benchmark([&]() { matrixVectorDotOptimizedUnrolled(a, b, result, n); }, repeats, a, result);
    matrixVectorDotOptimizedUnrolled(a, b, result, n);
    const double matrixSize = matrixMiB(n);
    const double sumCheck = checksum(result);

    const bool csvOk = appendCsvRow(csvPath,
                                    {"algorithm", "n", "matrix_mib", "repeats", "avg_ms", "checksum"},
                                    {"cache_optimized_row_major_unrolled8",
                                     to_string(n),
                                     formatFixed(matrixSize, 2),
                                     to_string(repeats),
                                     formatFixed(avgMs, 6),
                                     formatFixed(sumCheck, 3)});

    cout << "algorithm = cache_optimized_row_major_unrolled8" << '\n';
    cout << "n = " << n << '\n';
    cout << "matrix = " << fixed << setprecision(2) << matrixSize << " MiB" << '\n';
    cout << "repeats = " << repeats << '\n';
    cout << "avg_ms = " << setprecision(6) << avgMs << '\n';
    cout << "checksum = " << setprecision(3) << sumCheck << '\n';
    cout << "csv_path = " << csvPath << '\n';
    cout << "csv_write = " << (csvOk ? "ok" : "failed") << '\n';

    if (g_sink == -1.0) {
        cerr << g_sink << '\n';
    }
    return 0;
}
