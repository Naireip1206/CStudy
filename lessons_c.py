# -*- coding: utf-8 -*-
"""lessons_c.py —— 课程 19~27（指针深化 + 阶段四：自定义数据类型）

字段说明见 lessons_a.py。code 一律用 r\"\"\" 原始字符串，代码内只用英文标点。
"""

LESSONS = [
    {
        "block": 19,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.4 · 何钦铭 8、10",
        "title": "指针与字符串",
        "idea": "char *p 和 char s[] 看起来都能存字符串，但前者指向只读常量、后者是可改的数组，这是最容易踩的坑。",
        "basics": [
            ["两种写法的本质区别",
             "char s[] = \"hello\"; 在栈上分配 6 个字节，把字符复制进去，s[0] = 'H' 合法。"
             "char *p = \"hello\"; 把 p 指向程序只读段里的字符串常量，p[0] = 'H' 会崩溃（未定义行为）。"
             "结论：要改内容就用数组，只是读取用指针。"],
            ["用指针遍历字符串",
             "while (*p != '\\0') { ... p++; } 或更紧凑的 while (*p) p++;。因为字符串以 '\\0' 结尾，"
             "条件 *p 本身就表达了\"还没到结尾\"。这是 C 里最地道的写法，也是 strlen 的本质。"],
            ["指针版字符串函数",
             "自己实现 strcpy/strcat/strlen 是理解指针的经典练习：目标指针一路往后写，源指针一路往后读，最后补 '\\0'。"
             "标准库函数的原型都返回 char*，是为了支持链式调用（如 printf(\"%s\", strcpy(a, b))）。"],
            ["const 修饰指针",
             "const char *p：不能通过 p 改内容（内容只读），p 本身可以换指向——函数参数最常用这种，表示\"我只读不改\"。"
             "char * const p：p 本身不能改指向，但能改内容。const char * const p：两者都不能改。"],
        ],
        "points": [
            "字符串常量只读，char *p = \"abc\"; p[0] = 'x'; 会崩",
            "数组名不能自增，指针可以，所以遍历要用 char *p = s",
            "判断字符串结束看 *p 是否为 '\\0'，不是看长度",
            "字符串函数参数写 const char* 表示只读，是良好习惯",
            "char *names[3] 是三个指针，不是二维数组（第 21 节）",
            "把字符串赋给指针只是复制地址，两个指针指向同一块内容",
            "修改字符串内容前先确认它是不是数组",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

int my_strlen(const char *s) {       // 只读遍历，不修改内容
    int n = 0;
    while (*s != '\0') {
        n++;
        s++;                          // 指针往后走一个字符
    }
    return n;
}

char *my_strcpy(char *dst, const char *src) {
    char *start = dst;                // 记住起点，最后返回
    while ((*dst = *src) != '\0') {   // 赋值 + 判断，一步到位
        dst++;
        src++;
    }
    return start;
}

int main(void) {
    char buf[32] = "hello";           // 数组：内容可改
    char *p = buf;                    // 指针指向这个数组

    printf("my_strlen = %d，strlen = %d\n", my_strlen(buf), (int)strlen(buf));

    p[0] = 'H';                       // 通过指针改数组内容：合法
    printf("改后：%s\n", buf);

    char copy[32];
    my_strcpy(copy, buf);
    printf("复制后：%s\n", copy);

    const char *ro = "只读字符串";     // 指向常量，不能改内容
    printf("只读：%s，长度 %d\n", ro, my_strlen(ro));
    /* 下面这行如果打开，运行时会崩溃：
       ro[0] = 'X';
    */

    char *q = buf;
    while (*q) {                      // *q 非 0 就继续
        printf("[%c]", *q);
        q++;
    }
    printf("\n");
    return 0;
}""",
        "task": "把 char *p = buf; 改成 char *p = \"hello\"; 再执行 p[0] = 'H';，看程序怎么崩；然后写一个 my_strcat 用指针实现。",
        "pitfall": "char *p = \"abc\"; 后面想改 p[0]，编译能过、运行时崩溃——字符串常量在只读区，这是新手最难理解的崩溃之一。",
    },
    {
        "block": 20,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.5 · 何钦铭 8",
        "title": "指针作函数参数",
        "idea": "想让函数改到调用方的变量，就得把变量的地址传进去——这是 C 实现\"多返回值\"和\"原地修改\"的唯一办法。",
        "basics": [
            ["传地址 = 拥有修改权",
             "swap(int *a, int *b) 里 *a、*b 就是调用方的 x、y，交换它们就是交换外面的值。调用写 swap(&x, &y)。"
             "scanf(\"%d\", &n) 也是同一个道理：scanf 要改 n，就必须拿到 n 的地址。"],
            ["用指针返回多个结果",
             "函数只能 return 一个值，但可以顺便写进指针参数：void max_min(int a[], int n, int *mx, int *mn)。"
             "调用 max_min(arr, n, &big, &small) 之后 big、small 就有了结果。这是 C 标准库也常用的风格。"],
            ["指针参数与 const",
             "输入型参数写 const int *p（只读，防手滑）；输出型参数写 int *p（要写回）。约定清楚，调用者才不会给错指针。"
             "void 型指针 void *p 可以指向任何类型，用前要强制转换（如 malloc 返回 void*）。"],
            ["绝不能返回局部变量的地址",
             "int *f(void) { int x = 5; return &x; } 是严重错误：函数返回后 x 的内存已被回收，"
             "外面拿到的指针指向废内存。要返回指针，指向的必须是 static 变量、全局变量或 malloc 出来的内存。"],
        ],
        "points": [
            "要修改实参就传 &x，形参用 int *p，函数内写 *p = ...",
            "传指针前先确保它不是 NULL，函数内也可以判空",
            "指针既能当输入也能当输出，注释写清方向",
            "不要返回局部变量的地址（悬垂指针）",
            "const int * 是只读输入，int * 是可写输出",
            "void* 万能指针，用前要转换类型",
            "swap 的三个步骤：t = *a; *a = *b; *b = t;",
        ],
        "code": r"""#include <stdio.h>

void swap(int *a, int *b) {            // 传地址，才能真正交换
    int t = *a;
    *a = *b;
    *b = t;
}

void divmod(int a, int b, int *q, int *r) {   // 一次返回商和余数
    *q = a / b;
    *r = a % b;
}

void max_min(const int *a, int n, int *mx, int *mn) {  // 输入只读，输出写回
    int i;
    *mx = *mn = a[0];
    for (i = 1; i < n; i++) {
        if (a[i] > *mx) *mx = a[i];
        if (a[i] < *mn) *mn = a[i];
    }
}

int main(void) {
    int x = 1, y = 2;
    swap(&x, &y);
    printf("交换后 x=%d y=%d\n", x, y);

    int q, r;
    divmod(17, 5, &q, &r);
    printf("17 / 5 = %d 余 %d\n", q, r);

    int a[6] = {3, -2, 9, 0, 7, 4};
    int big, small;
    max_min(a, 6, &big, &small);
    printf("最大 %d，最小 %d\n", big, small);

    int *bad = NULL;
    if (bad == NULL) printf("空指针不能直接解引用，先判空\n");
    return 0;
}""",
        "task": "写一个 void stat(int a[], int n, int *sum, double *avg)，一次算出和与平均；再写 void swap3(int *a, int *b, int *c) 让三个数轮换。",
        "pitfall": "写了 swap(int *a, int *b) 却调用 swap(x, y)（忘了 &），gcc 只会警告，运行直接崩——传参写错是段错误头号来源。",
    },
    {
        "block": 21,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.6–8.8 · 何钦铭 11",
        "title": "指针数组、数组指针与多级指针",
        "idea": "指针数组是\"一堆指针\"，数组指针是\"指向一个数组的指针\"，多级指针是\"指向指针的指针\"——括号位置决定一切。",
        "basics": [
            ["指针数组 int *a[3]",
             "[] 优先级高于 *，所以这是\"3 个 int* 组成的数组\"。最常用的是 char *names[3] = {\"Tom\", \"Jerry\", \"Bob\"}，"
             "每个元素指向一个字符串，长度可以各不相同。注意字符串常量只读，排序时交换的是指针而不是内容。"],
            ["数组指针 int (*p)[4]",
             "括号把 * 和 p 绑在一起：p 是\"指向含 4 个 int 的数组\"的指针。p + 1 会跨过一整行（4 个 int = 16 字节）。"
             "二维数组的数组名 a 就是这种类型，所以 int a[3][4] 传参写 int (*a)[4] 或 int a[][4] 都对。"],
            ["多级指针 int **pp",
             "pp 存的是\"一个 int* 变量的地址\"。**pp 才取到最终的值，*pp 得到那个指针。"
             "用途：在函数里改调用方的指针本身（如 void create(int **p)），以及动态二维数组、字符串指针数组。"],
            ["怎么快速读懂复杂声明",
             "从变量名出发，先看右边再看左边，遇到括号先算括号。口诀：\"右左法则\"。"
             "int *a[4] → a 是数组，装着 4 个指针；int (*a)[4] → a 是指针，指向 4 个 int 的数组。"
             "拿不准就写 sizeof 或让编译器报错来验证。"],
        ],
        "points": [
            "int *a[4] 是指针数组，int (*a)[4] 是数组指针，差一对括号",
            "char *names[] 里每个字符串长度可不同，但内容只读",
            "排序字符串数组时交换指针，比交换内容高效",
            "二维数组传参：int a[][4] 或 int (*a)[4]，第二维不能省",
            "a + 1 在二维数组里跨一整行",
            "二级指针 **pp 要解引用两次才拿到值",
            "复杂声明用右左法则 + sizeof 验证",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    const char *names[4] = {"banana", "apple", "cherry", "date"};
    int i, j;

    for (i = 0; i < 3; i++) {                    // 冒泡排序：只交换指针
        for (j = 0; j < 3 - i; j++) {
            if (strcmp(names[j], names[j + 1]) > 0) {
                const char *t = names[j];        // 交换的是地址，不是内容
                names[j] = names[j + 1];
                names[j + 1] = t;
            }
        }
    }
    printf("排序后：");
    for (i = 0; i < 4; i++) printf("%s ", names[i]);
    printf("\n");

    int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int (*p)[3] = a;                             // 数组指针，一行 3 个 int
    printf("p[1][2] = %d, *(*(p+1)+2) = %d\n", p[1][2], *(*(p + 1) + 2));
    printf("p+1 比 p 大 %d 字节（一整行）\n", (int)((char*)(p + 1) - (char*)p));

    int x = 42;
    int *px = &x;
    int **ppx = &px;                             // 二级指针：指向指针的指针
    printf("x=%d, *px=%d, **ppx=%d\n", x, *px, **ppx);
    **ppx = 100;                                 // 顺着两级地址改回去
    printf("改完 x=%d\n", x);
    return 0;
}""",
        "task": "把 int (*p)[3] = a; 改成 int *p[3] = a; 编译看看报什么错，理解两者的类型差异；再用二级指针在函数里给指针重新赋值。",
        "pitfall": "把 int (*p)[4] 写成 int *p[4] 编译器不会提醒你\"写错了\"，只会报一堆类型不匹配——括号的位置就是含义。",
    },
    {
        "block": 22,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.7 · 何钦铭 11",
        "title": "函数指针",
        "idea": "函数也住在内存里，函数名就是它的地址；函数指针能存这个地址，于是\"函数\"可以像变量一样被传递。",
        "basics": [
            ["定义与调用",
             "int (*fp)(int, int) = add; 读法：fp 是指针，指向\"接收两个 int、返回 int\"的函数。"
             "调用可以写 fp(2, 3) 也可以写 (*fp)(2, 3)，两者等价。括号不能省，写成 int *fp(int, int) 就变成"
             "\"返回 int* 的函数\"了。"],
            ["核心用途：回调",
             "把函数当参数传进去，让调用方决定\"做什么\"。例如 void apply(int a[], int n, int (*f)(int)) 可以对每个元素做任意变换。"
             "标准库的 qsort、bsearch，以及事件处理、菜单分派都靠它。"],
            ["函数指针数组：菜单表",
             "int (*ops[4])(int, int) = {add, sub, mul, divi}; 用下标选操作，比一长串 switch 更好扩展。"
             "配合枚举和字符串表，可以写出\"命令 → 函数\"的映射，这正是很多框架的插件机制雏形。"],
            ["qsort 的用法",
             "void qsort(void *base, size_t n, size_t size, int (*cmp)(const void*, const void*))。"
             "比较函数返回负数表示 a 应排在 b 前，0 表示相等，正数表示 a 排后面。"
             "因为参数是 void*，比较前要强制转换成实际类型。"],
        ],
        "points": [
            "定义必须带括号：int (*fp)(int, int)",
            "函数指针的类型必须和被指函数完全一致（参数、返回值）",
            "typedef int (*Op)(int,int); 能让代码清爽很多",
            "回调函数由调用方提供，实现可插拔",
            "qsort 的比较函数返回负 / 0 / 正",
            "函数名作实参时不用加 &，直接用名字即可",
            "函数指针调用前最好判空",
        ],
        "code": r"""#include <stdio.h>
#include <stdlib.h>

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

typedef int (*Op)(int, int);          // 给函数指针类型起个短名字

int calc(Op f, int a, int b) {        // 把函数当参数传进来
    return f(a, b);
}

int cmp_desc(const void *a, const void *b) {   // qsort 用的比较函数：从大到小
    int x = *(const int*)a;
    int y = *(const int*)b;
    return y - x;                              // 反过来就是降序
}

int main(void) {
    Op table[3] = {add, sub, mul};             // 函数指针数组 = 操作表
    const char *name[3] = {"+", "-", "*"};

    int i;
    for (i = 0; i < 3; i++) {
        printf("10 %s 4 = %d\n", name[i], table[i](10, 4));
    }
    printf("calc(add, 2, 3) = %d\n", calc(add, 2, 3));

    int arr[6] = {3, 9, 1, 7, 5, 2};
    qsort(arr, 6, sizeof(int), cmp_desc);       // 传入比较函数
    printf("降序：");
    for (i = 0; i < 6; i++) printf("%d ", arr[i]);
    printf("\n");

    Op f = add;
    if (f != NULL) printf("判空后调用：%d\n", f(1, 1));
    return 0;
}""",
        "task": "往 table 里加一个除法函数 divi（注意除零判断），再写 int apply_all(int a[], int n, int (*f)(int)) 把数组每个元素都平方。",
        "pitfall": "忘写括号写成 int *fp(int, int) 时，编译器认为你在声明一个返回指针的函数，后面赋值会报类型不兼容。",
    },
    {
        "block": 23,
        "part": "阶段四 · 自定义数据类型",
        "ref": "谭浩强 9.1–9.3 · 何钦铭 9",
        "title": "结构体基础",
        "idea": "结构体把几个不同类型的数据打包成一个整体，用一个名字管理\"一个学生的全部信息\"这样的复合对象。",
        "basics": [
            ["定义与使用",
             "struct Student { char name[20]; int age; double score; }; 注意末尾分号。"
             "定义变量 struct Student s; 访问成员用点号 s.age。定义类型的语句只是\"画图纸\"，不占内存，定义变量才真正分配。"],
            ["初始化与赋值",
             "struct Student s = {\"小明\", 18, 91.5}; 按成员顺序填。同类型结构体可以直接整体赋值 s2 = s1;（连数组一起复制），"
             "但不能用 == 比较——C 没有自动的成员逐个比较。"],
            ["结构体数组",
             "struct Student cls[3]; 就是一张表，配合循环批量读入、统计平均分、按成绩排序都很自然。"
             "排序时交换的是整个结构体：struct Student t = cls[i]; cls[i] = cls[j]; cls[j] = t;"],
            ["内存对齐与 typedef",
             "编译器为了让成员对齐访问，可能在成员之间插入填充字节，所以 sizeof(struct) 通常大于各成员之和（例如 "
             "char + int 常常是 8 字节）。用 typedef struct Student Student; 之后就可以直接写 Student s; 省掉 struct 关键字。"],
        ],
        "points": [
            "结构体定义末尾必须有分号",
            "成员是字符数组时不能 s.name = \"Tom\"，要用 strcpy",
            "同类型结构体可以整体赋值，但不能用 == 比较",
            "结构体可以嵌套，访问写 s.birth.year",
            "sizeof 可能因对齐而偏大，不要自己手算",
            "typedef 能省掉 struct 关键字，工程里几乎都这么写",
            "结构体数组就是\"表\"，遍历 + 排序是高频题型",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

typedef struct {                 // typedef + 匿名结构体：类型名直接是 Student
    char  name[20];
    int   age;
    double score;
} Student;

int main(void) {
    Student s1 = {"小明", 18, 91.5};       // 按顺序初始化
    Student s2;
    s2 = s1;                               // 整体赋值：连 name 数组一起复制
    strcpy(s2.name, "小红");               // 但改名字必须用 strcpy
    s2.score = 88.0;

    printf("%s %d %.1f\n", s1.name, s1.age, s1.score);
    printf("%s %d %.1f\n", s2.name, s2.age, s2.score);
    printf("sizeof(Student) = %d\n", (int)sizeof(Student));

    Student cls[3] = {
        {"张三", 19, 76.5},
        {"李四", 18, 92.0},
        {"王五", 20, 85.0},
    };
    int i, j;
    for (i = 0; i < 2; i++) {                       // 按成绩从高到低排序
        for (j = 0; j < 2 - i; j++) {
            if (cls[j].score < cls[j + 1].score) {
                Student t = cls[j];                 // 整体交换
                cls[j] = cls[j + 1];
                cls[j + 1] = t;
            }
        }
    }
    for (i = 0; i < 3; i++) {
        printf("%s\t%d\t%.1f\n", cls[i].name, cls[i].age, cls[i].score);
    }

    double sum = 0;
    for (i = 0; i < 3; i++) sum += cls[i].score;
    printf("平均分 = %.2f\n", sum / 3);
    return 0;
}""",
        "task": "给 Student 加一个成员 char gender;，在初始化列表里一起填上；再写一段按年龄升序排序的代码。",
        "pitfall": "结构体定义最后忘了分号，编译器会在下一行报一堆莫名其妙的错误——报错位置常常不是真正出错的地方。",
    },
    {
        "block": 24,
        "part": "阶段四 · 自定义数据类型",
        "ref": "谭浩强 9.4 · 何钦铭 9",
        "title": "结构体指针",
        "idea": "结构体指针存结构体的地址，用 -> 访问成员；传指针给函数可以避免复制整个结构体，还能改到原对象。",
        "basics": [
            ["定义与 -> 运算符",
             "Student *p = &s1; 访问成员有两种写法：(*p).score 和 p->score，后者是等价的简写。"
             "括号不能省——因为 . 的优先级高于 *，*p.score 会被理解成 *(p.score) 而报错。"],
            ["结构体指针作函数参数",
             "void print(const Student *p) 只传 8 字节地址，不复制整个结构体；void raise(Student *p, double x) 能改到原对象。"
             "结构体一大（比如带 100 个成员的数组），传值复制的开销就不可忽视了。"],
            ["返回结构体 vs 传指针",
             "Student make(...) 返回结构体是值拷贝，小结构体没问题；要返回大结构体或需要修改调用方对象时，用指针 + 输出参数。"
             "切记不要返回指向函数内局部结构体的指针。"],
            ["为链表埋伏笔",
             "struct Node { int data; struct Node *next; }; —— 结构体里放一个指向\"自己这种类型\"的指针，"
             "就能把一个个结点串起来。这就是链表，下一节（第 26 节）的主角。"],
        ],
        "points": [
            "p->member 等价于 (*p).member，括号不能省",
            "传结构体是值拷贝，改不到外面；传指针才能改",
            "大结构体用指针参数，省内存也省时间",
            "const Student *p 表示只读，修改会编译报错",
            "结构体里的指针成员要注意浅拷贝问题",
            "不要返回局部结构体变量的地址",
            "链表结点 = 数据 + 指向同类型结点的指针",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

typedef struct {
    char   name[20];
    int    age;
    double score;
} Student;

void print_student(const Student *p) {          // 只读，不复制结构体
    printf("%s\t%d\t%.1f\n", p->name, p->age, p->score);
}

void add_score(Student *p, double bonus) {      // 能改到调用方的对象
    p->score += bonus;
}

void birthday(Student *p) {
    p->age++;
}

int main(void) {
    Student s = {"小明", 18, 80.0};
    Student *p = &s;

    printf("点号访问：%s %.1f\n", s.name, s.score);
    printf("箭头访问：%s %.1f\n", p->name, p->score);
    printf("括号写法：%s %.1f\n", (*p).name, (*p).score);   // 与 -> 完全等价

    add_score(p, 12.5);
    birthday(&s);
    print_student(&s);

    Student cls[2] = {{"张三", 19, 70}, {"李四", 18, 90}};
    Student *q = cls;                           // 指向数组首元素
    int i;
    for (i = 0; i < 2; i++) {
        print_student(q + i);                   // 指针偏移遍历结构体数组
    }

    printf("sizeof(Student*) = %d, sizeof(Student) = %d\n",
           (int)sizeof(Student*), (int)sizeof(Student));
    return 0;
}""",
        "task": "写一个 Student *find_top(Student *a, int n) 返回成绩最高者的指针，在 main 里用 -> 打印它的名字。",
        "pitfall": "写成 *p.age 会先算 p.age（成员不存在）再解引用，编译直接报错；正确写法是 (*p).age 或 p->age。",
    },
    {
        "block": 25,
        "part": "阶段四 · 自定义数据类型",
        "ref": "谭浩强 9.5–9.6 · 何钦铭 9",
        "title": "共用体、枚举与 typedef",
        "idea": "union 让几个成员挤同一块内存（省空间但互斥），enum 给整数起名字（可读性），typedef 给类型起别名（少打字）。",
        "basics": [
            ["共用体 union",
             "union Data { int i; double d; char c; }; 所有成员从同一个地址开始，大小等于最大的成员（这里 8 字节）。"
             "给一个成员赋值会覆盖其他成员的内容，所以同一时刻只有一个成员是有效的。"
             "常见用途：让同一块内存按不同类型解释（查看浮点的字节）、节省内存的变体记录。用\"标签 + union\"组合可记录当前哪种类型有效。"],
            ["枚举 enum",
             "enum Weekday { MON, TUE, WED, THU, FRI, SAT, SUN }; 默认从 0 开始依次加 1，也可以指定：enum {A = 1, B, C};。"
             "枚举本质就是 int，能比较、能当 switch 的 case、能当数组下标，只是多了可读的名字。"
             "比到处写魔法数字 0、1、2 好得多。"],
            ["typedef",
             "typedef unsigned long long u64; 之后 u64 x; 就是声明。它和 #define 不同：typedef 是编译器处理的类型别名，"
             "有真正的类型检查；宏只是文本替换，容易出括号问题。工程里几乎都写 typedef struct {...} Point;。"],
            ["三者组合的实用场景",
             "typedef enum { INT, DOUBLE, STR } Kind; typedef struct { Kind kind; union { int i; double d; char s[16]; } val; } Value; "
             "——用一个 kind 记住\"当前 union 里哪个有效\"，这是手写小型解释器、配置项、协议解析的常见套路。"],
        ],
        "points": [
            "union 的大小 = 最大成员的大小，成员共享内存",
            "union 写一个成员会覆盖另一个，读之前要知道当前是哪个",
            "enum 本质是 int，可以比较、可以当 case 标签",
            "enum 默认从 0 递增，可手动指定起始值",
            "typedef 有类型检查，#define 只是文本替换",
            "typedef struct {...} Name; 之后可直接写 Name",
            "#define 定义常量时记得给整体加括号：(x)*(x)",
        ],
        "code": r"""#include <stdio.h>

union Data {                 // 三个成员共用同一块 8 字节内存
    int    i;
    double d;
    char   bytes[8];
};

enum Weekday { MON = 1, TUE, WED, THU, FRI, SAT, SUN };   // 从 1 开始

typedef unsigned long long u64;      // 起个短别名

struct Value {                       // 标签 + union：记住当前有效类型
    int kind;                        // 0 = 整数，1 = 小数
    union {
        int    i;
        double d;
    } u;
};

int main(void) {
    union Data v;
    v.i = 65;
    printf("union 大小 = %d\n", (int)sizeof(union Data));
    printf("按 int 读：%d，按 char 读第一个字节：%d（就是 'A'）\n", v.i, v.bytes[0]);

    v.d = 3.14;                      // 覆盖了刚才的 i
    printf("改成 double 后按 int 读：%d（内容已变）\n", v.i);

    enum Weekday today = WED;
    switch (today) {
        case MON: printf("周一\n"); break;
        case WED: printf("周三\n"); break;
        default:  printf("其他日子\n");
    }
    printf("WED 的值 = %d，SAT 的值 = %d\n", WED, SAT);

    u64 big = 1234567890123ULL;
    printf("u64 = %llu\n", big);

    struct Value a, b;
    a.kind = 0; a.u.i = 42;
    b.kind = 1; b.u.d = 2.5;
    printf("a = %d（kind=%d），b = %.1f（kind=%d）\n",
           a.u.i, a.kind, b.u.d, b.kind);
    return 0;
}""",
        "task": "给 union Data 加一个 float f; 成员，重新打印 sizeof（还是 8，因为 double 最大）；再用 enum 表示一周并写一个返回中文名字的函数。",
        "pitfall": "先给 union 的 i 赋值、再读 d，得到的不是\"转换结果\"而是同一串二进制被当成 double 解释——这叫类型双关，不是类型转换。",
    },
    {
        "block": 26,
        "part": "阶段四 · 自定义数据类型",
        "ref": "谭浩强 9.7 · 何钦铭 11",
        "title": "单链表",
        "idea": "链表是一串结点，每个结点存\"数据 + 指向下一个结点的指针\"，靠指针把分散的内存串起来，插入删除不用搬家。",
        "basics": [
            ["结点与头指针",
             "struct Node { int data; struct Node *next; }; 最后一个结点的 next 是 NULL，表示结尾。"
             "head 指向第一个结点；head == NULL 就表示空链表。链表不像数组能下标访问，找第 k 个必须从头一步步走。"],
            ["动态申请结点",
             "struct Node *p = (struct Node*)malloc(sizeof(struct Node)); 用 malloc 在堆上要空间，用完必须 free。"
             "申请后立刻判空（内存可能不够）：if (p == NULL) 处理错误。"],
            ["建立链表：头插与尾插",
             "头插法：新结点 next 指向原 head，再让 head = 新结点——简单，但输出的顺序和输入相反。"
             "尾插法：用一个 tail 指针记住末尾，新结点接在 tail 后面再更新 tail——保持输入顺序，稍复杂但更常用。"],
            ["遍历、删除、逆置",
             "遍历：for (p = head; p != NULL; p = p->next)。删除值为 x 的结点：先找前驱 prev，再 prev->next = p->next，最后 free(p)。"
             "逆置：三指针法——prev 初始 NULL，逐把 cur->next 指向 prev，再把 prev、cur 各往后挪一步。"],
        ],
        "points": [
            "访问 p->next 之前先确保 p != NULL",
            "malloc 之后要判空，free 之后把指针置 NULL",
            "删除结点必须 free，否则内存泄漏",
            "头插法输出逆序，尾插法保持原序",
            "遍历条件写 p != NULL，不要写 p->next != NULL（会漏最后一个）",
            "链表不支持随机访问，查第 k 个是 O(n)",
            "尾结点的 next 一定要置 NULL，否则遍历跑飞",
        ],
        "code": r"""#include <stdio.h>
#include <stdlib.h>

typedef struct Node {              // 结点：数据 + 指向下一个结点的指针
    int data;
    struct Node *next;
} Node;

Node *create_node(int value) {     // 申请并初始化一个结点
    Node *p = (Node*)malloc(sizeof(Node));
    if (p == NULL) {               // 堆内存可能申请失败
        printf("内存不足\n");
        exit(1);
    }
    p->data = value;
    p->next = NULL;
    return p;
}

void push_front(Node **head, int value) {   // 头插：新结点成为第一个
    Node *p = create_node(value);
    p->next = *head;
    *head = p;
}

void print_list(Node *head) {
    Node *p;
    for (p = head; p != NULL; p = p->next) {  // 注意条件不是 p->next
        printf("%d -> ", p->data);
    }
    printf("NULL\n");
}

int delete_value(Node **head, int value) {    // 删除第一个值为 value 的结点
    Node *prev = NULL, *cur = *head;
    while (cur != NULL && cur->data != value) {
        prev = cur;
        cur = cur->next;
    }
    if (cur == NULL) return 0;                // 没找到
    if (prev == NULL) *head = cur->next;      // 删的是头结点
    else              prev->next = cur->next;
    free(cur);                                // 释放，避免内存泄漏
    return 1;
}

void reverse(Node **head) {                   // 三指针逆置
    Node *prev = NULL, *cur = *head, *next;
    while (cur != NULL) {
        next = cur->next;                     // 先存住下一个
        cur->next = prev;                     // 反转指向
        prev = cur;                           // 三个指针整体后移
        cur = next;
    }
    *head = prev;                             // 新的头
}

void free_list(Node **head) {
    Node *p = *head, *next;
    while (p != NULL) {
        next = p->next;
        free(p);
        p = next;
    }
    *head = NULL;
}

int main(void) {
    Node *head = NULL;
    int i;
    for (i = 1; i <= 5; i++) push_front(&head, i);
    printf("建立后：");
    print_list(head);

    reverse(&head);
    printf("逆置后：");
    print_list(head);

    delete_value(&head, 3);
    printf("删除 3 后：");
    print_list(head);

    free_list(&head);
    printf("释放后 head = %s\n", head == NULL ? "NULL" : "非空");
    return 0;
}""",
        "task": "把 push_front 改成尾插法 push_back（需要遍历找尾或维护 tail 指针），确认输出顺序变成 1 到 5；再写一个函数统计链表长度。",
        "pitfall": "free(cur) 之后还去访问 cur->next，读的是已释放内存（悬垂指针）——所以必须先保存 next 再 free。",
    },
    {
        "block": 27,
        "part": "阶段四 · 自定义数据类型",
        "ref": "谭浩强（旧版第 12 章）· 多数教材位运算专章",
        "title": "位运算",
        "idea": "位运算直接操作整数的二进制位，用 & | ^ ~ << >> 做\"按位\"的开关和取位，是底层编程和算法题的基本功。",
        "basics": [
            ["二进制与补码",
             "int 占 32 位，每一位是 0 或 1。负数用补码表示：-1 是 32 个 1。十六进制 0x1F 是最常用的查看方式"
             "（一位十六进制 = 4 位二进制）。打印二进制要自己写循环：for (i = 31; i >= 0; i--) putchar((n >> i) & 1 ? '1' : '0');"],
            ["五个运算符",
             "& 按位与（同为 1 才 1，用来取位/清零）；| 按位或（有 1 就 1，用来置位）；^ 按位异或（不同为 1，用来翻转/交换）；"
             "~ 按位取反；<< 左移（低位补 0，相当于乘 2 的幂）；>> 右移（无符号数补 0，相当于除 2 的幂）。"],
            ["四个必会技巧",
             "① n & 1：判断奇偶（比 % 2 快）；② x & (x - 1)：把最低位的 1 清成 0，用来判断是不是 2 的幂、数 1 的个数；"
             "③ (x >> k) & 1：取第 k 位；④ x ^= y; y ^= x; x ^= y;：不用临时变量交换两数（要求两数地址不同）。"],
            ["位运算的边界",
             "移位位数不能 ≥ 类型宽度（对 32 位 int 移 32 位是未定义行为）；有符号负数左移也是未定义行为；"
             "所以做位运算优先用 unsigned。位字段（struct 里的 int a : 3;）是它的近亲，用于协议头这种紧凑结构。"],
        ],
        "points": [
            "& 与 && 完全不同：前者按位，后者逻辑",
            "n & 1 判奇偶，n & (n-1) 清最低位的 1",
            "n & (n-1) == 0 且 n > 0 就是 2 的幂",
            "x << k 等于乘 2^k，x >> k 等于除以 2^k（整数）",
            "移位位数超过位宽是未定义行为",
            "用 ^ 交换两数时，两个变量不能是同一个地址",
            "无符号数做位运算最安全，避免符号位捣乱",
        ],
        "code": r"""#include <stdio.h>

void print_bin(unsigned int n) {          // 手写打印 32 位二进制
    int i;
    for (i = 31; i >= 0; i--) {
        putchar(((n >> i) & 1) ? '1' : '0');
        if (i % 8 == 0 && i != 0) putchar(' ');   // 每 8 位空格
    }
    putchar('\n');
}

int count_ones(unsigned int n) {          // 数二进制里 1 的个数
    int c = 0;
    while (n) {
        n &= n - 1;                       // 每次清掉最低位的 1
        c++;
    }
    return c;
}

int main(void) {
    int x = 5, y = 3;
    printf("x = %d -> ", x);   print_bin(x);
    printf("y = %d -> ", y);   print_bin(y);
    printf("x & y = %d\n", x & y);      // 0001
    printf("x | y = %d\n", x | y);      // 0111
    printf("x ^ y = %d\n", x ^ y);      // 0110
    printf("~x    = %d\n", ~x);         // 全取反，得负数
    printf("x << 1 = %d（乘 2），x >> 1 = %d（除 2）\n", x << 1, x >> 1);

    printf("x 是%s\n", (x & 1) ? "奇数" : "偶数");
    printf("x 第 2 位 = %d\n", (x >> 2) & 1);

    unsigned int n = 0xF0;             // 240
    printf("n = %u -> ", n);  print_bin(n);
    printf("n 中 1 的个数 = %d\n", count_ones(n));

    int a = 10, b = 20;
    a ^= b; b ^= a; a ^= b;            // 不用临时变量交换
    printf("交换后 a = %d, b = %d\n", a, b);

    unsigned int flag = 0;
    flag |= (1u << 3);                 // 置位：打开第 3 号标志
    printf("置位后 flag = %u\n", flag);
    flag &= ~(1u << 3);                // 清零：关掉第 3 号标志
    printf("清零后 flag = %u\n", flag);
    return 0;
}""",
        "task": "写一个 int get_bit(int n, int k) 取第 k 位、void set_bit(int *n, int k) 把第 k 位置 1，再用它实现\"用 32 位整数记录 32 个开关状态\"。",
        "pitfall": "把 n & 1 写成 n && 1：后者是逻辑与，结果恒为 1（只要 n 非 0），判断奇偶永远输出\"奇数\"。",
    },
]
