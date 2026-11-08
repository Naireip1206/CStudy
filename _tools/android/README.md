# 安卓 v2（本地编译判题）调研记录 · 2026-11-07

## 结论：可行，卡在"没有真机/模拟器"这一步

### 已确认可用的东西

| 项 | 结果 |
|---|---|
| Termux tcc 包（清华镜像） | `tcc_1:0.9.27-p20230415-2_aarch64.deb`，243 KB，已下载到本目录 |
| 包里的 `tcc` 二进制 | 370 KB，**ELF 64-bit aarch64**（machine 0xb7），能在 Android 上跑 |
| 附带文件 | `libtcc.a` 681 KB、`lib/tcc/libtcc1.a` 49 KB、`crtbegin_dynamic.o`、`crtend_android.o`、`tcc/include/*`（stddef/stdarg/stdbool/float 等） |
| 还缺什么 | **C 标准库头文件**（stdio.h/stdlib.h/string.h/math.h…）→ 从本机 NDK 拿：`D:\Android\Sdk\ndk\28.2.13676358\toolchains\llvm\prebuilt\windows-x86_64\sysroot\usr\include` + `.../aarch64-linux-android/...` |
| 本机 Android 工具链 | platform android-34/35/36、build-tools 36.0.0、NDK 28.2、JDK 21、Gradle 9.1 缓存、AGP 8.11~9.0 / Kotlin 2.x 缓存齐全 |
| 网络 | tuna 的 Termux 镜像可直连 |

### 待解决的三个问题

1. **没有可测试的设备**：`adb devices` 空，没装 emulator、没有 AVD。要验证必须插上小米 13（开 USB 调试），或装 emulator + x86_64 镜像（那样还得换 x86_64 版的 tcc）。
2. **Flutter SDK 路径失效**：`D:\dm\android\local.properties` 里写的是 `D:\flutter\flutter`，该目录不存在 → 走 Flutter 壳需要先重装/定位 Flutter；走 Kotlin + Gradle 更稳。
3. **Android 10+ 不能从私有目录 exec**：tcc 必须作为 `jniLibs/arm64-v8a/libtcc.so` 打进 APK（lib 目录允许执行）；`-run` 直接 JIT 执行可避开"生成 exe 再执行"的限制。

### 推荐的实现轮廓（下次接着做）

```
android/
├─ app/src/main/assets/web/        ← export_android.py 导出：index.html/app.js/style.css/icon.ico + lessons/quizzes/oj.json
├─ app/src/main/assets/tcc/        ← include/（NDK sysroot 头文件）+ libtcc1.a + crt*.o
├─ app/src/main/jniLibs/arm64-v8a/libtcc.so  ← 重命名的 tcc 可执行文件
└─ Kotlin: MainActivity(WebView) + JudgeBridge
      judge(code) = exec libtcc.so -run -I<assets/tcc/include> -B<assets/tcc>，stdin/stdout 走管道，超时 2s
```

前端不用改：在 `index.html` 里加载一个 `native-shim.js`，把 `fetch("/api/…")` 拦下来转成 `window.CStudyNative.xxx()`。

## 文件

- `tcc_1%3A0.9.27-p20230415-2_aarch64.deb`：Termux 的 tcc 包（243 KB），已解包验证过内容
- `_tools/android_probe.py`：下载/解包/查 ELF 架构的脚本，重跑可复现
