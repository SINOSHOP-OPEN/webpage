# -*- coding: utf-8 -*-
"""
20261031 · 生成「已提交审核数据集 · 仿真验证证据总览」公网 Markdown
================================================================================
用途：从权威 JSON（`DATASET_verify_links.json`，源自平台实况 × 归档材料实扫）
      生成**面向公网**的映射表 Markdown —— 只含公开信息，不含任何内部痕迹。

★ 公网版只含「数据集名称 → 验证形态 → 可点直链」；
  任何登记编号、内部台账字段与隔离声明**一律不出本机**。

用法：python build_public_dataset_map.py <json> <输出md>
"""
import json
import sys

KIND_TAG = {"A": "带核验结果 JSON", "B": "要素装配验证",
            "C": "可复算性验证", "D": "无独立仿真结论"}
KIND_ICON = {"A": "🟢", "B": "🔵", "C": "🟣", "D": "⚪"}
KIND_DESC = {
    "A": "归档包内含 `verify_NN_*` 核验结果 → 与公开仓同名文件一一对应",
    "B": "归档包内含 `要素装配与验证.json` → 由数据自洽性检验脚本承接复核",
    "C": "归档包内含可复算性核验 → 由数据自洽性检验脚本承接复核",
    "D": "纯几何载体 / 工程模型 / 编码规范 / 参数台账 / 展示成片 —— 本身即数据，无独立物理仿真结论",
}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    data = json.load(open(src, encoding="utf-8"))

    L = []
    A = L.append
    A("# 已提交审核数据集 · 仿真验证证据总览")
    A("")
    A("> 平台：广东省数据知识产权登记平台　｜　核对时间：2026-10-31")
    A("> 下列 **17 份**数据集**均已向平台提交登记，当前处于「待审核」阶段**，")
    A("> **尚未取得登记证书**。本页展示的是平台受理状态与**结论级验证证据**，")
    A("> **不构成任何形式的权利授予、认证或确权主张**。")
    A("> 每一条链接均为**公网直链**，点开即得文件本体，无需登录。")
    A("")
    A("---")
    A("")
    A("## 一、总览")
    A("")
    A("| # | 数据集名称 | 验证形态 | 核验结果链接数 |")
    A("|:--|:--|:--|--:|")
    for i, e in enumerate(data, 1):
        n = sum(1 for l in e["links"] if l.get("url"))
        A("| %d | %s | %s %s | %d |"
          % (i, e["name"], KIND_ICON.get(e["kind"], ""), KIND_TAG.get(e["kind"], "?"), n))
    A("")
    A("**验证形态说明**")
    A("")
    for k in ("A", "B", "C", "D"):
        A("- %s **%s** —— %s" % (KIND_ICON[k], KIND_TAG[k], KIND_DESC[k]))
    A("")
    A("---")
    A("")
    A("## 二、逐数据集验证证据")
    A("")
    for i, e in enumerate(data, 1):
        A("### %d. %s" % (i, e["name"]))
        A("")
        A("- **验证形态**：%s %s —— %s"
          % (KIND_ICON.get(e["kind"], ""), KIND_TAG.get(e["kind"], "?"), e["desc"]))
        A("")
        rows = [l for l in e["links"] if l.get("url")]
        if rows:
            A("| 验证主线 | 结果文件 | 公网直链 |")
            A("|:--|:--|:--|")
            for l in rows:
                A("| %s | `%s` | [打开](%s) |" % (l["mainline"], l["file"], l["url"]))
            A("")
        else:
            A("> %s" % KIND_DESC.get(e["kind"], ""))
            A("")
        notes = [l["note"] for l in e["links"] if l.get("note")]
        if notes:
            for n in dict.fromkeys(notes):
                A("> 注：%s" % n)
            A("")

    A("---")
    A("")
    A("## 三、公共验证层入口（对全部 17 份均适用）")
    A("")
    A("| 用途 | 直链 |")
    A("|:--|:--|")
    A("| **仿真验证证据总览（网页版）** | [evidence/index.html](https://sinoshop-open.github.io/webpage/docs/evidence/) |")
    A("| 聚合运行器（Gitee · 一条命令跑完 15 条主线） | [run_all_public_verifications.py](https://gitee.com/sinoshop/sinoport-public/raw/master/verify/run_all_public_verifications.py) |")
    A("| 聚合运行器（GitHub） | [run_all_public_verifications.py](https://raw.githubusercontent.com/SINOSHOP-OPEN/SinoPORT/main/verify/run_all_public_verifications.py) |")
    A("| 数字存证清单（43 份文件 SHA-256） | [MANIFEST_public_assertions.md](https://gitee.com/sinoshop/sinoport-public/raw/master/verify/MANIFEST_public_assertions.md) |")
    A("| AI Agent 最小骨架 | [agent_min_skeleton.py](https://gitee.com/sinoshop/sinoport-public/raw/master/verify/agent_min_skeleton.py) |")
    A("| 数据自洽性检验脚本（B / C 类承接） | [verify_public_dataset.py](https://gitee.com/sinoshop/sinoport-public/raw/master/verify/verify_public_dataset.py) |")
    A("| 门面入口（Gitee 主仓） | [sinoshop/SinoPORT](https://gitee.com/sinoshop/SinoPORT) |")
    A("| 门面入口（GitHub 主仓） | [SINOSHOP-OPEN/SinoPORT](https://github.com/SINOSHOP-OPEN/SinoPORT) |")
    A("")
    A("---")
    A("")
    A("## 四、边界声明")
    A("")
    A("- 本页只列**结论级**验证证据与可复现路径；")
    A("- 归档侧的真实几何尺寸、材料配比与流体参数**不在公网**；")
    A("- 结论由脚本判定，退出码为零才算通过；无法验证时如实报告 `BLOCKED`。")
    A("")
    A("> 人可以写文案，但不能写 PASS。")
    A("")

    open(dst, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("已生成：%s（%d 字节）" % (dst, len("\n".join(L))))


if __name__ == "__main__":
    main()
