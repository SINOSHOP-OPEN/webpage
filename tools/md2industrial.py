# -*- coding: utf-8 -*-
"""
20261031 · 通用 Markdown → 极简工业风 HTML 生成器
================================================================================
用途：把 Markdown 文档转成排版精美、阅读感极佳的独立网页（可部署到 GitHub Pages）。

视觉规范（船长指令）：
  · 深空灰 / 深蓝底色，纯白字体，翡翠绿高亮链接；
  · 纯文本表格 → CSS 渲染成**带斑马纹、有悬浮效果**的高级表格；
  · 代码块 → **带高亮的 UI 框**（含标题栏、语言标签、行号、复制提示）；
  · 极简工业风：细边框、克制的圆角、等宽字体点缀、大留白。

★ 自带 Markdown 解析器（环境无 markdown/pygments/mistune）——
  覆盖：H1-H6 / 段落 / 有序无序列表 / 表格 / 引用块 / 围栏代码块（含轻量语法高亮）/
        图片 / 链接 / 行内代码 / 粗体 / 斜体 / 分隔线 / HTML 注释。

用法：python md2industrial.py <输入md> <输出html> --title "…" --eyebrow "…"
      [--base 站点基址] [--nav 链接名=URL,链接名=URL] [--footer "页脚说明"]
"""
import argparse
import html as html_mod
import os
import re
import urllib.parse

FENCE = chr(96) * 3


# ══════════════════════════════════════════════════════════════════
#  极简工业风 CSS
# ══════════════════════════════════════════════════════════════════
CSS = """
:root{
  --bg:#0b1118; --bg-2:#0f1721; --panel:#131c27; --panel-2:#17212e;
  --line:#22303f; --line-2:#2c3d4f;
  --ink:#f2f6fa; --ink-2:#c3ced9; --ink-3:#8b9aab; --ink-4:#5f6f80;
  --green:#1d9e75; --green-l:#2ee6a8; --green-d:#146b4f;
  --blue:#2b6cb0; --gold:#c9a227; --red:#c05656;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,"JetBrains Mono",monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC","Hiragino Sans GB",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:var(--sans);font-size:15.5px;line-height:1.78;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
a{color:var(--green-l);text-decoration:none;border-bottom:1px solid rgba(46,230,168,.28);transition:.18s}
a:hover{color:#6bffd0;border-bottom-color:var(--green-l)}
strong{color:#fff;font-weight:650}
em{color:var(--ink-2)}

/* ── 页头 ── */
.hero{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(1100px 460px at 14% -12%,rgba(29,158,117,.16),transparent 62%),
    radial-gradient(900px 400px at 92% -18%,rgba(43,108,176,.14),transparent 60%),
    linear-gradient(180deg,#0d1620 0%,var(--bg) 100%);
  padding:52px 0 40px;position:relative;overflow:hidden;
}
.hero::after{
  content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--green) 22%,var(--blue) 62%,transparent);
}
.wrap{max-width:1120px;margin:0 auto;padding:0 26px}
.eyebrow{
  font-family:var(--mono);font-size:11.5px;letter-spacing:2.6px;color:var(--green-l);
  text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:11px;
}
.eyebrow::before{content:"";width:26px;height:1px;background:var(--green);flex:none}
.hero h1{
  margin:0 0 16px;font-size:clamp(26px,3.4vw,40px);line-height:1.24;font-weight:700;
  letter-spacing:-.4px;color:#fff;
}
.hero .lede{margin:0;max-width:760px;color:var(--ink-2);font-size:15.5px}
.hero .tags{margin-top:22px;display:flex;flex-wrap:wrap;gap:8px}
.tag{
  font-family:var(--mono);font-size:11.5px;letter-spacing:.4px;
  padding:5px 12px;border-radius:3px;border:1px solid var(--line-2);
  background:rgba(29,158,117,.09);color:var(--green-l);
}
.tag.b{background:rgba(43,108,176,.1);border-color:rgba(43,108,176,.42);color:#8fc4f5}
.tag.g{background:rgba(201,162,39,.1);border-color:rgba(201,162,39,.4);color:#e2c86a}
.tag.n{background:rgba(255,255,255,.03);color:var(--ink-3)}

/* ── 导航条 ── */
.nav{border-bottom:1px solid var(--line);background:rgba(10,16,23,.92);position:sticky;top:0;z-index:50;backdrop-filter:blur(10px)}
.nav .wrap{display:flex;align-items:center;gap:4px;height:52px;overflow-x:auto}
.nav .brand{font-family:var(--mono);font-size:12px;letter-spacing:1.6px;color:var(--ink-4);margin-right:14px;white-space:nowrap}
.nav a{
  font-size:13.5px;color:var(--ink-2);padding:7px 13px;border-radius:4px;
  border:1px solid transparent;white-space:nowrap;transition:.16s;
}
.nav a:hover{background:var(--panel);border-color:var(--line-2);color:#fff;border-bottom-color:transparent}
.nav a.back{color:var(--green-l);border-color:rgba(46,230,168,.3);background:rgba(29,158,117,.08)}

/* ── 正文 ── */
main{padding:44px 0 76px}
.doc{max-width:1120px}
.doc h1{display:none}
.doc h2{
  font-size:20px;margin:52px 0 18px;color:#fff;font-weight:680;letter-spacing:.2px;
  padding:0 0 12px 14px;border-left:3px solid var(--green);position:relative;
}
.doc h2::after{content:"";position:absolute;left:14px;right:0;bottom:0;height:1px;background:var(--line)}
.doc h3{font-size:16.5px;margin:32px 0 13px;color:#e8f0f7;font-weight:650;letter-spacing:.2px}
.doc h3::before{content:"▸";color:var(--green);margin-right:9px;font-size:13px}
.doc h4{font-size:14.5px;margin:22px 0 10px;color:var(--ink-2)}
.doc p{margin:0 0 15px;color:var(--ink-2)}
.doc ul,.doc ol{margin:0 0 18px;padding-left:22px;color:var(--ink-2)}
.doc li{margin:6px 0}
.doc li::marker{color:var(--green)}
.doc hr{border:0;height:1px;background:var(--line);margin:38px 0}

/* ── 表格（斑马纹 + 悬浮） ── */
.tw{overflow-x:auto;margin:0 0 24px;border:1px solid var(--line);border-radius:7px;background:var(--panel)}
table{width:100%;border-collapse:collapse;font-size:13.8px;min-width:520px}
thead th{
  background:var(--panel-2);color:#fff;font-weight:640;text-align:left;
  padding:13px 15px;border-bottom:1px solid var(--line-2);white-space:nowrap;
  font-size:13px;letter-spacing:.3px;position:sticky;top:0;
}
tbody td{padding:12px 15px;border-bottom:1px solid rgba(34,48,63,.55);color:var(--ink-2);vertical-align:top}
tbody tr:nth-child(even){background:rgba(23,33,46,.5)}
tbody tr:nth-child(odd){background:transparent}
tbody tr{transition:background .16s,box-shadow .16s}
tbody tr:hover{background:rgba(29,158,117,.10);box-shadow:inset 3px 0 0 var(--green)}
tbody tr:hover td{color:var(--ink)}
tbody tr:last-child td{border-bottom:0}

/* ── 代码块（带高亮 UI 框） ── */
.code{
  margin:0 0 24px;border:1px solid var(--line-2);border-radius:8px;overflow:hidden;
  background:#0a121a;box-shadow:0 12px 32px rgba(0,0,0,.34);
}
.code-hd{
  display:flex;align-items:center;gap:9px;padding:9px 14px;
  background:linear-gradient(180deg,#16202c,#111a24);border-bottom:1px solid var(--line);
}
.code-hd .dot{width:9px;height:9px;border-radius:50%;flex:none}
.code-hd .dot.r{background:#c05656}.code-hd .dot.y{background:#c9a227}.code-hd .dot.g{background:#1d9e75}
.code-hd .lang{
  font-family:var(--mono);font-size:11px;letter-spacing:1.4px;color:var(--ink-3);
  margin-left:6px;text-transform:uppercase;
}
.code-hd .hint{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:var(--ink-4);letter-spacing:.8px}
.code pre{margin:0;padding:16px 18px;overflow-x:auto}
.code code{
  font-family:var(--mono);font-size:13px;line-height:1.72;color:#d6e2ec;
  display:block;white-space:pre;
}
.tk-kw{color:#ff9ec4}.tk-str{color:#9ce6b4}.tk-num{color:#f5c877}
.tk-com{color:#5a6b7c;font-style:italic}.tk-fn{color:#8fc4f5}.tk-op{color:#9fb0c0}

/* ── 行内代码 ── */
code.inl{
  font-family:var(--mono);font-size:12.6px;background:rgba(29,158,117,.10);
  border:1px solid rgba(46,230,168,.18);color:#7fe8c4;padding:1.5px 6px;border-radius:4px;
}

/* ── 引用块 / 声明卡 ── */
blockquote{
  margin:0 0 24px;padding:16px 20px;background:var(--panel);
  border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:6px;color:var(--ink-2);
}
blockquote p:last-child{margin-bottom:0}
blockquote strong{color:#fff}
.statement{
  margin:0 0 26px;padding:18px 22px;border-radius:7px;
  background:linear-gradient(180deg,rgba(201,162,39,.09),rgba(201,162,39,.03));
  border:1px solid rgba(201,162,39,.34);border-left:3px solid var(--gold);
}
.statement strong{color:#f0d98a}

/* ── 图片 ── */
figure{margin:0 0 26px}
.doc img{
  max-width:100%;height:auto;display:block;border:1px solid var(--line-2);
  border-radius:8px;background:#fff;padding:8px;
  box-shadow:0 14px 34px rgba(0,0,0,.42);
}
figcaption{font-family:var(--mono);font-size:12px;color:var(--ink-4);margin-top:9px;text-align:center}

/* ── 页脚 ── */
.foot{border-top:1px solid var(--line);padding:30px 0 46px;color:var(--ink-4);font-size:13px}
.foot .row{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;margin-bottom:14px}
.foot a{color:var(--ink-2);border-bottom-color:var(--line-2)}
.foot a:hover{color:var(--green-l)}
.motto{
  font-family:var(--mono);font-size:13.5px;color:var(--green-l);letter-spacing:.5px;
  padding-top:18px;border-top:1px solid var(--line);margin-top:6px;
}
.foot .fine{font-size:12px;color:var(--ink-4);margin-top:10px;line-height:1.7}

@media(max-width:760px){
  .hero{padding:38px 0 30px}
  .wrap{padding:0 18px}
  main{padding:30px 0 56px}
  .doc h2{font-size:18px}
  tbody td{padding:10px 12px}
}
@media print{
  body{background:#fff;color:#000}
  .nav,.code-hd .hint{display:none}
}
"""


# ══════════════════════════════════════════════════════════════════
#  轻量语法高亮（Python / Bash / JSON / HTML）
# ══════════════════════════════════════════════════════════════════
KEYWORDS = {
    "python": ["False", "None", "True", "and", "as", "assert", "async", "await", "break",
               "class", "continue", "def", "del", "elif", "else", "except", "finally",
               "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
               "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
               "self", "print", "len", "range", "int", "float", "str", "list", "dict"],
    "bash": ["if", "then", "else", "fi", "for", "in", "do", "done", "while", "cd", "ls",
             "git", "clone", "echo", "python", "exit", "export", "source"],
    "json": ["true", "false", "null"],
}


def highlight(text, lang):
    """极简高亮 —— 只做安全的分词着色，不求完备，但视觉统一。"""
    lang = (lang or "").lower()
    if lang in ("python", "py"):
        kw = KEYWORDS["python"]
    elif lang in ("bash", "sh", "shell", "console"):
        kw = KEYWORDS["bash"]
    elif lang == "json":
        kw = KEYWORDS["json"]
    else:
        kw = []

    out = []
    # 注释与字符串优先
    parts = re.split(r'(#.*$|"[^"]*"|\'[^\']*\')', text, flags=re.M)
    for part in parts:
        if not part:
            continue
        if part.startswith("#") and (lang in ("python", "py", "bash", "sh", "shell", "yml", "yaml")):
            out.append('<span class="tk-com">%s</span>' % html_mod.escape(part))
        elif part[:1] in ('"', "'"):
            out.append('<span class="tk-str">%s</span>' % html_mod.escape(part))
        else:
            # 关键字 / 数字 / 函数调用
            def _kw(m):
                return ('<span class="tk-kw">%s</span>' % m.group(0)) if m.group(0) in kw else m.group(0)

            def _num(m):
                return '<span class="tk-num">%s</span>' % m.group(0)

            def _fn(m):
                return '<span class="tk-fn">%s</span>' % m.group(0)

            s = html_mod.escape(part)
            if kw:
                s = re.sub(r'\b[A-Za-z_]\w*\b', _kw, s)
            s = re.sub(r'(?<![\w.])\d+(?:\.\d+)?(?![\w.])', _num, s)
            s = re.sub(r'\b([A-Za-z_]\w*)(?=\()', _fn, s)
            out.append(s)
    return "".join(out)


# ══════════════════════════════════════════════════════════════════
#  行内元素
# ══════════════════════════════════════════════════════════════════
def inline(text, base=""):
    t = html_mod.escape(text)
    # 行内代码（先占位，避免其内部被其他规则改写）
    codes = []

    def _stash(m):
        codes.append(m.group(1))
        return "\x00C%d\x00" % (len(codes) - 1)

    t = re.sub(r'`([^`]+)`', _stash, t)
    # 图片
    t = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
               lambda m: '<img src="%s" alt="%s">' % (
                   _abs(m.group(2), base), m.group(1)), t)
    # 链接
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
               lambda m: '<a href="%s">%s</a>' % (_abs(m.group(2), base), m.group(1)), t)
    # 粗体 / 斜体
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'(?<!\w)_([^_\n]+)_(?!\w)', r'<em>\1</em>', t)
    # 行内代码回填
    t = re.sub(r"\x00C(\d+)\x00",
               lambda m: '<code class="inl">%s</code>' % codes[int(m.group(1))], t)
    return t


def _abs(url, base):
    if url.startswith(("http://", "https://", "#", "mailto:")):
        # ★ Gitee raw 是 302 跳 CDN 且带防盗链 —— 跨站 <img> 引用会加载失败（0px）。
        #   命中站内 evidence 资源时，改写为**站内相对路径**（同域、零风险、加载最快）。
        if "gitee.com" in url and "/raw/master/docs/evidence/" in url:
            # 同级目录（页面就在 docs/evidence/ 内）→ ./文件名
            return "./" + url.rsplit("/", 1)[-1]
        return url
    if url.startswith("/") or not base:
        return url
    return base.rstrip("/") + "/" + url.lstrip("/")


# ══════════════════════════════════════════════════════════════════
#  块级解析
# ══════════════════════════════════════════════════════════════════
def parse(md, base=""):
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        s = raw.strip()

        # HTML 注释块 → 丢弃
        if s.startswith("<!--"):
            while i < n and not lines[i].strip().endswith("-->"):
                i += 1
            i += 1
            continue

        # 围栏代码块
        if s.startswith(FENCE):
            lang = s[3:].strip() or "text"
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith(FENCE):
                buf.append(lines[i])
                i += 1
            i += 1
            code = "\n".join(buf)
            out.append(
                '<div class="code"><div class="code-hd">'
                '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
                '<span class="lang">%s</span><span class="hint">COPY · PASTE · RUN</span></div>'
                '<pre><code>%s</code></pre></div>'
                % (html_mod.escape(lang), highlight(code, lang)))
            continue

        # 分隔线
        if re.match(r"^-{3,}$", s):
            out.append("<hr>")
            i += 1
            continue

        # 表格
        if s.startswith("|"):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            out.append(_table(block, base))
            continue

        # 引用块
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner = []
            for b in buf:
                b = b.rstrip()
                if not b.strip():
                    if inner and inner[-1] != "":
                        inner.append("")
                    continue
                mh = re.match(r"^(#{1,6})\s+(.*)$", b)
                inner.append("<strong>%s</strong>" % inline(mh.group(2), base) if mh
                             else inline(b, base))
            while inner and inner[-1] == "":
                inner.pop()
            while inner and inner[0] == "":
                inner.pop(0)
            block_html = "<br>".join(inner)
            if "登记状态声明" in block_html:
                out.append('<div class="statement">%s</div>' % block_html)
            else:
                out.append("<blockquote>%s</blockquote>" % block_html)
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lv = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lv, inline(m.group(2), base), lv))
            i += 1
            continue

        # 无序列表
        if re.match(r"^\s*[-*]\s+", raw):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*[-*]\s+", "", lines[i]), base))
                i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in items))
            continue

        # 有序列表
        if re.match(r"^\s*\d+\.\s+", raw):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]), base))
                i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % x for x in items))
            continue

        # 独立图片
        if s.startswith("!["):
            mimg = re.match(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)", s)
            if mimg:
                alt, src = mimg.group(1), mimg.group(2)
                cap = mimg.group(3) or alt
                out.append('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>'
                           % (_abs(src, base), html_mod.escape(alt), html_mod.escape(cap)))
            i += 1
            continue

        # 空行
        if not s:
            i += 1
            continue

        # 段落（连续非空行合并）
        para = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|\||>|```|-{3,}$|!\[)", lines[i].strip()) \
                and not re.match(r"^\s*[-*]\s+", lines[i]) \
                and not re.match(r"^\s*\d+\.\s+", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para), base))
        else:
            i += 1

    return "\n".join(out)


def _table(block, base):
    rows = []
    for ln in block:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return ""
    head, body = rows[0], rows[2:]
    thead = "".join("<th>%s</th>" % inline(c, base) for c in head)
    tbody = ""
    for r in body:
        tbody += "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, base) for c in r)
    return ('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (thead, tbody))


# ══════════════════════════════════════════════════════════════════
#  页面装配
# ══════════════════════════════════════════════════════════════════
def build_page(md_text, title, eyebrow, lede, tags, nav, footer, base, body_html):
    tag_html = "".join(
        '<span class="tag%s">%s</span>' % (" b" if t[0] == "b" else " g" if t[0] == "g" else "",
                                          html_mod.escape(t[1:]))
        for t in tags) if tags else ""

    nav_html = ""
    if nav:
        items = []
        for label, url in nav:
            cls = " class=\"back\"" if "back" in label.lower() or "←" in label else ""
            items.append('<a href="%s"%s>%s</a>' % (url, cls, html_mod.escape(label)))
        nav_html = ('<nav class="nav"><div class="wrap"><span class="brand">SINOSHOP · SINO-PORT</span>'
                    '%s</div></nav>' % "".join(items))

    doc = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<style>%s</style>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="eyebrow">%s</div>
  <h1>%s</h1>
  <p class="lede">%s</p>
  <div class="tags">%s</div>
</div></header>
%s
<main><div class="wrap"><div class="doc">
%s
</div></div></main>
<footer class="foot"><div class="wrap">
  <div class="row">%s</div>
  %s
  <div class="fine">%s</div>
</div></footer>
</body>
</html>
""" % (
        html_mod.escape(title), html_mod.escape(lede), html_mod.escape(title),
        html_mod.escape(lede), CSS,
        html_mod.escape(eyebrow), html_mod.escape(title), lede, tag_html,
        nav_html, body_html,
        footer.get("row", ""), footer.get("motto", ""), footer.get("fine", ""),
    )
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--title", required=True)
    ap.add_argument("--eyebrow", default="SINOSHOP · SINO-PORT")
    ap.add_argument("--lede", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--nav", default="")
    ap.add_argument("--footer-row", default="")
    ap.add_argument("--footer-motto", default="")
    ap.add_argument("--footer-fine", default="")
    args = ap.parse_args()

    md = open(args.src, encoding="utf-8").read()
    body = parse(md, args.base)

    tags = []
    for t in args.tags.split(","):
        t = t.strip()
        if t:
            tags.append(("b" if t.startswith("b:") else "g" if t.startswith("g:") else "") + t.split(":", 1)[-1])

    nav = []
    for item in args.nav.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            k, v = item.split("=", 1)
            nav.append((k.strip(), v.strip()))

    footer = {"row": args.footer_row, "motto": args.footer_motto, "fine": args.footer_fine}

    doc = build_page(md, args.title, args.eyebrow, args.lede, tags, nav, footer,
                     args.base, body)
    os.makedirs(os.path.dirname(os.path.abspath(args.dst)), exist_ok=True)
    with open(args.dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print("已生成：%s（%d 字节）" % (args.dst, len(doc)))


if __name__ == "__main__":
    main()
