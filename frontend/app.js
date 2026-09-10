
const state = {
  courses: [],
  currentCourseId: null,
  materials: [],
  selectedMaterialId: null,
  searchTerm: "",
  searching: false,
  actionBusy: false,
};

const elements = {
  courseCount: document.querySelector("#course-count"),
  courseList: document.querySelector("#course-list"),
  courseTitle: document.querySelector("#course-title"),
  courseDescription: document.querySelector("#course-description"),
  uploadTarget: document.querySelector("#upload-target"),
  uploadForm: document.querySelector("#upload-form"),
  uploadSubmit: document.querySelector("#upload-submit"),
  fileInput: document.querySelector("#file-input"),
  fileLabel: document.querySelector("#file-label"),
  searchForm: document.querySelector("#search-form"),
  searchInput: document.querySelector("#search-input"),
  searchResultCount: document.querySelector("#search-result-count"),
  clearSearch: document.querySelector("#clear-search"),
  materialsList: document.querySelector("#materials-list"),
  materialDetail: document.querySelector("#material-detail"),
  detailContent: document.querySelector("#detail-content"),
  detailActions: document.querySelector("#detail-actions"),
  detailSummaryButton: document.querySelector("#detail-summary"),
  detailCardsButton: document.querySelector("#detail-cards"),
  statusPill: document.querySelector("#status-pill"),
  toast: document.querySelector("#toast"),
};

let toastTimer;

async function requestJSON(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `请求失败（${response.status}）`);
  }
  return payload;
}

function setStatus(message, tone = "neutral") {
  elements.statusPill.textContent = message;
  elements.statusPill.dataset.tone = tone;
}

function showToast(message, tone = "neutral") {
  window.clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.dataset.tone = tone;
  elements.toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => {
    elements.toast.classList.remove("is-visible");
  }, 3200);
}

function createElement(tag, className, text = "") {
  const element = document.createElement(tag);
  if (className) {
    element.className = className;
  }
  if (text !== "") {
    element.textContent = text;
  }
  return element;
}

function findMaterial(materialId) {
  return state.materials.find((item) => item.id === Number(materialId)) || null;
}

function renderCourses() {
  elements.courseCount.textContent = String(state.courses.length);
  elements.courseList.replaceChildren();

  if (!state.courses.length) {
    elements.courseList.append(createElement("p", "empty-state", "暂无课程数据"));
    return;
  }

  for (const course of state.courses) {
    const button = createElement("button", "course-button");
    button.type = "button";
    button.dataset.courseId = String(course.id);
    if (course.id === state.currentCourseId) {
      button.classList.add("is-active");
    }
    button.append(createElement("span", "course-name", course.name));
    button.append(createElement("span", "course-semester", course.semester));
    elements.courseList.append(button);
  }
}

function renderMaterials() {
  elements.materialsList.replaceChildren();
  elements.clearSearch.hidden = !state.searching;
  elements.searchResultCount.textContent = state.searching
    ? `搜索结果：${state.materials.length} 条`
    : `共 ${state.materials.length} 份`;

  if (!state.materials.length) {
    const message = state.searching ? "没有找到匹配资料" : "当前课程暂无资料";
    elements.materialsList.append(createElement("p", "empty-state", message));
    renderDetail();
    return;
  }

  for (const material of state.materials) {
    elements.materialsList.append(renderMaterial(material));
  }
  renderDetail();
}

function renderMaterial(material) {
  const article = createElement("article", "material-card");
  article.dataset.materialId = String(material.id);
  article.tabIndex = 0;
  if (material.id === state.selectedMaterialId) {
    article.classList.add("is-selected");
  }

  const header = createElement("div", "material-card-header");
  const titleBlock = createElement("div");
  titleBlock.append(createElement("h3", "material-title", material.title || "未命名资料"));

  const metaRow = createElement("div", "meta-row");
  metaRow.append(createElement("span", "meta-tag", material.type || "unknown"));
  if (material.filename) {
    metaRow.append(createElement("span", "meta-tag", material.filename));
  }
  if (material.extracted) {
    metaRow.append(createElement("span", "meta-tag is-positive", "已提取文本"));
  }
  if (material.summary_generated) {
    metaRow.append(createElement("span", "meta-tag is-positive", "已生成摘要"));
  }
  if (material.cards_generated) {
    metaRow.append(createElement("span", "meta-tag is-positive", "已生成卡片"));
  }
  titleBlock.append(metaRow);
  header.append(titleBlock);

  const actions = createElement("div", "card-actions");
  actions.append(createActionButton("summary", material.id, "摘要"));
  actions.append(createActionButton("cards", material.id, "卡片"));
  header.append(actions);
  article.append(header);

  const primaryText = material.ai_summary || material.text_preview || material.summary || "暂无可展示文本";
  article.append(createElement("p", "material-summary", primaryText));
  article.append(createElement("p", "select-hint", "点击查看资料详情"));

  return article;
}

function createActionButton(action, materialId, label) {
  const button = createElement("button", "small-button", label);
  button.type = "button";
  button.dataset.action = action;
  button.dataset.materialId = String(materialId);
  button.dataset.defaultLabel = label;
  return button;
}

function updateCourseHeading() {
  const course = state.courses.find((item) => item.id === state.currentCourseId);
  if (!course) {
    elements.courseTitle.textContent = "请选择一门课程";
    elements.courseDescription.textContent = "课程资料和复习工具会显示在这里。";
    elements.uploadTarget.textContent = "请先选择课程";
    elements.fileInput.disabled = true;
    elements.uploadSubmit.disabled = true;
    return;
  }
  elements.courseTitle.textContent = course.name;
  elements.courseDescription.textContent = `${course.semester} · ${course.description}`;
  elements.uploadTarget.textContent = `当前上传到：${course.name}`;
  elements.fileInput.disabled = false;
  elements.uploadSubmit.disabled = false;
}

function renderDetail() {
  const material = findMaterial(state.selectedMaterialId);
  if (!material) {
    elements.materialDetail.classList.add("is-empty");
    elements.detailContent.replaceChildren(
      createElement("p", "detail-empty-title", "请选择一份资料"),
      createElement("p", "muted", "资料的正文、摘要和学习卡片会显示在这里。"),
    );
    elements.detailActions.hidden = true;
    return;
  }

  elements.materialDetail.classList.remove("is-empty");
  elements.detailActions.hidden = false;
  elements.detailContent.replaceChildren();

  const title = createElement("h3", "detail-title", material.title || "未命名资料");
  const subtitle = createElement(
    "p",
    "detail-subtitle",
    material.filename ? `${material.type || "资料"} · ${material.filename}` : (material.type || "资料"),
  );
  elements.detailContent.append(title, subtitle);

  const infoGrid = createElement("dl", "detail-info-grid");
  appendInfo(infoGrid, "类型", material.type || "未提供");
  appendInfo(infoGrid, "文件名", material.filename || "未提供");
  appendInfo(infoGrid, "文本状态", material.extracted ? "已提取" : "未提取");
  appendInfo(infoGrid, "文本长度", String(material.text_length ?? 0));
  appendInfo(infoGrid, "摘要状态", material.summary_generated ? "已生成" : "未生成");
  elements.detailContent.append(infoGrid);

  appendDetailSection(elements.detailContent, "资料说明", material.summary || "暂无资料说明");
  appendDetailSection(elements.detailContent, "正文预览", material.text_preview || "暂无可提取文本");
  appendDetailSection(elements.detailContent, "AI 摘要", material.ai_summary || "尚未生成 mock AI 摘要");

  const cardsHeading = createElement("h4", "detail-section-title", "学习卡片");
  elements.detailContent.append(cardsHeading);
  if (Array.isArray(material.cards) && material.cards.length) {
    const cardList = createElement("ol", "detail-card-list");
    for (const card of material.cards) {
      const item = createElement("li", "detail-card-item");
      item.append(createElement("strong", "", card.question || "复习问题"));
      item.append(createElement("p", "", card.answer || "暂无答案"));
      cardList.append(item);
    }
    elements.detailContent.append(cardList);
  } else {
    elements.detailContent.append(createElement("p", "detail-muted", "尚未生成学习卡片"));
  }
  updateActionButtons();
}

function appendInfo(parent, label, value) {
  const term = createElement("dt", "", label);
  const description = createElement("dd", "", value);
  parent.append(term, description);
}

function appendDetailSection(parent, title, value) {
  parent.append(createElement("h4", "detail-section-title", title));
  parent.append(createElement("p", "detail-section-text", value));
}

function updateActionButtons() {
  const materialId = state.selectedMaterialId;
  const hasSelection = materialId !== null && Boolean(findMaterial(materialId));
  elements.detailSummaryButton.disabled = !hasSelection || state.actionBusy;
  elements.detailCardsButton.disabled = !hasSelection || state.actionBusy;
  for (const button of elements.materialsList.querySelectorAll("button[data-action]")) {
    button.disabled = state.actionBusy && Number(button.dataset.materialId) === materialId;
  }
  if (state.actionBusy) {
    elements.detailSummaryButton.textContent = "处理中...";
    elements.detailCardsButton.textContent = "处理中...";
  } else {
    elements.detailSummaryButton.textContent = "生成摘要";
    elements.detailCardsButton.textContent = "生成学习卡片";
  }
}

function selectMaterial(materialId) {
  const material = findMaterial(materialId);
  if (!material) {
    state.selectedMaterialId = null;
  } else {
    state.selectedMaterialId = material.id;
  }
  renderMaterials();
}

async function loadCourses() {
  const data = await requestJSON("/api/courses");
  state.courses = data.courses || [];
  renderCourses();
  if (state.courses.length) {
    await selectCourse(state.courses[0].id);
  } else {
    updateCourseHeading();
    renderMaterials();
  }
}

async function selectCourse(courseId) {
  state.currentCourseId = Number(courseId);
  state.selectedMaterialId = null;
  state.searching = false;
  state.searchTerm = "";
  elements.searchInput.value = "";
  updateCourseHeading();
  renderCourses();
  await loadMaterials();
}

async function loadMaterials() {
  if (state.currentCourseId === null) {
    state.materials = [];
    renderMaterials();
    return;
  }
  setStatus("正在加载资料...");
  const data = await requestJSON(`/api/courses/${state.currentCourseId}/materials`);
  state.materials = data.materials || [];
  if (!findMaterial(state.selectedMaterialId)) {
    state.selectedMaterialId = null;
  }
  renderMaterials();
  setStatus(`${data.count} 份资料`, "success");
}

async function searchMaterials() {
  const keyword = elements.searchInput.value.trim();
  if (!keyword) {
    showToast("请输入搜索关键词", "error");
    setStatus("等待搜索", "error");
    return;
  }
  if (state.currentCourseId === null) {
    showToast("请先选择课程", "error");
    setStatus("请先选择课程", "error");
    return;
  }

  setStatus("正在搜索...");
  const params = new URLSearchParams({
    q: keyword,
    course_id: String(state.currentCourseId),
  });
  const data = await requestJSON(`/api/materials/search?${params.toString()}`);
  state.materials = data.materials || [];
  state.searchTerm = keyword;
  state.searching = true;
  state.selectedMaterialId = null;
  renderMaterials();
  setStatus(`找到 ${data.count} 份资料`, "success");
}

async function uploadMaterial(event) {
  event.preventDefault();
  if (state.currentCourseId === null) {
    showToast("请先选择课程", "error");
    setStatus("请先选择课程", "error");
    return;
  }
  const file = elements.fileInput.files[0];
  if (!file) {
    showToast("请选择 TXT 或 Markdown 文件", "error");
    setStatus("请选择文件", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  setStatus("正在上传并提取文本...");
  elements.uploadSubmit.disabled = true;
  try {
    const data = await requestJSON(`/api/courses/${state.currentCourseId}/materials/upload`, {
      method: "POST",
      body: formData,
    });
    elements.uploadForm.reset();
    elements.fileLabel.textContent = "选择文件";
    state.searching = false;
    state.searchTerm = "";
    await loadMaterials();
    selectMaterial(data.id);
    showToast(`已上传并选中：${data.filename || file.name}`, "success");
  } finally {
    updateCourseHeading();
  }
}

async function generateSummary(materialId) {
  setStatus("正在生成 mock AI 摘要...");
  await requestJSON(`/api/materials/${materialId}/summary`, { method: "POST" });
  await refreshMaterials(materialId);
  showToast("摘要已生成并保存", "success");
}

async function generateCards(materialId) {
  setStatus("正在生成学习卡片...");
  const data = await requestJSON(`/api/materials/${materialId}/cards`, { method: "POST" });
  await refreshMaterials(materialId);
  showToast(`已生成 ${data.count} 张学习卡片`, "success");
}

async function refreshMaterials(selectedId = state.selectedMaterialId) {
  if (state.searching && state.searchTerm) {
    const params = new URLSearchParams({
      q: state.searchTerm,
      course_id: String(state.currentCourseId),
    });
    const data = await requestJSON(`/api/materials/search?${params.toString()}`);
    state.materials = data.materials || [];
    state.selectedMaterialId = Number(selectedId);
    renderMaterials();
    setStatus(`找到 ${data.count} 份资料`, "success");
    return;
  }
  state.selectedMaterialId = Number(selectedId);
  await loadMaterials();
  selectMaterial(selectedId);
}

async function runAction(action, materialId) {
  if (state.actionBusy) {
    return;
  }
  state.actionBusy = true;
  updateActionButtons();
  try {
    if (action === "summary") {
      await generateSummary(materialId);
    } else if (action === "cards") {
      await generateCards(materialId);
    }
  } catch (error) {
    setStatus(error.message, "error");
    showToast(error.message, "error");
  } finally {
    state.actionBusy = false;
    updateActionButtons();
  }
}

elements.courseList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-course-id]");
  if (!button) {
    return;
  }
  try {
    await selectCourse(button.dataset.courseId);
  } catch (error) {
    setStatus(error.message, "error");
    showToast(error.message, "error");
  }
});

elements.materialsList.addEventListener("click", (event) => {
  const actionButton = event.target.closest("button[data-action]");
  if (actionButton) {
    event.stopPropagation();
    runAction(actionButton.dataset.action, Number(actionButton.dataset.materialId));
    return;
  }
  const materialCard = event.target.closest("[data-material-id]");
  if (materialCard) {
    selectMaterial(Number(materialCard.dataset.materialId));
  }
});

elements.materialsList.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") {
    return;
  }
  const materialCard = event.target.closest("[data-material-id]");
  if (materialCard && event.target === materialCard) {
    event.preventDefault();
    selectMaterial(Number(materialCard.dataset.materialId));
  }
});

elements.detailSummaryButton.addEventListener("click", () => {
  if (state.selectedMaterialId !== null) {
    runAction("summary", state.selectedMaterialId);
  }
});

elements.detailCardsButton.addEventListener("click", () => {
  if (state.selectedMaterialId !== null) {
    runAction("cards", state.selectedMaterialId);
  }
});

elements.uploadForm.addEventListener("submit", async (event) => {
  try {
    await uploadMaterial(event);
  } catch (error) {
    event.preventDefault();
    setStatus(error.message, "error");
    showToast(error.message, "error");
    updateCourseHeading();
  }
});

elements.fileInput.addEventListener("change", () => {
  elements.fileLabel.textContent = elements.fileInput.files[0]?.name || "选择文件";
});

elements.searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await searchMaterials();
  } catch (error) {
    setStatus(error.message, "error");
    showToast(error.message, "error");
  }
});

elements.clearSearch.addEventListener("click", async () => {
  try {
    await selectCourse(state.currentCourseId);
  } catch (error) {
    setStatus(error.message, "error");
    showToast(error.message, "error");
  }
});

loadCourses().catch((error) => {
  setStatus(error.message, "error");
  showToast(`页面加载失败：${error.message}`, "error");
});
