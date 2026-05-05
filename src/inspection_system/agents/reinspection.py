from __future__ import annotations

from inspection_system.agents.base import BaseAgent
from inspection_system.schemas import AgentOutput, InspectionResult


class ReinspectionAgent(BaseAgent):
    name = "ReinspectionAgent"
    use_images = True
    role = (
        "你只负责复核缺陷检测结果，输出最终确认后的 defect_categories。"
        "输入的 previous_output 是缺陷检测 Agent 的输出。"
        "必须将 previous_output.objects 原样保留到 objects 字段。"
        "缺陷类别必须来自 previous_output.defect_categories，不能新增其它类别；"
        "如果证据不足或判断为误报，就从 defect_categories 中移除该类别。"
        "如果图像正常、缺陷检测结果为空、或所有候选缺陷都无法确认，defect_categories 必须输出空数组。"
        "不要为了给出结论而强行保留缺陷。"
    )

    def postprocess_output(self, output: AgentOutput, result: InspectionResult) -> AgentOutput:
        if not result.outputs:
            output.objects = []
            output.defect_categories = []
            return output

        previous_output = result.outputs[-1]
        previous_defects = set(previous_output.defect_categories)
        output.objects = previous_output.objects
        output.defect_categories = [
            defect for defect in output.defect_categories if defect in previous_defects
        ]
        return output
