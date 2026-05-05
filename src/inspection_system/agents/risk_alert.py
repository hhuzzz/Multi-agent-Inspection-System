from __future__ import annotations

from inspection_system.agents.base import BaseAgent
from inspection_system.schemas import AgentOutput, InspectionResult


class RiskAlertAgent(BaseAgent):
    name = "RiskAlertAgent"
    role = (
        "你只负责根据 previous_output 输出 summary 报告，"
        "概括检测对象、复检后的缺陷类别和风险建议。"
        "输入的 previous_output 是复检 Agent 的输出。"
        "必须将 previous_output.objects 原样保留到 objects 字段，"
        "并将 previous_output.defect_categories 原样保留到 defect_categories 字段。"
    )

    def postprocess_output(self, output: AgentOutput, result: InspectionResult) -> AgentOutput:
        if not result.outputs:
            return output

        previous_output = result.outputs[-1]
        output.objects = previous_output.objects
        output.defect_categories = previous_output.defect_categories
        return output
