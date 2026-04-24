# 多智能体协同隧道巡检系统

一个简洁的四 Agent 图像巡检流程，用大模型识别巡检对象、检测缺陷、复核结果，并生成风险摘要。

## 流程

```text
场景分析 Agent
    ↓
缺陷检测 Agent
    ↓
复检 Agent
    ↓
风险报警 Agent
```

- 场景分析 Agent：识别图像中的巡检对象。
- 缺陷检测 Agent：根据对象类型输出候选缺陷。
- 复检 Agent：确认或删除候选缺陷，不新增缺陷。
- 风险报警 Agent：根据前序结果输出简短报告。

如果场景分析结果只有 `其它`，系统会直接跳过后续 Agent。

## 支持范围

对象类别固定为：

```text
墙壁、电缆、变电箱、其它
```

缺陷类别固定为：

```text
墙壁：墙壁裂缝、墙壁渗水、墙壁剥落、墙壁鼓包变形
电缆：电缆绝缘破损、电缆松脱下垂、电缆老化开裂、电缆烧蚀过热
变电箱：变电箱箱体锈蚀、变电箱箱门异常、变电箱进水受潮、变电箱接线裸露
```

正常图像可以输出空缺陷数组，系统不会强制生成缺陷。

## 输出格式

每个 Agent 都输出同一个结构：

```json
{
  "agent_name": "SceneAnalysisAgent",
  "objects": ["墙壁"],
  "defect_categories": [],
  "summary": ""
}
```

字段说明：

- `agent_name`：当前 Agent 名称。
- `objects`：场景分析 Agent 输出的对象类别。
- `defect_categories`：缺陷检测和复检 Agent 输出的缺陷类别。
- `summary`：风险报警 Agent 输出的报告。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

编辑 `.env`：

```bash
OPENAI_API_KEY=your_api_key_here
MODEL_ID=gpt-4o-mini
OPENAI_TIMEOUT=60
# BASE_URL=https://api.example.com/v1
```

`MODEL_ID` 需要使用支持图像输入的模型。`BASE_URL` 用于 OpenAI-compatible 服务，可不填。

## 运行示例

示例入口：

```bash
python examples/run_inspection.py
```

示例图片配置在 [examples/run_inspection.py](examples/run_inspection.py)：

```python
inputs={
    "images": ["data/1.jpg"],
    "notes": "巡检补充说明"
}
```

`images` 支持本地图片路径、HTTP 图片 URL 或 data URL。

## 当前结构

```text
src/inspection_system/
├── agents/
│   ├── scene_analysis.py
│   ├── defect_detection.py
│   ├── reinspection.py
│   └── risk_alert.py
├── openai_client.py
├── pipeline.py
└── schemas.py
```
