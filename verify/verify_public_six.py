# -*- coding: utf-8 -*-
r"""SINOSFT 公开层 · 六大主线结论计数自洽断言（B 类验证）

纪律：
  1. 本脚本只读取 public_assertions.json 的结论计数与边界声明，做结构性自洽判定。
  2. 不含任何工程参数、结构细节、控制算法，也不含敏感词表 —— 我们给出结论，不给出底牌。
  3. 退出码 0 是唯一验收判据。人可以写文案，不能写 PASS。
  4. 带鉴别力测试：故意注入错误样本，断言器必须抓到，否则零命中毫无意义。

用法：
    python3 verify_public_six.py             # 正式验收
    python3 verify_public_six.py --selftest # 鉴别力测试（应全部被抓到）
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "public_assertions.json")
IDS = ["A", "B", "C", "D", "E", "F"]

with open(DATA, encoding="utf-8") as f:
    D = json.load(f)

FAILS = []
N = [0]


def ck(name, ok, detail=""):
    N[0] += 1
    if not ok:
        FAILS.append(name + (" | " + detail if detail else ""))
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  <- " + detail) if (not ok and detail) else ""))
    return bool(ok)


def run(d, quiet=False):
    global FAILS, N
    saved = (FAILS, N)
    FAILS, N = [], [0]
    lines = d.get("lines", [])
    bd = d.get("boundary", [])
    bde = d.get("boundary_en", [])
    ck("六条主线齐备且顺序为 A–F", [x.get("id") for x in lines] == IDS)
    ck("每条主线均有非空名称", all(isinstance(x.get("name_zh"), str) and x["name_zh"].strip() for x in lines))
    ck("每条主线均有正的断言计数", all(isinstance(x.get("assertions"), int) and x["assertions"] > 0 for x in lines))
    ck("每条主线退出码均为 0", all(x.get("exit_code") == 0 for x in lines))
    ck("每条主线均标注适用范围", all(isinstance(x.get("scope"), str) and x["scope"].strip() for x in lines))
    ck("边界声明不少于 5 条且逐条非空", len(bd) >= 5 and all(isinstance(x, str) and x.strip() for x in bd))
    ck("边界声明具备英文对应且条数一致", len(bde) == len(bd))
    ck("边界声明含「不替代专项设计与物理试验」", any("不替代专项设计" in x for x in bd))
    ck("边界声明含「不是物理实测量」", any("不是物理实测量" in x for x in bd))
    ck("边界声明含「不以达标口径对外表述」", any("不以达标口径" in x for x in bd))
    ck("元信息声明结论级口径", "conclusion-level" in d.get("_meta", {}).get("scope", ""))
    ck("元信息声明核心参数不在公开范围", "不在公开范围" in d.get("_meta", {}).get("note_zh", ""))
    p, f = N[0] - len(FAILS), len(FAILS)
    FAILS, N = saved
    return p, f


def main():
    if "--selftest" in sys.argv:
        cases = [
            ("删除一条主线", lambda x: {**x, "lines": x["lines"][:-1]}),
            ("把退出码改为非零", lambda x: {**x, "lines": [{**x["lines"][0], "exit_code": 1}] + x["lines"][1:]}),
            ("把断言计数清零", lambda x: {**x, "lines": [{**x["lines"][2], "assertions": 0}] + x["lines"][:2] + x["lines"][3:]}),
            ("删光边界声明", lambda x: {**x, "boundary": []}),
            ("抹掉元信息口径", lambda x: {**x, "_meta": {**x["_meta"], "scope": ""}}),
        ]
        caught = 0
        for name, mutate in cases:
            _, f = run(mutate(copy.deepcopy(D)))
            ok = f > 0
            caught += int(ok)
            print("  [%s] 鉴别力 · %s（应被抓到）" % ("PASS" if ok else "FAIL", name))
        print("\n鉴别力：%d / %d 被抓到" % (caught, len(cases)))
        return 0 if caught == len(cases) else 1
    p, f = run(D)
    print("\n合计 %d 条 | PASS %d | FAIL %d" % (p + f, p, f))
    print("人可以写文案，不能写 PASS —— 本文件即判据。")
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
