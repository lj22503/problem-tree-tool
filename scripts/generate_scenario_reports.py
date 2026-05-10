#!/usr/bin/env python3
"""
预生成场景报告脚本
把6个场景用 Map 深度模式跑一遍，生成预置报告
"""
import sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import create_backend
from core.prompt_engine import IterativeWaterfallEngine

SCENARIOS = [
    {
        "id": "entrepreneur",
        "icon": "🚀",
        "title": "创业者 / 独立开发者",
        "question": "我要不要做这个AI产品？",
        "desc": "脑子里100个问题，不知道先解哪个——游刃就是你的外脑",
    },
    {
        "id": "pm",
        "icon": "📋",
        "title": "产品经理 / 运营",
        "question": "这个版本该做什么功能？",
        "desc": "需求太多，优先级排不清——游刃是\"模糊变清晰\"的加速器",
    },
    {
        "id": "career",
        "icon": "🎯",
        "title": "职场转型 / 职业规划",
        "question": "35岁，想从传统行业转AI",
        "desc": "想转行但不知道转什么、怎么转——游刃帮你系统拆解决策",
    },
    {
        "id": "creator",
        "icon": "✍️",
        "title": "内容创作者 / 自媒体",
        "question": "AI时代，个人IP怎么做？",
        "desc": "选题枯竭，不知道写什么——好问题才有好内容",
    },
    {
        "id": "researcher",
        "icon": "🔬",
        "title": "学生 / 研究者",
        "question": "区块链+供应链，有什么研究价值？",
        "desc": "论文选题、研究方向不明确——游刃帮你找到研究缺口",
    },
    {
        "id": "review",
        "icon": "📝",
        "title": "年终复盘 / 日常反思",
        "question": "年终总结不知道怎么写，感觉一年下来没什么可写的",
        "desc": "觉得自己没成绩、找不到亮点——把一年拆开看，其实做了很多事",
    },
]


def generate_report(scenario, engine, backend):
    print(f"\n{'='*60}")
    print(f"生成中: {scenario['title']}")
    print(f"问题: {scenario['question']}")
    print(f"{'='*60}")
    start = time.time()
    try:
        result = engine.run(
            question=scenario["question"],
            backend=backend,
            context=None,
            max_tokens=6000,
            progress_callback=lambda msg: print(f"  >> {msg[:80]}"),
        )
        elapsed = time.time() - start
        print(f"✅ 完成，耗时 {elapsed:.1f}s，输出 {len(result)} 字")
        return result
    except Exception as e:
        print(f"❌ 失败: {e}")
        return None


def main():
    # 用 deepseek 作为 backend（需要 DEEPSEEK_API_KEY 环境变量）
    try:
        backend = create_backend("deepseek")
    except Exception as e:
        print(f"❌ 无法创建 DeepSeek backend: {e}")
        print("请设置 DEEPSEEK_API_KEY 环境变量")
        sys.exit(1)

    engine = IterativeWaterfallEngine()
    reports = {}

    for scenario in SCENARIOS:
        result = generate_report(scenario, engine, backend)
        reports[scenario["id"]] = {
            "question": scenario["question"],
            "report": result or "",
            "generated_at": time.strftime("%Y-%m-%d %H:%M"),
        }
        # 避免频率限制，场景之间稍作暂停
        time.sleep(2)

    # 写入 JSON 文件
    output_path = Path(__file__).parent.parent / "vercel_app" / "scenario_reports.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 报告已写入: {output_path}")
    print(f"   共 {len(reports)} 个场景")


if __name__ == "__main__":
    main()
