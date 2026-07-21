const titles = {
  dash: "数据看板",
  leads: "线索管理",
  chat: "在线客服",
  tickets: "工单",
  knowledge: "知识库",
  cases: "行业案例",
  news: "新闻",
  products: "产品",
  logs: "操作日志",
  site: "站点 / 备份",
};

let TOKEN = localStorage.getItem("kdgc_admin_token") || "";
let ROLE = localStorage.getItem("kdgc_admin_role") || "";
let activeChat = null;
let chatPollTimer = null;
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

function setAuth(ok, info) {
  document.getElementById("auth-state").textContent = ok ? "已登录" : "未登录";
  const badge = document.getElementById("role-badge");
  if (badge) badge.textContent = ok && info ? `${info.name || ""} · ${info.role || ROLE}` : "";
}

async function login() {
  TOKEN = tokenInput.value.trim();
  localStorage.setItem("kdgc_admin_token", TOKEN);
  try {
    const info = await api("/api/admin/login", { method: "POST" });
    ROLE = info.role || "";
    localStorage.setItem("kdgc_admin_role", ROLE);
    setAuth(true, info);
    await loadStats();
    alert(`登录成功：${info.name || ""}（${info.role}）`);
  } catch (e) {
    setAuth(false);
    alert("登录失败：" + e.message);
  }
}

document.getElementById("btn-login").onclick = login;

const publishBtn = document.getElementById("btn-publish");
if (publishBtn) {
  publishBtn.onclick = async () => {
    const log = document.getElementById("publish-log");
    publishBtn.disabled = true;
    log.textContent = "发布中…";
    try {
      const res = await api("/api/admin/publish", { method: "POST" });
      log.textContent = (res.message || "完成") + "\n" + (res.log || "");
      alert(res.message || "发布成功");
    } catch (e) {
      log.textContent = "失败：" + e.message;
      alert("发布失败：" + e.message);
    }
    publishBtn.disabled = false;
  };
}

const backupBtn = document.getElementById("btn-backup");
if (backupBtn) {
  backupBtn.onclick = async () => {
    const log = document.getElementById("backup-log");
    backupBtn.disabled = true;
    log.textContent = "备份中…";
    try {
      const res = await api("/api/admin/backup", { method: "POST" });
      log.textContent = JSON.stringify(res, null, 2);
      alert("备份完成");
    } catch (e) {
      log.textContent = "失败：" + e.message;
      alert("备份失败：" + e.message);
    }
    backupBtn.disabled = false;
  };
}

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
    if (tab === "chat") loadChats();
    if (tab === "tickets") loadTickets();
    if (tab === "knowledge") loadKnowledge();
    if (tab === "cases") loadCases();
    if (tab === "news") loadNews();
    if (tab === "products") loadProducts();
    if (tab === "logs") loadLogs();
    if (tab !== "chat") clearInterval(chatPollTimer);
  };
});

async function loadStats() {
  try {
    const s = await api("/api/admin/stats");
    document.getElementById("stats").innerHTML = [
      ["线索", s.leads],
      ["新线索", s.leads_new],
      ["待接待会话", s.chats_open],
      ["开放工单", s.tickets_open || 0],
      ["页面浏览", s.pageviews || 0],
      ["知识库", s.knowledge],
      ["行业案例", s.cases],
      ["新闻", s.news],
      ["产品", s.products],
    ].map(([k, v]) => `<div class="stat"><span>${k}</span><b>${v}</b></div>`).join("");
    const seriesBody = document.querySelector("#series-table tbody");
    if (seriesBody) {
      seriesBody.innerHTML = (s.series_7d || []).map((d) =>
        `<tr><td>${esc(d.date)}</td><td>${d.leads}</td><td>${d.pageviews}</td></tr>`
      ).join("") || `<tr><td colspan="3">暂无数据</td></tr>`;
    }
    const topBody = document.querySelector("#top-pages-table tbody");
    if (topBody) {
      topBody.innerHTML = (s.top_pages || []).map((d) =>
        `<tr><td>${esc(d.path)}</td><td>${d.views}</td></tr>`
      ).join("") || `<tr><td colspan="2">暂无数据</td></tr>`;
    }
    setAuth(true, { role: ROLE });
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
    <td>${esc(l.assignee || "-")}</td>
    <td>${esc(l.status)}</td>
    <td>
      <button class="btn" onclick="setLeadStatus(${l.id},'contacted')">已联系</button>
      <button class="btn" onclick="assignLead(${l.id})">分配</button>
      <button class="btn" onclick="setLeadStatus(${l.id},'closed')">关闭</button>
    </td>
  </tr>`).join("") || `<tr><td colspan="9">暂无线索</td></tr>`;
}
document.getElementById("lead-filter").onchange = loadLeads;

const exportBtn = document.getElementById("btn-export-leads");
if (exportBtn) {
  exportBtn.onclick = async (e) => {
    e.preventDefault();
    try {
      const r = await fetch("/api/admin/leads/export", { headers: headers(false) });
      if (!r.ok) throw new Error(await r.text());
      const blob = await r.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "kdgc-leads.csv";
      a.click();
    } catch (err) {
      alert("导出失败：" + err.message);
    }
  };
}

async function setLeadStatus(id, status) {
  await api(`/api/admin/leads/${id}`, { method: "PATCH", body: JSON.stringify({ status }) });
  loadLeads();
  loadStats();
}

async function assignLead(id) {
  const assignee = prompt("分配给（销售姓名/账号）");
  if (assignee == null) return;
  await api(`/api/admin/leads/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ assignee, status: "contacted" }),
  });
  loadLeads();
}

async function loadChats() {
  const rows = await api("/api/admin/chat/sessions");
  const filter = document.getElementById("chat-filter").value;
  const list = filter ? rows.filter((item) => item.status === filter) : rows;
  document.querySelector("#chat-table tbody").innerHTML = list.map((chat) => `<tr>
    <td>${esc((chat.last_message_at || chat.created_at || "").replace("T", " ").slice(0, 19))}</td>
    <td>${esc(chat.visitor_name || "匿名访客")}<br><span class="muted">${esc(chat.visitor_contact || "")}</span></td>
    <td>${esc((chat.last_message || "新会话").slice(0, 80))}</td>
    <td>${chat.status === "open" ? "待接待" : "已关闭"}</td>
    <td><button class="btn" onclick='openChat(${JSON.stringify(chat).replace(/'/g, "&#39;")})'>查看</button>
    ${chat.status === "closed" ? `<button class="btn" onclick="setChatStatus(${chat.id},'open')">重开</button>` : ""}</td>
  </tr>`).join("") || `<tr><td colspan="5">暂无客服会话</td></tr>`;
}
document.getElementById("chat-filter").onchange = loadChats;

async function openChat(chat) {
  activeChat = chat;
  document.getElementById("chat-admin-empty").hidden = true;
  document.getElementById("chat-admin-active").hidden = false;
  document.getElementById("chat-admin-title").textContent = chat.visitor_name || "匿名访客";
  document.getElementById("chat-admin-meta").textContent =
    [chat.visitor_contact, chat.page_url].filter(Boolean).join(" · ") || "未留联系方式";
  document.getElementById("chat-close-session").disabled = chat.status === "closed";
  await loadChatMessages();
  clearInterval(chatPollTimer);
  chatPollTimer = setInterval(loadChatMessages, 3000);
}

async function loadChatMessages() {
  if (!activeChat) return;
  const rows = await api(`/api/admin/chat/sessions/${activeChat.id}/messages`);
  const box = document.getElementById("chat-admin-messages");
  box.innerHTML = rows.map((message) => `<div class="chat-admin-message ${message.sender !== "visitor" ? "admin" : ""}">
    ${esc(message.body)}<small>${message.sender === "visitor" ? "访客" : (message.sender === "agent" ? "机器人" : "客服")} · ${esc((message.created_at || "").replace("T", " ").slice(0, 19))}</small>
  </div>`).join("") || `<div class="muted">会话暂无消息</div>`;
  box.scrollTop = box.scrollHeight;
}

async function sendChatReply() {
  if (!activeChat) return;
  const input = document.getElementById("chat-admin-input");
  const body = input.value.trim();
  if (!body) return;
  await api(`/api/admin/chat/sessions/${activeChat.id}/messages`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
  input.value = "";
  await loadChatMessages();
  await loadChats();
}

async function setChatStatus(id, status) {
  await api(`/api/admin/chat/sessions/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  if (activeChat?.id === id) {
    activeChat.status = status;
    document.getElementById("chat-close-session").disabled = status === "closed";
  }
  await loadChats();
  await loadStats();
}

document.getElementById("chat-admin-send").onclick = sendChatReply;
document.getElementById("chat-admin-input").onkeydown = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatReply();
  }
};
document.getElementById("chat-close-session").onclick = () => {
  if (activeChat) setChatStatus(activeChat.id, "closed");
};

const chatToTicket = document.getElementById("chat-to-ticket");
if (chatToTicket) {
  chatToTicket.onclick = async () => {
    if (!activeChat) return;
    try {
      const res = await api(`/api/admin/chat/sessions/${activeChat.id}/ticket`, { method: "POST" });
      alert(`已创建工单 #${res.id}`);
      loadTickets();
    } catch (e) {
      alert("转工单失败：" + e.message);
    }
  };
}

async function loadTickets() {
  const rows = await api("/api/admin/tickets");
  document.querySelector("#tickets-table tbody").innerHTML = rows.map((t) => `<tr>
    <td>${esc((t.created_at || "").replace("T", " ").slice(0, 19))}</td>
    <td>${esc(t.title)}</td>
    <td>${esc(t.category)}</td>
    <td>${esc(t.priority)}</td>
    <td>${esc(t.assignee || "-")}</td>
    <td>${esc(t.status)}</td>
    <td>
      <button class="btn" onclick="setTicketStatus(${t.id},'progress')">处理中</button>
      <button class="btn" onclick="assignTicket(${t.id})">分配</button>
      <button class="btn" onclick="setTicketStatus(${t.id},'done')">完成</button>
    </td>
  </tr>`).join("") || `<tr><td colspan="7">暂无工单</td></tr>`;
}

async function createTicket() {
  const title = prompt("工单标题");
  if (!title) return;
  const body = prompt("问题描述") || "";
  await api("/api/admin/tickets", {
    method: "POST",
    body: JSON.stringify({ title, body, category: "support" }),
  });
  loadTickets();
}

async function setTicketStatus(id, status) {
  await api(`/api/admin/tickets/${id}`, { method: "PATCH", body: JSON.stringify({ status }) });
  loadTickets();
  loadStats();
}

async function assignTicket(id) {
  const assignee = prompt("分配给");
  if (assignee == null) return;
  await api(`/api/admin/tickets/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ assignee, status: "progress" }),
  });
  loadTickets();
}

async function loadLogs() {
  const rows = await api("/api/admin/logs");
  document.querySelector("#logs-table tbody").innerHTML = rows.map((x) => `<tr>
    <td>${esc((x.created_at || "").replace("T", " ").slice(0, 19))}</td>
    <td>${esc(x.actor)}</td>
    <td>${esc(x.role)}</td>
    <td>${esc(x.action)}</td>
    <td>${esc(x.target || "")}</td>
    <td>${esc(x.detail || "")}</td>
    <td>${esc(x.ip || "")}</td>
  </tr>`).join("") || `<tr><td colspan="7">暂无日志</td></tr>`;
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
