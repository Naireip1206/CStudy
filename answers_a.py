# -*- coding: utf-8 -*-
"""answers_a.py —— OJ 第 1~14 题的参考答案（reference）与最佳答案（best）

reference：朴素、直白、好懂，对应课程里刚学的写法
best：更短或更省（公式/指针/静态变量等），注释说明改进点
两个都是真跑过样例的，改了请跑 python verify_oj.py
"""

ANSWERS = {
    1: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);      // 读入两个整数
    printf("%d\n", a + b);       // 输出和
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) return 1;   // 检查输入是否合法
    printf("%d\n", a + b);
    return 0;
}""",
    },
    2: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int c;
    scanf("%d", &c);
    double f = c * 9.0 / 5.0 + 32;   // 9.0 保证是小数除法
    printf("%.1f\n", f);             // 保留 1 位小数
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int c;
    if (scanf("%d", &c) != 1) return 1;
    /* 直接算：c * 9.0 / 5 + 32，省掉中间变量；
       写成 9 / 5 会得到 1，结果就错了 */
    printf("%.1f\n", c * 9.0 / 5 + 32);
    return 0;
}""",
    },
    3: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);

    int q = a / b;               // 整数商
    int r = a % b;               // 余数
    double d = (double)a / b;    // 真实商：先强转成小数

    printf("%d %d %.2f\n", q, r, d);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    /* 一行输出三个值，注意 (double) 只作用于 a，
       写成 (double)(a / b) 会先把整数除法算完再转换，结果没有小数 */
    printf("%d %d %.2f\n", a / b, a % b, (double)a / b);
    return 0;
}""",
    },
    4: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i;
    char c;
    scanf("%d %c", &n, &c);      // %c 前面的空格：跳过数字后的空白

    for (i = 0; i < n; i++) {
        putchar(c);              // 逐个输出字符
    }
    putchar('\n');
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int n;
    char c;
    if (scanf("%d %c", &n, &c) != 2) return 1;
    while (n-- > 0) putchar(c);  // 边减边输出，省掉循环变量
    putchar('\n');
    return 0;
}""",
    },
    5: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int y;
    scanf("%d", &y);

    int leap;
    if (y % 400 == 0) {
        leap = 1;
    } else if (y % 100 == 0) {
        leap = 0;
    } else if (y % 4 == 0) {
        leap = 1;
    } else {
        leap = 0;
    }

    printf("%s\n", leap ? "yes" : "no");
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int y;
    scanf("%d", &y);
    /* 一个表达式搞定：能被 4 整除且不能被 100 整除，或者能被 400 整除
       注意 || 和 && 的优先级，括号别省 */
    int leap = (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
    printf("%s\n", leap ? "yes" : "no");
    return 0;
}""",
    },
    6: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int a, b;
    char op;
    scanf("%d %c %d", &a, &op, &b);

    switch (op) {
        case '+': printf("%d\n", a + b); break;
        case '-': printf("%d\n", a - b); break;
        case '*': printf("%d\n", a * b); break;
        case '/': printf("%d\n", a / b); break;   // 题目保证能整除
        default:  printf("error\n");
    }
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int a, b;
    char op;
    if (scanf("%d %c %d", &a, &op, &b) != 3) return 1;

    /* 每个分支只有一条语句，仍建议保留 break：
       漏一个 break 会继续执行下一个分支，而且不报错 */
    switch (op) {
        case '+': printf("%d\n", a + b); break;
        case '-': printf("%d\n", a - b); break;
        case '*': printf("%d\n", a * b); break;
        case '/': printf("%d\n", b ? a / b : 0); break;
        default:  printf("error\n");
    }
    return 0;
}""",
    },
    7: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i;
    long long sum = 0;              // n 到 10 万时和是 50 亿，int 装不下，必须 long long
    scanf("%d", &n);

    for (i = 1; i <= n; i++) {
        sum += i;
    }
    printf("%lld\n", sum);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int n;
    scanf("%d", &n);
    /* 等差数列公式：1+...+n = n*(n+1)/2，O(1) 搞定
       注意先乘后除，且要转 long long 防溢出 */
    long long ans = (long long)n * (n + 1) / 2;
    printf("%lld\n", ans);
    return 0;
}""",
    },
    8: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int a, b, t;
    scanf("%d %d", &a, &b);

    while (b != 0) {          // 辗转相除：a 存余数，b 存上一个余数
        t = a % b;
        a = b;
        b = t;
    }
    printf("%d\n", a);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int gcd(int a, int b) {        // 递归版：出口是 b == 0
    return b == 0 ? a : gcd(b, a % b);
}

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\n", gcd(a, b));
    return 0;
}""",
    },
    9: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i;
    int a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }

    for (i = n - 1; i >= 0; i--) {   // 从最后一个元素往前输出
        printf("%d", a[i]);
        if (i > 0) printf(" ");
    }
    printf("\n");
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    /* 用指针倒着走，等价于 a[n-1-i] 的写法 */
    int *p = a + n - 1;
    for (i = 0; i < n; i++) {
        printf("%d%s", p[-i], i == n - 1 ? "\n" : " ");
    }
    return 0;
}""",
    },
    10: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int m, n, i, j;
    int a[10][10];

    scanf("%d %d", &m, &n);
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            scanf("%d", &a[i][j]);
        }
    }

    for (j = 0; j < n; j++) {       // 输出时行列互换
        for (i = 0; i < m; i++) {
            printf("%d", a[i][j]);
            if (i < m - 1) printf(" ");
        }
        printf("\n");
    }
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int m, n, i, j, a[10][10];
    scanf("%d %d", &m, &n);
    for (i = 0; i < m; i++)
        for (j = 0; j < n; j++)
            scanf("%d", &a[i][j]);

    /* 转置的本质就是输出 a[j][i]：
       外层走原矩阵的列，内层走原矩阵的行 */
    for (j = 0; j < n; j++) {
        for (i = 0; i < m; i++)
            printf("%d%c", a[i][j], i == m - 1 ? '\n' : ' ');
    }
    return 0;
}""",
    },
    11: {
        "reference": r"""#include <stdio.h>

int main(void) {
    char s[105];
    int i, count = 0;

    scanf("%s", s);             // 不含空格，直接读
    for (i = 0; s[i] != '\0'; i++) {
        if (s[i] >= 'a' && s[i] <= 'z') count++;
    }
    printf("%d\n", count);
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <ctype.h>              // islower 在这里

int main(void) {
    char s[105];
    int i, count = 0;
    scanf("%104s", s);          // 限宽防止越界

    for (i = 0; s[i]; i++)      // s[i] 非 0 就继续
        if (islower((unsigned char)s[i])) count++;

    printf("%d\n", count);
    return 0;
}""",
    },
    12: {
        "reference": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char s[105];
    scanf("%s", s);

    int L = (int)strlen(s);
    int i, ok = 1;
    for (i = 0; i < L / 2; i++) {
        if (s[i] != s[L - 1 - i]) {   // 首尾对比
            ok = 0;
            break;
        }
    }
    printf("%s\n", ok ? "yes" : "no");
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char s[105];
    scanf("%104s", s);

    /* 双指针向中间夹：i 从头、j 从尾，碰到不相等就停 */
    int i = 0, j = (int)strlen(s) - 1, ok = 1;
    while (i < j) {
        if (s[i] != s[j]) { ok = 0; break; }
        i++; j--;
    }
    printf("%s\n", ok ? "yes" : "no");
    return 0;
}""",
    },
    13: {
        "reference": r"""#include <stdio.h>

int is_prime(int n) {               // 是素数返回 1
    int i;
    if (n < 2) return 0;
    for (i = 2; i * i <= n; i++) {  // 只试到根号 n
        if (n % i == 0) return 0;
    }
    return 1;
}

int main(void) {
    int n, i, count = 0;
    scanf("%d", &n);

    for (i = 2; i <= n; i++)
        if (is_prime(i)) count++;
    printf("%d\n", count);

    int first = 1;
    for (i = 2; i <= n; i++) {
        if (is_prime(i)) {
            if (!first) printf(" ");
            printf("%d", i);
            first = 0;
        }
    }
    printf("\n");
    return 0;
}""",
        "best": r"""#include <stdio.h>

#define MAXN 10005
int flag[MAXN];                     // 0 表示还是素数，1 表示被筛掉

int main(void) {
    int n, i, j, count = 0;
    scanf("%d", &n);

    /* 埃氏筛：i 是素数就把它的倍数全标记成合数，
       复杂度 O(n log log n)，比逐个判断快得多 */
    for (i = 2; i <= n; i++) {
        if (!flag[i]) {
            count++;
            for (j = i * 2; j <= n; j += i) flag[j] = 1;
        }
    }
    printf("%d\n", count);

    int first = 1;
    for (i = 2; i <= n; i++) {
        if (!flag[i]) {
            if (!first) printf(" ");
            printf("%d", i);
            first = 0;
        }
    }
    printf("\n");
    return 0;
}""",
    },
    14: {
        "reference": r"""#include <stdio.h>

int next_fib(void) {
    static int a = 1, b = 1;        // 只初始化一次，跨调用保留
    int v = a;
    int t = a + b;
    a = b;
    b = t;
    return v;
}

int main(void) {
    int n, i;
    scanf("%d", &n);

    for (i = 0; i < n; i++) {
        printf("%d", next_fib());
        if (i < n - 1) printf(" ");
    }
    printf("\n");
    return 0;
}""",
        "best": r"""#include <stdio.h>

int next_fib(void) {
    /* 用两个静态变量滚动：a 是当前项，b 是下一项
       若把 static 去掉，每次调用都从 1 开始，输出就全错了 */
    static int a = 1, b = 1;
    int v = a;
    a = b;
    b = v + b;
    return v;
}

int main(void) {
    int n;
    scanf("%d", &n);
    while (n-- > 0) printf("%d%c", next_fib(), n ? ' ' : '\n');
    return 0;
}""",
    },
}
