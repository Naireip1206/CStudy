# -*- coding: utf-8 -*-
"""answers_c.py —— OJ 第 28~36 题的参考答案与最佳答案

28 文件/EOF 之后进入工程与算法区：EOF 处理、按行读、sscanf、宏、排序查找、
高精度、动态内存、边界调试、标准库综合。
"""

ANSWERS = {
    28: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int x, count = 0;
    long long sum = 0;

    while (scanf("%d", &x) == 1) {   // 返回 1 表示成功读到一个数
        count++;
        sum += x;
    }
    printf("%d %lld\n", count, sum);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int x, count = 0;
    long long sum = 0;

    /* 读到 EOF 时 scanf 返回 EOF(-1)，循环自然退出。
       sum 用 long long：1000 个 10^6 的和是 10^9，
       刚好卡在 int 边界附近，别赌 */
    while (scanf("%d", &x) != EOF) {
        count++;
        sum += x;
    }
    printf("%d %lld\n", count, sum);
    return 0;
}""",
    },
    29: {
        "reference": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char buf[256];
    int lines = 0, maxlen = 0;

    while (fgets(buf, sizeof buf, stdin) != NULL) {   // 读不到就退出
        buf[strcspn(buf, "\n")] = '\0';               // 去掉换行
        int L = (int)strlen(buf);
        lines++;
        if (L > maxlen) maxlen = L;
    }
    printf("%d %d\n", lines, maxlen);
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char buf[256];
    int lines = 0, maxlen = 0;

    /* 用 fgets 返回值当循环条件，比 while(!feof()) 稳：
       feof 要等读失败之后才为真，会多跑一轮 */
    while (fgets(buf, sizeof buf, stdin)) {
        int L = (int)strcspn(buf, "\n");   // 换行位置 = 实际长度
        buf[L] = '\0';
        lines++;
        if (L > maxlen) maxlen = L;
    }
    printf("%d %d\n", lines, maxlen);
    return 0;
}""",
    },
    30: {
        "reference": r"""#include <stdio.h>

int main(void) {
    char s[32];
    int y, m, d;

    scanf("%31s", s);            // 先当字符串读进来
    sscanf(s, "%d-%d-%d", &y, &m, &d);   // 再按格式拆字段

    printf("%d %d %d\n", y, m, d);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int y, m, d;

    /* 格式串里的 - 要原样匹配，%d 自动跳过数字前的空白。
       直接对 stdin 用 scanf 也行，效果一样 */
    if (scanf("%d-%d-%d", &y, &m, &d) != 3) {
        printf("格式不对\n");
        return 1;
    }
    printf("%d %d %d\n", y, m, d);
    return 0;
}""",
    },
    31: {
        "reference": r"""#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))   // 参数和整体都要括号

int main(void) {
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);

    int m = MAX(a, b);
    m = MAX(m, c);
    printf("%d\n", m);
    return 0;
}""",
        "best": r"""#include <stdio.h>

/* 宏是文本替换：MAX(a,b) 展开成 ((a)>(b)?(a):(b))
   不加括号时 MAX(1+2, 3) 会变成 1+2>3?1+2:3，结果错 */
#define MAX(a, b) ((a) > (b) ? (a) : (b))

int main(void) {
    int a, b, c;
    if (scanf("%d %d %d", &a, &b, &c) != 3) return 1;
    printf("%d\n", MAX(MAX(a, b), c));   // 嵌套用，一次算到底
    return 0;
}""",
    },
    32: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i, j, a[1000], x;
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);
    scanf("%d", &x);

    for (i = 0; i < n - 1; i++) {          // 冒泡升序
        for (j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                int t = a[j]; a[j] = a[j + 1]; a[j + 1] = t;
            }
        }
    }
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');

    int left = 0, right = n - 1, pos = -1;
    while (left <= right) {                // 二分查找
        int mid = left + (right - left) / 2;
        if (a[mid] == x) { pos = mid; break; }
        if (a[mid] < x) left = mid + 1;
        else            right = mid - 1;
    }
    printf("%d\n", pos);
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <stdlib.h>

int cmp_int(const void *a, const void *b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);          // 返回 -1/0/1，避免相减溢出
}

int main(void) {
    int n, i, a[1000], x;
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);
    scanf("%d", &x);

    qsort(a, (size_t)n, sizeof a[0], cmp_int);
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');

    /* 二分：手写循环，注意 left <= right（= 时还要再比一次） */
    int lo = 0, hi = n - 1, pos = -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == x) { pos = mid; break; }
        if (a[mid] < x) lo = mid + 1;
        else            hi = mid - 1;
    }
    printf("%d\n", pos);
    return 0;
}""",
    },
    33: {
        "reference": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char a[105], b[105];
    int x[105] = {0}, y[105] = {0}, z[110] = {0};
    int i, la, lb, L;

    scanf("%104s %104s", a, b);
    la = (int)strlen(a);
    lb = (int)strlen(b);

    for (i = 0; i < la; i++) x[i] = a[la - 1 - i] - '0';   // 低位存在前面
    for (i = 0; i < lb; i++) y[i] = b[lb - 1 - i] - '0';

    L = la > lb ? la : lb;
    for (i = 0; i < L; i++) {
        z[i] += x[i] + y[i];
        z[i + 1] = z[i] / 10;
        z[i] %= 10;
    }
    if (z[L]) L++;

    for (i = L - 1; i >= 0; i--) putchar('0' + z[i]);
    putchar('\n');
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char a[105], b[105];
    int x[110] = {0}, y[110] = {0};
    scanf("%104s %104s", a, b);

    /* 直接倒序存进 int 数组：a 的最低位放进 x[0] */
    int la = (int)strlen(a), lb = (int)strlen(b);
    for (int i = 0; i < la; i++) x[i] = a[la - 1 - i] - '0';
    for (int i = 0; i < lb; i++) y[i] = b[lb - 1 - i] - '0';

    /* 边加边进位，把结果写回 x（省一个数组） */
    int L = la > lb ? la : lb;
    for (int i = 0; i < L; i++) {
        x[i] += y[i];
        if (x[i] >= 10) { x[i] -= 10; x[i + 1]++; }
    }
    if (x[L]) L++;                     // 最高位进位了

    for (int i = L - 1; i >= 0; i--) putchar('0' + x[i]);
    putchar('\n');
    return 0;
}""",
    },
    34: {
        "reference": r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n, i;
    scanf("%d", &n);

    int *a = (int*)malloc((size_t)n * sizeof(int));
    if (a == NULL) return 1;           // 申请失败

    long long sum = 0;
    for (i = 0; i < n; i++) {
        scanf("%d", &a[i]);
        sum += a[i];
    }
    printf("%lld\n", sum);

    free(a);                          // 用完释放
    a = NULL;
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) return 1;

    /* 边读边加，其实不用存整份数组；
       这里仍申请了，是为了演示 malloc/free 的正确姿势 */
    int *a = (int*)malloc((size_t)n * sizeof *a);
    if (!a) return 1;

    long long sum = 0;
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
        sum += a[i];
    }
    printf("%lld\n", sum);

    free(a);
    a = NULL;                          // 释放后立刻置空，防止悬垂指针
    return 0;
}""",
    },
    35: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    int mx = a[0], mi = 0;
    for (i = 1; i < n; i++) {
        if (a[i] > mx) {          // 严格大于：并列时保留第一次出现的下标
            mx = a[i];
            mi = i;
        }
    }
    printf("%d %d\n", mx, mi);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int n, x, i;
    scanf("%d", &n);

    /* 不用数组：读一个比一个，省内存也省一次遍历 */
    int mx = 0, mi = 0;
    for (i = 0; i < n; i++) {
        scanf("%d", &x);
        if (i == 0 || x > mx) { mx = x; mi = i; }
    }
    printf("%d %d\n", mx, mi);
    return 0;
}""",
    },
    36: {
        "reference": r"""#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int cmp_up(const void *a, const void *b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}

int main(void) {
    int n, i, a[1000];
    scanf("%d", &n);
    long long sum = 0;
    for (i = 0; i < n; i++) {
        scanf("%d", &a[i]);
        sum += a[i];
    }

    qsort(a, (size_t)n, sizeof a[0], cmp_up);
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');

    double avg = (double)sum / n;
    printf("%.2f\n", avg);
    printf("%.2f\n", sqrt(avg));
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* 比较函数返回 -1/0/1 而不是 a-b：a-b 在极小整数相减时会溢出 */
int cmp_up(const void *a, const void *b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}

int main(void) {
    int n, i, a[1000];
    if (scanf("%d", &n) != 1 || n <= 0) return 1;

    long long sum = 0;
    for (i = 0; i < n; i++) { scanf("%d", &a[i]); sum += a[i]; }

    qsort(a, (size_t)n, sizeof a[0], cmp_up);   /* 标准库排序 */
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');

    double avg = (double)sum / n;               /* 先转 double 再除 */
    printf("%.2f\n%.2f\n", avg, sqrt(avg));     /* math.h 的 sqrt */
    return 0;
}""",
    },
}
