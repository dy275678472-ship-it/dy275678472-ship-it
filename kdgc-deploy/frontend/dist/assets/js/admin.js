const titles = {
  dash: "概览",
  leads: "线索管理",
  knowledge: "知识库",
  cases: "行业案例",
  news: "新闻",
  products: "产品",
  site: "站点信息",
};

let TOKEN = localStorage.getItem("kdgc_admin_token") || "";
const tokenInput = document.getElementById("token");
tokenInput.value = TOKEN;

function headers(json = true) {
  const h = { "X-Admin-Token": TOKEN };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

async function api(path, opts = {}) {
  const r = await fetch(path, { ...opts, headers: { ...headers(!!opts.body), ...(opts.headers || {}) } });
  const text = await r.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!r.ok) throw new Error((data && data.detail) || r.statusText || "请求失败");
  return data;
}

function setAuth(ok) {
  document.getElementById("auth-state").textContent = ok ? "已登录" : "未登录";
}

async function login() {
  TOKEN = tokenInput.value.trim();
  localStorage.setItem("kdgc_admin_token", TOKEN);
  try {
    await api("/api/admin/login", { method: "POST" });
    setAuth(true);
    await loadStats();
    alert("登录成功");
  } catch (e) {
    setAuth(false);
    alert("登录失败：" + e.message);
  }
}

document.getElementById("btn-login").onclick = login;

document.querySelectorAll(".side nav button").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll(".side nav button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    document.getElementById("tab-" + tab).classList.add("active");
    document.getElementById("page-title").textContent = titles[tab] || tab;
    if (tab === "dash") loadStats();
    if (tab === "leads") loadLeads();
    if (tab === "knowledge") loadKnowledge();
    if (tab === "cases") loadCases();
    if (tab === "news") loadNews();
    if (tab === "products") loadProducts();
  };
});

async function loadStats() {
  try {
    const s = await api("/api/admin/stats");
    document.getElementById("stats").innerHTML = [
      ["线索", s.leads],
      ["新线索", s.leads_new],
      ["知识库", s.knowledge],
      ["行业案例", s.cases],
      ["新闻", s.news],
      ["产品", s.products],
    ].map(([k, v]) => `<div class="stat"><span>${k}</span><b>${v}</b></div>`).join("");
    setAuth(true);
  } catch {
    document.getElementById("stats").innerHTML = `<div class="card">请先登录后台 Token</div>`;
  }
}

async function loadLeads() {
  const rows = await api("/api/admin/leads");
  const filter = document.getElementById("lead-filter").value;
  const list = filter ? rows.filter((x) => x.status === filter) : rows;
  const tb = document.querySelector("#leads-table tbody");
  tb.innerHTML = list.map((l) => `<tr>
    <td>${(l.created_at || "").replace("T", " ").slice(0, 19)}</td>
    <td>${esc(l.company)}</td>
    <td>${esc(l.contact_name)}</td>
    <td>${esc(l.phone)}<br>${esc(l.email || "")}</td>
    <td>${esc(l.product_interest || "")}</td>
    <td>${esc(l.requirement || "")}</td>
    <td>${esc(l.status)}</td>
    <td>
      <button class="btn" onclick="setLeadStatus(${l.id},'contacted')">已联系</button>
      <button class="btn" onclick="setLeadStatus(${l.id},'closed')">关闭</button>
      <button class="btn" onclick="setLeadStatus(${l.id},'new')">重开</button>
    </td>
  </tr>`).join("") || `<tr><td colspan="8">暂无线索</td></tr>`;
}
document.getElementById("lead-filter").onchange = loadLeads;

async function setLeadStatus(id, status) {
  await api(`/api/admin/leads/${id}`, { method: "PATCH", body: JSON.stringify({ status }) });
  loadLeads();
  loadStats();
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function openEditor(title, fields, onSave) {
  const dlg = document.getElementById("editor");
  document.getElementById("editor-title").textContent = title;
  const box = document.getElementById("editor-fields");
  box.innerHTML = fields.map((f) => {
    if (f.type === "textarea") return `<label>${f.label}</label><textarea name="${f.name}">${esc(f.value || "")}</textarea>`;
    if (f.type === "checkbox") return `<label><input type="checkbox" name="${f.name}" ${f.value ? "checked" : ""}> ${f.label}</label>`;
    return `<label>${f.label}</label><input name="${f.name}" value="${esc(f.value || "")}">`;
  }).join("");
  const saveBtn = document.getElementById("editor-save");
  saveBtn.onclick = async (e) => {
    e.preventDefault();
    const data = {};
    fields.forEach((f) => {
      const el = box.querySelector(`[name="${f.name}"]`);
      if (!el) return;
      data[f.name] = f.type === "checkbox" ? el.checked : el.value;
    });
    await onSave(data);
    dlg.close();
  };
  dlg.showModal();
}

async function loadKnowledge() {
  const rows = await api("/api/admin/knowledge");
  document.querySelector("#kb-table tbody").innerHTML = rows.map((k) => `<tr>
    <td>${esc(k.category)}</td><td>${esc(k.title)}</td><td>${esc(k.slug)}</td>
    <td>${k.is_published ? "是" : "否"}</td>
    <td><button class="btn" onclick='editKnowledge(${JSON.stringify(k).replace(/'/g, "&#39;")})'>编辑</button>
    <button class="btn" onclick="delItem('/api/admin/knowledge/${k.id}', loadKnowledge)">删除</button></td>
  </tr>`).join("") || `<tr><td colspan="5">暂无文章，可新建或运行 seed</td></tr>`;
}

function editKnowledge(item) {
  const it = typeof item === "string" ? JSON.parse(item) : item || {};
  openEditor(it.id ? "编辑知识库文章" : "新建知识库文章", [
    { name: "title", label: "标题", value: it.title },
    { name: "slug", label: "Slug", value: it.slug },
    { name: "category", label: "分类", value: it.category || "原理" },
    { name: "summary", label: "摘要", type: "textarea", value: it.summary },
    { name: "content", label: "正文 HTML", type: "textarea", value: it.content },
    { name: "cover_image", label: "封面路径", value: it.cover_image },
    { name: "is_published", label: "发布", type: "checkbox", value: it.is_published !== false },
    { name: "sort_order", label: "排序", value: it.sort_order ?? 0 },
  ], async (data) => {
    data.sort_order = Number(data.sort_order) || 0;
    if (it.id) await api(`/api/admin/knowledge/${it.id}`, { method: "PUT", body: JSON.stringify(data) });
    else await api("/api/admin/knowledge", { method: "POST", body: JSON.stringify(data) });
    loadKnowledge();
  });
}

async function loadCases() {
  const rows = await api("/api/admin/cases");
  document.querySelector("#cases-table tbody").innerHTML = rows.map((c) => `<tr>
    <td>${esc(c.industry)}</td><td>${esc(c.title)}</td><td>${esc(c.customer_alias)}</td>
    <td>${c.is_published ? "是" : "否"}</td>
    <td><button class="btn" onclick='editCase(${JSON.stringify(c).replace(/'/g, "&#39;")})'>编辑</button>
    <button class="btn" onclick="delItem('/api/admin/cases/${c.id}', loadCases)">删除</button></td>
  </tr>`).join("") || `<tr><td colspan="5">暂无案例</td></tr>`;
}

function editCase(item) {
  const it = typeof item === "string" ? JSON.parse(item) : item || {};
  openEditor(it.id ? "编辑行业案例" : "新建行业案例", [
    { name: "title", label: "标题", value: it.title },
    { name: "slug", label: "Slug", value: it.slug },
    { name: "industry", label: "行业", value: it.industry },
    { name: "customer_alias", label: "客户代名词", value: it.customer_alias },
    { name: "challenge", label: "挑战", type: "textarea", value: it.challenge },
    { name: "solution", label: "方案", type: "textarea", value: it.solution },
    { name: "result", label: "结果", type: "textarea", value: it.result },
    { name: "cover_image", label: "封面路径", value: it.cover_image },
    { name: "is_published", label: "发布", type: "checkbox", value: it.is_published !== false },
    { name: "sort_order", label: "排序", value: it.sort_order ?? 0 },
  ], async (data) => {
    data.sort_order = Number(data.sort_order) || 0;
    if (it.id) await api(`/api/admin/cases/${it.id}`, { method: "PUT", body: JSON.stringify(data) });
    else await api("/api/admin/cases", { method: "POST", body: JSON.stringify(data) });
    loadCases();
  });
}

async function loadNews() {
  const rows = await api("/api/admin/news");
  document.querySelector("#news-table tbody").innerHTML = rows.map((n) => `<tr>
    <td>${esc(n.title)}</td><td>${esc(n.slug)}</td><td>${n.is_published ? "是" : "否"}</td>
    <td><button class="btn" onclick='editNews(${JSON.stringify(n).replace(/'/g, "&#39;")})'>编辑</button>
    <button class="btn" onclick="delItem('/api/admin/news/${n.id}', loadNews)">删除</button></td>
  </tr>`).join("") || `<tr><td colspan="4">暂无新闻</td></tr>`;
}

function editNews(item) {
  const it = typeof item === "string" ? JSON.parse(item) : item || {};
  openEditor(it.id ? "编辑新闻" : "新建新闻", [
    { name: "title", label: "标题", value: it.title },
    { name: "slug", label: "Slug", value: it.slug },
    { name: "summary", label: "摘要", type: "textarea", value: it.summary },
    { name: "content", label: "正文", type: "textarea", value: it.content },
    { name: "cover_image", label: "封面", value: it.cover_image },
    { name: "is_published", label: "发布", type: "checkbox", value: it.is_published !== false },
  ], async (data) => {
    if (it.id) await api(`/api/admin/news/${it.id}`, { method: "PUT", body: JSON.stringify(data) });
    else await api("/api/admin/news", { method: "POST", body: JSON.stringify(data) });
    loadNews();
  });
}

async function loadProducts() {
  const rows = await api("/api/admin/products");
  document.querySelector("#products-table tbody").innerHTML = rows.map((p) => `<tr>
    <td>${esc(p.name)}</td><td>${esc(p.slug)}</td><td>${esc(p.tagline)}</td>
    <td>${p.is_published ? "是" : "否"}</td>
    <td><button class="btn" onclick='editProduct(${JSON.stringify(p).replace(/'/g, "&#39;")})'>编辑</button></td>
  </tr>`).join("");
}

function editProduct(item) {
  const it = typeof item === "string" ? JSON.parse(item) : item;
  openEditor("编辑产品", [
    { name: "name", label: "名称", value: it.name },
    { name: "slug", label: "Slug", value: it.slug },
    { name: "category", label: "分类", value: it.category },
    { name: "tagline", label: "卖点", value: it.tagline },
    { name: "summary", label: "摘要", type: "textarea", value: it.summary },
    { name: "content", label: "详情", type: "textarea", value: it.content },
    { name: "image_url", label: "图片", value: it.image_url },
    { name: "is_featured", label: "推荐", type: "checkbox", value: !!it.is_featured },
    { name: "is_published", label: "发布", type: "checkbox", value: it.is_published !== false },
    { name: "sort_order", label: "排序", value: it.sort_order ?? 0 },
  ], async (data) => {
    data.sort_order = Number(data.sort_order) || 0;
    await api(`/api/admin/products/${it.id}`, { method: "PUT", body: JSON.stringify(data) });
    loadProducts();
  });
}

async function delItem(url, reload) {
  if (!confirm("确认删除？")) return;
  await api(url, { method: "DELETE" });
  reload();
}

// boot
if (TOKEN) {
  loadStats().catch(() => setAuth(false));
}
