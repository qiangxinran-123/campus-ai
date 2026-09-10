# CampusAI API 总览

本地开发 Base URL：`http://127.0.0.1:8000`

交互式 Swagger 文档：`GET /docs`

以下接口说明以当前 V0.1 代码和测试为准。API 路径、请求方法、参数名和 JSON 字段保持英文原样，中文只用于解释用途和行为。

## 系统与课程接口

| 方法 | 路径 | 功能说明 | 关键参数 | 成功行为 | 失败行为 |
| --- | --- | --- | --- | --- | --- |
| GET | `/` | 返回 API 欢迎信息。 | 无 | `200`，返回项目名称和版本。 | 无特殊失败分支。 |
| GET | `/hello` | 最小后端问候接口。 | 无 | `200`，返回问候信息。 | 无特殊失败分支。 |
| GET | `/health` | 检查服务是否正常运行。 | 无 | `200`，返回 `status: ok`。 | 无特殊失败分支。 |
| GET | `/api/project/status` | 返回项目基础状态信息。 | 无 | `200`，返回项目状态元数据。 | 当前为基础状态接口。 |
| GET | `/api/courses` | 获取全部课程。 | 无 | `200`，返回 `count` 和 `courses`。 | 无特殊失败分支。 |
| GET | `/api/courses/{course_id}` | 获取指定课程详情。 | `course_id` 路径参数 | `200`，返回课程对象。 | 课程不存在返回 `404`。 |
| GET | `/api/courses/{course_id}/materials` | 获取指定课程的全部资料。 | `course_id` 路径参数 | `200`，返回 `course_id`、`count` 和 `materials`。 | 课程不存在返回 `404`。 |
| POST | `/api/courses/{course_id}/materials` | 创建一条 JSON 资料记录。 | `course_id`；JSON 字段 `title`、`type`、`summary` | `201`，返回新资料。 | 课程不存在返回 `404`；请求体不合法时由 FastAPI 返回校验错误。 |

## 文件上传与文本提取

| 方法 | 路径 | 功能说明 | 关键参数 | 成功行为 | 失败行为 |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/courses/{course_id}/materials/upload` | 上传并登记一份课程资料文件。 | `course_id`；multipart 表单字段 `file` | `201`，文件保存到课程目录，并返回资料记录。 | 无文件名或文件类型不支持返回 `400`；课程不存在返回 `404`。 |

支持的文件扩展名：`.pdf`、`.ppt`、`.pptx`、`.doc`、`.docx`、`.txt`、`.md`。

`.txt` 和 `.md` 上传后会保存：

- `text_preview`：正文前 300 个字符
- `text_length`：正文字符数
- `extracted`：是否成功提取

其他允许上传的格式当前只保存文件，返回 `extracted: false`、空的 `text_preview` 和 `0` 的 `text_length`。

## mock AI 与复习接口

| 方法 | 路径 | 功能说明 | 关键参数 | 成功行为 | 失败行为 |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/materials/{material_id}/summary` | 根据资料已有文本生成并保存 mock 摘要。 | `material_id` 路径参数 | `200`，返回包含 `ai_summary`、`summary_method`、`summary_updated_at` 的资料。 | 资料不存在返回 `404`；没有可用文本返回 `400`。 |
| POST | `/api/materials/{material_id}/cards` | 根据资料文本生成并保存 3 张 mock 学习卡片。 | `material_id` 路径参数 | `200`，返回 `material_id`、`count`、`cards` 和 `cards_generated_at`。 | 资料不存在返回 `404`；没有可用文本返回 `400`。 |

学习卡片字段示例：

```json
{
  "id": 10201,
  "question": "What is the core topic of this material?",
  "answer": "Mock summary: ...",
  "source_material_id": 102,
  "card_type": "concept",
  "created_at": "2026-01-01T00:00:00+00:00"
}
```

当前摘要和卡片均为本地 mock 实现，不调用外部模型服务。

## 资料搜索

| 方法 | 路径 | 功能说明 | 关键参数 | 成功行为 | 失败行为 |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/materials/search` | 在不修改 JSON 的前提下搜索资料。 | 必填 `q`；可选 `course_id` | `200`，返回 `query`、`count` 和匹配资料；每条结果包含 `course_id`。 | `q` 缺失或为空返回 `400`；课程不存在返回 `404`。 |

搜索不区分大小写，范围包括：`title`、`summary`、`filename`、`text_preview`、`ai_summary`。

示例：

```text
GET /api/materials/search?q=cache&course_id=1
```

没有匹配结果时仍返回 `200`，但 `count` 为 `0`、`materials` 为空数组。

## 持久化配置

- 默认课程和资料数据：`backend/app/data/courses.json`
- 默认上传目录：`backend/app/uploads/`
- `CAMPUSAI_COURSE_DATA_FILE`：为测试或隔离运行指定临时 JSON 文件
- `CAMPUSAI_UPLOAD_DIR`：为测试或隔离运行指定临时上传目录
