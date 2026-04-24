from __future__ import annotations

from inspection_system.agents.base import BaseAgent


class SceneAnalysisAgent(BaseAgent):
    name = "SceneAnalysisAgent"
    use_images = True
    role = (
        "你只负责识别需要检测的 objects。objects 只能从「墙壁、电缆、变电箱、其它」中选择，"
        "可以多选；如果画面主体不属于墙壁、电缆、变电箱，则只输出「其它」。不要判断缺陷。"
    )
