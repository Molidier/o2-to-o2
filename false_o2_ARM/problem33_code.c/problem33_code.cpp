#include <stdio.h>
#include <math.h>

double func0(const double *xs, int size) {
    double ans = 0.0;
    double value, driv, x_pow;
    int i;

    value = xs[0];
    for (i = 1; i < size; i++) {
        x_pow = 1.0;
        for (int j = 0; j < i; j++) {
            x_pow *= ans;
        }
        value += xs[i] * x_pow;
    }

    while (fabs(value) > 1e-6) {
        driv = 0.0;
        for (i = 1; i < size; i++) {
            x_pow = 1.0;
            for (int j = 1; j < i; j++) {
                x_pow *= ans;
            }
            driv += i * xs[i] * x_pow;
        }
        ans = ans - value / driv;

        value = xs[0];
        for (i = 1; i < size; i++) {
            x_pow = 1.0;
            for (int j = 0; j < i; j++) {
                x_pow *= ans;
            }
            value += xs[i] * x_pow;
        }
    }

    return ans;
}
