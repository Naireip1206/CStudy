# -*- coding: utf-8 -*-
"""lessons_b.py —— 课程 10~18（阶段二收尾 + 阶段三：指针）

字段说明见 lessons_a.py。code 一律用 r\"\"\" 原始字符串，代码内只用英文标点。
"""

LESSONS = [
    {
        "block": 10,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 6.3 · 何钦铭 7.2",
        "title": "二维数组与矩阵",
        "idea": "二维数组就是\"数组的数组\"：a[3][4] 是 3 个长度为 4 的一维数组排在一起，用两个下标定位。",
        "basics": [
            ["定义与下标",
             "int a[3][4]; 表示 3 行 4 列共 12 个 int。访问 a[i][j]，i 是行号（0~2），j 是列号（0~3）。"
             "把第一维想成\"第几个班\"、第二维想成\"班里第几个学生\"最容易理解。"],
            ["初始化",
             "按行写最清楚：int a[2][3] = {{1,2,3},{4,5,6}};。也可以把所有数摊平写：int a[2][3] = {1,2,3,4,5,6};"
             "（按行优先依次填）。只写部分元素时其余自动补 0。第二维长度不能省略，第一维可以：int a[][3] = {{1,2,3}}。"],
            ["内存布局：行优先",
             "二维数组在内存里是一条连续的线，按\"先第一行全部、再第二行……\"的顺序排列。"
             "所以 a[i][j] 的地址 = 首地址 + (i * 列数 + j) * sizeof(int)。理解这一点，后面学数组指针才不懵。"],
            ["常见矩阵操作",
             "输入输出（双重循环）、每行求和、每列求和、求最大值及其行列、主/副对角线和、转置（行列互换）、杨辉三角。"
             "注意转置只能对\"新数组\"做，对非方阵原地转置会互相覆盖。"],
        ],
        "points": [
            "a[3][4] 合法下标是 a[0][0] ~ a[2][3]，别用到 a[3]",
            "第二维长度必须写，函数参数里也要写全：int a[][4]",
            "遍历习惯是外层 i 走行、内层 j 走列",
            "按行优先存储：a[i][j] 前面有 i*列数+j 个元素",
            "转置要写入另一个数组：b[j][i] = a[i][j]",
            "打印对齐用 %4d，否则列会错开",
            "两个下标都从 0 开始，i 和 j 千万别写反",
        ],
        "code": r"""#include <stdio.h>

int main(void) {
    int a[3][3];
    int i, j;

    printf("输入 3x3 矩阵：\n");
    for (i = 0; i < 3; i++) {            // 外层走行
        for (j = 0; j < 3; j++) {        // 内层走列
            scanf("%d", &a[i][j]);
        }
    }

    printf("你输入的矩阵：\n");
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 3; j++) {
            printf("%4d", a[i][j]);      // %4d 保证列对齐
        }
        printf("\n");
    }

    for (i = 0; i < 3; i++) {            // 每行求和
        int row_sum = 0;
        for (j = 0; j < 3; j++) row_sum += a[i][j];
        printf("第 %d 行和 = %d\n", i + 1, row_sum);
    }

    int trace = 0;
    for (i = 0; i < 3; i++) trace += a[i][i];   // 主对角线 i == j
    printf("主对角线和 = %d\n", trace);

    printf("转置：\n");
    for (i = 0; i < 3; i++) {                   // 注意输出时行列互换
        for (j = 0; j < 3; j++) {
            printf("%4d", a[j][i]);
        }
        printf("\n");
    }
    return 0;
}""",
        "task": "把转置改成写进新数组 b[3][3]，再遍历 b 打印；然后把 3x3 改成 3x4，试试还能不能原地转置。",
        "pitfall": "把 a[j][i] 写成 a[i][j] 是最常见的转置错误——结果看着\"没错\"，其实一行都没换。",
    },
    {
        "block": 11,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 6.4 · 何钦铭 7.3–7.4",
        "title": "字符数组与字符串",
        "idea": "C 没有专门的字符串类型，字符串就是一串 char，靠末尾的 '\\0' 告诉程序\"到这儿结束了\"。",
        "basics": [
            ["字符串的本质",
             "字符串 = 字符数组 + 末尾的 '\\0'（编码为 0 的字符）。所以 \"hello\" 占 6 个字节，不是 5 个。"
             "'\\0' 是结束标记，不是字符 '0'（'0' 的编码是 48）。所有字符串函数都靠它找结尾。"],
            ["三种定义方式",
             "char s[10] = \"hello\";（可修改，剩余补 0）、char s[] = \"hello\";（自动长度 6）、"
             "char s[6] = {'h','e','l','l','o','\\0'};（手工逐个填，别忘了 '\\0'）。"
             "char *p = \"hello\"; 是指向只读字符串常量的指针，内容不能改。"],
            ["输入输出",
             "scanf(\"%s\", s) 遇到空格/换行就停，且不检查长度；输出用 printf(\"%s\") 或 puts(s)（自动换行）。"
             "要连空格一起读，用 fgets(s, sizeof(s), stdin)，它会保留换行符，需要自己处理。"
             "字符数组的名字本身就是地址，scanf 时不要加 &。"],
            ["标准字符串函数（#include <string.h>）",
             "strlen(s) 求长度（不含 '\\0'）；strcpy(dst, src) 复制；strcat(dst, src) 拼接；"
             "strcmp(a, b) 比较，相等返回 0，a 大返回正数，a 小返回负数。这些函数都假定目标空间够大，"
             "自己不检查长度——这个责任在你。"],
        ],
        "points": [
            "'\\0' 一定占一个字节，char s[5] = \"hello\" 放不下，会越界",
            "字符串长度是不含 '\\0' 的字符数，strlen(\"abc\") = 3",
            "比较字符串用 strcmp，用 == 比较的是两个地址",
            "strcpy/strcat 不检查目标长度，目标数组要够大",
            "字符数组名是地址，scanf 时不加 &",
            "字符串常量不能修改：char *p = \"abc\"; p[0] = 'x'; 会崩",
            "fgets 保留换行符，讲长度前要先把结尾的 '\\n' 去掉",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>              // strlen/strcpy/strcat/strcmp 都在这里

int main(void) {
    char name[20];
    printf("输入名字：");
    scanf("%19s", name);         // 限宽 19，留 1 个字节给 '\0'
    printf("你好，%s（长度 %d）\n", name, (int)strlen(name));

    char a[20] = "C";
    char b[]   = "语言";
    strcat(a, b);                // 把 b 接到 a 后面，a 必须够大
    printf("拼接后：%s\n", a);

    char copy[20];
    strcpy(copy, a);             // 复制，注意目标空间
    printf("复制后：%s\n", copy);

    printf("strcmp(\"abc\",\"abd\") = %d\n", strcmp("abc", "abd"));   // 负数：abc 更小
    printf("strcmp(\"abc\",\"abc\") = %d\n", strcmp("abc", "abc"));   // 0：相等

    char line[50];
    printf("输入一句话（可含空格）：\n");
    fgets(line, sizeof(line), stdin);       // 会读到上一行残留的换行
    fgets(line, sizeof(line), stdin);       // 再读一次才拿到真正输入
    line[strcspn(line, "\n")] = '\0';       // 去掉末尾换行
    printf("你说的是：[%s]，长度 %d\n", line, (int)strlen(line));
    return 0;
}""",
        "task": "把 char name[20] 改成 char name[5]，输入超过 4 个字的名字，看看会发生什么；再把 strcmp(\"abc\",\"abd\") 换成 \"abd\",\"abc\" 看符号变不变。",
        "pitfall": "用 if (s1 == s2) 比较字符串永远不成立（比的是地址），必须写 if (strcmp(s1, s2) == 0)。",
    },
    {
        "block": 12,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 6.4 例题 · 何钦铭 7.4、10",
        "title": "字符串实战",
        "idea": "字符串题的套路只有三个：逐字符遍历、双指针首尾夹、借助 strlen/strstr 这类现成函数。",
        "basics": [
            ["逐字符遍历",
             "for (i = 0; s[i] != '\\0'; i++) 是最稳的写法——不依赖 strlen，也不怕中途改内容。"
             "统计字母/数字/空格、大小写转换、加密解密都靠它。判断数字字符用 s[i] >= '0' && s[i] <= '9'，不要写 0 <= s[i] <= 9。"],
            ["双指针首尾夹",
             "回文判断的标准写法：i 指向头、j 指向尾，s[i] == s[j] 就 i++、j--，一旦不等直接判否。"
             "原地反转也用它：交换 s[i] 和 s[j] 直到 i >= j。"],
            ["单词计数",
             "用标志变量 in_word 记录\"当前是否在单词里\"：遇到非空白且 in_word == 0 时，单词数加一并把标志置 1；"
             "遇到空白把标志清 0。这样不管中间有几个空格都不会重复计数。"],
            ["子串与删除",
             "查找子串可以直接用 strstr(s, sub)，返回首次出现的指针（找不到返回 NULL）。"
             "删除字符要\"把后面的往前挪\"：找到目标后用循环 s[i] = s[i+1] 覆盖，最后记得补 '\\0'；"
             "更省事的写法是双指针原地过滤（保留的才写入新位置）。"],
        ],
        "points": [
            "遍历字符串的终止条件是 s[i] != '\\0'，不是长度写死",
            "字符判断要用字符区间：c >= 'a' && c <= 'z'",
            "单词数 = 从空白进入非空白的次数",
            "回文判断不需要真的反转，双指针比较即可",
            "strstr 返回指针，配合 s - str 可算出起始下标",
            "删除/插入后一定要维护 '\\0'",
            "中文是多字节编码，按字节统计出来的长度不是字数",
        ],
        "code": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char s[100];
    printf("输入一行字符：\n");
    fgets(s, sizeof(s), stdin);
    s[strcspn(s, "\n")] = '\0';      // 去掉换行

    int letters = 0, digits = 0, spaces = 0, words = 0, in_word = 0;
    int i;
    for (i = 0; s[i] != '\0'; i++) {
        char c = s[i];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) letters++;
        else if (c >= '0' && c <= '9') digits++;
        else if (c == ' ') spaces++;

        if (c != ' ' && !in_word) { words++; in_word = 1; }   // 进入新单词
        if (c == ' ') in_word = 0;                            // 离开单词
    }
    printf("字母 %d，数字 %d，空格 %d，单词 %d\n", letters, digits, spaces, words);

    char p[100];
    strcpy(p, s);
    int L = (int)strlen(p), is_pal = 1;
    for (i = 0; i < L / 2; i++) {
        if (p[i] != p[L - 1 - i]) { is_pal = 0; break; }
    }
    printf("是否回文：%s\n", is_pal ? "是" : "否");

    for (i = 0; p[i] != '\0'; i++) {          // 大写转小写
        if (p[i] >= 'A' && p[i] <= 'Z') p[i] = p[i] - 'A' + 'a';
    }
    printf("转小写后：%s\n", p);
    return 0;
}""",
        "task": "再加一段统计每个字母出现次数（用 int cnt[26] = {0};，cnt[c - 'a']++）；然后输入一个包含 a 的句子，把 a 全部删除后输出。",
        "pitfall": "统计单词数时只看\"当前是空格\"会多数或少数；必须记录\"上一个状态\"，用 in_word 标志最稳。",
    },
    {
        "block": 13,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 7.1–7.3 · 何钦铭 5",
        "title": "函数",
        "idea": "函数是把一段代码打包、起名、留出入口（参数）和出口（返回值），需要时喊一声就执行。",
        "basics": [
            ["定义与调用",
             "返回类型 函数名(参数表) { 函数体 }。int add(int a, int b) { return a + b; }，调用 add(3, 5)。"
             "没有返回值写 void；不接收参数写 (void)。函数必须先声明/定义再调用，否则编译器不知道它长什么样。"],
            ["形参与实参：值传递",
             "调用时把实参的值复制一份给形参，函数里改的只是副本，改不到外面的变量。这是 C 的默认规则，"
             "也是后面必须学指针的原因（见第 15、20 节）。函数只能 return 一个值，需要多个结果时用指针参数或结构体。"],
            ["声明、定义、头文件",
             "大型程序里，函数声明放在 .h 头文件或 main 之前，定义可以写在文件后面。"
             "声明只要\"返回类型 + 名字 + 参数类型\"，不用写函数体：int add(int a, int b);。"],
            ["分而治之",
             "好函数的标志：只做一件事、名字说清干什么、长度普遍不超过一屏。"
             "把\"判断素数\"抽成 is_prime(n)，主函数就只剩\"循环 + 调用\"，可读性和复用性立刻上去。"
             "标准库函数（printf、strlen、sqrt）也是函数，只是别人写好了。"],
        ],
        "points": [
            "函数不能定义在另一个函数里面（不能嵌套定义）",
            "非 void 函数一定要 return，否则返回值不确定",
            "形参是副本，函数内修改不影响实参",
            "一个函数只能返回一个值",
            "函数名不要和标准库重名（abs、max 之类要小心）",
            "参数个数、类型要和声明一致，编译器会帮你查",
            "能复用的代码就抽成函数，别复制粘贴三遍",
        ],
        "code": r"""#include <stdio.h>
#include <math.h>

int add(int a, int b);              // 函数声明（原型），让编译器提前知道
int is_prime(int n);                // 判断素数：是返回 1，否返回 0

int main(void) {
    printf("add(3, 5) = %d\n", add(3, 5));

    int n, i;
    printf("输入 n，输出 n 以内的素数：");
    scanf("%d", &n);
    int count = 0;
    for (i = 2; i <= n; i++) {
        if (is_prime(i)) {          // 直接当条件用，返回 1/0
            printf("%d ", i);
            count++;
        }
    }
    printf("\n共 %d 个\n", count);
    printf("sqrt(2) = %.4f\n", sqrt(2.0));
    return 0;
}

int is_prime(int n) {
    if (n < 2) return 0;            // 0、1 和负数都不是素数
    int i;
    for (i = 2; i * i <= n; i++) {  // 只试到根号 n，效率高
        if (n % i == 0) return 0;   // 找到因子，立刻返回假
    }
    return 1;
}

int add(int a, int b) {             // 定义可以放在后面
    return a + b;
}""",
        "task": "写一个 int max3(int a, int b, int c) 返回三个数的最大值，在 main 里读三个数并调用它；再写一个 void print_line(int n) 打印 n 个星号。",
        "pitfall": "把函数定义写在调用之后又不加声明，会报 implicit declaration of function，并在新标准里直接报错。",
    },
    {
        "block": 14,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 7.4–7.5 · 何钦铭 10",
        "title": "作用域与存储类别",
        "idea": "作用域管\"这个名字在哪儿能被看见\"，存储类别管\"这个变量活多久、放在哪儿\"。",
        "basics": [
            ["局部变量",
             "在函数或大括号里定义的变量，出了这对大括号就消失，别处用不了。局部变量不初始化时里面是垃圾值，"
             "所以必须手动赋值。不同函数里的同名局部变量互不影响。"],
            ["全局变量",
             "在所有函数外面定义，从定义处往下都能用，程序运行期间一直存在，且自动初始化为 0。"
             "方便但有代价：谁都能改，出 bug 难查，还容易和局部变量重名。能用参数传就别用全局。"],
            ["static 的两种含义",
             "① 修饰局部变量：只初始化一次，函数返回后值还在，下次调用接着用（典型用途是计数器、缓存）；"
             "② 修饰全局变量/函数：把可见范围限制在本文件内，别的 .c 文件看不到，避免命名冲突。"],
            ["extern 与 register",
             "extern 是声明\"这个变量/函数在别处定义\"，用于跨文件共享；register 只是建议把变量放进寄存器，"
             "现代编译器基本自己决定，可以不用。"],
        ],
        "points": [
            "局部变量出作用域即销毁，全局变量活到程序结束",
            "同名时局部优先，想用全局需要 ::（C 没有）——所以干脆别重名",
            "static 局部变量只初始化一次，值跨调用保留",
            "全局数组自动清零，局部数组不会",
            "作用域越小越好：能用局部就别写全局",
            "static 函数只在本文件可见，是模块化的常用手段",
            "变量在使用处附近定义（C99 允许），可读性更好",
        ],
        "code": r"""#include <stdio.h>

int total = 0;                     // 全局变量，自动初始化为 0

int next_id(void) {
    static int id = 0;             // 只初始化一次，下次调用还接着涨
    id++;
    return id;
}

void add_to_total(int x) {
    total += x;                    // 改的是全局变量
}

int main(void) {
    printf("next_id: %d %d %d\n", next_id(), next_id(), next_id());

    int i;
    for (i = 1; i <= 3; i++) {
        add_to_total(i * 10);
    }
    printf("total = %d\n", total);

    {
        int local = 99;            // 只在这个大括号里存在
        printf("块内 local = %d\n", local);
    }
    printf("循环变量 i 出了循环仍然可见（C89 规则）= %d\n", i);

    for (int k = 0; k < 2; k++) {  // C99：循环内定义，仅循环内可见
        printf("k = %d\n", k);
    }
    return 0;
}""",
        "task": "把 static int id = 0; 改成 int id = 0;，再连续调用三次 next_id，观察输出变成什么（每次都返回 1）。",
        "pitfall": "以为 static 局部变量\"每次调用都重新初始化\"——它只初始化一次，这正是它做计数器的原理。",
    },
    {
        "block": 15,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 7.6 · 何钦铭 5、7",
        "title": "数组作函数参数与值传递",
        "idea": "普通变量传给函数是复制一份，改不到原变量；数组传的却是首地址，所以函数能改到数组内容。",
        "basics": [
            ["值传递：为什么 swap 不管用",
             "void swap(int a, int b) 里交换的只是两个副本，函数结束后原变量纹丝不动。这是 C 的默认行为，不是 bug。"
             "想真交换必须传地址：void swap(int *a, int *b)，调用时写 swap(&x, &y)（第 20 节详讲）。"],
            ["数组参数的真相",
             "形参写成 int a[] 或 int a[10]，编译器都当成 int *a——传进来的只是首地址，不是整个数组的拷贝。"
             "所以：① 函数里对 a[i] 的修改会反映到调用方；② 函数里 sizeof(a) 得到的是指针大小（8），不是数组总字节数，"
             "因此长度必须另传一个 n。"],
            ["数组参数的标准写法",
             "int sum(int a[], int n) 或 int sum(int *a, int n)，两种写法完全等价。调用时直接写 sum(arr, n)，"
             "数组名不用加 &。返回值可以返回和、最大值，但只有一个——要同时拿最大值和下标，就得用指针参数。"],
            ["函数划分的实战思路",
             "一道数组题通常拆成：input(a, n) 读入、process(a, n) 处理、output(a, n) 输出。"
             "这样 main 只剩三行，逻辑一眼看清，也方便单独调试某一步。"],
        ],
        "points": [
            "普通变量按值传递，数组按地址传递（本质是传首地址）",
            "函数里算数组长度必须用参数 n，不能用 sizeof",
            "形参 int a[10] 不代表只能传 10 个元素，那只是书写形式",
            "传数组时实参不写 &，写 arr 就行",
            "函数内越界同样会踩内存，边界检查得自己负责",
            "想返回多个结果用指针参数",
            "数组元素很多时传地址比复制高效得多",
        ],
        "code": r"""#include <stdio.h>

int sum_array(int a[], int n) {          // 形参 int a[] 等价于 int *a
    int s = 0, i;
    for (i = 0; i < n; i++) s += a[i];
    return s;
}

double average(int a[], int n) {
    return (double)sum_array(a, n) / n;  // 复用上面的函数
}

void swap_bad(int a, int b) {            // 反例：只换了副本
    int t = a; a = b; b = t;
}

void swap_ok(int *a, int *b) {           // 正解：换地址里的内容
    int t = *a; *a = *b; *b = t;
}

void print_array(int a[], int n) {
    int i;
    for (i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    int a[5] = {3, 1, 4, 1, 5};
    printf("和 = %d，平均 = %.2f\n", sum_array(a, 5), average(a, 5));
    printf("函数里 sizeof(a) 会得到 %d（指针大小），不是 20\n", (int)sizeof(&a[0]));

    int x = 1, y = 2;
    swap_bad(x, y);
    printf("swap_bad 之后 x=%d y=%d（没变）\n", x, y);
    swap_ok(&x, &y);
    printf("swap_ok  之后 x=%d y=%d（变了）\n", x, y);

    print_array(a, 5);
    return 0;
}""",
        "task": "写一个 int find_max(int a[], int n, int *max_index) 返回最大值并把下标写进 *max_index，在 main 里调用验证。",
        "pitfall": "在函数里写 n = sizeof(a) / sizeof(a[0]) 求长度，结果永远是 2 或 1（指针相除），必须把 n 当参数传进来。",
    },
    {
        "block": 16,
        "part": "阶段二 · 批量数据与函数",
        "ref": "谭浩强 7.7 · 何钦铭 10",
        "title": "递归",
        "idea": "递归就是函数自己调用自己：把大问题变成同样形状的小问题，直到小到能直接回答。",
        "basics": [
            ["两个必备条件",
             "① 出口（base case）：能直接给出答案的最小情况，比如 factorial(0) 返回 1；"
             "② 递推：把 n 的问题化成 n-1 的问题，且每一步都在向出口靠近。缺任何一个都会无限递归，"
             "最终栈溢出（程序直接崩溃）。"],
            ["执行过程：栈",
             "factorial(3) 会先挂起自己、去算 factorial(2)，再挂起、算 factorial(1)……回来后一层层乘上去。"
             "函数的局部变量在每一层都各有一份（存在栈上），互不干扰。递归层数太深（几万层）会爆栈。"],
            ["经典模型",
             "阶乘 n! = n * (n-1)!；斐波那契 f(n) = f(n-1) + f(n-2)；最大公约数 gcd(a,b) = gcd(b, a%b)；"
             "汉诺塔 hanoi(n) = 2*hanoi(n-1) + 1 步；二分查找、快速排序、树的遍历也都靠递归。"],
            ["递归 vs 循环",
             "能用循环且更直观（求和、遍历）就用循环；问题本身是\"分治/树形\"（汉诺塔、全排列、快排）时递归代码最短。"
             "朴素递归求斐波那契是 O(2^n)，n=40 就明显卡，这时要换成循环或记忆化。"],
        ],
        "points": [
            "必须先写出口，再写递推，顺序不能反",
            "递归参数一定要朝着出口变化（n-1、n/2、a%b）",
            "每层局部变量独立，别指望下一层能改上一层的变量",
            "朴素递归可能重复计算，注意复杂度",
            "递归深度几千层就可能爆栈，工程上要评估",
            "汉诺塔 n 个盘子需要 2^n - 1 步",
            "写不出递推式时，先想\"n 的情况能不能用 n-1 的答案拼出来\"",
        ],
        "code": r"""#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 1;               // 出口：0! 和 1! 都是 1
    return n * factorial(n - 1);        // 递推：n! = n * (n-1)!
}

int fib(int n) {
    if (n <= 2) return 1;               // 出口
    return fib(n - 1) + fib(n - 2);     // 递推
}

int gcd(int a, int b) {
    if (b == 0) return a;               // 出口：余数为 0
    return gcd(b, a % b);               // 辗转相除的递归写法
}

void hanoi(int n, char from, char via, char to) {
    if (n == 1) {                       // 只剩一个盘子，直接搬
        printf("%c -> %c\n", from, to);
        return;
    }
    hanoi(n - 1, from, to, via);        // 先把上面 n-1 个挪到中转柱
    printf("%c -> %c\n", from, to);     // 搬最大的那个
    hanoi(n - 1, via, from, to);        // 再把 n-1 个挪到目标柱
}

int main(void) {
    printf("5! = %lld\n", factorial(5));
    printf("fib(10) = %d\n", fib(10));
    printf("gcd(48, 18) = %d\n", gcd(48, 18));
    printf("3 层汉诺塔步骤：\n");
    hanoi(3, 'A', 'B', 'C');
    return 0;
}""",
        "task": "写一个递归函数 int sum_to(int n) 求 1+...+n；再写 int power(int base, int exp) 用递归算乘方，比较它和循环版的写法。",
        "pitfall": "删掉 if (n <= 1) return 1; 这一行，程序立刻栈溢出崩溃——递归没有出口就等于无限调用。",
    },
    {
        "block": 17,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.1–8.2 · 何钦铭 8",
        "title": "指针基础",
        "idea": "内存每个字节都有编号（地址），指针就是专门用来存地址的变量，顺着地址就能读写那块内存。",
        "basics": [
            ["地址与取地址",
             "变量存在内存里，&x 取得它的地址。地址本身是个整数（64 位系统 8 字节），用 %p 打印，"
             "习惯配合 (void*) 转换。取地址符 & 只能用于变量，不能用于常量或表达式。"],
            ["指针变量的定义与使用",
             "int *p = &a; 读法：p 是\"指向 int 的指针\"。* 在定义里表示类型，在表达式里表示解引用（取地址里的值）。"
             "所以 *p 就是 a，改 *p 等于改 a。指针的类型很重要，它决定 *(p+1) 往后走几个字节。"],
            ["空指针与野指针",
             "int *p = NULL; 表示\"暂时不指向任何东西\"，解引用它会崩溃。定义指针却没初始化（野指针）更危险——"
             "它指向一个随机地址，写进去可能破坏别处数据。规则：定义时要么给有效地址，要么给 NULL。"],
            ["指针的大小与类型",
             "不管指向 int 还是 double，指针本身在 64 位系统里都是 8 字节（sizeof(p) == 8）。"
             "但 p+1 的步长由指向类型决定：int* 走 4 字节，double* 走 8 字节，char* 走 1 字节。"],
        ],
        "points": [
            "& 取地址，* 解引用，两者互为逆运算",
            "指针使用前必须指向有效内存，或至少是 NULL",
            "不能解引用 NULL 和野指针，会段错误",
            "int *p, q; 里只有 p 是指针，q 是普通 int",
            "指针大小固定 8 字节（64 位），与指向类型无关",
            "指针相减得到相隔的元素个数，相加没有意义",
            "打印地址用 printf(\"%p\", (void*)p)",
        ],
        "code": r"""#include <stdio.h>

int main(void) {
    int a = 10;
    int *p = &a;                       // p 保存 a 的地址

    printf("a 的值 = %d\n", a);
    printf("a 的地址 = %p\n", (void*)&a);
    printf("p 里存的 = %p\n", (void*)p);
    printf("*p 取到的 = %d\n", *p);     // 顺着地址找回来，就是 10

    *p = 99;                           // 通过指针改 a
    printf("改完 a = %d\n", a);

    int b = 20;
    p = &b;                            // 指针可以改指向
    printf("现在 *p = %d\n", *p);

    int *q = NULL;                     // 空指针：明确表示不指向任何东西
    if (q != NULL) printf("%d\n", *q); // 解引用前先判空，这是纪律
    else printf("q 是空指针，不能解引用\n");

    printf("sizeof(int*) = %d，sizeof(int) = %d\n",
           (int)sizeof(int*), (int)sizeof(int));
    return 0;
}""",
        "task": "定义 double d = 2.5; double *pd = &d; 打印 pd、*pd 和 sizeof(pd)；再试试 int *bad; *bad = 1; 看程序怎么崩（理解野指针）。",
        "pitfall": "int *p; 之后直接 *p = 5; 是野指针写入，程序可能当下不崩、过几行才莫名其妙崩——定义指针时一定要初始化。",
    },
    {
        "block": 18,
        "part": "阶段三 · 指针",
        "ref": "谭浩强 8.3 · 何钦铭 8",
        "title": "指针与一维数组",
        "idea": "数组名就是首元素地址，所以指针能像数组一样用：a[i] 和 *(a+i) 是同一件事。",
        "basics": [
            ["数组名 = 首地址",
             "在表达式里，数组名 a 会自动退化成 &a[0]。于是 *(a + i) 就是 a[i]，两者完全等价（连 i[a] 都合法，但别这么写）。"
             "区别只有一个：a 是常量，不能 a++；想移动就用指针 int *p = a;"],
            ["指针算术",
             "p + 1 不是地址加 1 字节，而是\"往后跳一个元素\"（int* 跳 4 字节）。"
             "所以 for (p = a; p < a + n; p++) 正好遍历 n 个元素；两个指针相减得到它们之间隔了几个元素。"],
            ["三种等价的遍历写法",
             "下标法 a[i]；指针偏移 *(a + i)；指针自增 *p++。考试爱考\"这三段输出是否相同\"，答案是相同。"
             "注意 *p++ 的含义：先取 *p，再让 p 自增（因为 ++ 优先级高于 *，但这里是后缀，先取值）。"],
            ["&a 与 a 的区别",
             "a 是首元素地址，类型 int*，+1 走 4 字节；&a 是整个数组的地址，类型 int(*)[n]，+1 走整个数组（n*4 字节）。"
             "两者数值相同，含义不同——这是面试和考试的高频辨析点。"],
        ],
        "points": [
            "a[i] ≡ *(a + i)，数组和指针在访问上完全等价",
            "数组名是常量地址，不能自增；指针变量可以",
            "p + 1 按元素大小跳，不是按字节",
            "两个指针相减 = 相隔元素个数，类型是 ptrdiff_t",
            "遍历时用 p < a + n 作条件，别用 p <= a + n - 1 绕晕自己",
            "指针越界和数组越界一样是未定义行为，不报错但危险",
            "&a 的类型是 int(*)[n]，与 a 不是同一类型",
        ],
        "code": r"""#include <stdio.h>

int main(void) {
    int a[5] = {10, 20, 30, 40, 50};
    int *p = a;                       // 等价于 p = &a[0]

    printf("下标法：");
    for (int i = 0; i < 5; i++) printf("%d ", a[i]);
    printf("\n指针偏移法：");
    for (int i = 0; i < 5; i++) printf("%d ", *(a + i));
    printf("\n指针自增法：");
    for (p = a; p < a + 5; p++) printf("%d ", *p);
    printf("\n");

    int sum = 0;
    for (p = a; p < a + 5; p++) sum += *p;
    printf("和 = %d\n", sum);

    int *q = &a[4];
    printf("q - a = %d（相隔 %d 个元素）\n", (int)(q - a), (int)(q - a));

    printf("a      = %p（首元素地址，+1 走 %d 字节）\n", (void*)a, (int)sizeof(*a));
    printf("&a     = %p（整个数组地址，+1 走 %d 字节）\n", (void*)&a, (int)sizeof(a));

    p = a + 2;                        // 指向 30
    printf("p[0]=%d, p[-1]=%d, p[1]=%d\n", p[0], p[-1], p[1]);  // 指针也能用下标
    return 0;
}""",
        "task": "用指针写一个 void reverse(int *a, int n) 原地反转数组；再验证 *(a + i) 和 a[i] 输出是否永远一致。",
        "pitfall": "写 a++ 想移动数组名会直接编译报错（lvalue required）——数组名是常量，要移动必须用指针变量。",
    },
]
