const categoryInfo = {
  산림작업: { icon: "🌲", description: "조림·숲가꾸기·목재수확과 현장 시업 기준" },
  산림계획: { icon: "🧭", description: "경영계획·자원조사·수확조절 실무" },
  법령: { icon: "⚖", description: "산림 관련 법률·시행령·시행규칙" },
  행정규칙: { icon: "📋", description: "훈령·예규·고시·지침 원문과 기준" },
  매뉴얼: { icon: "📖", description: "산림청 매뉴얼·편람의 챕터별 정리" },
  국유재산: { icon: "🏛", description: "취득·사용허가·대부·매각·재산관리" },
  타부처법령: { icon: "🔗", description: "계약·안전 등 산림행정 연계 법령" },
  운영: { icon: "🗂", description: "법령체계와 위키 협업·운영 가이드" },
};

const categoryOrder = Object.keys(categoryInfo);
const categoryGrid = document.querySelector("#category-grid");
const documentCount = document.querySelector("#document-count");
const categoryCount = document.querySelector("#category-count");

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderCategories(categories = {}) {
  categoryGrid.innerHTML = categoryOrder
    .map((category) => {
      const info = categoryInfo[category];
      const count = categories[category] || 0;
      return `
        <article class="category-card">
          <span class="category-icon" aria-hidden="true">${info.icon}</span>
          <h3>${escapeHtml(category)}</h3>
          <p>${escapeHtml(info.description)}</p>
          <span class="category-meta">${count.toLocaleString("ko-KR")}개 문서</span>
        </article>`;
    })
    .join("");
}

async function initialize() {
  categoryCount.textContent = categoryOrder.length.toLocaleString("ko-KR");

  try {
    const response = await fetch("./data/wiki.json");
    if (!response.ok) throw new Error("위키 현황을 불러오지 못했습니다.");

    const data = await response.json();
    documentCount.textContent = data.total.toLocaleString("ko-KR");
    renderCategories(data.categories);
  } catch (error) {
    documentCount.textContent = "—";
    categoryGrid.innerHTML = `
      <p class="category-error">
        현재 문서 수를 표시하지 못했습니다. NotebookLM에서는 자료 검색과 질문을 그대로 이용할 수 있습니다.
      </p>`;
  }
}

initialize();
