# CampusAI

CampusAI 是一个面向大学生的 AI 学习资料管理与复习辅助平台。项目围绕“课程资料上传、文本提取、摘要生成、资料搜索和复习卡片生成”构建了一条完整、可测试的后端流程。

CampusAI is a FastAPI-based AI study assistant for university students, focused on organizing learning materials and turning them into searchable summaries and review cards.

> 重要说明：当前 V0.1 使用本地规则实现的 mock AI 摘要和 mock 学习卡片生成，不调用真实外部大模型 API，也不依赖 API Key。

## 项目状态

- 当前版本：`V0.1`
- 当前进度：V0.1 发布范围已完成
- 项目定位：面向大学生的 AI 学习资料管理与复习辅助平台
- 后端框架：FastAPI
- 数据存储：本地 JSON 文件
- 测试方式：基于真实 HTTP 请求的 `unittest` 集成测试

推荐 GitHub 仓库描述：

```text
CampusAI：面向大学生的 AI 学习资料管理与复习辅助平台 | FastAPI-based AI study assistant for students
```

## 技术栈

- Python 3
- FastAPI、Uvicorn
- Pydantic
- `python-multipart` 文件上传
- 本地 JSON 持久化
- Python 标准库 `unittest`

## 核心功能

- 课程列表和课程详情查询
- 课程资料列表和 JSON 资料创建
- 上传 `.pdf`、`.ppt`、`.pptx`、`.doc`、`.docx`、`.txt`、`.md` 文件
- 按课程保存上传文件到 `backend/app/uploads/course_{course_id}/`
- 自动提取 `.txt`、`.md` 文本，保存 `text_preview`、`text_length`、`extracted`
- 生成并持久化 mock AI 摘要
- 按标题、文件名、资料摘要、提取文本和 AI 摘要搜索资料
- 生成并持久化学习复习卡片
- 新增资料和处理结果写回 JSON，服务重启后仍然保留

## API 概览

| 功能 | API | 说明 |
| --- | --- | --- |
| 健康检查 | `GET /health` | 检查后端是否正常运行 |
| 课程列表 | `GET /api/courses` | 获取全部课程 |
| 课程资料 | `GET /api/courses/{course_id}/materials` | 获取指定课程的资料 |
| 文件上传 | `POST /api/courses/{course_id}/materials/upload` | 上传并登记课程资料 |
| mock 摘要 | `POST /api/materials/{material_id}/summary` | 生成并保存本地 mock 摘要 |
| 资料搜索 | `GET /api/materials/search?q={keyword}&course_id={optional}` | 搜索资料，不修改 JSON |
| 学习卡片 | `POST /api/materials/{material_id}/cards` | 生成并保存 mock 复习卡片 |

完整接口说明见 [API 总览](docs/API_OVERVIEW.md)。

## 项目结构

```text
campus-ai/
├── backend/
│   ├── main.py                     # FastAPI 应用入口
│   ├── app/
│   │   ├── api/                    # 课程、资料和处理接口
│   │   ├── schemas/                # Pydantic 请求与响应模型
│   │   ├── services/               # 持久化、提取、摘要和卡片服务
│   │   ├── data/courses.json       # 默认示例课程与资料数据
│   │   └── uploads/                # 运行时上传目录，不提交真实用户文件
│   └── tests/test_courses_api.py   # HTTP 集成测试
├── docs/
│   ├── API_OVERVIEW.md             # API 中文总览
│   ├── DEMO_SCRIPT.md              # 比赛演示讲稿
│   ├── DEVELOPMENT_LOG.md          # 分阶段开发日志
│   └── V0.1_ACCEPTANCE.md          # V0.1 最终验收清单
└── requirements.txt
```

## 本地运行

在项目根目录执行：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

启动后打开 FastAPI 交互式文档：

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

默认数据文件为 `backend/app/data/courses.json`。测试或本地隔离运行时，可以通过环境变量切换数据文件和上传目录：

```bash
CAMPUSAI_COURSE_DATA_FILE=/path/to/courses.json
CAMPUSAI_UPLOAD_DIR=/path/to/uploads
```

## 运行测试

```bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai \
.venv/bin/python -m unittest backend.tests.test_courses_api
```

测试覆盖课程与资料接口、JSON 持久化、文件上传、文本提取、mock 摘要、资料搜索和学习卡片生成。

## 当前 mock AI 能力

当前阶段不接入真实外部大模型，所有 AI 相关能力都使用本地规则服务完成：

- mock 摘要根据已提取文本生成简短摘要，并保存 `ai_summary`、`summary_method`、`summary_updated_at`。
- mock 卡片优先使用 `ai_summary`，其次使用 `text_preview`，最后使用资料原始 `summary`。
- 重复生成摘要或卡片时更新原资料，不创建重复资料。
- 摘要和卡片服务位于 `backend/app/services/`，后续可以在不改变 API 的情况下替换为真实 LLM 服务。

## 比赛展示亮点

- 从课程资料上传到复习卡片生成，形成完整后端闭环
- 数据写回 JSON，服务重启后仍然可读
- 服务层职责清晰，便于后续接入真实 AI 能力
- 使用真实 HTTP 集成测试验证，而不是只验证孤立函数
- 不依赖 API Key 和外部网络，现场演示稳定、可复现
- 文档、开发日志和 Demo 脚本完整，适合比赛评审和简历展示

## 后续规划

- 接入真实 LLM，替换当前 mock 摘要和卡片服务
- 增加 Embedding、RAG 检索和向量数据库
- 支持 PDF、PowerPoint、Word 的正文提取
- 增加学生端前端页面和课程复习视图
- 增加用户认证、资料归属和协作能力
- 将 JSON 存储升级为数据库，并支持异步处理

## 项目文档

- [分阶段开发日志](docs/DEVELOPMENT_LOG.md)
- [API 总览](docs/API_OVERVIEW.md)
- [比赛 Demo 脚本](docs/DEMO_SCRIPT.md)
- [V0.1 最终验收清单](docs/V0.1_ACCEPTANCE.md)
