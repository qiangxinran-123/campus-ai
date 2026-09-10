# CampusAI 演示数据说明

本项目默认使用 backend/app/data/courses.json 作为本地演示数据。数据规模小、内容可公开展示，适合比赛现场直接打开首页演示，不包含个人隐私和大文件。

## 示例课程

| 课程 | 资料 | 适合展示的能力 |
| --- | --- | --- |
| Computer Organization / 计算机组成原理 | Cache Memory Notes、CPU Pipeline and Hazards | 文本预览、cache 搜索、摘要和卡片 |
| Machine Learning / 机器学习 | Gradient Descent Notes、Classification Review | gradient 搜索、mock AI 摘要、复习卡片 |
| Data Structures / 数据结构 | Linked List Review、Trees and Graphs Basics | linked list 搜索、课程切换和详情展示 |

每门课程默认包含两条资料，每条资料都预置了：

- text_preview、text_length、extracted
- ai_summary、summary_generated、summary_method
- 三张 cards、cards_generated、cards_generated_at

因此首次打开前端时就可以直接展示资料详情、摘要和学习卡片。点击生成按钮仍然可以验证接口会更新原资料，而不是新增重复记录。

## 推荐搜索关键词

建议在页面中选择对应课程后搜索：

- cache：计算机组成原理中的 Cache Memory Notes
- pipeline：计算机组成原理中的 CPU Pipeline and Hazards
- gradient：机器学习中的 Gradient Descent Notes
- classification：机器学习中的 Classification Review
- linked list：数据结构中的 Linked List Review
- breadth-first：数据结构中的 Trees and Graphs Basics

搜索框当前按课程过滤。切换课程后再使用对应关键词，可以清楚展示课程范围过滤效果。

## 推荐演示顺序

1. 打开首页，展示三门课程和当前课程的两条资料。
2. 选择 Machine Learning / 机器学习，点击 Gradient Descent Notes。
3. 在右侧详情中展示 extracted、text_length、text_preview、ai_summary 和 cards。
4. 搜索 gradient，展示搜索结果数量，再点击结果回到资料详情。
5. 点击“生成摘要”和“生成学习卡片”，展示处理中状态和完成提示。
6. 清空搜索，切换到 Data Structures / 数据结构，搜索 linked list。
7. 如需展示上传流程，再选择本地准备的 .txt 或 .md 文件上传；上传资料会写回 JSON，建议演示后使用临时数据文件隔离运行。

## 数据重置

如果现场演示过程中修改了默认 JSON，可以从 Git 恢复示例数据：

~~~bash
git restore backend/app/data/courses.json
~~~

更稳妥的方式是使用临时数据文件启动服务，避免修改仓库中的默认演示数据：

~~~bash
cp backend/app/data/courses.json /tmp/campusai-demo-courses.json
CAMPUSAI_COURSE_DATA_FILE=/tmp/campusai-demo-courses.json bash scripts/start_dev.sh
~~~

演示前建议先确认：

- 页面能看到 3 门课程。
- 当前课程至少有 2 条资料。
- 搜索 cache、gradient、linked list 至少各有一个结果。
- 资料详情中已经显示摘要和学习卡片。
