# CampusAI 比赛演示脚本

建议演示时长：4-6 分钟。

本脚本以 CampusAI 原生前端页面为主要演示入口，/docs 作为 API 结构和调试补充。演示时应明确说明：当前摘要和学习卡片是本地 mock AI，不是已经接入真实大模型的最终产品。

## 1. 项目简介

讲解词：

> CampusAI 是一个面向大学生的 AI 学习资料管理与复习辅助平台。当前版本先完成一条可运行、可持久化、可测试的学习资料闭环：选择课程、上传资料、提取文本、生成 mock 摘要、搜索资料，并生成复习卡片。前端使用原生 HTML、CSS 和 JavaScript，便于现场演示和后续学习维护。

展示 README 中的技术栈和项目结构，重点说明 FastAPI、Pydantic、本地 JSON 和 unittest。

## 2. 启动后端并打开前端

在项目根目录启动服务：

~~~bash
uvicorn backend.main:app --reload
~~~

打开浏览器访问：

~~~text
http://127.0.0.1:8000
~~~

讲解词：

> FastAPI 同时提供后端 API 和静态前端页面。首页不需要额外的 Node.js、构建工具或外部 CDN，启动一个服务即可完成演示。

演示前可以准备一个 demo-notes.txt 或 demo-notes.md 文件，写入两三句课程内容，例如：

~~~text
缓存可以减少重复计算和数据访问的成本。
局部性原理包括时间局部性和空间局部性。
~~~

## 3. 查看课程列表并选择课程

1. 在页面左侧查看课程列表和课程数量。
2. 点击一门课程。
3. 确认页面标题、学期、课程简介和资料列表同步更新。
4. 说明中间是当前课程资料，右侧是选中资料详情。

讲解词：

> 课程数据来自本地 JSON 文件。选择课程后，页面调用 GET /api/courses/{course_id}/materials 加载对应资料。

## 4. 上传 txt/md 资料并查看文本提取

1. 确认页面显示“当前上传到：某门课程”。
2. 在上传区域选择准备好的 .txt 或 .md 文件。
3. 点击“上传并提取文本”。
4. 确认新资料出现在列表中，并被自动选中。
5. 在右侧资料详情中查看：
   - title
   - type
   - filename
   - extracted
   - text_length
   - text_preview
   - summary

讲解词：

> 上传成功后，文件保存在课程对应的本地目录，资料记录写回 courses.json。对于 .txt 和 .md，系统会立即提取正文，因此页面可以直接展示文本状态和预览内容。

## 5. 生成 mock AI 摘要

1. 保持刚才上传的资料处于选中状态。
2. 点击右侧资料详情中的“生成摘要”。
3. 观察按钮进入处理中状态，避免重复提交。
4. 生成完成后查看 ai_summary 和“已生成摘要”状态。

讲解词：

> 当前摘要由本地 mock summarizer 根据已提取文本生成，不调用外部模型，不需要 API Key。摘要结果会保存到 JSON，刷新页面或重启服务后仍然可以读取。

## 6. 搜索资料

1. 在“搜索资料”区域输入正文中的关键词，例如“缓存”。
2. 点击“搜索当前课程”。
3. 展示搜索结果数量和匹配资料。
4. 点击某条搜索结果，确认右侧详情定位到对应资料。
5. 点击“返回课程资料”，恢复当前课程的完整资料列表。
6. 可额外演示空关键词，页面会提示“请输入搜索关键词”，不会发送请求。

讲解词：

> 搜索接口覆盖标题、文件名、资料说明、正文预览和 AI 摘要。搜索只读，不会修改原始 JSON 数据。

## 7. 生成学习卡片

1. 在资料详情中点击“生成学习卡片”。
2. 观察按钮进入处理中状态。
3. 确认页面出现 3 张学习卡片，每张包含问题和答案。
4. 再次点击生成，说明系统会更新旧卡片，不会无限追加重复内容。

讲解词：

> mock card generator 优先使用 AI 摘要，其次使用正文预览，最后使用资料说明。它展示了从一份课程资料生成复习产物的完整流程。

## 8. 用 /docs 补充查看 API

打开：

~~~text
http://127.0.0.1:8000/docs
~~~

讲解词：

> 前端页面适合展示完整用户流程，FastAPI Swagger 文档则适合查看接口、参数和返回结构。两者使用同一套后端 API，核心业务行为保持一致。

可快速展示：

- GET /api/courses
- GET /api/courses/{course_id}/materials
- POST /api/courses/{course_id}/materials/upload
- POST /api/materials/{material_id}/summary
- GET /api/materials/search
- POST /api/materials/{material_id}/cards

## 9. 项目价值与后续升级

总结讲解词：

> CampusAI 当前的重点不是堆叠功能，而是把课程资料从上传、持久化、文本提取到复习产物生成串成一条可运行、可测试、可演示的闭环。下一步可以接入真实 LLM、Embedding、RAG 和向量数据库，并继续完善前端、用户认证和协作能力。

最后可展示测试命令：

~~~bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai .venv/bin/python -m unittest backend.tests.test_courses_api
~~~

说明当前测试覆盖课程、资料、上传、持久化、文本提取、mock 摘要、搜索和学习卡片接口。
