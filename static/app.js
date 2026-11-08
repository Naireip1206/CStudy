// ============================================================
// app.js —— C 语言学习器（网页版）前端逻辑
// ============================================================
const $ = (s) => document.querySelector(s);

// ============================================================
// 前端日志上报
// 页面里的错后端看不到（页面白屏、点了没反应），统一 POST /api/log
// 写进和 Python 端同一个日志文件，出问题时一个文件就能查全。
// 上报本身绝不允许影响页面：全部 try/catch + 静默失败。
// ============================================================
function reportLog(level, message, extra) {
  try {
    const body = JSON.stringify(Object.assign({
      level: level || "ERROR",
      source: "web",
      where: (location.hash || location.pathname || "") + "",
      message: String(message || "").slice(0, 1500),
      stack: "",
    }, extra || {}));
    fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body,
      keepalive: true,          // 页面正在关闭时也尽量发出去
    }).catch(() => {});
  } catch (e) { /* 忽略 */ }
}

window.addEventListener("error", (e) => {
  reportLog("ERROR", e.message || "资源加载失败", {
    where: (e.filename || "?") + ":" + (e.lineno || 0) + ":" + (e.colno || 0),
    stack: (e.error && e.error.stack) ? e.error.stack : "",
  });
});

window.addEventListener("unhandledrejection", (e) => {
  const r = e.reason;
  reportLog("ERROR", (r && r.message) ? r.message : String(r), {
    where: "unhandledrejection",
    stack: (r && r.stack) ? r.stack : "",
  });
});

let DATA = null;         // 全部数据
let editor = null;       // CodeMirror 编辑器实例
let currentOjId = null;  // 当前正在编辑的 OJ 题号

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ============================================================
// C 语法高亮：词表 + 行内 hl() + 代码块 highlightC()
// 高亮只为好看，不改变任何文本内容（复制出去还是原样代码）
// ============================================================
const C_KW = new Set(("auto break case const continue default do else enum extern for goto if inline "
  + "register restrict return sizeof static struct switch typedef union volatile while").split(" "));
const C_TY = new Set(("char double float int long short signed unsigned void FILE size_t ptrdiff_t bool").split(" "));
const C_MACRO = new Set(("NULL EOF SEEK_SET SEEK_CUR SEEK_END stdin stdout stderr EXIT_SUCCESS "
  + "EXIT_FAILURE RAND_MAX BUFSIZ").split(" "));
const C_FN = new Set(("main printf scanf sprintf sscanf snprintf vprintf fprintf fscanf fgetc fputc fgets fputs "
  + "fopen fclose fflush fread fwrite fseek ftell rewind feof ferror getchar putchar gets puts perror "
  + "strlen strcpy strncpy strcat strncat strcmp strncmp strstr strchr strrchr strcspn strspn "
  + "memset memcpy memmove memcmp atoi atol atof strtol strtod "
  + "malloc calloc realloc free qsort bsearch exit abort system rand srand "
  + "abs labs llabs fabs sqrt pow ceil floor round trunc fmod sin cos tan exp log log10 "
  + "toupper tolower isalpha isdigit isalnum isspace islower isupper ispunct isxdigit "
  + "assert time localtime clock difftime").split(" "));

const TK = {
  kw: "tk-kw", ty: "tk-ty", fn: "tk-fn", macro: "tk-macro",
  str: "tk-str", num: "tk-num", com: "tk-com", pp: "tk-pp", hd: "tk-hd", fmt: "tk-fmt",
};

function tk(cls, text) {
  return '<span class="' + cls + '">' + esc(text) + "</span>";
}

function wordClass(w) {
  if (C_KW.has(w)) return TK.kw;
  if (C_TY.has(w)) return TK.ty;
  if (C_MACRO.has(w)) return TK.macro;
  if (C_FN.has(w)) return TK.fn;
  return "";
}

// 行内高亮：正文里的 int / printf / <stdio.h> / %d / #define / MAX 都变成彩色小代码
function hl(text) {
  if (text === null || text === undefined) return "";
  const s = String(text);
  const re = /#[A-Za-z_]+|<[A-Za-z_][\w.]*\.h>|%[-+ 0#]*\d*(?:\.\d+)?[diouxXeEfgGcs%]|[A-Za-z_][A-Za-z0-9_]*/g;
  let out = "";
  let last = 0;
  let m;
  while ((m = re.exec(s)) !== null) {
    out += esc(s.slice(last, m.index));
    const t = m[0];
    if (t.charAt(0) === "#") {
      out += '<code class="tok ' + TK.pp + '">' + esc(t) + "</code>";
    } else if (t.charAt(0) === "<" && t.slice(-3) === ".h>") {
      out += '<code class="tok ' + TK.hd + '">' + esc(t) + "</code>";
    } else if (t.charAt(0) === "%") {
      out += '<code class="tok ' + TK.fmt + '">' + esc(t) + "</code>";
    } else {
      // 全大写标识符（MAX、SQR、EOF）按宏着色
      const cls = /^[A-Z][A-Z0-9_]+$/.test(t) ? TK.macro : wordClass(t);
      out += cls ? '<code class="tok ' + cls + '">' + esc(t) + "</code>" : esc(t);
    }
    last = m.index + t.length;
  }
  out += esc(s.slice(last));
  return out;
}

// 代码块高亮：逐字符扫描，处理注释 / 字符串 / 预处理 / 数字 / 标识符
function highlightC(src) {
  const s = String(src);
  const n = s.length;
  const isIdStart = (c) => /[A-Za-z_]/.test(c);
  const isId = (c) => /[A-Za-z0-9_]/.test(c);
  let out = "";
  let i = 0;

  while (i < n) {
    const c = s[i];

    // 行注释
    if (c === "/" && s[i + 1] === "/") {
      let j = s.indexOf("\n", i);
      if (j < 0) j = n;
      out += tk(TK.com, s.slice(i, j));
      i = j;
      continue;
    }
    // 块注释
    if (c === "/" && s[i + 1] === "*") {
      let j = s.indexOf("*/", i + 2);
      j = j < 0 ? n : j + 2;
      out += tk(TK.com, s.slice(i, j));
      i = j;
      continue;
    }
    // 字符串 / 字符常量
    if (c === '"' || c === "'") {
      let j = i + 1;
      while (j < n && s[j] !== c) {
        if (s[j] === "\\") j++;
        j++;
      }
      j = Math.min(j + 1, n);
      out += tk(TK.str, s.slice(i, j));
      i = j;
      continue;
    }
    // 预处理指令：#include / #define / #ifdef ...
    if (c === "#" && (i === 0 || /\n/.test(s.slice(Math.max(0, i - 1), i)) || /^[ \t]*$/.test(s.slice(s.lastIndexOf("\n", i - 1) + 1, i)))) {
      const m = /^#[ \t]*[A-Za-z_]+/.exec(s.slice(i));
      const w = m ? m[0] : "#";
      out += tk(TK.pp, w);
      i += w.length;
      continue;
    }
    // 尖括号头文件
    if (c === "<") {
      const m = /^<[A-Za-z_][\w.]*\.h>/.exec(s.slice(i));
      if (m) {
        out += tk(TK.hd, m[0]);
        i += m[0].length;
        continue;
      }
    }
    // 数字
    if (/[0-9]/.test(c)) {
      const m = /^(0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)[uUlLfF]*/.exec(s.slice(i));
      if (m) {
        out += tk(TK.num, m[0]);
        i += m[0].length;
        continue;
      }
    }
    // 标识符
    if (isIdStart(c)) {
      let j = i;
      while (j < n && isId(s[j])) j++;
      const w = s.slice(i, j);
      const cls = wordClass(w);
      out += cls ? tk(cls, w) : esc(w);
      i = j;
      continue;
    }

    out += esc(c);
    i++;
  }
  return out;
}

// 代码卡片：标题 + 高亮代码（复制出去仍是纯文本）
function codeCard(src, head) {
  return '<div class="code-card"><div class="code-head">' + esc(head || "C") +
    '</div><pre class="code-body">' + highlightC(src) + "</pre></div>";
}

// ---- C 语言自动补全：关键字 + 常用函数 + 文档里出现过的单词 ----
const C_WORDS = ("int char double float long short void unsigned signed const static struct typedef enum union sizeof "
  + "if else for while do return break continue switch case default goto "
  + "printf scanf puts gets strlen strcmp strcpy strcat getchar putchar malloc free "
  + "include define main NULL EOF true false").split(" ");

function cHint(cm) {
  const cur = cm.getCursor();
  const token = cm.getTokenAt(cur);
  const word = cm.getLine(cur.line).slice(token.start, cur.ch);
  const docWords = new Set(cm.getValue().split(/[^a-zA-Z_]/).filter(Boolean));
  const pool = new Set([...C_WORDS, ...docWords]);
  const list = [...pool].filter((w) => w.startsWith(word) && w !== word).slice(0, 30);
  return {
    list: list.map((w) => w),
    from: CodeMirror.Pos(cur.line, token.start),
    to: CodeMirror.Pos(cur.line, cur.ch),
  };
}

async function init() {
  let res;
  try {
    res = await fetch("/api/data", { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
  } catch (e) {
    reportLog("ERROR", "连不上本地服务 / 加载数据失败：" + e, { where: "init" });
    $("body").insertAdjacentHTML("afterbegin",
      `<div class="offline-bar">连不上本地服务：程序可能已经关掉了。请重新双击「C 语言学习器」，等黑窗口出现后再刷新本页。</div>`);
    return;
  }
  try {
    DATA = await res.json();
  } catch (e) {
    // 数据文件坏了（后端返回的不是合法 JSON）也是白屏的常见原因，必须留痕
    reportLog("ERROR", "解析 /api/data 返回的 JSON 失败：" + e, { where: "init" });
    $("body").insertAdjacentHTML("afterbegin",
      `<div class="offline-bar">数据读取失败：${esc(String(e))}（细节已写进运行日志）</div>`);
    return;
  }
  if (DATA.app && DATA.app.version) document.title = `${DATA.app.name} v${DATA.app.version}`;
  $("#days").textContent = `累计学习 ${DATA.progress.days} 天`;
  document.querySelectorAll(".nav-item").forEach((b) =>
    b.addEventListener("click", () => switchPage(b.dataset.page))
  );
  switchPage("lessons");
}

function switchPage(page) {
  document.querySelectorAll(".nav-item").forEach((b) =>
    b.classList.toggle("active", b.dataset.page === page)
  );
  const c = $("#content");
  ({ lessons: renderLessons, quiz: renderQuiz, oj: renderOJ, wrongbook: renderWrongbook,
     mycode: renderMyCode, progress: renderProgress, about: renderAbout }[page])(c);
}

function saveProgress() {
  fetch("/api/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lessons: DATA.progress.lessons,
      oj: DATA.progress.oj,
      quiz_wrong: DATA.progress.quiz_wrong,
      notes: DATA.progress.notes,
    }),
  });
}

function lessonState(n) {
  const e = DATA.progress.lessons[n];
  return { done: !!e && !!e.done, score: e ? e.score : -1 };
}

// ============================================================
// 课程页
// ============================================================
function renderLessons(c) {
  let h = `<div class="content-inner">
    <div class="page-head"><div class="kicker">COURSE</div><h1>课程</h1>
    <div class="desc">共 ${DATA.lessons.length} 节：printf → 结构体 / 链表 / 位运算，每节含基础知识、要点清单、可运行示例，点击展开。</div></div>
    <div class="lesson-list">`;
  DATA.lessons.forEach((L, i) => {
    const n = i + 1;
    const st = lessonState(String(n));
    const tag = st.done
      ? (st.score >= 0 ? `<span class="tag tag--accent">已学 · ${st.score} 分</span>` : `<span class="tag tag--accent">已学</span>`)
      : `<span class="tag">未学</span>`;
    h += `<button class="lesson-item" data-i="${i}"><span class="idx">${String(n).padStart(2, "0")}</span><span style="flex:1">${hl(L.title)}</span>${tag}</button>
    <div class="lesson-detail" data-detail="${i}" hidden></div>`;
  });
  h += `</div></div>`;
  c.innerHTML = h;
  c.querySelectorAll(".lesson-item").forEach((btn) =>
    btn.addEventListener("click", () => toggleLesson(btn, Number(btn.dataset.i)))
  );
}

function toggleLesson(btn, i) {
  const detail = btn.nextElementSibling;
  if (!detail.hidden) { detail.hidden = true; return; }
  const L = DATA.lessons[i];
  const basics = (L.basics || [])
    .map(([h2, p]) => `<div class="sec-head">${hl(h2)}</div><div class="body">${hl(p)}</div>`)
    .join("");
  const points = (L.points && L.points.length)
    ? `<div class="sec-head">要点清单</div><ul class="points">${L.points.map((p) => `<li>${hl(p)}</li>`).join("")}</ul>`
    : "";
  const meta = L.block
    ? `<div class="lesson-ref">第 ${L.block} 块 · ${esc(L.part || "")}${L.ref ? " · 教材：" + esc(L.ref) : ""}</div>`
    : "";
  detail.innerHTML = `<div style="margin:2px 0 14px 42px">
    ${meta}
    <div class="sec-head">一句话原理</div><div class="body">${hl(L.idea)}</div>
    ${basics}
    ${points}
    <div class="sec-head">示例代码</div>
    ${codeCard(L.code, "C · 可直接复制运行")}
    <div class="sec-head">动手改一改</div><div class="task">${hl(L.task)}</div>
    <div class="sec-head">一句话坑</div><div class="pit">${hl(L.pitfall)}</div>
    <button class="btn btn--primary" data-mark="${i}">标记为已学</button>
  </div>`;
  detail.hidden = false;
  detail.querySelector("[data-mark]").addEventListener("click", () => markLesson(String(i + 1)));
}

function markLesson(n) {
  if (!DATA.progress.lessons[n]) DATA.progress.lessons[n] = {};
  DATA.progress.lessons[n].done = 1;
  saveProgress();
  switchPage("lessons");
}

// ============================================================
// 测验页
// ============================================================
function renderQuiz(c) {
  let h = `<div class="content-inner"><div class="page-head"><div class="kicker">QUIZ</div><h1>测验</h1>
    <div class="desc">每个知识点 2 道四选一，共 ${DATA.quizzes.length} 道，选一个知识点开始。</div></div><div class="lesson-list">`;
  DATA.lessons.forEach((L, i) => {
    const n = i + 1;
    const qn = DATA.quizzes.filter((q) => q.lesson === n).length;
    const sc = lessonState(String(n)).score;
    const suffix = qn === 0 ? "（待出题）" : sc >= 0 ? `（上次 ${sc} 分）` : "（未测）";
    const attr = qn === 0 ? "disabled style=\"opacity:.55;cursor:default\"" : `data-quiz="${i}"`;
    h += `<button class="lesson-item" ${attr}><span class="idx">${String(n).padStart(2, "0")}</span><span style="flex:1">${hl(L.title)}</span><span class="tag">${suffix}</span></button>`;
  });
  h += `</div></div>`;
  c.innerHTML = h;
  c.querySelectorAll("[data-quiz]").forEach((b) =>
    b.addEventListener("click", () => startQuiz(Number(b.dataset.quiz) + 1))
  );
}

function startQuiz(lessonNo) {
  const qs = DATA.quizzes.filter((q) => q.lesson === lessonNo);
  if (qs.length === 0) { alert("这个知识点还没出题，先看课程吧。"); return; }
  let qi = 0, right = 0;
  const c = $("#content");

  function show() {
    if (qi >= qs.length) { result(); return; }
    const q = qs[qi];
    const letters = ["A", "B", "C", "D"];
    let h = `<div class="content-inner"><div class="page-head"><div class="kicker">QUIZ · 第 ${lessonNo} 节</div>
      <h1>${qi + 1} / ${qs.length}</h1></div>
      <div class="quiz-question">${hl(q.question)}</div>
      <div class="quiz-options">`;
    q.options.forEach((opt, oi) => {
      h += `<button class="quiz-opt" data-oi="${oi}"><span class="letter">${letters[oi]}.</span><span>${hl(opt)}</span></button>`;
    });
    h += `</div><div class="feedback" id="fb"></div><button class="btn btn--secondary" id="next" style="display:none">下一题 →</button></div>`;
    c.innerHTML = h;

    const opts = c.querySelectorAll(".quiz-opt");
    opts.forEach((b) =>
      b.addEventListener("click", () => {
        const oi = Number(b.dataset.oi);
        opts.forEach((x) => (x.disabled = true));
        if (oi === q.answer) {
          right++;
          b.classList.add("correct");
          $("#fb").innerHTML = `<span style="color:var(--terracotta-dk)">回答正确。</span>`;
        } else {
          b.classList.add("wrong");
          opts[q.answer].classList.add("correct");
          $("#fb").innerHTML = `<span style="color:var(--terracotta-dk)">正确答案是 ${letters[q.answer]}。</span><br>${hl(q.explain)}`;
          // 记录错题（去重）
          const idx = DATA.quizzes.indexOf(q);
          if (!DATA.progress.quiz_wrong.includes(idx)) {
            DATA.progress.quiz_wrong.push(idx);
            saveProgress();
          }
        }
        $("#next").style.display = "inline-block";
      })
    );
    $("#next").addEventListener("click", () => { qi++; show(); });
  }

  function result() {
    const score = qs.length ? Math.round((100 * right) / qs.length) : 0;
    const n = String(lessonNo);
    if (!DATA.progress.lessons[n]) DATA.progress.lessons[n] = {};
    DATA.progress.lessons[n].score = score;
    saveProgress();
    c.innerHTML = `<div class="content-inner"><div class="page-head"><div class="kicker">QUIZ · 第 ${lessonNo} 节</div>
      <h1>测验完成</h1></div>
      <p style="font-size:16px">答对 <b>${right}</b> / ${qs.length} 题，得分 <b>${score}</b> 分。</p>
      <p style="font-size:15px;color:var(--olive)">${score >= 80 ? "表现不错，可以去学下一节了。" : "建议回头看看这一节的示例代码，再刷一遍。"}</p>
      <button class="btn btn--secondary" data-back>← 返回章节选择</button></div>`;
    c.querySelector("[data-back]").addEventListener("click", () => switchPage("quiz"));
  }

  show();
}

// ============================================================
// OJ 页（CodeMirror 编辑器 + 提交历史 + 答案展示）
// ============================================================
function renderOJ(c) {
  c.innerHTML = `<div class="content-inner"><div class="page-head"><div class="kicker">ONLINE JUDGE</div><h1>OJ 刷题</h1>
    <div class="desc">${DATA.oj.length} 道题，一题对应一个知识块：写 C 代码，一键编译判分，报错自动翻译成中文。
    左边的选题菜单是固定的，看长题目时它不会跟着跑。</div></div>
    <div class="oj-layout"><nav class="oj-menu" id="ojlist"></nav><div id="ojdetail"></div></div></div>`;

  const list = $("#ojlist");
  const levels = ["入门", "基础", "进阶"];
  let html = `<div class="oj-menu-title"><span>题目列表</span><span>${DATA.oj.length} 题</span></div>`;
  levels.forEach((lv) => {
    const items = DATA.oj.filter((p) => p.difficulty === lv);
    if (!items.length) return;
    const done = items.filter((p) => DATA.progress.oj[p.id] === "AC").length;
    html += `<details class="oj-group" open>
      <summary><span class="g-name">${lv}</span><span class="g-cnt">${done}/${items.length}</span></summary>
      <div class="oj-items">${items.map((p) => {
        const st = DATA.progress.oj[p.id];
        const s = st === "AC" ? `<span class="st ac">AC</span>` : st ? `<span class="st">${esc(st)}</span>` : "";
        return `<button class="oj-item" data-pid="${p.id}"><span class="oj-item-title">${p.id}. ${hl(p.title)}</span>
          <span class="oj-block">第${p.block}块</span>${s}</button>`;
      }).join("")}</div>
    </details>`;
  });
  list.innerHTML = html;

  list.querySelectorAll("[data-pid]").forEach((b) =>
    b.addEventListener("click", () => showOJ(Number(b.dataset.pid), b))
  );
  if (DATA.oj.length) showOJ(DATA.oj[0].id, list.querySelector(".oj-item"));
}

function showOJ(id, btn) {
  // 切题前，保存当前编辑器内容
  if (editor && currentOjId) {
    DATA.oj_codes[currentOjId] = editor.getValue();
  }
  currentOjId = id;

  document.querySelectorAll(".oj-item").forEach((x) => x.classList.remove("active"));
  if (btn) btn.classList.add("active");
  const contentEl = document.getElementById("content");
  if (contentEl) contentEl.scrollTop = 0;   // 换题后回到题目开头，菜单固定不动
  const p = DATA.oj.find((x) => x.id === id);
  const d = $("#ojdetail");

  let samples = p.samples.map((s) =>
    `<div class="sample-block"><div class="in">输入　${hl(s.input.replace(/\n/g, " ⏎ "))}</div><div class="out">输出　${hl(s.output)}</div></div>`
  ).join("");

  // 该题的提交历史
  const hist = DATA.progress.submissions.filter((s) => s.pid === id).slice(-8).reverse();

  // 这题如果通过过，就把留档代码折叠展示出来
  const acRec = DATA.ac && DATA.ac[String(id)];
  const myacHTML = acRec
    ? `<details class="answer-block"><summary>我的通过代码（留档 · ${esc(acRec.last || acRec.first || "")}）</summary>
        ${codeCard(acRec.code, "我的通过代码 · " + p.title)}</details>`
    : "";

  d.innerHTML = `<h2>${p.id}. ${hl(p.title)} <span class="tag">${esc(p.difficulty)}</span> <span class="tag">第 ${p.block} 块</span></h2>
    <p>${hl(p.description)}</p>
    <h3>输入格式</h3><p style="font-size:15px;color:var(--olive)">${hl(p.input_format)}</p>
    <h3>输出格式</h3><p style="font-size:15px;color:var(--olive)">${hl(p.output_format)}</p>
    <h3>样例</h3>${samples}
    <h3>你的代码</h3>
    <div id="editor"></div>
    <div style="margin-top:12px;display:flex;gap:10px">
      <button class="btn btn--primary" id="submit">提交判题</button>
      <button class="btn btn--secondary" id="open">在 VS Code 打开</button>
    </div>
    <div class="result" id="result"></div>
    <div id="answers"></div>
    ${myacHTML}
    ${hist.length ? `<h3 style="margin-top:22px">提交记录</h3><div class="sub-list">${hist.map((s) =>
      `<div class="sub-row"><span class="sub-time">${esc(s.time)}</span><span class="sub-verdict ${s.verdict.toLowerCase()}">${esc(s.verdict)}</span></div>`).join("")}</div>` : ""}`;

  $("#submit").addEventListener("click", () => submitJudge(id));
  $("#open").addEventListener("click", () => fetch(`/api/open/${id}`));

  // 初始化 CodeMirror 编辑器
  editor = CodeMirror(document.getElementById("editor"), {
    value: DATA.oj_codes[id] || "",
    mode: "text/x-csrc",
    lineNumbers: true,
    indentUnit: 4,
    autoCloseBrackets: true,
    extraKeys: { "Tab": "autocomplete", "Ctrl-Space": "autocomplete" },
    hintOptions: { hint: cHint, completeSingle: true },
  });
}

async function submitJudge(id) {
  const r = document.getElementById("result");
  const a = document.getElementById("answers");
  a.innerHTML = "";
  r.innerHTML = `<span style="color:var(--muted)">正在判题……</span>`;
  const code = editor.getValue();
  let data;
  try {
    // 60 秒还没回来就主动放弃，避免页面永远停在"正在判题……"
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 60000);
    const res = await fetch("/api/judge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, code }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error("HTTP " + res.status);
    data = await res.json();
  } catch (e) {
    // 判题请求本身失败（服务关了 / 超时 / 返回 500）—— 一定要留痕，
    // 否则用户只看到「判题没有响应」，作者完全不知道发生了什么。
    reportLog("ERROR", "判题请求失败：" + e, { where: "judge#" + id, stack: (e && e.stack) || "" });
    r.innerHTML = `<div style="color:var(--terracotta);line-height:1.7">
      判题没有响应：本地服务可能已经关掉了（那个黑色窗口没了）。<br>
      请重新双击「C 语言学习器」，等黑窗口出现后刷新本页，再点一次提交。<br>
      <span style="font-size:12.5px;color:var(--olive)">技术细节：${esc(String(e))}（已写进运行日志）</span></div>`;
    return;
  }
  DATA.progress = data.progress;
  if (data.ac) DATA.ac = data.ac;      // 通过后刷新留档，页面和"通过代码"页都同步

  const vtext = { AC: "通过", WA: "答案错误", CE: "编译错误", TLE: "超时", RE: "运行错误" };
  const color = data.verdict === "AC" ? "var(--terracotta-dk)" : "var(--terracotta)";
  let h = `<div style="font-weight:500;color:${color}">${data.verdict} · ${vtext[data.verdict] || data.verdict}</div>`;
  if (data.verdict === "CE") {
    h += `<pre class="msg">${hl(data.message)}</pre>`;
  } else {
    h += `<div style="margin-top:4px">${hl(data.message)}</div>`;
    if (data.detail) {
      data.detail.forEach((dd) => {
        if (dd.verdict === "WA") {
          h += `<pre class="msg">样例 ${dd.no}：你的输出 [${hl(dd.actual)}]，期望 [${hl(dd.expected)}]</pre>`;
        }
      });
    }
  }
  r.innerHTML = h;

  // 通过后展示参考答案 + 最佳答案
  let answerHTML = "";
  if (data.verdict === "AC") {
    const p = DATA.oj.find((x) => x.id === id);
    answerHTML = `<details class="answer-block" open>
      <summary>参考答案（朴素正确）</summary>
      ${codeCard(p.reference, "参考答案 · 朴素写法")}</details>
      <details class="answer-block">
      <summary>最佳答案（更简洁/高效，看注释）</summary>
      ${codeCard(p.best, "最佳答案 · 更简洁高效")}</details>`;
    a.innerHTML = answerHTML;
  }

  // 刷新左侧列表状态 + 提交记录
  renderOJ($("#content"));
  const items = document.querySelectorAll(".oj-item");
  const target = [...items].find((x) => x.textContent.startsWith(id + "."));
  if (target) showOJ(id, target);

  // 上面重建了整个页面，结果区和答案区会被清空，这里贴回去
  const r2 = $("#result");
  const a2 = $("#answers");
  if (r2) r2.innerHTML = h;
  if (a2) a2.innerHTML = answerHTML;
}

// ============================================================
// 错题本
// ============================================================
function noteBox(type, key, note) {
  return `<div class="note-box">
    <div class="note-label">我的笔记</div>
    <textarea class="note-input" data-note data-type="${type}" data-key="${key}" placeholder="记下这道题为什么错、要注意什么……">${esc(note)}</textarea>
  </div>`;
}

function saveNote(ta) {
  const type = ta.dataset.type;
  const key = ta.dataset.key;
  if (!DATA.progress.notes[type]) DATA.progress.notes[type] = {};
  DATA.progress.notes[type][key] = ta.value;
  saveProgress();
}

function renderWrongbook(c) {
  const letters = ["A", "B", "C", "D"];
  let h = `<div class="content-inner"><div class="page-head"><div class="kicker">WRONG BOOK</div><h1>错题本</h1>
    <div class="desc">答错的测验题 + 没通过的 OJ 题。OJ 错题点开看错误提交的代码，每道都能记笔记。</div></div>`;

  // 测验错题
  h += `<h3>测验错题</h3>`;
  if (DATA.progress.quiz_wrong.length === 0) {
    h += `<p style="color:var(--olive)">还没有答错的题，继续保持。</p>`;
  } else {
    DATA.progress.quiz_wrong.forEach((idx) => {
      const q = DATA.quizzes[idx];
      if (!q) return;
      const note = (DATA.progress.notes.quiz && DATA.progress.notes.quiz[idx]) || "";
      h += `<div class="card wrong-card">
        <div style="font-size:15px">${hl(q.question)}</div>
        <div class="wrong-answer">正确答案：${letters[q.answer]}. ${hl(q.options[q.answer])}</div>
        <div style="font-size:13.5px;color:var(--olive);margin-top:6px">${hl(q.explain)}</div>
        ${noteBox("quiz", idx, note)}
      </div>`;
    });
  }

  // OJ 未通过
  h += `<h3 style="margin-top:26px">OJ 未通过</h3>`;
  const notAc = DATA.oj.filter((p) => DATA.progress.oj[p.id] && DATA.progress.oj[p.id] !== "AC");
  if (notAc.length === 0) {
    h += `<p style="color:var(--olive)">OJ 全部通过，厉害。</p>`;
  } else {
    notAc.forEach((p) => {
      const st = DATA.progress.oj[p.id];
      const note = (DATA.progress.notes.oj && DATA.progress.notes.oj[p.id]) || "";
      const errSubs = DATA.progress.submissions.filter((s) => s.pid === p.id && s.verdict !== "AC");
      h += `<details class="answer-block wrong-oj">
        <summary>${p.id}. ${esc(p.title)} &nbsp;<span class="tag">${esc(st)}</span></summary>
        <div class="wrong-oj-body">
          ${errSubs.length ? errSubs.slice(-3).map((s) => `
            <div class="sub-detail">
              <div class="sub-meta"><span class="sub-time">${esc(s.time)}</span><span class="sub-verdict ${s.verdict.toLowerCase()}">${esc(s.verdict)}</span></div>
              <div style="font-size:13px;color:var(--olive);margin:4px 0">${hl(s.message)}</div>
              ${(s.detail || []).filter((d) => d.verdict === "WA").map((d) => `<div style="font-size:12.5px;color:var(--olive)">样例 ${d.no}：你的输出 [${esc(d.actual)}] 期望 [${esc(d.expected)}]</div>`).join("")}
              ${codeCard(s.code, "当时的提交")}
            </div>
          `).join("") : `<p style="color:var(--olive)">暂无错误提交记录</p>`}
          ${noteBox("oj", p.id, note)}
        </div>
      </details>`;
    });
  }
  h += `</div>`;
  c.innerHTML = h;

  // 笔记失焦自动保存
  c.querySelectorAll("[data-note]").forEach((ta) => ta.addEventListener("blur", () => saveNote(ta)));
}

// ============================================================
// 进度页
// ============================================================
// 通过代码（AC 留档）
function renderMyCode(c) {
  const ids = Object.keys(DATA.ac || {}).map(Number).sort((a, b) => a - b);
  let h = `<div class="content-inner"><div class="page-head"><div class="kicker">MY CODE</div><h1>通过代码</h1>
    <div class="desc">OJ 判题通过（AC）时，代码会自动留档到这里，共 ${ids.length} 题。
    之后改坏了也不影响这份记录，重新 AC 才会更新；文件同时在 ac 文件夹里存着，可以直接用编辑器打开。</div></div>`;

  if (!ids.length) {
    h += `<div class="card"><p style="color:var(--olive);margin:0">还没有通过的题。
      去「OJ 刷题」做一道，判题通过后会立刻出现在这里。</p></div>`;
  } else {
    h += `<div class="code-list">`;
    ids.forEach((pid) => {
      const p = DATA.oj.find((x) => x.id === pid) || { title: "题目 " + pid, difficulty: "", block: pid };
      const rec = DATA.ac[String(pid)];
      const first = rec.first && rec.first !== rec.last ? ` · 首次 ${rec.first}` : "";
      h += `<details class="answer-block">
        <summary>${pid}. ${hl(p.title)} <span class="tag">${esc(p.difficulty || "")}</span>
          <span class="ac-meta">${esc(rec.last || rec.first || "")}${esc(first)} · ${rec.lines} 行 · 通过 ${rec.count || 1} 次</span></summary>
        <div class="ac-tools"><button class="btn btn--secondary btn--sm" data-copy="${pid}">复制代码</button></div>
        ${codeCard(rec.code, "我的通过代码 · " + p.title)}
      </details>`;
    });
    h += `</div>`;
  }
  h += `</div>`;
  c.innerHTML = h;

  c.querySelectorAll("[data-copy]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const code = (DATA.ac[btn.dataset.copy] || {}).code || "";
      const done = () => {
        const old = btn.textContent;
        btn.textContent = "已复制 ✓";
        setTimeout(() => (btn.textContent = old), 1500);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(code).then(done).catch(done);
      else done();
    })
  );
}

// 关于页：作者信息 + vibe coding 说明 + 版本 + 卸载入口
function renderAbout(c) {
  const app = DATA.app || {};
  const a = app.author || {};
  const stack = (a.stack || []).map((s) => `<li>${hl(s)}</li>`).join("");
  const mono = (t) => `<code class="tok tk-fn">${esc(t)}</code>`;

  c.innerHTML = `<div class="content-inner"><div class="page-head"><div class="kicker">ABOUT</div>
    <h1>关于</h1>
    <div class="desc">一个自己做的 C 语言练习册：36 节课、72 道测验、36 道 OJ，判题用的是本地编译器。</div></div>

    <div class="card about-hero">
      <div class="about-avatar">${esc(a.avatar || "C")}</div>
      <div style="flex:1">
        <h2 style="margin:0">${esc(a.name || "")}</h2>
      </div>
      <div class="about-version">v${esc(app.version || "")}</div>
    </div>

    <div class="card">
      <h3>作者信息</h3>
      <div class="about-grid">
        <div><span>作者</span>${esc(a.name || "-")}</div>
        <div><span>QQ</span>${esc(a.qq || "-")}</div>
      </div>
      <p class="about-note">${esc(a.note || "")}</p>
    </div>

    <div class="card">
      <h3>这个软件是怎么做出来的</h3>
      <p class="about-note"><b>全程 vibe coding</b>：从需求、结构设计，到 36 节课程内容、72 道测验、
      36 道 OJ 题目与判题器、前端语法高亮、打包脚本，都是在 AI 辅助下一点点迭代出来的。
      作者负责定方向、试错、验收和修 bug —— 代码是聊出来的，东西是自己想要的。</p>
      <p class="about-note">课程体系参考谭浩强《C 程序设计》与何钦铭《C 语言程序设计》，
      题目、示例代码与界面均为原创；判题在自己电脑上用 gcc 真编译、真运行。</p>
      <ul class="about-stack">${stack}</ul>
    </div>

    <div class="card">
      <h3>版本与数据</h3>
      <div class="about-grid">
        <div><span>版本</span>v${esc(app.version || "")}（${esc(app.build || "")}）</div>
        <div><span>形态</span>${app.frozen ? "安装版" : "开发版 / 便携版"}</div>
        <div><span>学习数据</span>${mono(app.data_dir || "")}</div>
        <div><span>编译器</span>MinGW-w64 gcc</div>
      </div>
      <div class="about-actions">
        ${app.uninstaller
          ? `<button class="btn btn--secondary" id="uninstall">卸载本软件</button>
             <span class="about-hint">学习进度不会被删除。</span>`
          : `<span class="about-hint">当前是开发版 / 便携版，没有卸载程序：删掉程序文件夹就行，学习数据在上面的目录里。</span>`}
      </div>
    </div>

    <div class="card">
      <h3>运行日志</h3>
      <p class="about-note">启动失败、判题没反应、页面白屏这类问题，后端和页面都会写进同一个日志文件。
      真出问题时点「查看最近日志」，把内容复制发给作者就能定位。日志按天分文件，只保留最近 7 天。</p>
      <div class="about-actions">
        <button class="btn btn--secondary" id="showlog">查看最近日志</button>
        <button class="btn btn--secondary" id="openlog">打开日志文件夹</button>
        <span class="about-hint" id="loghint">${mono(app.log_dir || "")}</span>
      </div>
      <pre class="msg" id="logbox" style="display:none;max-height:340px;overflow:auto;white-space:pre-wrap;word-break:break-all"></pre>
    </div>
  </div>`;

  const btn = $("#uninstall");
  if (btn) {
    btn.addEventListener("click", async () => {
      if (!confirm("确定要卸载「C 语言学习器」吗？学习进度会保留。")) return;
      btn.disabled = true;
      try {
        const res = await fetch("/api/uninstall", { method: "POST" });
        const d = await res.json();
        alert(d.message || "已启动卸载程序");
      } catch (e) {
        alert("启动卸载程序失败：" + e);
        reportLog("ERROR", "卸载请求失败：" + e, { where: "about/uninstall" });
      }
    });
  }

  // ---- 运行日志：查看 / 打开文件夹 ----
  const showBtn = $("#showlog");
  const logBox = $("#logbox");
  if (showBtn && logBox) {
    showBtn.addEventListener("click", async () => {
      if (logBox.style.display !== "none") {
        logBox.style.display = "none";
        showBtn.textContent = "查看最近日志";
        return;
      }
      logBox.style.display = "block";
      logBox.textContent = "读取中……";
      showBtn.textContent = "收起日志";
      try {
        const res = await fetch("/api/logs?n=300", { cache: "no-store" });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const j = await res.json();
        const lines = j.lines || [];
        logBox.textContent = lines.length ? lines.join("\n") : "（今天还没有日志）";
        logBox.scrollTop = logBox.scrollHeight;
        if (j.path) $("#loghint").textContent = j.path;
      } catch (e) {
        logBox.textContent = "读日志失败：" + e + "\n（本地服务可能已经关掉了）";
        reportLog("ERROR", "读取 /api/logs 失败：" + e, { where: "about/logs" });
      }
    });
  }

  const openLogBtn = $("#openlog");
  if (openLogBtn) {
    openLogBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/open-log", { method: "POST" });
        const j = await res.json();
        if (!j.ok) alert("打不开日志文件夹：" + (j.message || "未知原因"));
      } catch (e) {
        alert("打不开日志文件夹：" + e);
        reportLog("ERROR", "打开日志文件夹失败：" + e, { where: "about/openlog" });
      }
    });
  }
}

function renderProgress(c) {
  let h = `<div class="content-inner"><div class="page-head"><div class="kicker">PROGRESS</div><h1>我的进度</h1>
    <div class="desc">累计学习 ${DATA.progress.days} 天。</div></div><div class="card">
    <h3 style="margin-top:0">课程</h3><div class="progress-table">`;
  let learned = 0;
  DATA.lessons.forEach((L, i) => {
    const n = i + 1;
    const st = lessonState(String(n));
    if (st.done) learned++;
    const s = st.done
      ? (st.score >= 0 ? `<span class="st ac">已学 · ${st.score} 分</span>` : `<span class="st ac">已学</span>`)
      : `<span class="st">未学</span>`;
    h += `<div class="progress-row"><span class="title">第 ${n} 节 ${hl(L.title)}</span>${s}</div>`;
  });
  h += `</div><div style="margin-top:10px;font-size:14px;color:var(--olive)">已学 ${learned} / ${DATA.lessons.length} 节</div>
    <div class="divider"></div>
    <h3>OJ 刷题</h3><div class="progress-table">`;
  let ac = 0;
  DATA.oj.forEach((p) => {
    const st = DATA.progress.oj[p.id];
    if (st === "AC") ac++;
    const s = st === "AC" ? `<span class="st ac">AC</span>` : `<span class="st">${st || "未做"}</span>`;
    h += `<div class="progress-row"><span class="title">${p.id}. ${hl(p.title)}</span>${s}</div>`;
  });
  h += `</div><div style="margin-top:10px;font-size:14px;color:var(--olive)">OJ 通过 ${ac} / ${DATA.oj.length} 题</div></div></div>`;
  c.innerHTML = h;
}

init();
