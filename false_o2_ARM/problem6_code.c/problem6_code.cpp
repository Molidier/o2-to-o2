#include <stdio.h>
#include <stdlib.h>

int *func0(const int numbers[], int size, int delimiter, int *out_size) {
    //               x20        x21 -> x8       x19             x3
    *out_size = size > 0 ? (size * 2) - 1 : 0;
    int *out = (int *)malloc(*out_size * sizeof(int)); //x0 -> return value
    if (size > 0) out[0] = numbers[0];
    for (int i = 1, j = 1; i < size; ++i) {
        out[j++] = delimiter;
        out[j++] = numbers[i];
    }
    return out;
}
