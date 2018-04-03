#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int main() {
    srand(time(0));
    int num = rand() % 10 + 1;
    printf("%d\n", num);
    for (int i = 0; i < num; ++i) {
        printf("%d ", rand() % 100);
    }
}