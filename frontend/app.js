const state = {
  courses: [],
  currentCourseId: null,
  materials: [],
  searchTerm: "",
  searching: false,
};

const elements = {
  courseCount: document.querySelector("#course-count"),
  courseList: document.querySelector("#course-list"),
  courseTitle: document.querySelector("#course-title"),
  courseDescription: document.querySelector("#course-description"),
  materialsList: document.querySelector("#materials-list"),
  uploadForm: document.querySelector("#upload-form"),
  fileInput: document.querySelector("#file-input"),
  fileLabel: document.querySelector("#file-label"),
  searchForm: document.querySelector("#search-form"),
  searchInput: document.querySelector("#search-input"),
  clearSearch: document.querySelector("#clear-search"),
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
  if (text) {
    element.textContent = text;
  }
  return element;
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

  if (!state.materials.length) {
    const message = state.searching ? "没有找到匹配资料" : "当前课程暂无资料";
    elements.materialsList.append(createElement("p", "empty-state", message));
    return;
  }

  for (const material of state.materials) {
    elements.materialsList.append(renderMaterial(material));
  }
}

function renderMaterial(material) {
  const article = createElement("article", "material-card");
  const header = createElement("div", "material-card-header");
  const titleBlock = createElement("div");
  titleBlock.append(createElement("h3", "material-title", material.title));

  const metaRow = createElement("div", "meta-row");
  metaRow.append(createElement("span", "meta-tag", material.type));
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
  actions.append(createActionButton("summary", material.id, "生成摘要"));
  actions.append(createActionButton("cards", material.id, "生成卡片"));
  header.append(actions);
  article.append(header);

  const primaryText = material.ai_summary || material.text_preview || material.summary || "暂无可展示文本";
  article.append(createElement("p", "material-summary", primaryText));

  if (material.text_preview || material.ai_summary) {
    const detail = createElement("div", "detail-block");
    if (material.text_preview) {
      detail.append(createElement("p", "detail-line", `文本预览：${material.text_preview}`));
    }
    if (material.ai_summary) {
      detail.append(createElement("p", "detail-line", `AI 摘要：${material.ai_summary}`));
    }
    article.append(detail);
  }

  if (Array.isArray(material.cards) && material.cards.length) {
    const cardList = createElement("ol", "card-preview");
    for (const card of material.cards) {
      cardList.append(createElement("li", "", `${card.question} ${card.answer}`));
    }
    article.append(cardList);
  }

  return article;
}

function createActionButton(action, materialId, label) {
  const button = createElement("button", "small-button", label);
  button.type = "button";
  button.dataset.action = action;
  button.dataset.materialId = String(materialId);
  return button;
}

function updateCourseHeading() {
  const course = state.courses.find((item) => item.id === state.currentCourseId);
  if (!course) {
    elements.courseTitle.textContent = "请选择一门课程";
    elements.courseDescription.textContent = "课程资料和复习工具会显示在这里。";
    return;
  }
  elements.courseTitle.textContent = course.name;
  elements.courseDescription.textContent = `${course.semester} · ${course.description}`;
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
  renderMaterials();
  setStatus(`找到 ${data.count} 份资料`, "success");
}

async function uploadMaterial(event) {
  event.preventDefault();
  if (state.currentCourseId === null) {
    showToast("请先选择课程", "error");
    return;
  }
  const file = elements.fileInput.files[0];
  if (!file) {
    showToast("请选择 TXT 或 Markdown 文件", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  setStatus("正在上传...");
  const data = await requestJSON(`/api/courses/${state.currentCourseId}/materials/upload`, {
    method: "POST",
    body: formData,
  });
  elements.uploadForm.reset();
  elements.fileLabel.textContent = "选择文件";
  state.searching = false;
  await loadMaterials();
  showToast(`已上传：${data.filename}`, "success");
}

async function generateSummary(materialId) {
  setStatus("正在生成摘要...");
  await requestJSON(`/api/materials/${materialId}/summary`, { method: "POST" });
  await refreshMaterials();
  showToast("摘要已生成并保存", "success");
}

async function generateCards(materialId) {
  setStatus("正在生成学习卡片...");
  const data = await requestJSON(`/api/materials/${materialId}/cards`, { method: "POST" });
  await refreshMaterials();
  showToast(`已生成 ${data.count} 张学习卡片`, "success");
}

async function refreshMaterials() {
  if (state.searching && state.searchTerm) {
    const params = new URLSearchParams({
      q: state.searchTerm,
      course_id: String(state.currentCourseId),
    });
    const data = await requestJSON(`/api/materials/search?${params.toString()}`);
    state.materials = data.materials || [];
    renderMaterials();
    setStatus(`找到 ${data.count} 份资料`, "success");
    return;
  }
  await loadMaterials();
}

async function runAction(action, materialId, button) {
  button.disabled = true;
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
    button.disabled = false;
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
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }
  runAction(button.dataset.action, Number(button.dataset.materialId), button);
});

elements.uploadForm.addEventListener("submit", async (event) => {
  try {
    await uploadMaterial(event);
  } catch (error) {
    event.preventDefault();
    setStatus(error.message, "error");
    showToast(error.message, "error");
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
