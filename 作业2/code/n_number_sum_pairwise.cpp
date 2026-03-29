#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
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

vector<double> buildData(int n) {
    vector<double> data(n);
    for (int i = 0; i < n; ++i) {
        data[i] = 0.25 * ((i % 113) + 1);
    }
    return data;
}

NOINLINE double pairwiseReductionSum(const vector<double> &input, vector<double> &work) {
    copy(input.begin(), input.end(), work.begin());
    int length = static_cast<int>(input.size());
    while (length > 1) {
        int nextLength = 0;
        int i = 0;
        for (; i + 1 < length; i += 2) {
            work[nextLength++] = work[i] + work[i + 1];
        }
        if (i < length) {
            work[nextLength++] = work[i];
        }
        length = nextLength;
    }
    return work[0];
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

} // namespace

int main(int argc, char *argv[]) {
    const int n = argc >= 2 ? max(1, atoi(argv[1])) : 65536;
    const int repeats = argc >= 3 ? max(1, atoi(argv[2])) : chooseRepeats(n);

    vector<double> data = buildData(n);
    vector<double> work(n, 0.0);
    double result = pairwiseReductionSum(data, work);
    const double avgMs = benchmark([&]() { return pairwiseReductionSum(data, work); }, repeats, data, result);
    result = pairwiseReductionSum(data, work);

    cout << "algorithm = pairwise_reduction" << '\n';
    cout << "n = " << n << '\n';
    cout << "repeats = " << repeats << '\n';
    cout << "avg_ms = " << fixed << setprecision(6) << avgMs << '\n';
    cout << "result = " << setprecision(3) << result << '\n';

    if (g_sink == -1.0) {
        cerr << g_sink << '\n';
    }
    return 0;
}
