#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int x = 5;
    int y = 10;
    
    int sum = add(x, y);

    printf("The sum of %d and %d is %d\n", x, y, sum);

    return 0;
}
