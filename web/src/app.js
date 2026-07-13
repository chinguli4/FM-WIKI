const GITHUB_BASE = "https://github.com/chinguli4/FM-WIKI/blob/main/wiki/";

const categoryInfo = {
  산림작업: { icon: "🌲", description: "조림·숲가꾸기·벌채와 현장 시업 기준" },
  산림계획: { icon: "🧭", description: "경영계획·자원조사·수확조절 실무" },
  법령: { icon: "⚖", description: "산림 관련 법률·시행령·시행규칙" },
  행정규칙: { icon: "📋", description: "훈령·예규·고시·지침 원문과 기준" },
  매뉴얼: { icon: "📖", description: "산림청 매뉴얼·편람의 챕터별 정리" },
  국유재산: { icon: "🏛", description: "취득·사용허가·대부·매각·재산관리" },
  타부처법령: { icon: "🔗", description: "계약·안전 등 산림행정 연계 법령" },
};

const categoryOrder = Object.keys(categoryInfo);
const state = {
  data: null,
  documents: [],
  query: "",
  category: "",
  visible: 9,
  current: null,
  pathMap: new Map(),
  titleMap: new Map(),
};

const elements = {
  searchForm: document.querySelector("#search-form"),
  searchInput: document.querySelector("#search-input"),
  categoryGrid: document.querySelector("#category-grid"),
  documentGrid: document.querySelector("#document-grid"),
  documentCount: document.querySelector("#document-count"),
  categoryCount: document.querySelector("#category-count"),
  resultsKicker: document.querySelector("#results-kicker"),
  resultsTitle: document.querySelector("#results-title"),
  resultsCount: document.querySelector("#results-count"),
  filterClear: document.querySelector("#filter-clear"),
  loadMore: document.querySelector("#load-more"),
  documentsSection: document.querySelector("#documents-section"),
  drawer: document.querySelector("#document-drawer"),
  drawerBackdrop: document.querySelector("#drawer-backdrop"),
  drawerClose: document.querySelector("#drawer-close"),
  drawerCategory: document.querySelector("#drawer-category"),
  drawerTitle: document.querySelector("#drawer-title"),
  drawerPath: document.querySelector("#drawer-path"),
  drawerBody: document.querySelector("#drawer-body"),
  drawerGithub: document.querySelector("#drawer-github"),
};

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalize(value = "") {
  return value
    .normalize("NFKC")
    .toLocaleLowerCase("ko")
    .replace(/[^0-9a-z가-힣\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function scoreDocument(document, query) {
  const tokens = normalize(query).split(" ").filter(Boolean);
  if (!tokens.length) return 0;

  const title = normalize(document.title);
  const headings = normalize(document.headings.join(" "));
  const summary = normalize(document.summary);
  const content = normalize(document.markdown);
  const combined = `${title} ${headings} ${summary} ${content}`;
  if (!tokens.every((token) => combined.includes(token))) return -1;

  return tokens.reduce((score, token) => {
    if (title.includes(token)) score += 14;
    if (headings.includes(token)) score += 7;
    if (summary.includes(token)) score += 4;
    if (content.includes(token)) score += 1;
    return score;
  }, 0);
}

function getFilteredDocuments() {
  let documents = state.documents;
  if (state.category) documents = documents.filter((document) => document.category === state.category);
  if (state.query) {
    documents = documents
      .map((document) => ({ document, score: scoreDocument(document, state.query) }))
      .filter((item) => item.score >= 0)
      .sort((a, b) => b.score - a.score || a.document.rank - b.document.rank)
      .map((item) => item.document);
  }
  return documents;
}

function renderCategories() {
  elements.categoryGrid.innerHTML = categoryOrder
    .map((category) => {
      const info = categoryInfo[category];
      const count = state.data.categories[category] || 0;
      const isActive = state.category === category;
      return `
        <button class="category-card${isActive ? " active" : ""}" type="button" data-category="${escapeHtml(category)}" aria-pressed="${isActive}">
          <span class="category-icon" aria-hidden="true">${info.icon}</span>
          <h3>${escapeHtml(category)}</h3>
          <p>${escapeHtml(info.description)}</p>
          <span class="category-meta"><span>${count.toLocaleString("ko-KR")}개 문서</span><span class="category-arrow" aria-hidden="true">→</span></span>
        </button>`;
    })
    .join("");
}

function documentCard(document) {
  return `
    <article class="document-card">
      <span class="document-tag">${escapeHtml(document.category)}</span>
      <h3>${escapeHtml(document.title)}</h3>
      <p>${escapeHtml(document.summary)}</p>
      <div class="document-footer">
        <span class="document-path" title="${escapeHtml(document.path)}">wiki/${escapeHtml(document.path)}</span>
        <button class="document-open" type="button" data-document="${encodeURIComponent(document.path)}">문서 보기 →</button>
      </div>
    </article>`;
}

function renderDocuments({ scroll = false } = {}) {
  const filtered = getFilteredDocuments();
  const shown = filtered.slice(0, state.visible);

  if (state.query) {
    elements.resultsKicker.textContent = "SEARCH RESULTS";
    elements.resultsTitle.textContent = `“${state.query}” 검색 결과`;
  } else if (state.category) {
    elements.resultsKicker.textContent = "PRACTICE AREA";
    elements.resultsTitle.textContent = `${state.category} 문서`;
  } else {
    elements.resultsKicker.textContent = "QUICK ACCESS";
    elements.resultsTitle.textContent = "주요 문서 바로가기";
  }

  elements.resultsCount.textContent = `${filtered.length.toLocaleString("ko-KR")}개`;
  elements.filterClear.hidden = !state.query && !state.category;
  elements.loadMore.hidden = shown.length >= filtered.length;
  elements.loadMore.textContent = `문서 더 보기 (${(filtered.length - shown.length).toLocaleString("ko-KR")})`;

  elements.documentGrid.innerHTML = shown.length
    ? shown.map(documentCard).join("")
    : `<div class="empty-state"><strong>일치하는 문서를 찾지 못했습니다.</strong><span>검색어를 줄이거나 다른 표현으로 다시 찾아보세요.</span></div>`;

  renderCategories();
  if (scroll) elements.documentsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setSearch(query, { scroll = true } = {}) {
  state.query = query.trim();
  state.category = "";
  state.visible = 12;
  elements.searchInput.value = state.query;
  renderDocuments({ scroll });
}

function setCategory(category) {
  state.category = state.category === category ? "" : category;
  state.query = "";
  state.visible = 12;
  elements.searchInput.value = "";
  renderDocuments({ scroll: true });
}

function stashFactory() {
  const values = [];
  return {
    put(value) {
      const key = `@@WIKI_TOKEN_${values.length}@@`;
      values.push(value);
      return key;
    },
    restore(value) {
      return value.replace(/@@WIKI_TOKEN_(\d+)@@/g, (_, index) => values[Number(index)] || "");
    },
  };
}

function renderInline(input = "") {
  const stash = stashFactory();
  let value = input;

  value = value.replace(/`([^`]+)`/g, (_, code) => stash.put(`<code>${escapeHtml(code)}</code>`));
  value = value.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => {
    const caption = label || target;
    return stash.put(`<button class="wiki-link" type="button" data-wiki-target="${encodeURIComponent(target.trim())}">${escapeHtml(caption.trim())}</button>`);
  });
  value = value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const trimmedHref = href.trim();
    if (/^https?:\/\//i.test(trimmedHref)) {
      return stash.put(`<a href="${escapeHtml(trimmedHref)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`);
    }
    return stash.put(`<a href="#" data-md-link="${encodeURIComponent(trimmedHref)}">${escapeHtml(label)}</a>`);
  });

  value = escapeHtml(value)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/__([^_]+)__/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");

  return stash.restore(value);
}

function tableCells(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function isTableDivider(line = "") {
  const cells = tableCells(line);
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell));
}

function isBlockStart(lines, index) {
  const line = lines[index]?.trim() || "";
  if (!line) return true;
  return /^#{1,6}\s/.test(line) || /^```/.test(line) || /^>/.test(line) || /^([-*_])(?:\s*\1){2,}$/.test(line) || /^[-*+]\s+/.test(line) || /^\d+\.\s+/.test(line) || (line.includes("|") && isTableDivider(lines[index + 1] || ""));
}

function renderMarkdown(markdown = "") {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const output = [];
  let index = 0;

  while (index < lines.length) {
    const raw = lines[index];
    const line = raw.trim();
    if (!line) { index += 1; continue; }

    if (/^```/.test(line)) {
      const code = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index].trim())) {
        code.push(lines[index]);
        index += 1;
      }
      index += 1;
      output.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    if (line.includes("|") && isTableDivider(lines[index + 1] || "")) {
      const headers = tableCells(line);
      index += 2;
      const rows = [];
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        rows.push(tableCells(lines[index]));
        index += 1;
      }
      output.push(`<table><thead><tr>${headers.map((cell) => `<th>${renderInline(cell)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table>`);
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = Math.min(heading[1].length, 4);
      output.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^([-*_])(?:\s*\1){2,}$/.test(line)) {
      output.push("<hr />"); index += 1; continue;
    }

    if (/^>/.test(line)) {
      const quote = [];
      while (index < lines.length && /^>/.test(lines[index].trim())) {
        quote.push(lines[index].trim().replace(/^>\s?/, ""));
        index += 1;
      }
      output.push(`<blockquote>${quote.map((item) => renderInline(item)).join("<br />")}</blockquote>`);
      continue;
    }

    const unordered = /^[-*+]\s+/.test(line);
    const ordered = /^\d+\.\s+/.test(line);
    if (unordered || ordered) {
      const items = [];
      const pattern = unordered ? /^[-*+]\s+/ : /^\d+\.\s+/;
      while (index < lines.length && pattern.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(pattern, ""));
        index += 1;
      }
      const tag = unordered ? "ul" : "ol";
      output.push(`<${tag}>${items.map((item) => `<li>${renderInline(item)}</li>`).join("")}</${tag}>`);
      continue;
    }

    const paragraph = [line];
    index += 1;
    while (index < lines.length && !isBlockStart(lines, index)) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    output.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
  }

  return output.join("\n");
}

function normalizePath(pathValue) {
  const segments = [];
  for (const segment of pathValue.replaceAll("\\", "/").split("/")) {
    if (!segment || segment === ".") continue;
    if (segment === "..") segments.pop();
    else segments.push(segment);
  }
  return segments.join("/");
}

function resolveDocument(target, current = state.current) {
  let decoded = target;
  try { decoded = decodeURIComponent(target); } catch { /* keep original */ }
  decoded = decoded.split("#")[0].split("?")[0].trim().replace(/^wiki\//i, "").replace(/^\//, "");
  const currentDirectory = current?.path.includes("/") ? current.path.slice(0, current.path.lastIndexOf("/") + 1) : "";
  const candidates = [decoded, `${decoded}.md`, normalizePath(`${currentDirectory}${decoded}`), normalizePath(`${currentDirectory}${decoded}.md`)];

  for (const candidate of candidates) {
    const match = state.pathMap.get(candidate.toLocaleLowerCase("ko"));
    if (match) return match;
  }

  const titleMatch = state.titleMap.get(normalize(decoded.replace(/\.md$/i, "").split("/").pop()));
  if (titleMatch) return titleMatch;

  const suffix = decoded.replace(/\.md$/i, "").toLocaleLowerCase("ko");
  return state.documents.find((document) => document.id.toLocaleLowerCase("ko").endsWith(suffix)) || null;
}

function openDocument(document, { updateHistory = true } = {}) {
  state.current = document;
  elements.drawerCategory.textContent = document.category.toUpperCase();
  elements.drawerTitle.textContent = document.title;
  elements.drawerPath.textContent = `wiki/${document.path}`;
  elements.drawerGithub.href = `${GITHUB_BASE}${document.path.split("/").map(encodeURIComponent).join("/")}`;
  elements.drawerBody.innerHTML = renderMarkdown(document.markdown);
  elements.drawerBackdrop.hidden = false;
  elements.drawer.classList.add("open");
  elements.drawer.setAttribute("aria-hidden", "false");
  window.document.body.classList.add("drawer-open");
  elements.drawer.scrollTop = 0;
  elements.drawerClose.focus();
  if (updateHistory) history.pushState({ document: document.path }, "", `#doc=${encodeURIComponent(document.path)}`);
}

function closeDocument({ updateHistory = true } = {}) {
  if (!state.current) return;
  state.current = null;
  elements.drawer.classList.remove("open");
  elements.drawer.setAttribute("aria-hidden", "true");
  elements.drawerBackdrop.hidden = true;
  window.document.body.classList.remove("drawer-open");
  if (updateHistory) history.pushState({}, "", `${location.pathname}${location.search}`);
}

function openFromHash() {
  const match = location.hash.match(/^#doc=(.+)$/);
  if (!match) { closeDocument({ updateHistory: false }); return; }
  const document = resolveDocument(match[1], null);
  if (document) openDocument(document, { updateHistory: false });
}

function bindEvents() {
  elements.searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    setSearch(elements.searchInput.value);
  });

  document.querySelectorAll("[data-query]").forEach((button) => {
    button.addEventListener("click", () => setSearch(button.dataset.query));
  });

  elements.categoryGrid.addEventListener("click", (event) => {
    const card = event.target.closest("[data-category]");
    if (card) setCategory(card.dataset.category);
  });

  elements.documentGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-document]");
    if (!button) return;
    const document = state.pathMap.get(decodeURIComponent(button.dataset.document).toLocaleLowerCase("ko"));
    if (document) openDocument(document);
  });

  elements.filterClear.addEventListener("click", () => {
    state.query = ""; state.category = ""; state.visible = 9; elements.searchInput.value = ""; renderDocuments({ scroll: true });
  });
  elements.loadMore.addEventListener("click", () => { state.visible += 12; renderDocuments(); });
  elements.drawerClose.addEventListener("click", () => closeDocument());
  elements.drawerBackdrop.addEventListener("click", () => closeDocument());

  elements.drawerBody.addEventListener("click", (event) => {
    const wikiLink = event.target.closest("[data-wiki-target]");
    const markdownLink = event.target.closest("[data-md-link]");
    const target = wikiLink?.dataset.wikiTarget || markdownLink?.dataset.mdLink;
    if (!target) return;
    event.preventDefault();
    const document = resolveDocument(target);
    if (document) openDocument(document);
    else event.target.classList.add("broken-link");
  });

  window.addEventListener("keydown", (event) => { if (event.key === "Escape" && state.current) closeDocument(); });
  window.addEventListener("popstate", openFromHash);
  window.addEventListener("hashchange", openFromHash);
}

function setupSearchExamples() {
  const examples = ["솎아베기 기준", "국유림 사용허가", "산불피해지 복구", "산림기술자 이중취업"];
  const desktopPlaceholder = "예: 솎아베기 기준, 산림기술자 이중취업, 국유림 사용허가";
  const mobileViewport = window.matchMedia("(max-width: 680px)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let exampleIndex = 0;

  const updatePlaceholder = () => {
    if (elements.searchInput.value || document.activeElement === elements.searchInput) return;
    elements.searchInput.placeholder = mobileViewport.matches
      ? `예: ${examples[exampleIndex]}`
      : desktopPlaceholder;
  };

  elements.searchInput.addEventListener("focus", () => {
    if (mobileViewport.matches && !elements.searchInput.value) elements.searchInput.placeholder = "검색어를 입력하세요";
  });
  elements.searchInput.addEventListener("blur", updatePlaceholder);
  mobileViewport.addEventListener("change", updatePlaceholder);
  updatePlaceholder();

  if (!reducedMotion) {
    window.setInterval(() => {
      if (!mobileViewport.matches || elements.searchInput.value || document.activeElement === elements.searchInput) return;
      exampleIndex = (exampleIndex + 1) % examples.length;
      updatePlaceholder();
    }, 3200);
  }
}

async function initialize() {
  try {
    const response = await fetch("./data/wiki.json");
    if (!response.ok) throw new Error("문서 인덱스를 불러오지 못했습니다.");
    state.data = await response.json();
    state.documents = state.data.documents;
    for (const document of state.documents) {
      state.pathMap.set(document.path.toLocaleLowerCase("ko"), document);
      state.titleMap.set(normalize(document.title), document);
    }
    elements.documentCount.textContent = state.data.total.toLocaleString("ko-KR");
    elements.categoryCount.textContent = categoryOrder.length.toLocaleString("ko-KR");
    renderCategories();
    renderDocuments();
    bindEvents();
    setupSearchExamples();
    openFromHash();
  } catch (error) {
    elements.documentGrid.innerHTML = `<div class="empty-state"><strong>문서를 불러오지 못했습니다.</strong><span>${escapeHtml(error.message)}</span></div>`;
    elements.categoryGrid.innerHTML = "";
  }
}

initialize();
