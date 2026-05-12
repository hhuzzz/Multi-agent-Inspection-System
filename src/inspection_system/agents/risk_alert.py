from __future__ import annotations

from inspection_system.agents.base import BaseAgent
from inspection_system.schemas import AgentOutput, InspectionResult


class RiskAlertAgent(BaseAgent):
    name = "RiskAlertAgent"
    role = (
        "你只根据复检 Agent 的 previous_output 输出 summary，"
        "概括检测对象、复检后的缺陷类别和风险建议。"
        "objects 和 defect_categories 必须原样保留 previous_output 的值。"
    )

    def postprocess_output(self, output: AgentOutput, result: InspectionResult) -> AgentOutput:
        if not result.outputs:
            return output

        previous_output = result.outputs[-1]
        output.objects = previous_output.objects
        output.defect_categories = previous_output.defect_categories
        return output
