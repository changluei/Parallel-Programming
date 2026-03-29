#ifndef CSV_UTILS_H
#define CSV_UTILS_H

#include <direct.h>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

inline string formatFixed(double value, int precision) {
    ostringstream out;
    out << fixed << setprecision(precision) << value;
    return out.str();
}

inline string escapeCsvField(const string &field) {
    bool needQuotes = false;
    for (char ch : field) {
        if (ch == '"' || ch == ',' || ch == '\n' || ch == '\r') {
            needQuotes = true;
            break;
        }
    }

    if (!needQuotes) {
        return field;
    }

    string escaped = "\"";
    for (char ch : field) {
        if (ch == '"') {
            escaped += "\"\"";
        } else {
            escaped += ch;
        }
    }
    escaped += "\"";
    return escaped;
}

inline void createDirectoriesForPath(const string &path) {
    string current;
    size_t start = 0;

    if (path.size() >= 2 && path[1] == ':') {
        current = path.substr(0, 2);
        start = 2;
    }

    for (size_t i = start; i < path.size(); ++i) {
        current += path[i];
        if (path[i] == '/' || path[i] == '\\') {
            string dir = current.substr(0, current.size() - 1);
            if (!dir.empty()) {
                _mkdir(dir.c_str());
            }
        }
    }
}

inline string buildDefaultCsvPath(const string &prefix, int n) {
    const string resultsDir = "results";
    _mkdir(resultsDir.c_str());
    return resultsDir + "\\" + prefix + "_n" + to_string(n) + ".csv";
}

inline bool csvFileHasContent(const string &path) {
    ifstream input(path, ios::binary);
    return input && input.peek() != ifstream::traits_type::eof();
}

inline void writeCsvLine(ofstream &output, const vector<string> &fields) {
    for (size_t i = 0; i < fields.size(); ++i) {
        if (i != 0) {
            output << ',';
        }
        output << escapeCsvField(fields[i]);
    }
    output << '\n';
}

inline bool appendCsvRow(const string &path, const vector<string> &header, const vector<string> &row) {
    createDirectoriesForPath(path);

    const bool needHeader = !csvFileHasContent(path);
    ofstream output(path, ios::app);
    if (!output) {
        return false;
    }

    if (needHeader) {
        writeCsvLine(output, header);
    }
    writeCsvLine(output, row);
    return true;
}

#endif
