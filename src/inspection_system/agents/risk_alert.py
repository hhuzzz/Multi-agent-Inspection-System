from __future__ import annotations

from inspection_system.agents.base import BaseAgent


class RiskAlertAgent(BaseAgent):
    name = "RiskAlertAgent"
    role = "你只负责根据前序结果输出 summary 报告，概括检测对象、复检后的缺陷类别和风险建议。"
