from __future__ import annotations

import json

from inspection_system.openai_client import OpenAIClient
from inspection_system.schemas import AgentInput, AgentOutput, InspectionResult


class BaseAgent:
    name: str
    role: str
    use_images: bool = False

    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    def run(self, result: InspectionResult) -> AgentOutput:
        image_paths = result.task.inputs.get("images", []) if self.use_images else []
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        if image_paths:
            print(f"{self.name} 输入图片数量: {len(image_paths)}", flush=True)

        output = self.client.parse(
            system_prompt=self.system_prompt(result),
            user_prompt=self.build_user_prompt(result),
            output_model=AgentOutput,
            image_paths=image_paths,
        )
        return self.postprocess_output(output, result)

    def build_user_prompt(self, result: InspectionResult) -> str:
        agent_input = AgentInput(
            task=result.task,
            previous_output=result.outputs[-1] if result.outputs else None,
        )
        return json.dumps(agent_input.model_dump(mode="json"), ensure_ascii=False, indent=2)

    def system_prompt(self, result: InspectionResult | None = None) -> str:
        return (
            f"你是 {self.name}。{self.role}"
            "你必须只输出符合 AgentOutput schema 的结构化结果。"
            "输入只包含任务信息和上一个 Agent 的 previous_output。"
            "后续 Agent 应保留 previous_output 中仍然有效的 objects 和 defect_categories，"
            "并只更新自己负责判断的字段。"
            "当前 Agent 不负责且没有上下文依据的字段必须留空数组或空字符串。"
            "如果没有明确结果，允许输出空数组或空字符串，不要编造。"
            "不要输出 Markdown，不要输出多余字段。"
        )

    def postprocess_output(self, output: AgentOutput, result: InspectionResult) -> AgentOutput:
        return output
