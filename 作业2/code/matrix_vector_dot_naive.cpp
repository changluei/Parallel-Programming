#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <vector>

using namespace std;

namespace {

using Clock = chrono::steady_clock;

volatile double g_sink = 0.0;

#if defined(__GNUC__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

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

NOINLINE void matrixVectorDotNaive(const vector<double> &a, const vector<double> &b, vector<double> &sum, int n) {
    for (int col = 0; col < n; ++col) {
        double value = 0.0;
        for (int row = 0; row < n; ++row) {
            value += b[static_cast<size_t>(row) * n + col] * a[row];
        }
        sum[col] = value;
    }
}

double checksum(const vector<double> &values) {
    return accumulate(values.begin(), values.end(), 0.0);
}

int chooseRepeats(int n) {
    const long long work = max(1LL, 1LL * n * n);
    const long long targetWork = 64LL * 1024 * 1024;
    long long repeats = targetWork / work;
    repeats = max(5LL, repeats);
    repeats = min(2000LL, repeats);
    return static_cast<int>(repeats);
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

} // namespace

int main(int argc, char *argv[]) {
    const int n = argc >= 2 ? max(1, atoi(argv[1])) : 1024;
    const int repeats = argc >= 3 ? max(1, atoi(argv[2])) : chooseRepeats(n);

    vector<double> a = buildInputVector(n);
    vector<double> b = buildMatrix(n);
    vector<double> result(n, 0.0);

    matrixVectorDotNaive(a, b, result, n);
    const double avgMs = benchmark([&]() { matrixVectorDotNaive(a, b, result, n); }, repeats, a, result);
    matrixVectorDotNaive(a, b, result, n);

    cout << "algorithm = naive_column_major" << '\n';
    cout << "n = " << n << '\n';
    cout << "matrix = " << fixed << setprecision(2) << matrixMiB(n) << " MiB" << '\n';
    cout << "repeats = " << repeats << '\n';
    cout << "avg_ms = " << setprecision(6) << avgMs << '\n';
    cout << "checksum = " << setprecision(3) << checksum(result) << '\n';

    if (g_sink == -1.0) {
        cerr << g_sink << '\n';
    }
    return 0;
}
