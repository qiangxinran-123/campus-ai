# CampusAI 比赛演示脚本

建议演示时长：4-6 分钟。

本脚本可以直接作为比赛演示视频讲稿使用。演示时应明确说明：V0.1 的摘要和学习卡片是本地 mock AI，不是已经接入真实大模型的最终产品。

## 1. 项目简介

讲解词：

> CampusAI 是一个面向大学生的 AI 学习资料管理与复习辅助平台。V0.1 先完成一条可运行、可测试的后端闭环：上传课程资料、提取文本、生成 mock 摘要、搜索学习资料，并生成复习卡片。当前 AI 能力使用本地规则实现，后续可以替换为真实 LLM 和 RAG 服务。

展示项目根目录的 README，简要说明 FastAPI、Pydantic、本地 JSON 和 unittest 技术栈。

## 2. 启动后端并打开 `/docs`

在项目根目录启动服务：

```bash
uvicorn backend.main:app --reload
```

打开浏览器访问：

```text
http://127.0.0.1:8000/docs
```

讲解词：

> FastAPI 自动生成 Swagger 交互式文档，评审可以直接在页面中试用当前 API。课程接口和资料接口分别归类展示，便于理解后端结构。

## 3. 查看课程列表

1. 在 Swagger 中打开 `GET /api/courses`。
2. 点击 `Try it out`，再点击 `Execute`。
3. 展示返回的 `count` 和 `courses`。
4. 记录一个课程 ID，例如 `1`。
5. 打开 `GET /api/courses/{course_id}/materials`，输入课程 ID 查看已有资料。

讲解词：

> 课程和资料默认来自 `backend/app/data/courses.json`，资料写入后会持久化，服务重启不会丢失。

## 4. 上传 txt/md 资料

提前准备一个 `demo-notes.txt` 或 `demo-notes.md` 文件，写入两三句课程内容，例如缓存、机器学习或数据结构知识。

1. 打开 `POST /api/courses/{course_id}/materials/upload`。
2. 输入课程 ID `1`。
3. 选择 `demo-notes.txt` 或 `demo-notes.md`。
4. 点击 `Execute`，记录返回的 `id`。
5. 展示 `filename`、`file_path` 和资料类型。

讲解词：

> 当前支持常见课程资料上传。`.txt` 和 `.md` 会在上传后立即进入文本提取流程，其他格式暂时先保存文件。

## 5. 查看文本提取结果

在上传接口的响应中展示：

- `text_preview`
- `text_length`
- `extracted: true`

然后重新执行 `GET /api/courses/1/materials`，确认新增资料仍然带有这些字段。

讲解词：

> 文本提取结果会写入资料记录，后续摘要和学习卡片服务可以直接复用这些文本字段。

## 6. 生成 mock AI 摘要

1. 打开 `POST /api/materials/{material_id}/summary`。
2. 输入刚才记录的资料 ID。
3. 执行请求。
4. 展示 `ai_summary`、`summary_method: mock` 和 `summary_updated_at`。

讲解词：

> 这里是可替换的摘要服务边界。当前使用本地 mock 规则，不需要 API Key，也不产生网络和费用；后续可以将服务实现替换为真实 LLM。

## 7. 搜索资料

1. 打开 `GET /api/materials/search`。
2. 在 `q` 中输入上传文本里的关键词，或者输入 `mock summary`。
3. 可选填写 `course_id=1`。
4. 执行请求，展示匹配资料、`count` 和结果中的 `course_id`。

讲解词：

> 搜索是只读操作，覆盖标题、文件名、原始摘要、提取文本和 mock AI 摘要，方便资料数量增加后快速定位内容。

## 8. 生成学习卡片

1. 打开 `POST /api/materials/{material_id}/cards`。
2. 输入同一个资料 ID。
3. 执行请求，展示返回的 3 张 cards。
4. 说明每张卡片包含 `question`、`answer`、`source_material_id`、`card_type` 和 `created_at`。
5. 再执行一次，说明重复生成会覆盖旧 cards，不会无限追加重复卡片。
6. 再次执行 `GET /api/courses/1/materials`，展示资料中已经保存 `cards`、`cards_generated` 和 `cards_generated_at`。

讲解词：

> 卡片生成优先使用 `ai_summary`，其次使用 `text_preview`，最后使用资料原始 `summary`。它展示了从一份学习资料生成复习产物的完整流程。

## 9. 项目价值与后续升级

总结讲解词：

> CampusAI V0.1 的重点不是堆叠功能，而是完成一条可运行、可持久化、可测试和可演示的学习资料处理闭环。当前版本已经具备清晰的服务层边界，下一步可以接入真实 LLM、RAG、Embedding 和向量数据库，并增加学生端前端、用户认证和协作能力。

最后可以展示测试命令：

```bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai \
.venv/bin/python -m unittest backend.tests.test_courses_api
```

说明当前测试通过，覆盖课程、资料、上传、持久化、文本提取、mock 摘要、搜索和学习卡片接口。
