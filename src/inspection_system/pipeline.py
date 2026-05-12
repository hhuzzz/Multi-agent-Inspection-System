from __future__ import annotations

import json
import time

from inspection_system.agents import (
    DefectDetectionAgent,
    ReinspectionAgent,
    RiskAlertAgent,
    SceneAnalysisAgent,
)
from inspection_system.openai_client import OpenAIClient
from inspection_system.schemas import ACTIONABLE_OBJECTS, AgentOutput, InspectionResult, InspectionTask


class InspectionPipeline:
    """Four-agent workflow with reinspection loopback support."""

    def __init__(
        self, client: OpenAIClient | None = None, max_reinspect_retries: int = 2
    ) -> None:
        self.client = client or OpenAIClient()
        self.max_retries = max_reinspect_retries
        self._scene_agent = SceneAnalysisAgent(self.client)
        self._defect_agent = DefectDetectionAgent(self.client)
        self._reinspect_agent = ReinspectionAgent(self.client)
        self._risk_agent = RiskAlertAgent(self.client)

    def run(self, task: InspectionTask) -> InspectionResult:
        result = InspectionResult(task=task, outputs=[])

        pipeline_start = time.perf_counter()
        print(f"[Pipeline] 开始巡检任务: {task.task_id} -> {task.target}", flush=True)

        # ── 1. SceneAnalysis ──
        output = self._run_agent(self._scene_agent, result)
        result.outputs.append(output)
        if _should_skip_after_scene(output):
            print(
                "\n[Pipeline] 场景分析结果为其它或无可处理对象，跳过后续 Agent。",
                flush=True,
            )
            return result

        # ── 2. DefectDetection（首轮） ──
        output = self._run_agent(self._defect_agent, result)
        result.outputs.append(output)

        # ── 3. Reinspection + 循环回退 ──
        retry_count = 0
        while retry_count <= self.max_retries:
            output = self._run_agent(self._reinspect_agent, result)
            result.outputs.append(output)

            if not output.uncertain_defects:
                print(f"[Pipeline] 复检确认完成，无不确定项。", flush=True)
                break

            if retry_count >= self.max_retries:
                print(
                    f"[Pipeline] 已达最大重试次数 ({self.max_retries})，"
                    f"不确定缺陷 {output.uncertain_defects} 将被忽略。",
                    flush=True,
                )
                break

            retry_count += 1
            print(
                f"\n[Pipeline] 复检发现不确定项: {output.uncertain_defects}，"
                f"第 {retry_count} 次回退到缺陷检测...",
                flush=True,
            )

            # 弹出刚添加的 Reinspection 输出
            result.outputs.pop()
            # 弹出原来的 DefectDetection 输出
            result.outputs.pop()

            # 设置重新检测上下文
            self._defect_agent.re_examine_context = {
                "uncertain_defects": output.uncertain_defects
            }

            # 重新执行 DefectDetection
            output = self._run_agent(self._defect_agent, result)
            result.outputs.append(output)

        # ── 4. RiskAlert ──
        output = self._run_agent(self._risk_agent, result)
        result.outputs.append(output)

        total_elapsed = time.perf_counter() - pipeline_start
        print(f"\n[Pipeline] 巡检任务执行完成，总耗时 {total_elapsed:.2f}s", flush=True)
        return result

    def _run_agent(self, agent, result: InspectionResult) -> AgentOutput:
        index = self._agent_index(agent)
        agent_start = time.perf_counter()
        print(f"\n[{index}/4] 开始执行 {agent.name}", flush=True)
        try:
            output = agent.run(result)
        except Exception as exc:
            elapsed = time.perf_counter() - agent_start
            print(
                f"[{index}/4] {agent.name} 执行失败，耗时 {elapsed:.2f}s: {exc}",
                flush=True,
            )
            raise
        elapsed = time.perf_counter() - agent_start
        print(f"[{index}/4] {agent.name} 执行完成，耗时 {elapsed:.2f}s", flush=True)
        print(
            json.dumps(output.model_dump(mode="json"), ensure_ascii=False, indent=2),
            flush=True,
        )
        return output

    @staticmethod
    def _agent_index(agent) -> int:
        name = agent.name
        if "Scene" in name:
            return 1
        if "Defect" in name:
            return 2
        if "Reinspect" in name:
            return 3
        return 4


def _should_skip_after_scene(output: AgentOutput) -> bool:
    return not any(obj in ACTIONABLE_OBJECTS for obj in output.objects)
