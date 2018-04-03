#include <stdio.h>
#include <stdlib.h>

int comp(const void* a, const void* b) {
    return *(int *) a - *(int *) b;
}
int main() {
    int num = 0;
    scanf("%d", &num);
    int a[100] = {};
    for (int i = 0; i < num; ++i) {
        scanf("%d", &a[i]);
    }
    qsort(a, num, sizeof(a[0]), comp);
    for (int i = 0; i < num; ++i) {
        printf("%d ", a[i]);
    }
    printf("\n");
}
