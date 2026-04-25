from __future__ import annotations

from inspection_system.agents.base import BaseAgent
from inspection_system.schemas import DEFECTS_BY_OBJECT, AgentOutput, InspectionResult


class DefectDetectionAgent(BaseAgent):
    name = "DefectDetectionAgent"
    use_images = True
    role = "你只负责根据场景分析结果和图像输出 defect_categories。"

    def postprocess_output(self, output: AgentOutput, result: InspectionResult) -> AgentOutput:
        output.objects = _previous_objects(result)
        allowed_defects = _allowed_defects_for_scene(result)
        output.defect_categories = [
            defect for defect in output.defect_categories if defect in allowed_defects
        ]
        return output

    def system_prompt(self, result: InspectionResult | None = None) -> str:
        allowed_objects = _previous_objects(result) if result is not None else []
        defect_rules = []
        for obj in allowed_objects:
            defects = DEFECTS_BY_OBJECT.get(obj, [])
            if defects:
                defect_rules.append(f"如果 objects 包含{obj}，只能输出：{'、'.join(defects)}。")

        if defect_rules:
            object_rule = "".join(defect_rules)
        else:
            object_rule = "场景分析结果没有可检测对象，defect_categories 必须输出空数组。"

        role = (
            "你只负责根据场景分析结果和图像输出 defect_categories。"
            "输入的 previous_output 是场景分析 Agent 的输出。"
            "必须将 previous_output.objects 原样保留到 objects 字段。"
            f"{object_rule}"
            "不要输出不属于已识别 objects 的缺陷类别。"
            "如果图像正常、没有明确可见缺陷，defect_categories 必须输出空数组，不要编造缺陷。"
            "宁可输出空数组，也不要为了匹配类别而强行输出缺陷。"
        )
        return (
            f"你是 {self.name}。{role}"
            "你必须只输出符合 AgentOutput schema 的结构化结果。"
            "输入只包含任务信息和上一个 Agent 的 previous_output。"
            "后续 Agent 应保留 previous_output 中仍然有效的 objects 和 defect_categories，"
            "并只更新自己负责判断的字段。"
            "当前 Agent 不负责且没有上下文依据的字段必须留空数组或空字符串。"
            "如果没有明确结果，允许输出空数组或空字符串，不要编造。"
            "不要输出 Markdown，不要输出多余字段。"
        )


def _previous_objects(result: InspectionResult) -> list[str]:
    if result.outputs:
        return [obj for obj in result.outputs[-1].objects if obj in DEFECTS_BY_OBJECT]
    return []


def _allowed_defects_for_scene(result: InspectionResult) -> set[str]:
    allowed_defects: set[str] = set()
    for obj in _previous_objects(result):
        allowed_defects.update(DEFECTS_BY_OBJECT[obj])
    return allowed_defects
