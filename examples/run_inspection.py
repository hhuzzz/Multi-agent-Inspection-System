from __future__ import annotations

import json

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

from inspection_system.pipeline import InspectionPipeline
from inspection_system.schemas import InspectionTask


def main() -> None:
    if load_dotenv is not None:
        load_dotenv()

    task = InspectionTask(
        task_id="demo-001",
        target="隧道 K12+300 区段",
        description="对指定隧道区段进行巡检，判断是否存在结构或环境风险。",
        inputs={
            "images": ["data/2.jpg"],
            "notes": "示例输入。真实使用时可放图片路径、检测文本、传感器摘要等。",
        },
    )

    pipeline = InspectionPipeline()
    result = pipeline.run(task)
    print("\n========== 最终完整结果 ==========", flush=True)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
