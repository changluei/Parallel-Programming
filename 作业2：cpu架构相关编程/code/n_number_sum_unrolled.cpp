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

double unrolledFourWaySum(const vector<double> &data) {
    double sum0 = 0.0;
    double sum1 = 0.0;
    double sum2 = 0.0;
    double sum3 = 0.0;

    int i = 0;
    const int n = static_cast<int>(data.size());
    for (; i + 7 < n; i += 8) {
        sum0 += data[i];
        sum1 += data[i + 1];
        sum2 += data[i + 2];
        sum3 += data[i + 3];
        sum0 += data[i + 4];
        sum1 += data[i + 5];
        sum2 += data[i + 6];
        sum3 += data[i + 7];
    }
    for (; i + 3 < n; i += 4) {
        sum0 += data[i];
        sum1 += data[i + 1];
        sum2 += data[i + 2];
        sum3 += data[i + 3];
    }
    for (; i < n; ++i) {
        sum0 += data[i];
    }
    return (sum0 + sum1) + (sum2 + sum3);
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
    const string csvPath = argc >= 4 ? argv[3] : buildDefaultCsvPath("n_number_sum_unrolled", n);

    vector<double> data = buildData(n);
    double result = unrolledFourWaySum(data);
    const double avgMs = benchmark([&]() { return unrolledFourWaySum(data); }, repeats, data, result);
    result = unrolledFourWaySum(data);

    const bool csvOk = appendCsvRow(csvPath,
                                    {"algorithm", "n", "repeats", "avg_ms", "result"},
                                    {"four_way_unrolled_chain",
                                     to_string(n),
                                     to_string(repeats),
                                     formatFixed(avgMs, 6),
                                     formatFixed(result, 3)});

    cout << "algorithm = four_way_unrolled_chain" << '\n';
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
