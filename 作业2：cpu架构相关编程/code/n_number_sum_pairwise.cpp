#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>

#include "csv_utils.h"

using namespace std;

using Clock = chrono::steady_clock;

const int DEFAULT_REPEATS = 100;

volatile double g_sink = 0.0;

vector<double> buildData(int n) {
    vector<double> data(n);
    for (int i = 0; i < n; ++i) {
        data[i] = 0.25 * ((i % 113) + 1);
    }
    return data;
}

double pairwiseReductionSum(const vector<double> &input, vector<double> &work) {
    copy(input.begin(), input.end(), work.begin());
    for (int m = static_cast<int>(input.size()); m > 1; m /= 2) {
        for (int i = 0; i < m / 2; ++i) {
            work[i] = work[i * 2] + work[i * 2 + 1];
        }
    }
    return work[0];
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
    const int repeats = argc >= 3 ? max(1, atoi(argv[2])) : DEFAULT_REPEATS;
    const string csvPath = argc >= 4 ? argv[3] : buildDefaultCsvPath("n_number_sum", n);

    vector<double> data = buildData(n);
    vector<double> work(n, 0.0);
    double result = pairwiseReductionSum(data, work);
    const double avgMs = benchmark([&]() { return pairwiseReductionSum(data, work); }, repeats, data, result);
    result = pairwiseReductionSum(data, work);

    const bool csvOk = appendCsvRow(csvPath,
                                    {"algorithm", "n", "repeats", "avg_ms", "result"},
                                    {"pairwise_reduction",
                                     to_string(n),
                                     to_string(repeats),
                                     formatFixed(avgMs, 6),
                                     formatFixed(result, 3)});

    cout << "algorithm = pairwise_reduction" << '\n';
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
