from __future__ import annotations

import json

from inspection_system.agents import (
    DefectDetectionAgent,
    ReinspectionAgent,
    RiskAlertAgent,
    SceneAnalysisAgent,
)
from inspection_system.openai_client import OpenAIClient
from inspection_system.schemas import ACTIONABLE_OBJECTS, AgentOutput, InspectionResult, InspectionTask


class InspectionPipeline:
    """Fixed four-agent workflow for tunnel inspection."""

    def __init__(self, client: OpenAIClient | None = None) -> None:
        self.client = client or OpenAIClient()
        self.agents = [
            SceneAnalysisAgent(self.client),
            DefectDetectionAgent(self.client),
            ReinspectionAgent(self.client),
            RiskAlertAgent(self.client),
        ]

    def run(self, task: InspectionTask) -> InspectionResult:
        result = InspectionResult(task=task, outputs=[])

        total = len(self.agents)
        print(f"[Pipeline] 开始巡检任务: {task.task_id} -> {task.target}", flush=True)

        for index, agent in enumerate(self.agents, start=1):
            print(f"\n[{index}/{total}] 开始执行 {agent.name}", flush=True)

            try:
                output = agent.run(result)
            except Exception as exc:
                print(f"[{index}/{total}] {agent.name} 执行失败: {exc}", flush=True)
                raise

            result.outputs.append(output)
            print(f"[{index}/{total}] {agent.name} 执行完成", flush=True)
            print(json.dumps(output.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)

            if isinstance(agent, SceneAnalysisAgent) and _should_skip_after_scene(output):
                print(
                    "\n[Pipeline] 场景分析结果为其它或无可处理对象，跳过后续 Agent。",
                    flush=True,
                )
                break

        print("\n[Pipeline] 巡检任务执行完成", flush=True)
        return result


def _should_skip_after_scene(output: AgentOutput) -> bool:
    return not any(obj in ACTIONABLE_OBJECTS for obj in output.objects)
