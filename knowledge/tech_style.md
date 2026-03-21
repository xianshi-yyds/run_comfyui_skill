# Tech Blogger Generation Rules 科技博主文案规则

## 1. 结构化规范
每一条短视频脚本都必须按照分镜头结构输出为严格的 JSON 格式。包含以下四个关键字段：
- `id`: 镜头编号（从 1 开始累加）
- `visual`: 画面描述，供后续视听团队打底。
- `tts_text`: 口播文案，字数必须精简。
- `workflow_type`: 标记这一步后续使用的关键步骤，如 "avatar_speaking"（仅出数字人） 或 "screen_record"（需要配操作视频）。

## 2. 口播语气指南
- 开门见山，绝对不要在开头说废话（禁止“大家好”、“欢迎来到”）。第一句必须是“今天发现了一个绝了的工具...”。
- 语速要快，情绪需要带有一种强烈的分享欲。
- 如果介绍 AI 工具，必须要举一个能结合生活/打工场景的具体例子。

## 3. 标准 JSON 输出结构例子
```json
{
  "project_name": "tech_tool_update",
  "scenes": [
    {
      "id": 1,
      "visual": "固定人物出镜，背景是霓虹科技风。",
      "tts_text": "今天发现了一个绝了的工具，能让你十分钟搞定一整天的活儿！",
      "workflow_type": "avatar_speaking"
    },
    {
      "id": 2,
      "visual": "展示该软件的操作主界面录屏。",
      "tts_text": "不管是排版还是写代码，你只管提需求，它直接生成出代码跑起来，这可是真真切切在拯救打工人啊！",
      "workflow_type": "screen_record"
    }
  ]
}
```
