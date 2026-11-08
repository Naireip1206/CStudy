# -*- coding: utf-8 -*-
"""answers_b.py —— OJ 第 15~27 题的参考答案（reference）与最佳答案（best）

写法约定同 answers_a.py：reference 直白、best 精简或更高效。
"""

ANSWERS = {
    15: {
        "reference": r"""#include <stdio.h>

long long sum_array(int a[], int n) {     // 数组参数 + 长度参数
    long long s = 0;
    int i;
    for (i = 0; i < n; i++) s += a[i];
    return s;
}

double average(int a[], int n) {
    return (double)sum_array(a, n) / n;   // 复用求和函数
}

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    printf("%lld %.2f\n", sum_array(a, n), average(a, n));
    return 0;
}""",
        "best": r"""#include <stdio.h>

/* 函数里 sizeof(a) 只是指针大小，
   所以长度必须由调用方传进来 —— 这是数组参数的核心 */
long long sum_array(int *a, int n) {
    long long s = 0;
    while (n-- > 0) s += *a++;            // 指针一路往后走
    return s;
}

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    long long s = sum_array(a, n);
    printf("%lld %.2f\n", s, (double)s / n);
    return 0;
}""",
    },
    16: {
        "reference": r"""#include <stdio.h>

long long fact(int n) {
    if (n <= 1) return 1;          // 出口：0! 和 1! 都是 1
    return (long long)n * fact(n - 1);   // 递推：n! = n * (n-1)!
}

int main(void) {
    int n;
    scanf("%d", &n);
    printf("%lld\n", fact(n));
    return 0;
}""",
        "best": r"""#include <stdio.h>

long long fact(int n) {
    /* 递归三要素：出口、递推、向出口靠近
       20! = 2432902008176640000，正好是 long long 装得下的极限 */
    return n <= 1 ? 1 : (long long)n * fact(n - 1);
}

int main(void) {
    int n;
    scanf("%d", &n);
    printf("%lld\n", fact(n));
    return 0;
}""",
    },
    17: {
        "reference": r"""#include <stdio.h>

void swap(int *a, int *b) {        // 形参是地址
    int t = *a;
    *a = *b;
    *b = t;
}

int main(void) {
    int x, y;
    scanf("%d %d", &x, &y);
    swap(&x, &y);                  // 传地址，才能改到外面的变量
    printf("%d %d\n", x, y);
    return 0;
}""",
        "best": r"""#include <stdio.h>

/* 如果写成 swap(int a, int b)，交换的只是副本，外面不会变。
   这是理解指针最重要的一步。 */
void swap(int *a, int *b) {
    int t = *a; *a = *b; *b = t;
}

int main(void) {
    int x, y;
    if (scanf("%d %d", &x, &y) != 2) return 1;
    swap(&x, &y);
    printf("%d %d\n", x, y);
    return 0;
}""",
    },
    18: {
        "reference": r"""#include <stdio.h>

int main(void) {
    int n, i, a[100];
    int *p;
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    int mx = a[0], mn = a[0];
    for (p = a; p < a + n; p++) {     // 指针遍历
        if (*p > mx) mx = *p;
        if (*p < mn) mn = *p;
    }
    printf("%d %d\n", mx, mn);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    /* *(a+i) 与 a[i] 完全等价，这里用指针偏移演示
       mx/mn 初值取第一个元素，全部是负数时才不会出错 */
    int mx = a[0], mn = a[0];
    for (i = 1; i < n; i++) {
        int v = *(a + i);
        if (v > mx) mx = v;
        if (v < mn) mn = v;
    }
    printf("%d %d\n", mx, mn);
    return 0;
}""",
    },
    19: {
        "reference": r"""#include <stdio.h>

int main(void) {
    char s[105];
    char *p;
    scanf("%104s", s);

    int len = 0;
    for (p = s; *p != '\0'; p++) len++;   // 指针版 strlen

    /* 原地反转：首尾交换 */
    int i;
    for (i = 0; i < len / 2; i++) {
        char t = s[i];
        s[i] = s[len - 1 - i];
        s[len - 1 - i] = t;
    }
    printf("%d %s\n", len, s);
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    char s[105], *p = s, *q, t;
    scanf("%104s", s);

    while (*p) p++;                 // p 走到 '\0'，此时 p - s 就是长度
    int len = (int)(p - s);

    /* 双指针交换：p 退到最后一个字符，和 s 一起往中间夹 */
    for (q = s, p--; q < p; q++, p--) {
        t = *q; *q = *p; *p = t;
    }
    printf("%d %s\n", len, s);
    return 0;
}""",
    },
    20: {
        "reference": r"""#include <stdio.h>

void swap(int *a, int *b) {
    int t = *a; *a = *b; *b = t;
}

int main(void) {
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);

    if (a > b) swap(&a, &b);       // 三步冒泡：先把最大的换到最后
    if (b > c) swap(&b, &c);
    if (a > b) swap(&a, &b);

    printf("%d %d %d\n", a, b, c);
    return 0;
}""",
        "best": r"""#include <stdio.h>

void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

int main(void) {
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);

    /* 三个数只需三次比较，顺序是：a,b → b,c → a,b
       这就是冒泡排序 n=3 的全部过程 */
    if (a > b) swap(&a, &b);
    if (b > c) swap(&b, &c);
    if (a > b) swap(&a, &b);

    printf("%d %d %d\n", a, b, c);
    return 0;
}""",
    },
    21: {
        "reference": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    int n, i, j;
    char buf[20][35];              // 真正存字符的地方
    char *w[20];                   // 指针数组，排序时只动这里
    scanf("%d", &n);

    for (i = 0; i < n; i++) {
        scanf("%s", buf[i]);
        w[i] = buf[i];             // 指针指向各自的缓冲区
    }

    for (i = 0; i < n - 1; i++) {          // 冒泡排序
        for (j = 0; j < n - 1 - i; j++) {
            if (strcmp(w[j], w[j + 1]) > 0) {
                char *t = w[j];            // 只交换指针
                w[j] = w[j + 1];
                w[j + 1] = t;
            }
        }
    }

    for (i = 0; i < n; i++) printf("%s\n", w[i]);
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    int n, i, j;
    char buf[20][35];
    char *w[20];
    scanf("%d", &n);
    for (i = 0; i < n; i++) { scanf("%s", buf[i]); w[i] = buf[i]; }

    /* w 是指针数组：交换 8 字节的指针，比搬 35 字节的字符串快 */
    for (i = 1; i < n; i++) {                     // 插入排序，已读入的前 i 个有序
        char *key = w[i];
        for (j = i - 1; j >= 0 && strcmp(w[j], key) > 0; j--)
            w[j + 1] = w[j];
        w[j + 1] = key;
    }

    for (i = 0; i < n; i++) puts(w[i]);
    return 0;
}""",
    },
    22: {
        "reference": r"""#include <stdio.h>
#include <stdlib.h>

int cmp_desc(const void *a, const void *b) {
    int x = *(const int*)a;
    int y = *(const int*)b;
    return y - x;                  // b - a 就是降序
}

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    qsort(a, n, sizeof(int), cmp_desc);   // 传函数指针作比较器
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <stdlib.h>

int cmp_desc(const void *a, const void *b) {
    /* qsort 的比较函数：返回 <0 表示 a 排在 b 前面
       这里 return y - x，把大的排前面，就是降序 */
    return *(const int*)b - *(const int*)a;
}

int main(void) {
    int n, i, a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);

    qsort(a, (size_t)n, sizeof a[0], cmp_desc);
    for (i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');
    return 0;
}""",
    },
    23: {
        "reference": r"""#include <stdio.h>

typedef struct {
    char name[35];
    int  score;
} Student;

int main(void) {
    int n, i;
    Student a[100];
    scanf("%d", &n);

    for (i = 0; i < n; i++) {
        scanf("%s %d", a[i].name, &a[i].score);
    }

    int best = 0;                       // 记录最高分下标
    for (i = 1; i < n; i++) {
        if (a[i].score > a[best].score) best = i;   // 严格大于：并列保留先出现的
    }
    printf("%s\n", a[best].name);
    return 0;
}""",
        "best": r"""#include <stdio.h>

typedef struct { char name[35]; int score; } Student;

int main(void) {
    int n, i;
    Student a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) scanf("%s %d", a[i].name, &a[i].score);

    /* 用结构体指针找最大：省掉下标来回写 a[best] */
    Student *p = a, *top = a;
    for (i = 1, p = a + 1; i < n; i++, p++)
        if (p->score > top->score) top = p;

    puts(top->name);
    return 0;
}""",
    },
    24: {
        "reference": r"""#include <stdio.h>

typedef struct {
    char name[35];
    int  score;
} Student;

void add_bonus(Student *s, int bonus) {   // 结构体指针：能改到原对象
    s->score += bonus;
}

int main(void) {
    int n, i;
    Student a[100];
    scanf("%d", &n);

    for (i = 0; i < n; i++) {
        scanf("%s %d", a[i].name, &a[i].score);
        add_bonus(&a[i], 5);              // 传地址，函数里才改得动
        printf("%s %d\n", a[i].name, a[i].score);
    }
    return 0;
}""",
        "best": r"""#include <stdio.h>

typedef struct { char name[35]; int score; } Student;

/* 传值 add_bonus(Student s) 只会改副本，
   这里必须传指针；-> 等价于 (*s).score */
void add_bonus(Student *s, int bonus) { s->score += bonus; }

int main(void) {
    int n, i;
    Student a[100];
    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%s %d", a[i].name, &a[i].score);
        add_bonus(&a[i], 5);
        printf("%s %d\n", a[i].name, a[i].score);
    }
    return 0;
}""",
    },
    25: {
        "reference": r"""#include <stdio.h>

enum Weekday { MON = 1, TUE, WED, THU, FRI, SAT, SUN };   // 从 1 开始

int main(void) {
    int d;
    scanf("%d", &d);

    switch (d) {
        case MON: puts("Monday");    break;
        case TUE: puts("Tuesday");   break;
        case WED: puts("Wednesday"); break;
        case THU: puts("Thursday");  break;
        case FRI: puts("Friday");    break;
        case SAT: puts("Saturday");  break;
        case SUN: puts("Sunday");    break;
        default:  puts("invalid");
    }
    return 0;
}""",
        "best": r"""#include <stdio.h>

/* 枚举让 case 好读：MON 就是 1，比写数字清楚
   一张字符串表也能做，但 switch 更贴合枚举的语义 */
enum Weekday { MON = 1, TUE, WED, THU, FRI, SAT, SUN };

int main(void) {
    static const char *name[] = {
        "invalid",
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    };
    int d;
    scanf("%d", &d);

    if (d >= MON && d <= SUN) puts(name[d]);
    else                      puts(name[0]);
    return 0;
}""",
    },
    26: {
        "reference": r"""#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

int main(void) {
    int n, i, v, x;
    Node *head = NULL, *tail = NULL;
    scanf("%d", &n);

    for (i = 0; i < n; i++) {              // 尾插法：保持输入顺序
        scanf("%d", &v);
        Node *p = (Node*)malloc(sizeof(Node));
        p->data = v;
        p->next = NULL;
        if (head == NULL) head = p;
        else              tail->next = p;
        tail = p;
    }

    scanf("%d", &x);
    Node *cur = head, *prev = NULL;
    while (cur != NULL) {                  // 删除所有等于 x 的结点
        if (cur->data == x) {
            Node *tmp = cur;
            if (prev == NULL) head = cur->next;   // 删的是头结点
            else              prev->next = cur->next;
            cur = cur->next;
            free(tmp);
        } else {
            prev = cur;
            cur = cur->next;
        }
    }

    if (head == NULL) {
        printf("empty\n");
        return 0;
    }
    for (cur = head; cur != NULL; cur = cur->next)
        printf("%d%c", cur->data, cur->next ? ' ' : '\n');
    return 0;
}""",
        "best": r"""#include <stdio.h>
#include <stdlib.h>

typedef struct Node { int data; struct Node *next; } Node;

int main(void) {
    int n, i, v, x;
    Node *head = NULL, **tail = &head;     // 二级指针直接挂尾，省掉 tail 特判
    scanf("%d", &n);

    for (i = 0; i < n; i++) {
        scanf("%d", &v);
        Node *p = (Node*)malloc(sizeof(Node));
        p->data = v;
        p->next = NULL;
        *tail = p;
        tail = &p->next;
    }

    scanf("%d", &x);
    /* 用「指向指针的指针」删结点：不用单独处理头结点
       cur 始终指向"该接在上一结点后面的那个位置" */
    Node **cur = &head;
    while (*cur != NULL) {
        if ((*cur)->data == x) {
            Node *tmp = *cur;
            *cur = tmp->next;
            free(tmp);
        } else {
            cur = &(*cur)->next;
        }
    }

    if (head == NULL) { printf("empty\n"); return 0; }
    for (Node *p = head; p; p = p->next)
        printf("%d%c", p->data, p->next ? ' ' : '\n');
    return 0;
}""",
    },
    27: {
        "reference": r"""#include <stdio.h>

int main(void) {
    unsigned int n;
    int k, i, count = 0;
    scanf("%u %d", &n, &k);

    for (i = 0; i < 32; i++) {          // 逐位统计 1 的个数
        if ((n >> i) & 1u) count++;
    }
    printf("%d\n", count);
    printf("%u\n", (n >> k) & 1u);      // 取第 k 位
    printf("%u\n", n << 1);             // 左移一位 = 乘 2
    return 0;
}""",
        "best": r"""#include <stdio.h>

int main(void) {
    unsigned int n;
    int k, count = 0;
    scanf("%u %d", &n, &k);

    /* n & (n-1) 每次清掉最低位的 1，
       循环次数就是 1 的个数（比逐位判断快） */
    unsigned int t = n;
    while (t) { t &= t - 1; count++; }

    printf("%d\n", count);
    printf("%u\n", (n >> k) & 1u);
    printf("%u\n", n << 1);             // 左移：低位补 0，相当于 n*2
    return 0;
}""",
    },
}
