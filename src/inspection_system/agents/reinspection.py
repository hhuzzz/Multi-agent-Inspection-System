from __future__ import annotations

from inspection_system.agents.base import BaseAgent


class ReinspectionAgent(BaseAgent):
    name = "ReinspectionAgent"
    use_images = True
    role = (
        "你只负责复核缺陷检测结果，输出最终确认后的 defect_categories。"
        "缺陷类别必须来自缺陷检测 Agent 已输出的类别，不能新增其它类别；"
        "如果证据不足或判断为误报，就从 defect_categories 中移除该类别。"
        "如果图像正常、缺陷检测结果为空、或所有候选缺陷都无法确认，defect_categories 必须输出空数组。"
        "不要为了给出结论而强行保留缺陷。"
    )
