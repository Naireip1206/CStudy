# -*- coding: utf-8 -*-
"""quizzes.py —— 全部测验题（72 道，覆盖 36 个知识块，每块 2 道）

字段：
    lesson   对应知识块编号（1~36）
    question 题干（代码换行用 \n）
    options  四个选项 [A, B, C, D]
    answer   正确选项下标 0~3（不是字母！）
    explain  解析

data.py 通过 `from quizzes import QUIZZES` 取用。
"""

QUIZZES = [
    {
        "lesson": 1,
        "question": "下面哪一行能正确打印出 \"Hello\" 并换行？",
        "options": [
            "printf(\"Hello\");",
            "printf(\"Hello\\n\");",
            "print(\"Hello\\n\");",
            "printf(Hello\\n);"
        ],
        "answer": 1,
        "explain": "printf 才是正确函数名；\\n 是换行；文字必须用双引号包起来。"
    },
    {
        "lesson": 1,
        "question": "程序末尾 return 0; 里的 0 表示什么？",
        "options": [
            "程序出错了",
            "打印 0 个字符",
            "程序正常结束",
            "返回到第 0 行"
        ],
        "answer": 2,
        "explain": "约定俗成：return 0 表示程序正常结束；返回非 0 才表示出错。"
    },
    {
        "lesson": 2,
        "question": "printf(\"x=%d\", x); 里的 %d 是什么意思？",
        "options": [
            "打印一个字符",
            "打印一个小数",
            "打印一个整数",
            "打印一个地址"
        ],
        "answer": 2,
        "explain": "%d 是整数的占位符；%f 是小数、%c 是字符、%p 是地址。"
    },
    {
        "lesson": 2,
        "question": "想存一个带小数的数，应该用哪种类型？",
        "options": [
            "int",
            "double",
            "char",
            "void"
        ],
        "answer": 1,
        "explain": "int 只能存整数，double 才能存小数（float 也可以，但精度更低）。"
    },
    {
        "lesson": 3,
        "question": "int a = 7, b = 2;\nprintf(\"%d %d\", a / b, a % b);\n输出是什么？",
        "options": [
            "3 1",
            "3.5 1",
            "3 3.5",
            "2 1"
        ],
        "answer": 0,
        "explain": "两边都是 int，a/b 做整数除法得 3（小数被截掉），a%b 取余得 1。想要 3.5 必须写成 7.0/2 或 (double)a/b。"
    },
    {
        "lesson": 3,
        "question": "表达式 5 % 3 + 5 / 2 的值是多少？",
        "options": [
            "4",
            "3.5",
            "5",
            "3"
        ],
        "answer": 0,
        "explain": "% 和 / 优先级相同且高于 +，从左往右算：5%3=2，5/2=2（整除），2+2=4。"
    },
    {
        "lesson": 4,
        "question": "要把一个整数读进变量 n，正确的是？",
        "options": [
            "scanf(\"%d\", n);",
            "scanf(\"%d\", &n);",
            "scanf(\"%f\", &n);",
            "scanf(\"%c\", &n);"
        ],
        "answer": 1,
        "explain": "scanf 读整数用 %d，而且变量名前必须加 &（取地址）；%f 是小数、%c 是字符。"
    },
    {
        "lesson": 4,
        "question": "输入 5 后，下面代码输出什么？\n  int n;\n  scanf(\"%d\", &n);\n  printf(\"%d\", n * 2);",
        "options": [
            "5",
            "10",
            "n*2",
            "编译报错"
        ],
        "answer": 1,
        "explain": "n 读进 5，n*2 = 10，所以打印 10。"
    },
    {
        "lesson": 5,
        "question": "判断变量 x 是否等于 10，正确的是？",
        "options": [
            "if (x = 10)",
            "if (x == 10)",
            "if (x === 10)",
            "if x == 10"
        ],
        "answer": 1,
        "explain": "相等比较用 ==（两个等号）；一个 = 是赋值，=== 是别的语言才有的写法。"
    },
    {
        "lesson": 5,
        "question": "当 x = 7 时，下面代码输出什么？\n  if (x > 5)\n      printf(\"A\");\n  else\n      printf(\"B\");",
        "options": [
            "A",
            "B",
            "AB",
            "没有输出"
        ],
        "answer": 0,
        "explain": "7 > 5 成立，走 if 分支打印 A；else 分支不会执行。"
    },
    {
        "lesson": 6,
        "question": "int x = 2;\nswitch (x) {\n    case 1: printf(\"A\");\n    case 2: printf(\"B\");\n    case 3: printf(\"C\");\n}\n输出是什么？",
        "options": [
            "BC",
            "B",
            "ABC",
            "C"
        ],
        "answer": 0,
        "explain": "匹配到 case 2 后执行 printf(\"B\")，但后面没有 break，会继续「穿透」执行 case 3，所以输出 BC。"
    },
    {
        "lesson": 6,
        "question": "下面哪个不能作为 switch 的表达式类型？",
        "options": [
            "double 变量",
            "int 变量",
            "char 变量",
            "枚举变量"
        ],
        "answer": 0,
        "explain": "switch 只接受整型（int、char、枚举等），float/double 和字符串都不行，因为 case 必须是整数常量。"
    },
    {
        "lesson": 7,
        "question": "for (i = 1; i <= 3; i++) 的循环体会执行几次？",
        "options": [
            "2 次",
            "3 次",
            "4 次",
            "无限次"
        ],
        "answer": 1,
        "explain": "i 依次为 1、2、3 时条件成立，共 3 次；i 变成 4 时 i<=3 不成立，停止。"
    },
    {
        "lesson": 7,
        "question": "下面代码输出什么？\n  for (i = 0; i < 3; i++)\n      printf(\"%d\", i);",
        "options": [
            "123",
            "012",
            "0123",
            "1 2 3"
        ],
        "answer": 1,
        "explain": "i 从 0 开始，依次打印 0、1、2，连在一起就是 012。"
    },
    {
        "lesson": 8,
        "question": "while 循环和 for 循环最大的区别是？",
        "options": [
            "while 运行更快",
            "while 适合次数未知、由条件决定",
            "while 不能嵌套",
            "while 不能写判断条件"
        ],
        "answer": 1,
        "explain": "for 适合\"确定要跑几次\"；while 适合\"不知道几次，看条件\"。"
    },
    {
        "lesson": 8,
        "question": "下面代码输出什么？\n  int n = 3;\n  while (n > 0) {\n      printf(\"%d\", n);\n      n--;\n  }",
        "options": [
            "321",
            "123",
            "3",
            "死循环"
        ],
        "answer": 0,
        "explain": "n 依次是 3、2、1，每次先打印再减 1，所以是 321。"
    },
    {
        "lesson": 9,
        "question": "int a[3] = {1, 2, 3}; 那么 a[1] 的值是？",
        "options": [
            "1",
            "2",
            "3",
            "未知"
        ],
        "answer": 1,
        "explain": "a[0]=1、a[1]=2、a[2]=3，所以 a[1] 是 2。"
    },
    {
        "lesson": 9,
        "question": "int a[5]; 里合法的下标范围是？",
        "options": [
            "1 ~ 5",
            "0 ~ 5",
            "0 ~ 4",
            "1 ~ 4"
        ],
        "answer": 2,
        "explain": "下标从 0 开始，5 个元素的下标是 0、1、2、3、4。"
    },
    {
        "lesson": 10,
        "question": "int a[3][4]; 下面哪个下标是合法的？",
        "options": [
            "a[2][3]",
            "a[3][0]",
            "a[0][4]",
            "a[3][4]"
        ],
        "answer": 0,
        "explain": "3 行 4 列，行下标 0~2，列下标 0~3，所以最大合法下标是 a[2][3]。"
    },
    {
        "lesson": 10,
        "question": "要遍历 int a[3][4] 的每个元素，内层循环的列条件应该写？",
        "options": [
            "j < 4",
            "j <= 4",
            "j < 3",
            "j <= 3"
        ],
        "answer": 0,
        "explain": "列数是 4，列下标 0~3，条件写 j < 4；写成 j <= 4 会访问 a[i][4]，越界。"
    },
    {
        "lesson": 11,
        "question": "字符串 \"ABC\" 在内存里实际占几个字节（含结束标记）？",
        "options": [
            "3 个",
            "4 个",
            "5 个",
            "不确定"
        ],
        "answer": 1,
        "explain": "A、B、C 三个字符，末尾还有一个 '\\0' 结束标记，共 4 个字节。"
    },
    {
        "lesson": 11,
        "question": "用 scanf 读一个字符串到 char name[20]，正确写法是？",
        "options": [
            "scanf(\"%s\", &name);",
            "scanf(\"%s\", name);",
            "scanf(\"%c\", name);",
            "scanf(\"%d\", name);"
        ],
        "answer": 1,
        "explain": "数组名 name 本身就是地址，前面不用加 &；%s 才是字符串格式。"
    },
    {
        "lesson": 12,
        "question": "char s[] = \"hello\";\nstrlen(s) 和 sizeof(s) 分别是多少？",
        "options": [
            "5 和 6",
            "6 和 6",
            "5 和 5",
            "6 和 5"
        ],
        "answer": 0,
        "explain": "strlen 数到 '\\0' 前为止，是 5；sizeof 算整个数组的字节数，包含末尾的 '\\0'，是 6。"
    },
    {
        "lesson": 12,
        "question": "统计一行里的单词个数，最关键是记录什么？",
        "options": [
            "上一个字符是否空白（标志变量）",
            "字符串总长度",
            "空格的总个数",
            "第一个字符是什么"
        ],
        "answer": 0,
        "explain": "单词数 = 从空白进入非空白的次数。用 in_word 标志记录「当前是否在单词里」，连续多个空格才不会重复计数。"
    },
    {
        "lesson": 13,
        "question": "int add(int a, int b) 里，函数名前面那个 int 表示？",
        "options": [
            "参数的类型",
            "返回值的类型",
            "函数占多少内存",
            "参数的个数"
        ],
        "answer": 1,
        "explain": "函数名前的 int 表示\"这个函数返回一个 int 值\"；括号里的 int 才是参数类型。"
    },
    {
        "lesson": 13,
        "question": "函数里 return 的作用是？",
        "options": [
            "把结果打印出来",
            "结束整个程序",
            "把结果返回给调用者",
            "让函数重新执行一遍"
        ],
        "answer": 2,
        "explain": "return 把结果\"交回去\"给调用它的地方；打印靠 printf，不是靠 return。"
    },
    {
        "lesson": 14,
        "question": "int f(void) {\n    static int x = 0;\n    return ++x;\n}\n连续调用三次 f()，返回值依次是？",
        "options": [
            "1、2、3",
            "1、1、1",
            "0、1、2",
            "3、3、3"
        ],
        "answer": 0,
        "explain": "static 局部变量只初始化一次，函数返回后值仍保留，所以每次调用接着往上加：1、2、3。"
    },
    {
        "lesson": 14,
        "question": "全局变量如果没有显式初始化，它的初值是什么？",
        "options": [
            "0",
            "随机垃圾值",
            "1",
            "编译报错"
        ],
        "answer": 0,
        "explain": "全局变量和 static 变量存放在静态区，编译器自动清零；局部变量（auto）不初始化才是垃圾值。"
    },
    {
        "lesson": 15,
        "question": "void f(int a[], int n) 里执行 sizeof(a) 得到什么？",
        "options": [
            "指针的大小（8 字节）",
            "整个数组的字节数",
            "元素个数",
            "编译错误"
        ],
        "answer": 0,
        "explain": "形参 int a[] 等价于 int *a，函数里拿到的只是首地址，sizeof(a) 是指针大小，所以长度必须另传 n。"
    },
    {
        "lesson": 15,
        "question": "调用 f(arr, 5) 时，arr 传给函数的是什么？",
        "options": [
            "数组首元素的地址",
            "整个数组的副本",
            "数组最后一个元素",
            "数组的字节数"
        ],
        "answer": 0,
        "explain": "数组名在表达式中退化为首元素地址，函数里通过这个地址访问原数组，所以能改到原数据。"
    },
    {
        "lesson": 16,
        "question": "long long fact(int n) {\n    if (n <= 1) return 1;\n    return n * fact(n - 1);\n}\n调用 fact(4) 时，fact 一共被调用了几次？",
        "options": [
            "4 次",
            "3 次",
            "5 次",
            "24 次"
        ],
        "answer": 0,
        "explain": "fact(4) → fact(3) → fact(2) → fact(1)，共 4 次调用，返回 24。递归函数必须有出口 n <= 1。"
    },
    {
        "lesson": 16,
        "question": "递归函数忘记写出口会发生什么？",
        "options": [
            "无限递归导致栈溢出，程序崩溃",
            "返回 0",
            "编译器报错",
            "自动变成循环"
        ],
        "answer": 0,
        "explain": "每层调用都占栈空间，没有出口就一直调下去，最后栈耗尽（stack overflow），程序异常终止。"
    },
    {
        "lesson": 17,
        "question": "int *p = &a; 里 &a 表示？",
        "options": [
            "a 的值",
            "a 的地址",
            "p 的地址",
            "a 乘以 p"
        ],
        "answer": 1,
        "explain": "& 是取地址符，&a 就是\"变量 a 在内存里的地址\"。"
    },
    {
        "lesson": 17,
        "question": "若指针 p 指向变量 a，那么 *p 表示？",
        "options": [
            "p 的地址",
            "p 存的值（也就是 a 的地址）",
            "a 的值",
            "a 的地址"
        ],
        "answer": 2,
        "explain": "p 存的是 a 的地址；*p 是\"解引用\"，顺着地址取到 a 的值。"
    },
    {
        "lesson": 18,
        "question": "int a[5]; int *p = a;\n执行 p++ 之后，p 指向哪里？",
        "options": [
            "a[1]",
            "a[0] 的第二个字节",
            "a[4]",
            "a[0]"
        ],
        "answer": 0,
        "explain": "p 的类型是 int*，p+1 按元素大小前进（前进 4 字节），所以指向 a[1]，不是前进 1 字节。"
    },
    {
        "lesson": 18,
        "question": "int a[5]; 下面哪个表达式和 a[2] 完全等价？",
        "options": [
            "*(a + 2)",
            "*a + 2",
            "a + 2",
            "&a[2]"
        ],
        "answer": 0,
        "explain": "a[i] 就是 *(a+i)。*(a+2) 取到 a[2] 的值；*a+2 是 a[0]+2；a+2 是地址；&a[2] 也是地址。"
    },
    {
        "lesson": 19,
        "question": "char *p = \"abc\";\np[0] = 'x';\n会发生什么？",
        "options": [
            "运行时崩溃（未定义行为）",
            "正常把首字母改成 x",
            "编译报错",
            "什么都不发生"
        ],
        "answer": 0,
        "explain": "字符串常量存放在只读区，不能修改。要改内容必须用数组：char s[] = \"abc\"; 然后在 s 上改。"
    },
    {
        "lesson": 19,
        "question": "char *p = s;\nwhile (*p) p++;\n循环结束时 p 指向什么？",
        "options": [
            "字符串末尾的 '\\0'",
            "字符串的最后一个字符",
            "字符串开头",
            "NULL"
        ],
        "answer": 0,
        "explain": "条件 *p 为 0（即 '\\0'）时退出，此时 p 正好停在结束标记上，所以 p - s 就是字符串长度。"
    },
    {
        "lesson": 20,
        "question": "void swap(int a, int b) { int t = a; a = b; b = t; }\n调用 swap(x, y) 后 x、y 会交换吗？",
        "options": [
            "不会，函数里改的只是副本",
            "会交换",
            "只有 x 变",
            "编译报错"
        ],
        "answer": 0,
        "explain": "值传递把 x、y 的值复制给形参，函数内交换的是副本。要真交换必须传地址：swap(&x, &y)。"
    },
    {
        "lesson": 20,
        "question": "函数 void change(int *p) 想让调用方的变量 n 被修改，正确的调用是？",
        "options": [
            "change(&n)",
            "change(n)",
            "change(*n)",
            "change(n, 1)"
        ],
        "answer": 0,
        "explain": "形参是指针，就必须传地址 &n；函数里写 *p = 新值 才能改到 n。"
    },
    {
        "lesson": 21,
        "question": "int (*p)[4];\n执行 p + 1 时地址前进多少字节？（int 占 4 字节）",
        "options": [
            "16 字节",
            "4 字节",
            "8 字节",
            "1 字节"
        ],
        "answer": 0,
        "explain": "p 指向「含 4 个 int 的数组」，p+1 跨过整个数组：4 × 4 = 16 字节，也就是二维数组的一整行。"
    },
    {
        "lesson": 21,
        "question": "int *a[4]; 这个声明表示什么？",
        "options": [
            "4 个 int 指针组成的数组",
            "指向含 4 个 int 的数组的指针",
            "4 个 int 的二维数组",
            "编译错误"
        ],
        "answer": 0,
        "explain": "[] 优先级高于 *，所以先看 a[4]：a 是数组；再看元素类型 int*。它是「指针数组」。数组指针要写成 int (*a)[4]。"
    },
    {
        "lesson": 22,
        "question": "int (*fp)(int, int); 这个声明表示什么？",
        "options": [
            "fp 是指向「两个 int 参数、返回 int」函数的指针",
            "fp 是返回 int 指针的函数",
            "fp 是含两个 int 的数组",
            "fp 是 int 数组指针"
        ],
        "answer": 0,
        "explain": "括号把 * 和 fp 绑在一起：fp 是指针；右边 (int,int) 是参数表，左边 int 是返回类型。没有括号就变成返回指针的函数。"
    },
    {
        "lesson": 22,
        "question": "qsort 的比较函数返回负数表示什么？",
        "options": [
            "第一个参数应排在第二个前面",
            "两个元素相等",
            "第一个参数应排在后面",
            "交换两个元素"
        ],
        "answer": 0,
        "explain": "返回值 <0 表示 a 排在 b 前，=0 表示相等，>0 表示 a 排在 b 后。降序只要把 return 的两个参数反过来。"
    },
    {
        "lesson": 23,
        "question": "struct Student { char name[20]; int age; };\nstruct Student s;\n给 age 赋值 18 应该写？",
        "options": [
            "s.age = 18;",
            "s->age = 18;",
            "Student.age = 18;",
            "s.age == 18;"
        ],
        "answer": 0,
        "explain": "普通结构体变量用点号访问成员；-> 只能用于结构体指针。== 是比较不是赋值。"
    },
    {
        "lesson": 23,
        "question": "两个同类型的结构体变量可以直接做什么操作？",
        "options": [
            "整体赋值 s2 = s1",
            "用 s1 == s2 比较相等",
            "用 s1 + s2 相加",
            "用 printf(\"%s\", s1) 输出"
        ],
        "answer": 0,
        "explain": "同类型结构体支持整体赋值（连数组成员一起复制），但没有内置的 == 比较，需要自己逐成员比较。"
    },
    {
        "lesson": 24,
        "question": "struct Student { char name[20]; int score; };\nstruct Student s, *p = &s;\n下面哪个和 p->score 等价？",
        "options": [
            "(*p).score",
            "*p.score",
            "*p->score",
            "&p.score"
        ],
        "answer": 0,
        "explain": "-> 就是 (*p). 的简写。*p.score 会被理解成 *(p.score) 而报错，因为 . 优先级高于 *。"
    },
    {
        "lesson": 24,
        "question": "把结构体变量（而不是指针）传给函数，函数里修改成员会影响原变量吗？",
        "options": [
            "不会，传的是副本",
            "会，直接改到原变量",
            "只有数组成员会变",
            "取决于结构体大小"
        ],
        "answer": 0,
        "explain": "结构体作参数也是值传递，整个结构体被复制一份。要修改原对象必须传地址，形参用 struct X *。"
    },
    {
        "lesson": 25,
        "question": "enum Color { RED, GREEN, BLUE };\nBLUE 的值是多少？",
        "options": [
            "2",
            "3",
            "1",
            "不确定"
        ],
        "answer": 0,
        "explain": "枚举默认从 0 开始依次递增：RED=0、GREEN=1、BLUE=2。也可以手动指定起始值。"
    },
    {
        "lesson": 25,
        "question": "union Data { int i; double d; char c; };\nsizeof(union Data) 是多少？",
        "options": [
            "最大成员的大小",
            "所有成员大小之和",
            "最小成员的大小",
            "固定 4 字节"
        ],
        "answer": 0,
        "explain": "共用体所有成员共用同一块内存，大小等于最大的成员（这里是 double 的 8 字节，可能再按对齐补齐）。"
    },
    {
        "lesson": 26,
        "question": "删除链表中某个结点时，必须先做什么？",
        "options": [
            "先保存它的 next，再改前驱指针，最后 free",
            "直接 free 就行",
            "先 free 再访问 next",
            "只把 data 改成 0"
        ],
        "answer": 0,
        "explain": "free 之后那块内存就不能再用，所以要先保存 next、让前驱指向 next，最后才 free，顺序错就是悬垂指针。"
    },
    {
        "lesson": 26,
        "question": "遍历单链表 p 从 head 开始，循环条件应该写？",
        "options": [
            "p != NULL",
            "p->next != NULL",
            "p->next->next != NULL",
            "p == NULL"
        ],
        "answer": 0,
        "explain": "条件是 p 本身非空。写成 p->next != NULL 会漏掉最后一个结点，还会解引用空指针。"
    },
    {
        "lesson": 27,
        "question": "x & (x - 1) 这个操作的作用是？",
        "options": [
            "把二进制最低位的 1 变成 0",
            "把最低位取反",
            "判断是否为偶数",
            "左移一位"
        ],
        "answer": 0,
        "explain": "x-1 会把最低位的 1 变 0、后面的 0 全变 1，再与 x 相与就清掉了最低位的 1。用来数 1 的个数、判 2 的幂。"
    },
    {
        "lesson": 27,
        "question": "表达式 n & 1 的结果为 1，说明 n 是什么数？",
        "options": [
            "奇数",
            "偶数",
            "正数",
            "2 的幂"
        ],
        "answer": 0,
        "explain": "二进制最低位是 1 就是奇数，是 0 就是偶数。& 1 比 % 2 更快，而且对负数也成立。"
    },
    {
        "lesson": 28,
        "question": "FILE *fp = fopen(\"data.txt\", \"r\"); 打开失败时 fp 的值是？",
        "options": [
            "NULL",
            "0 号文件描述符",
            "EOF",
            "随机地址"
        ],
        "answer": 0,
        "explain": "fopen 失败返回 NULL，所以必须写 if (fp == NULL) 处理；不判空直接用会崩溃。"
    },
    {
        "lesson": 28,
        "question": "用 \"w\" 模式打开一个已经存在且有内容的文件，会发生什么？",
        "options": [
            "文件内容被清空",
            "从末尾追加",
            "打开失败",
            "自动备份原文件"
        ],
        "answer": 0,
        "explain": "\"w\" 是截断写：文件存在就清空重写。想保留原内容要改用 \"a\"（追加）或 \"r+\"。"
    },
    {
        "lesson": 29,
        "question": "fgets 读到文件末尾、没读到任何字符时返回什么？",
        "options": [
            "NULL",
            "空字符串 \"\"",
            "EOF",
            "-1"
        ],
        "answer": 0,
        "explain": "fgets 返回 char*：成功返回 buf，失败或到末尾返回 NULL。所以 while (fgets(...) != NULL) 是标准写法。"
    },
    {
        "lesson": 29,
        "question": "fgets(buf, 100, fp) 读到的字符串里包含换行符吗？",
        "options": [
            "包含（如果没读满）",
            "不包含，自动去掉",
            "只在 Windows 下包含",
            "取决于文件编码"
        ],
        "answer": 0,
        "explain": "fgets 会把 '\\n' 一起存进去，末尾再补 '\\0'，所以比较前通常要 buf[strcspn(buf, \"\\n\")] = '\\0' 去掉它。"
    },
    {
        "lesson": 30,
        "question": "fseek(fp, -10, SEEK_END) 的含义是？",
        "options": [
            "从文件末尾往前移动 10 字节",
            "从文件开头往后移动 10 字节",
            "从当前位置往前 10 字节",
            "把文件截断到 10 字节"
        ],
        "answer": 0,
        "explain": "第三个参数是基准：SEEK_SET 开头、SEEK_CUR 当前位置、SEEK_END 末尾。用它可以直接跳到想读的位置。"
    },
    {
        "lesson": 30,
        "question": "fwrite 的参数顺序正确的是？",
        "options": [
            "(地址, 单块大小, 块数, 文件指针)",
            "(文件指针, 地址, 大小, 块数)",
            "(地址, 块数, 单块大小, 文件指针)",
            "(文件指针, 块数, 大小, 地址)"
        ],
        "answer": 0,
        "explain": "fwrite(const void *ptr, size_t size, size_t n, FILE *fp)：先给数据地址，再给单块字节数和块数，最后文件指针。"
    },
    {
        "lesson": 31,
        "question": "#define SQR(x) x * x\nprintf(\"%d\", SQR(1 + 2));\n输出是什么？",
        "options": [
            "5",
            "9",
            "3",
            "编译错误"
        ],
        "answer": 0,
        "explain": "宏是纯文本替换：1 + 2 * 1 + 2 = 5。写成 #define SQR(x) ((x)*(x)) 才得 9。"
    },
    {
        "lesson": 31,
        "question": "头文件里写 #ifndef A_H / #define A_H ... #endif，作用是？",
        "options": [
            "防止头文件被重复包含",
            "加快编译速度",
            "定义全局变量",
            "开启调试模式"
        ],
        "answer": 0,
        "explain": "这叫宏卫。多个 .c 互相包含同一个头文件时，宏卫保证内容只展开一次，避免重复定义错误。"
    },
    {
        "lesson": 32,
        "question": "n = 100000 时，冒泡排序和快速排序的时间复杂度大致是？",
        "options": [
            "O(n²) 和 O(n log n)",
            "都是 O(n)",
            "O(n log n) 和 O(n²)",
            "都是 O(n²)"
        ],
        "answer": 0,
        "explain": "冒泡是 O(n²)（10^10 次操作，肯定超时），快排平均 O(n log n)（约 1.7×10^6），所以大数据必须换排序算法。"
    },
    {
        "lesson": 32,
        "question": "二分查找能用的前提是什么？",
        "options": [
            "数据已经按关键字有序",
            "数据全是正数",
            "数据个数是偶数",
            "数据存放在数组里就行"
        ],
        "answer": 0,
        "explain": "二分靠「中间元素比较后砍掉一半」，数据无序就无法判断该往哪边找。无序就先排序。"
    },
    {
        "lesson": 33,
        "question": "为什么大数加法要用数组逐位计算？",
        "options": [
            "内置整型装不下（超出 long long）",
            "数组算得更快",
            "因为输入是字符串",
            "为了省内存"
        ],
        "answer": 0,
        "explain": "long long 最大约 9.2×10^18，100 位的大数远超范围，只能自己用数组存每一位，模拟竖式加法并处理进位。"
    },
    {
        "lesson": 33,
        "question": "把十进制数转换成二进制，标准做法是？",
        "options": [
            "反复 % 2 取余并 / 2，余数倒着读",
            "反复 / 2 取商，商倒着读",
            "从最高位开始逐位试减",
            "乘 2 取整"
        ],
        "answer": 0,
        "explain": "n % 2 得到最低位，n /= 2 去掉最低位，重复到 n 为 0，得到的余数序列倒过来就是二进制。"
    },
    {
        "lesson": 34,
        "question": "free(p) 之后还继续用 p 访问内存，这种错误叫什么？",
        "options": [
            "悬垂指针（释放后使用）",
            "内存泄漏",
            "数组越界",
            "重复定义"
        ],
        "answer": 0,
        "explain": "内存已还给系统，指针还指着那块地址，再访问是未定义行为。free 后应立刻 p = NULL。"
    },
    {
        "lesson": 34,
        "question": "malloc(10 * sizeof(int)) 申请到的内存里，初值是什么？",
        "options": [
            "不确定（垃圾值）",
            "全是 0",
            "全是 1",
            "编译时报错"
        ],
        "answer": 0,
        "explain": "malloc 不清零，内容随机；要清零用 calloc，或者申请后 memset(a, 0, ...)。"
    },
    {
        "lesson": 35,
        "question": "gcc 报错 stray '\\357' in program，最可能的原因是？",
        "options": [
            "代码里混进了中文标点",
            "少写了头文件",
            "变量名拼错",
            "数组越界"
        ],
        "answer": 0,
        "explain": "中文全角符号（，；（）「」）在 UTF-8 下是多字节，编译器看到第一个字节就会报 stray。检查报错行附近。"
    },
    {
        "lesson": 35,
        "question": "程序运行到一半出现「段错误」，最不可能的原因是？",
        "options": [
            "printf 少写了换行",
            "解引用空指针",
            "数组下标越界",
            "free 后又使用指针"
        ],
        "answer": 0,
        "explain": "段错误是访问了非法内存：空指针、野指针、越界、重复释放都会导致；少写换行只是输出格式问题。"
    },
    {
        "lesson": 36,
        "question": "要给任意类型（比如结构体数组）排序，标准库提供的函数是？",
        "options": [
            "qsort",
            "sort",
            "bubble_sort",
            "printf"
        ],
        "answer": 0,
        "explain": "qsort(base, n, size, cmp) 接受 void* 和比较函数，任何类型都能排，只要写出正确的 cmp。"
    },
    {
        "lesson": 36,
        "question": "调用 ctype.h 里的 isdigit(c) 时，推荐先把 c 转成什么类型？",
        "options": [
            "unsigned char",
            "long long",
            "double",
            "char 直接传就行"
        ],
        "answer": 0,
        "explain": "isdigit 的参数是 int，但如果传入负值（某些编码下的高位字符）是未定义行为，先转 unsigned char 最安全。"
    }
]
