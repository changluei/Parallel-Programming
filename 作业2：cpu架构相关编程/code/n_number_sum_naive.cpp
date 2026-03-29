#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>

#include "csv_utils.h"

using namespace std;

using Clock = chrono::steady_clock;

volatile double g_sink = 0.0;

vector<double> buildData(int n) {
    vector<double> data(n);
    for (int i = 0; i < n; ++i) {
        data[i] = 0.25 * ((i % 113) + 1);
    }
    return data;
}

double naiveChainSum(const vector<double> &data) {
    double sum = 0.0;
    for (double value : data) {
        sum += value;
    }
    return sum;
}

int chooseRepeats(int n) {
    const long long work = max(1LL, static_cast<long long>(n));
    const long long targetWork = 32LL * 1024 * 1024;
    long long repeats = targetWork / work;
    repeats = max(20LL, repeats);
    repeats = min(100000LL, repeats);
    return static_cast<int>(repeats);
}

template <class Func>
double benchmark(Func func, int repeats, vector<double> &data, double &resultHolder) {
    auto begin = Clock::now();
    double local = 0.0;
    for (int r = 0; r < repeats; ++r) {
        const size_t index = static_cast<size_t>(r) % data.size();
        const double delta = (r & 1) ? 0.125 : -0.125;
        data[index] += delta;
        resultHolder = func();
        data[index] -= delta;
        local += resultHolder;
    }
    auto end = Clock::now();
    g_sink += local;
    chrono::duration<double, milli> elapsed = end - begin;
    return elapsed.count() / repeats;
}

int main(int argc, char *argv[]) {
    const int n = argc >= 2 ? max(1, atoi(argv[1])) : 65536;
    const int repeats = argc >= 3 ? max(1, atoi(argv[2])) : chooseRepeats(n);
    const string csvPath = argc >= 4 ? argv[3] : "n_number_sum_results.csv";

    vector<double> data = buildData(n);
    double result = naiveChainSum(data);
    const double avgMs = benchmark([&]() { return naiveChainSum(data); }, repeats, data, result);
    result = naiveChainSum(data);

    const bool csvOk = appendCsvRow(csvPath,
                                    {"algorithm", "n", "repeats", "avg_ms", "result"},
                                    {"naive_chain",
                                     to_string(n),
                                     to_string(repeats),
                                     formatFixed(avgMs, 6),
                                     formatFixed(result, 3)});

    cout << "algorithm = naive_chain" << '\n';
    cout << "n = " << n << '\n';
    cout << "repeats = " << repeats << '\n';
    cout << "avg_ms = " << fixed << setprecision(6) << avgMs << '\n';
    cout << "result = " << setprecision(3) << result << '\n';
    cout << "csv_path = " << csvPath << '\n';
    cout << "csv_write = " << (csvOk ? "ok" : "failed") << '\n';

    if (g_sink == -1.0) {
        cerr << g_sink << '\n';
    }
    return 0;
}
