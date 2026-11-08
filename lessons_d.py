# -*- coding: utf-8 -*-
"""lessons_d.py —— 课程 28~36（阶段五：文件与工程化；阶段六：算法与精通）

字段说明见 lessons_a.py。code 一律用 r\"\"\" 原始字符串，代码内只用英文标点。
"""

LESSONS = [
    {
        "block": 28,
        "part": "阶段五 · 文件与工程化",
        "ref": "谭浩强 10.1 · 何钦铭 12",
        "title": "文件基础：打开、读写、关闭",
        "idea": "文件操作就三步：fopen 拿到文件指针，通过它读写，最后 fclose 关掉——中间任何一步失败都要处理。",
        "basics": [
            ["为什么需要文件",
             "程序里的变量在内存中，程序一结束就没了。想让数据留下来（成绩单、日志、配置）就要写进文件，"
             "下次运行再读回来。C 用 FILE 结构体表示一个打开的文件，我们手里拿到的只是指向它的指针 FILE *fp。"],
            ["fopen 的两种模式",
             "文本模式：r 只读（文件必须存在）、w 只写（不存在就建、存在就清空）、a 追加；"
             "加 + 变成可读可写（r+ w+ a+）；加 b 表示二进制（rb、wb）。模式写错是最常见的错误来源——"
             "用 w 打开已有文件会把内容清空，这是不可恢复的。"],
            ["必须判空",
             "fopen 失败（文件不存在、没有权限、路径写错）返回 NULL。不判空直接读，程序当场崩溃。"
             "标准写法：FILE *fp = fopen(\"data.txt\", \"r\"); if (fp == NULL) { perror(\"打开失败\"); return 1; }"],
            ["关闭与 EOF",
             "fclose(fp) 把缓冲区里的内容真正写盘并释放资源，忘写可能导致最后一段数据丢失。"
             "读到文件末尾时，fgetc 返回 EOF（值 -1），所以字符要用 int 接收，不能用 char——char 可能存不下 -1。"],
        ],
        "points": [
            "文件操作三步：fopen → 读写 → fclose，缺一不可",
            "fopen 失败返回 NULL，必须判空再使用",
            "w 模式会清空原文件，想保留内容用 a（追加）",
            "fclose 不写会导致缓冲区数据没落盘",
            "fgetc 返回 int，用 char 接收会丢 EOF 判断",
            "路径里的反斜杠要写两个：\"D:\\\\data\\\\a.txt\"",
            "同一文件不要同时用两个 FILE* 打开同一模式写",
        ],
        "code": r"""#include <stdio.h>

int main(void) {
    const char *path = "demo_hello.txt";

    /* ---------- 写 ---------- */
    FILE *fp = fopen(path, "w");        // w：不存在就创建，存在就清空
    if (fp == NULL) {                   // 一定要判空
        perror("打开写入失败");
        return 1;
    }
    fprintf(fp, "Hello, file!\n");      // 用法和 printf 一样，只是多个 fp
    fprintf(fp, "%d %s\n", 2026, "C");
    fclose(fp);                         // 关闭：把缓冲区内容真正写盘

    /* ---------- 读 ---------- */
    fp = fopen(path, "r");
    if (fp == NULL) {
        perror("打开读取失败");
        return 1;
    }
    int ch, lines = 0;
    while ((ch = fgetc(fp)) != EOF) {   // 用 int 接，才能判断 EOF
        putchar(ch);
        if (ch == '\n') lines++;
    }
    fclose(fp);
    printf("共 %d 行\n", lines);
    return 0;
}""",
        "task": "把 w 改成 a 再运行一次，看文件里是不是变成了四行；然后把文件名改成不存在的路径，观察 perror 输出。",
        "pitfall": "用 \"w\" 打开一个已有文件会把里面清空——调试时一不小心就把数据洗掉了，改内容优先用 \"r+\" 或先备份。",
    },
    {
        "block": 29,
        "part": "阶段五 · 文件与工程化",
        "ref": "谭浩强 10.2 · 何钦铭 12",
        "title": "按字符与按行读写",
        "idea": "按字符读写适合处理任意内容，按行读写适合处理一行一条记录的数据（日志、名单、配置）。",
        "basics": [
            ["fgetc / fputc",
             "fgetc(fp) 读一个字符，到末尾返回 EOF；fputc(ch, fp) 写一个字符。"
             "它们和 getchar/putchar 是同一套东西，只是多了个文件指针。逐字符处理可以做字符统计、加密、文件复制。"],
            ["fgets / fputs",
             "fgets(buf, size, fp) 最多读 size-1 个字符，遇到换行就停，并且**把换行符也存进去**，末尾自动补 '\\0'；"
             "读不到（EOF）返回 NULL。fputs(str, fp) 把字符串写进去，不自动加换行。"
             "所以按行处理时通常要自己去掉结尾的 '\\n'。"],
            ["EOF 与返回值配合",
             "按行循环的标准写法：while (fgets(buf, sizeof buf, fp) != NULL) { 处理 buf; }。"
             "不要用 while (!feof(fp)) 作为唯一条件——feof 要等读到末尾之后才变真，会多处理一次空数据。"],
            ["典型任务",
             "① 文件复制（逐字符或按行）；② 统计行数、字符数、单词数；③ 按行读入再拆分字段（学号 姓名 成绩）；"
             "④ 追加日志（a 模式 + 时间戳）。这些是后面所有文件题的基础。"],
        ],
        "points": [
            "fgets 会保留换行符，用之前记得去掉：buf[strcspn(buf, \"\\n\")] = '\\0'",
            "fgets 读满 size-1 个字符也会返回，长行会被拆成两次读",
            "fgets 到 EOF 返回 NULL，用它当循环条件最稳",
            "fputs 不加换行，需要自己写 \"\\n\"",
            "fgetc 返回 int，判断 != EOF 才算读到结尾",
            "用 feof 当唯一循环条件容易多跑一轮",
            "文本模式下 Windows 的 \\r\\n 会被自动转成 \\n",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    const char *path = "demo_lines.txt";

    /* 写三行，fputs 不会自动加换行，得自己写 */
    FILE *fp = fopen(path, "w");
    if (fp == NULL) { perror("写打开失败"); return 1; }
    fputs("第一行：小明 90\n", fp);
    fputs("第二行：小红 95\n", fp);
    fputs("第三行：小刚 88\n", fp);
    fclose(fp);

    /* 按行读：统计行数、总字符数，并给每行编号打印 */
    fp = fopen(path, "r");
    if (fp == NULL) { perror("读打开失败"); return 1; }

    char buf[256];
    int line_no = 0, total = 0;
    while (fgets(buf, sizeof buf, fp) != NULL) {   // 读不到就返回 NULL
        buf[strcspn(buf, "\n")] = '\0';            // 去掉结尾换行
        line_no++;
        total += (int)strlen(buf);
        printf("第 %d 行（%d 字符）：%s\n", line_no, (int)strlen(buf), buf);
    }
    fclose(fp);
    printf("共 %d 行，合计 %d 个字符\n", line_no, total);
    return 0;
}""",
        "task": "把 fputs 里的 \\n 去掉，再运行看行数统计变成几行；然后加一段：只统计含「小」字的行数。",
        "pitfall": "fgets 读进来的字符串带着换行，直接拿去做 strcmp 比较永远不相等——先去掉 '\\n' 再比。",
    },
    {
        "block": 30,
        "part": "阶段五 · 文件与工程化",
        "ref": "谭浩强 10.3–10.4 · 何钦铭 12",
        "title": "格式化读写与随机访问",
        "idea": "fprintf/fscanf 像 printf/scanf 但作用于文件，fread/fwrite 按字节块搬数据，fseek 能直接跳到文件任意位置。",
        "basics": [
            ["fprintf / fscanf",
             "fprintf(fp, \"%s %d\\n\", name, score) 把格式化的文本写进文件；fscanf(fp, \"%s %d\", name, &score) 反过来读。"
             "它们适合人看得懂的文本文件，但格式必须严格对应，文件里多一个空格都可能读错。"],
            ["sscanf / sprintf：在内存里做格式化",
             "sscanf(str, \"%d-%d-%d\", &y, &m, &d) 从字符串里按格式拆数据；sprintf(buf, \"%s:%d\", name, score) 拼成字符串。"
             "处理「一行里多个字段」时特别顺手，也是解析配置、日期的常用工具。"],
            ["fread / fwrite：二进制块",
             "fwrite(&s, sizeof s, 1, fp) 把整个结构体原样写进文件，fread 读回来。"
             "速度快、精度无损（浮点、结构体都能存），但文件是二进制，记事本打开是乱码，而且和机器字节序有关。"],
            ["fseek / ftell / rewind：随机访问",
             "fseek(fp, offset, SEEK_SET/SEEK_CUR/SEEK_END) 把读写位置挪到指定处；ftell 告诉你当前位置；rewind 回到开头。"
             "配合 fread/fwrite 就能实现「直接读第 n 条记录」，不用从头扫——这是数据库索引的雏形。"],
        ],
        "points": [
            "fscanf 的格式串要和文件内容严格对应，否则读一半就失败",
            "fscanf 返回成功读到的项数，判断它能发现格式错误",
            "sscanf/sprintf 处理字符串里的字段比手工切分更省事",
            "fread/fwrite 的参数是 (地址, 单块大小, 块数, fp)",
            "二进制文件必须用 rb/wb 模式打开",
            "fseek 之后可以直接 fread，不必从头读",
            "写完记得 fclose，否则文件可能不完整",
        ],
        "code": r"""#include <stdio.h>

typedef struct {
    int   id;
    char  name[16];
    int   score;
} Rec;

int main(void) {
    const char *txt = "demo_students.txt";
    const char *bin = "demo_students.dat";
    int i;

    /* -------- 文本：fprintf 写、fscanf 读 -------- */
    FILE *fp = fopen(txt, "w");
    if (fp == NULL) { perror("写失败"); return 1; }
    fprintf(fp, "1 Tom 80\n");
    fprintf(fp, "2 Jerry 95\n");
    fprintf(fp, "3 Bob 88\n");
    fclose(fp);

    fp = fopen(txt, "r");
    if (fp == NULL) { perror("读失败"); return 1; }
    Rec r;
    printf("文本文件内容：\n");
    while (fscanf(fp, "%d %15s %d", &r.id, r.name, &r.score) == 3) {  // 返回 3 才读全
        printf("  %d %s %d\n", r.id, r.name, r.score);
    }
    fclose(fp);

    /* -------- 二进制：fwrite 整块写、fseek 直接跳到第 2 条 -------- */
    Rec all[3] = {{1, "Tom", 80}, {2, "Jerry", 95}, {3, "Bob", 88}};
    fp = fopen(bin, "wb");
    if (fp == NULL) { perror("二进制写失败"); return 1; }
    fwrite(all, sizeof(Rec), 3, fp);       // 3 条记录一次写完
    fclose(fp);

    fp = fopen(bin, "rb");
    if (fp == NULL) { perror("二进制读失败"); return 1; }
    fseek(fp, (long)sizeof(Rec) * 1, SEEK_SET);   // 跳到第 2 条（下标 1）
    Rec one;
    fread(&one, sizeof(Rec), 1, fp);
    printf("直接跳到第 2 条：%d %s %d\n", one.id, one.name, one.score);
    printf("文件总大小：%ld 字节，单条 %d 字节\n",
           (long)(fseek(fp, 0, SEEK_END), ftell(fp)), (int)sizeof(Rec));
    fclose(fp);
    return 0;
}""",
        "task": "把 fseek 的偏移改成 sizeof(Rec)*2，看读到的是谁；再把文本文件里某行的分数改成字母，观察 fscanf 的返回值变成几。",
        "pitfall": "fscanf(\"%d %s %d\") 在文件格式不对时只读到一半就返回，如果直接拿去计算，变量里是上次的旧值或垃圾值。",
    },
    {
        "block": 31,
        "part": "阶段五 · 文件与工程化",
        "ref": "谭浩强各章 + 附录 · 何钦铭 10",
        "title": "预处理与多文件工程",
        "idea": "预处理在编译之前跑：宏替换、文件包含、条件编译；多文件工程靠头文件声明和 extern/static 控制可见性。",
        "basics": [
            ["#define 常量与宏函数",
             "#define N 10 是文本替换，没有类型、没有分号。#define SQR(x) ((x)*(x)) 是宏函数，"
             "参数和整体都要加括号，否则 SQR(1+2) 会变成 1+2*1+2 得 5。宏没有类型检查，也不会有函数调用的开销。"],
            ["#include 的两种写法",
             "#include <stdio.h> 从系统目录找；#include \"myfile.h\" 先从当前目录找。头文件里只放声明（函数原型、宏、"
             "结构体定义、extern 变量），不放定义——否则多个 .c 包含它时会重复定义。"],
            ["条件编译",
             "#ifdef DEBUG ... #endif、#ifndef HEADER_H 宏卫（防止头文件被重复包含）、#if defined(X) ... #else ... #endif。"
             "用途：调试开关、跨平台差异、一份代码编出多个版本。"],
            ["多文件工程",
             "把功能拆成 add.c / add.h，主文件 #include \"add.h\" 后直接调用；编译时把所有 .c 一起交给 gcc："
             "gcc main.c add.c -o app。加 static 的函数/全局变量只在本文件可见，能避免重名冲突——这就是模块化。"],
        ],
        "points": [
            "宏是文本替换，参数和整体都要括号",
            "宏没有类型检查，调试时看不到变量",
            "#define 定义常量不加分号",
            "头文件里只放声明，不放变量定义（除非 extern）",
            "每个头文件都加宏卫 #ifndef X_H / #define X_H / #endif",
            "多文件编译要把所有 .c 一起交给 gcc",
            "static 修饰的函数只在本文件可见，是最轻量的封装",
        ],
        "code": r"""#include <stdio.h>

#define N 5                          /* 常量宏：没有类型，也没有分号 */
#define SQR(x) ((x) * (x))           /* 宏函数：参数和整体都加括号 */
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define DEBUG 1                      /* 改成 0 就关掉调试输出 */

int main(void) {
    int a[N] = {3, 1, 4, 1, 5};
    int i;

#ifdef DEBUG                         /* 条件编译：DEBUG 有定义才编进去 */
    printf("[调试] N = %d，SQR(2+1) = %d\n", N, SQR(2 + 1));
#endif

    int m = a[0];
    for (i = 1; i < N; i++) {
        m = MAX(m, a[i]);
    }
    printf("最大值 = %d\n", m);

#if DEBUG
    printf("[调试] 数组内容：");
    for (i = 0; i < N; i++) printf("%d ", a[i]);
    printf("\n");
#endif

    printf("去掉括号会怎样：SQR(1+2) = %d，手写 1+2*1+2 = %d\n",
           SQR(1 + 2), 1 + 2 * 1 + 2);
    return 0;
}""",
        "task": "把 #define DEBUG 1 改成 0 重新编译，看调试输出是否消失；再把 SQR 的括号去掉，观察 SQR(1+2) 的结果变化。",
        "pitfall": "宏参数不加括号是经典事故：SQR(1+2) 展开成 1+2*1+2 = 5，而不是 9，而且编译器不会提醒你。",
    },
    {
        "block": 32,
        "part": "阶段六 · 算法与精通",
        "ref": "何钦铭（算法部分）· 数据结构教材",
        "title": "排序与查找",
        "idea": "排序是把无序变有序（冒泡/选择/插入/快排），查找是在有序数据里快速定位（二分）——两者是算法入门的主干。",
        "basics": [
            ["三种 O(n²) 排序",
             "冒泡：相邻两个比较，大的往后换，每轮把最大值送到末尾；选择：每轮找最小值放到前面；"
             "插入：把当前元素插到前面已排好的序列里（像整理扑克牌）。三者都好写，数据量上千就明显慢了。"],
            ["快速排序（分治）",
             "选一个基准，把比它小的放左边、大的放右边，再对左右两段递归。平均 O(n log n)，是最常用的通用排序。"
             "实际工程里直接调 qsort，不必手写——但要能说清它的思路。"],
            ["顺序查找与二分查找",
             "顺序查找：从头到尾比一遍，O(n)，对数据没要求。二分查找：**必须有序**，每次比较中间元素，"
             "范围减半，O(log n)——100 万个数据最多 20 次比较。"],
            ["复杂度怎么看",
             "O(1) 常数、O(log n) 对数、O(n) 线性、O(n log n)、O(n²)、O(2^n)。"
             "经验：n ≤ 1000 用 O(n²) 没问题；n 到 10 万就必须 O(n log n) 或 O(n)；判题超时（TLE）多半是复杂度过高。"],
        ],
        "points": [
            "冒泡每轮结束，末尾就多一个已排好的元素",
            "选择排序交换次数少，冒泡相邻交换多",
            "插入排序对近乎有序的数据非常快",
            "二分查找的前提是有序，条件写 while (left <= right)",
            "二分中点用 (left + right) / 2 可能溢出，大数据用 left + (right-left)/2",
            "qsort 的比较函数返回负/0/正",
            "判题 TLE 先想复杂度，不是先想优化常数",
        ],
        "code": r"""#include <stdio.h>

void bubble_sort(int a[], int n) {          /* 冒泡：相邻比较，大的往后冒 */
    int i, j;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                int t = a[j]; a[j] = a[j + 1]; a[j + 1] = t;
            }
        }
    }
}

int binary_search(int a[], int n, int key) {  /* 二分：返回下标，找不到 -1 */
    int left = 0, right = n - 1;
    while (left <= right) {                   /* 注意是 <= */
        int mid = left + (right - left) / 2;  /* 防溢出写法 */
        if (a[mid] == key) return mid;
        if (a[mid] < key) left = mid + 1;
        else              right = mid - 1;
    }
    return -1;
}

int main(void) {
    int a[8] = {5, 2, 9, 1, 7, 3, 8, 4};
    int n = 8, i;

    bubble_sort(a, n);
    printf("排序后：");
    for (i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");

    int keys[3] = {7, 100, 1};
    for (i = 0; i < 3; i++) {
        int pos = binary_search(a, n, keys[i]);
        if (pos >= 0) printf("%d 在下标 %d\n", keys[i], pos);
        else          printf("%d 不存在\n", keys[i]);
    }

    /* 插入排序演示：把 6 插进已排好的序列，体会「像理牌」 */
    int b[9] = {1, 3, 5, 7, 9, 0};
    int m = 6, key = 6, j = m - 1;
    while (j >= 0 && b[j] > key) { b[j + 1] = b[j]; j--; }
    b[j + 1] = key;
    printf("插入 6 后：");
    for (i = 0; i <= m; i++) printf("%d ", b[i]);
    printf("\n");
    return 0;
}""",
        "task": "把 bubble_sort 换成选择排序（每轮找最小值换到前面），对比交换次数；再对 10000 个随机数分别跑冒泡和 qsort，感受差距。",
        "pitfall": "二分查找写成 while (left < right) 会漏掉最后一个元素；right 用 n 还是 n-1 也要和循环条件配套。",
    },
    {
        "block": 33,
        "part": "阶段六 · 算法与精通",
        "ref": "习题集 / 竞赛入门",
        "title": "经典算法专题",
        "idea": "这一节不教新语法，只教五个「换个思路就通」的套路：筛法、进制转换、高精度、日期推算、递归穷举。",
        "basics": [
            ["素数筛",
             "判断单个素数用试除到根号 n 就够；要一次性求 n 以内所有素数，用埃氏筛："
             "从 2 开始，把每个素数的倍数全标记成合数，剩下的就是素数，复杂度 O(n log log n)。"],
            ["进制转换",
             "十进制转 r 进制：不断 n % r 取余、n /= r，余数倒着读。r 进制转十进制：从高位起 ans = ans * r + 当前位（霍纳法则）。"
             "十六进制用 A~F 表示 10~15，用字符表和下标互换即可。"],
            ["高精度（大数）",
             "C 的整数最大到 2^64，超过就要用数组存每一位。高精度加法：字符串倒着存进数组，逐位相加、处理进位、"
             "去掉前导零。乘法用双重循环算每一位的贡献再统一进位。"],
            ["日期与枚举",
             "日期题先写闰年判断和每月天数表，再用「累加天数」的思路算星期几、第几天。"
             "穷举类（百钱百鸡、水仙花、全排列、八皇后）靠循环 + 剪枝，递归做全排列时交换元素再回溯。"],
        ],
        "points": [
            "筛法从 i*i 开始标记就能再快一倍",
            "进制转换用 do-while，避免 n=0 时一位都不输出",
            "高精度要从低位往高位加，进位单独处理",
            "高精度输出前要跳过前导零（结果为 0 要特判）",
            "日期题一定先判断闰年再取每月天数",
            "穷举题先估计算量，三层循环到 1000 就是 10 亿次，会超时",
            "递归全排列靠「交换 - 递归 - 换回」的回溯三件套",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

#define MAXLEN 105

/* 高精度加法：把两个大整数字符串相加 */
void big_add(const char *a, const char *b, char *out) {
    int x[MAXLEN] = {0}, y[MAXLEN] = {0}, z[MAXLEN] = {0};
    int la = (int)strlen(a), lb = (int)strlen(b), i;

    for (i = 0; i < la; i++) x[i] = a[la - 1 - i] - '0';   /* 倒着存，低位在前 */
    for (i = 0; i < lb; i++) y[i] = b[lb - 1 - i] - '0';

    int L = la > lb ? la : lb;
    for (i = 0; i < L; i++) {
        z[i] += x[i] + y[i];
        z[i + 1] = z[i] / 10;      /* 进位 */
        z[i] %= 10;
    }
    if (z[L] > 0) L++;             /* 最高位还有进位 */

    int k = 0;
    for (i = L - 1; i >= 0; i--) out[k++] = (char)('0' + z[i]);   /* 倒回来输出 */
    out[k] = '\0';
}

int main(void) {
    char sum[MAXLEN];
    big_add("99999999999999999999", "1", sum);
    printf("99999999999999999999 + 1 = %s\n", sum);

    /* 进制转换：十进制 255 转二进制 / 十六进制 */
    int n = 255, base, digits[64], cnt = 0, i;
    for (base = 2; base <= 16; base *= 8) {   /* 2 和 16 */
        n = 255; cnt = 0;
        do {
            digits[cnt++] = n % base;
            n /= base;
        } while (n > 0);
        printf("255 转 %d 进制 = ", base);
        for (i = cnt - 1; i >= 0; i--) {
            if (digits[i] < 10) putchar('0' + digits[i]);
            else                putchar('A' + digits[i] - 10);
        }
        printf("\n");
    }

    /* 埃氏筛：求 100 以内的素数 */
    int is_comp[101] = {0}, count = 0;
    for (i = 2; i * i <= 100; i++) {
        if (!is_comp[i]) {
            for (int j = i * i; j <= 100; j += i) is_comp[j] = 1;
        }
    }
    printf("100 以内素数：");
    for (i = 2; i <= 100; i++) {
        if (!is_comp[i]) { printf("%d ", i); count++; }
    }
    printf("\n共 %d 个\n", count);
    return 0;
}""",
        "task": "用 big_add 算 12345678901234567890 + 98765432109876543210；再把进制转换改成支持用户输入任意 n 和任意进制。",
        "pitfall": "高精度转成数组时忘了「倒着存」，从高位开始加会让进位方向反掉，结果完全错位。",
    },
    {
        "block": 34,
        "part": "阶段六 · 算法与精通",
        "ref": "谭浩强 9.7 · 何钦铭 11",
        "title": "动态内存管理",
        "idea": "数组长度写死不够灵活时，用 malloc 在堆上按需申请内存，用完 free 还给系统——申请多少、用多久，由你决定。",
        "basics": [
            ["三个函数",
             "malloc(n) 申请 n 字节，返回 void*（要强转），失败返回 NULL；calloc(k, size) 申请 k 个并清零；"
             "realloc(p, newSize) 把已申请的内存调整大小（可能搬家，返回新地址）；free(p) 释放。"],
            ["malloc 返回的是「裸内存」",
             "malloc 不清零，里面是垃圾值；calloc 会清零。用完必须 free，且只能 free 一次，free 之后要把指针置 NULL，"
             "否则就是悬垂指针。free(NULL) 是安全的，不会出错。"],
            ["动态数组套路",
             "int *a = malloc(n * sizeof(int)); 然后当数组用 a[i]；不够大时 a = realloc(a, m * sizeof(int));"
             "最后 free(a)。注意 realloc 可能失败，失败时原指针还在，所以要先用临时变量接：int *t = realloc(a, ...); if (t) a = t;"],
            ["常见错误清单",
             "① 忘记 free → 内存泄漏（程序越跑越占内存）；② free 后继续用 → 悬垂指针，随时崩；"
             "③ 越界写 → 破坏堆结构，崩在别处；④ 重复 free → 直接崩溃；⑤ 用 sizeof(指针) 当数组长度 → 永远只有 8 字节。"],
        ],
        "points": [
            "malloc 之后必须判空再使用",
            "malloc 申请的内存不清零，需要初始化就用 calloc 或 memset",
            "free 之后立刻把指针置 NULL，防止二次释放",
            "realloc 可能返回新地址，要用临时变量接住",
            "动态数组的长度要自己记，sizeof 拿不到",
            "只 free 堆上的内存，别 free 栈变量或数组名",
            "函数里 malloc 的内存若返回给调用方，就要约好由谁 free",
        ],
        "code": r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n, i;
    printf("要读几个整数？");
    if (scanf("%d", &n) != 1 || n <= 0) return 1;

    int *a = (int*)malloc((size_t)n * sizeof(int));   // 按需申请
    if (a == NULL) {                                  // 一定判空
        printf("内存申请失败\n");
        return 1;
    }

    for (i = 0; i < n; i++) a[i] = (i + 1) * 3;       // 当数组用
    long long sum = 0;
    for (i = 0; i < n; i++) sum += a[i];
    printf("前 %d 个元素之和 = %lld\n", n, sum);

    /* 扩容：再要 2n 个 int，realloc 可能搬家 */
    int *t = (int*)realloc(a, (size_t)n * 2 * sizeof(int));
    if (t == NULL) {
        free(a);                                      // 失败时原内存还在，要自己释放
        printf("扩容失败\n");
        return 1;
    }
    a = t;
    for (i = n; i < n * 2; i++) a[i] = 0;             // 新区域是垃圾值，手动初始化
    printf("扩容后第 %d 个元素 = %d\n", n * 2 - 1, a[n * 2 - 1]);

    free(a);                                          // 还给系统
    a = NULL;                                         // 防止悬垂指针
    printf("已释放，a = %s\n", a == NULL ? "NULL" : "非空");
    return 0;
}""",
        "task": "把 malloc 换成 calloc，打印 a[0] 看是否为 0；再故意把 free(a) 写两遍，观察程序怎么崩（理解重复释放）。",
        "pitfall": "free(a) 之后还用 a[0] 是悬垂指针，可能当下不崩、过几行才崩——释放后立刻置 NULL，是必须养成的习惯。",
    },
    {
        "block": 35,
        "part": "阶段六 · 算法与精通",
        "ref": "工程实践（配合 judge.py 的报错中文化）",
        "title": "调试与错误排查",
        "idea": "调试不是靠猜，而是靠「缩小范围」：先看编译器说什么，再看程序在哪一步偏离预期，最后用打印或断点定位。",
        "basics": [
            ["先读懂 gcc 的报错",
             "报错格式是 文件:行:列: error: 内容。第一行错误往往最可信，后面的常是连锁反应。"
             "常见：expected ';' before ...（漏分号）、undeclared identifier（变量名拼错/没声明）、"
             "implicit declaration（忘 #include 或忘函数声明）、stray '\\357'（混进中文标点）、"
             "format '%d' expects int（printf 类型不匹配）。"],
            ["编译警告不是噪音",
             "gcc -Wall -Wextra 能提前发现未初始化、类型不匹配、数组越界风险。警告一律当成待修问题，"
             "很多线上事故就是「编译时有警告，没人看」。"],
            ["运行时错误怎么定位",
             "段错误（Segmentation fault）：野指针、越界、free 已释放内存、递归太深。"
             "结果不对但不崩：先检查变量初值、循环边界（< 还是 <=）、整数除法、数组下标。"
             "死循环/超时：循环变量没变、条件永远为真。"],
            ["调试手段",
             "① printf 大法：在关键位置打印变量和标记，最土但最快；② assert(cond)：条件不成立就中止并报出错行；"
             "③ 断点单步：gdb 或 VS Code 里打断点，看调用栈和变量；④ 缩小输入：用一个最小的、你能手算的输入复现问题。"],
        ],
        "points": [
            "先修第一个 error，后面的错误常常是它引起的",
            "中文标点导致的 stray 错误最难认，看行号附近有没有全角符号",
            "段错误九成是空指针/野指针/越界，先查指针和下标",
            "循环少跑或多跑一次，先看 < 与 <=、初值和终值",
            "printf 调试要打印「在哪 + 值是多少」，否则分不清输出顺序",
            "assert 适合检查「绝不该发生」的情况，正式发布可关掉",
            "改一处、跑一次，别一次改五个地方",
        ],
        "code": r"""#include <stdio.h>
#include <assert.h>

/* 一个"带自检"的数组求和：演示边界检查 + assert + 调试打印 */
long long safe_sum(const int *a, int n) {
    assert(a != NULL);                 /* 空指针立刻暴露，而不是崩在深处 */
    assert(n >= 0);

#ifdef DEBUG
    printf("[调试] safe_sum 收到 n=%d\n", n);
#endif

    long long s = 0;
    int i;
    for (i = 0; i < n; i++) {          /* 是 < 不是 <=，否则越界 */
        s += a[i];
#ifdef DEBUG
        printf("[调试] a[%d]=%d, 累计=%lld\n", i, a[i], s);
#endif
    }
    return s;
}

int main(void) {
    int a[5] = {3, 1, 4, 1, 5};

    printf("n=5 时：%lld\n", safe_sum(a, 5));
    printf("n=0 时：%lld（空数组应该得 0）\n", safe_sum(a, 0));

    /* 手动模拟一次「边界写错」的后果，理解为什么会算错。
       这里不真的越界（那是未定义行为，可能崩），
       用 other 假装是排在数组后面的别的变量 */
    int other = 777;                  /* 模拟邻居内存里的值 */
    long long wrong = 0;
    int i;
    for (i = 0; i < 5; i++) wrong += a[i];
    wrong += other;                   /* 相当于多加了 a[5] 那一格 */
    printf("若下标写成 i<=5，会多读一格别人的内存，结果变成 %lld\n", wrong);
    return 0;
}""",
        "task": "用 gcc -DDEBUG 编译运行，看调试信息；然后删掉一个分号、把 printf 的 %d 改成 %f，分别读一遍编译器给的报错。",
        "pitfall": "看到一屏报错就想全改，结果越改越乱——先只修第一条 error，重新编译，往往剩下的错误自己就消失了。",
    },
    {
        "block": 36,
        "part": "阶段六 · 算法与精通",
        "ref": "工程实践（标准库 + 代码规范）",
        "title": "标准库与工程规范",
        "idea": "C 的标准库已经把常用轮子造好了，会用它们能少写一半代码；工程规范则决定半年后你还看不看得懂自己的代码。",
        "basics": [
            ["stdio.h / stdlib.h / string.h",
             "stdio：printf/scanf/fopen/fgets/puts；stdlib：malloc/free/qsort/atoi/strtol/exit；"
             "string：strlen/strcpy/strcmp/strstr/memset。这些名字要熟，遇到需求先查库再动手写。"],
            ["math.h / ctype.h / time.h",
             "math：sqrt/pow/fabs/ceil/floor，链接时可能需要 -lm；ctype：isalpha/isdigit/isspace/toupper/tolower，"
             "注意参数要用 unsigned char 转换；time：time(NULL) 取时间戳，localtime 拆成年月日。"],
            ["qsort 与自定义比较",
             "qsort(base, n, size, cmp) 能排任何类型：结构体按分数排、字符串按字典序排，都只改比较函数。"
             "比较函数里把 void* 转成实际类型，返回负数/0/正数。"],
            ["代码规范与模块划分",
             "命名：变量小写加下划线，常量全大写，函数用动词开头；一个函数只做一件事，超过一屏就拆；"
             "参数不超过 5 个，多了就用结构体打包；所有输入都要校验；头文件加宏卫；"
             "文件按职责拆（输入、处理、输出各自一个文件）。"],
        ],
        "points": [
            "用 qsort 而不是每次手写排序",
            "字符串比较用 strcmp，复制用 strncpy/strcpy 并确认目标够大",
            "memset 只能用来填 0 或 -1，别用它填其他整数",
            "atoi 不做错误检查，要严格解析用 strtol",
            "ctype 系列函数传参前转 unsigned char",
            "数学函数返回 double，输出用 %f",
            "命名和注释是给三个月后的自己看的，别省",
        ],
        "code": r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <time.h>

/* qsort 的比较函数：按分数从高到低 */
typedef struct { char name[16]; int score; } Stu;

int cmp_score(const void *a, const void *b) {
    const Stu *x = (const Stu*)a;
    const Stu *y = (const Stu*)b;
    return y->score - x->score;
}

int main(int argc, char *argv[]) {
    printf("命令行参数个数 = %d\n", argc);
    for (int i = 0; i < argc; i++) printf("  argv[%d] = %s\n", i, argv[i]);

    Stu s[3] = {{"Tom", 80}, {"Jerry", 95}, {"Bob", 88}};
    qsort(s, 3, sizeof s[0], cmp_score);
    printf("按分数降序：%s(%d) %s(%d) %s(%d)\n",
           s[0].name, s[0].score, s[1].name, s[1].score, s[2].name, s[2].score);

    const char *text = "Hello C 2026!";
    int letters = 0, digits = 0;
    for (int i = 0; text[i]; i++) {
        unsigned char c = (unsigned char)text[i];
        if (isalpha(c)) letters++;
        if (isdigit(c)) digits++;
    }
    printf("字母 %d 个，数字 %d 个\n", letters, digits);

    char up[32];
    strcpy(up, text);                      /* 先复制，不能直接改字符串常量 */
    for (int i = 0; up[i]; i++) up[i] = (char)toupper((unsigned char)up[i]);
    printf("转大写：%s\n", up);

    printf("sqrt(2) = %.4f, pow(2,10) = %.0f\n", sqrt(2.0), pow(2.0, 10));

    time_t now = time(NULL);
    printf("时间戳 = %lld\n", (long long)now);
    return 0;
}""",
        "task": "把 cmp_score 改成按名字字典序（strcmp）排一次；再用 strtol 把 argv[1] 转成整数（运行时传个数字试试）。",
        "pitfall": "想改字符串内容却直接改字符串常量（char *p = \"abc\"; p[0] = 'A';）会崩溃——先 strcpy 到数组里再改。",
    },
]
