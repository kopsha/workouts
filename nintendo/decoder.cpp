#include <iostream>
#include <iomanip>

using namespace std;

void print(unsigned int arr[], int size) {
    for (int i = 0; i < size; i++) {
        if (i > 0) {
            cout << ' ';
        }
        cout << setfill('0') << setw(8) << hex << arr[i];
    }
    cout << endl;
}


int main() {
    const int size = 2;
    unsigned int a[size];
    unsigned int b[size];

    for (int ai = 0; ai < 16; ai++) {
        std::fill(b, b + size, 0);

        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++) {
                b[(i + j) / 32] ^= ((a[i / 32] >> (i % 32)) &
                    (a[j / 32 + size / 32] >> (j % 32)) & 1) << ((i + j) % 32);
            }

        cout << "--- " << ai << " ---" << endl;
        print(a, size);
        print(a, size);
    }


    return 0;
}

