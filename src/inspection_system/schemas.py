from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


ObjectCategory = Literal["墙壁", "电缆", "变电箱", "其它"]
DefectCategory = Literal[
    "墙壁裂缝",
    "墙壁渗水",
    "墙壁剥落",
    "墙壁鼓包变形",
    "电缆绝缘破损",
    "电缆松脱下垂",
    "电缆老化开裂",
    "电缆烧蚀过热",
    "变电箱箱体锈蚀",
    "变电箱箱门异常",
    "变电箱进水受潮",
    "变电箱接线裸露",
]

ACTIONABLE_OBJECTS = {"墙壁", "电缆", "变电箱"}
DEFECTS_BY_OBJECT: dict[str, list[DefectCategory]] = {
    "墙壁": ["墙壁裂缝", "墙壁渗水", "墙壁剥落", "墙壁鼓包变形"],
    "电缆": ["电缆绝缘破损", "电缆松脱下垂", "电缆老化开裂", "电缆烧蚀过热"],
    "变电箱": ["变电箱箱体锈蚀", "变电箱箱门异常", "变电箱进水受潮", "变电箱接线裸露"],
}


class AgentOutput(StrictModel):
    agent_name: str
    objects: list[ObjectCategory] = Field(default_factory=list)
    defect_categories: list[DefectCategory] = Field(default_factory=list)
    summary: str = ""


class InspectionTask(StrictModel):
    task_id: str
    target: str
    description: str
    inputs: dict[str, Any]


class AgentInput(StrictModel):
    task: InspectionTask
    previous_output: Optional[AgentOutput] = None


class InspectionResult(StrictModel):
    task: InspectionTask
    outputs: list[AgentOutput] = Field(default_factory=list)
