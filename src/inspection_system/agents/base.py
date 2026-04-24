from __future__ import annotations

import json

from inspection_system.openai_client import OpenAIClient
from inspection_system.schemas import AgentOutput, InspectionResult


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

        return self.client.parse(
            system_prompt=self.system_prompt(),
            user_prompt=json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            output_model=AgentOutput,
            image_paths=image_paths,
        )

    def system_prompt(self) -> str:
        return (
            f"你是 {self.name}。{self.role}"
            "你必须只输出符合 AgentOutput schema 的结构化结果。"
            "当前 Agent 不负责的字段必须留空数组或空字符串。"
            "如果没有明确结果，允许输出空数组或空字符串，不要编造。"
            "不要输出 Markdown，不要输出多余字段。"
        )
