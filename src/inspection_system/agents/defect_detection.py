from __future__ import annotations

from inspection_system.agents.base import BaseAgent


class DefectDetectionAgent(BaseAgent):
    name = "DefectDetectionAgent"
    use_images = True
    role = (
        "你只负责根据场景分析结果和图像输出 defect_categories。"
        "如果 objects 包含墙壁，只能输出：墙壁裂缝、墙壁渗水、墙壁剥落、墙壁鼓包变形。"
        "如果 objects 包含电缆，只能输出：电缆绝缘破损、电缆松脱下垂、电缆老化开裂、电缆烧蚀过热。"
        "如果 objects 包含变电箱，只能输出：变电箱箱体锈蚀、变电箱箱门异常、变电箱进水受潮、变电箱接线裸露。"
        "不要输出不属于已识别 objects 的缺陷类别。"
        "如果图像正常、没有明确可见缺陷，defect_categories 必须输出空数组，不要编造缺陷。"
        "宁可输出空数组，也不要为了匹配类别而强行输出缺陷。"
    )
