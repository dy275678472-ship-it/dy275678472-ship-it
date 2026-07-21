document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.menu-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.querySelectorAll('a').forEach((a) => {
      a.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
      }
    });
  });

  const form = document.getElementById('lead-form');
  if (form) {
    const params = new URLSearchParams(window.location.search);
    const productMap = {
      'kd0100-02s-t1': ['KD0100-02S-T1 探头', 'KD0100-02S-T1 Probe'],
      'kd0100-02s-to': ['KD0100-02S-TO 插针', 'KD0100-02S-TO Pin'],
      'mask-o2-sensor': ['面罩用氧传感器', 'Mask O₂ Sensor'],
    };
    const productSlug = params.get('product');
    const reqSpec = params.get('req') === 'spec';
    if (productSlug && productMap[productSlug]) {
      const sel = form.querySelector('[name="product_interest"]');
      if (sel) {
        const opts = productMap[productSlug];
        for (const o of sel.options) {
          if (opts.includes(o.value)) { sel.value = o.value; break; }
        }
      }
    }
    if (reqSpec) {
      const ta = form.querySelector('[name="requirement"]');
      if (ta && !ta.value.trim()) {
        ta.value = document.documentElement.lang === 'en'
          ? 'Please send the product datasheet (PDF).'
          : '请发送产品规格书（PDF）';
      }
    }
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const msg = form.querySelector('.form-msg');
      const btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      const data = Object.fromEntries(new FormData(form));
      try {
        const res = await fetch('/api/leads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || '提交失败');
        msg.className = 'form-msg ok';
        msg.textContent = json.message || '提交成功';
        form.reset();
        if (typeof gtag === 'function') gtag('event', 'lead_submit');
      } catch (err) {
        msg.className = 'form-msg err';
        msg.textContent = err.message || '提交失败，请稍后重试';
      }
      btn.disabled = false;
    });
  }

  const chatOpen = document.getElementById('chat-open');
  const wechatOpen = document.getElementById('wechat-open');
  const chatPanel = document.getElementById('chat-panel');
  const wechatPanel = document.getElementById('wechat-panel');
  const chatSend = document.getElementById('chat-send');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');
  const chatState = document.getElementById('chat-state');
  let chatSession = null;
  let pollTimer = null;
  let lastMessageId = 0;

  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));

  const setPanel = (panel, open) => {
    [chatPanel, wechatPanel].forEach((p) => {
      if (p && p !== panel) {
        p.classList.remove('open');
        p.setAttribute('aria-hidden', 'true');
      }
    });
    if (!panel) return;
    panel.classList.toggle('open', open);
    panel.setAttribute('aria-hidden', open ? 'false' : 'true');
  };

  const renderMessage = (message) => {
    if (!chatMessages || chatMessages.querySelector(`[data-message-id="${message.id}"]`)) return;
    const bubble = document.createElement('div');
    bubble.className = `support-bubble ${message.sender === 'visitor' ? 'visitor' : 'agent'}`;
    bubble.dataset.messageId = message.id;
    bubble.innerHTML = esc(message.body).replace(/\n/g, '<br>');
    chatMessages.appendChild(bubble);
    lastMessageId = Math.max(lastMessageId, Number(message.id) || 0);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  const restoreSession = () => {
    try {
      const saved = JSON.parse(localStorage.getItem('kdgc_chat_session') || 'null');
      if (saved?.public_id && saved?.token) chatSession = saved;
    } catch {
      localStorage.removeItem('kdgc_chat_session');
    }
  };

  const ensureSession = async () => {
    if (chatSession) return chatSession;
    const res = await fetch('/api/chat/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        visitor_name: document.getElementById('chat-name')?.value.trim() || null,
        visitor_contact: document.getElementById('chat-phone')?.value.trim() || null,
        page_url: location.pathname,
      }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || '无法创建会话');
    chatSession = json;
    localStorage.setItem('kdgc_chat_session', JSON.stringify(chatSession));
    return chatSession;
  };

  const pollMessages = async () => {
    if (!chatSession || document.hidden) return;
    try {
      const res = await fetch(`/api/chat/sessions/${chatSession.public_id}/messages?token=${encodeURIComponent(chatSession.token)}&after=${lastMessageId}`);
      if (res.status === 404 || res.status === 403) {
        localStorage.removeItem('kdgc_chat_session');
        chatSession = null;
        return;
      }
      if (!res.ok) return;
      const rows = await res.json();
      rows.forEach(renderMessage);
    } catch {
      // A temporary network error should not interrupt the visitor.
    }
  };

  const startPolling = () => {
    clearInterval(pollTimer);
    pollMessages();
    pollTimer = setInterval(pollMessages, 4000);
  };

  const sendMessage = async () => {
    const body = chatInput?.value.trim();
    if (!body || !chatSend) return;
    chatSend.disabled = true;
    if (chatState) chatState.textContent = '正在发送…';
    try {
      const session = await ensureSession();
      const res = await fetch(`/api/chat/sessions/${session.public_id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: session.token, body }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || '发送失败');
      renderMessage(json);
      chatInput.value = '';
      if (chatState) chatState.textContent = '已发送，客服回复会自动显示';
      startPolling();
    } catch (error) {
      if (chatState) chatState.textContent = error.message || '发送失败，请稍后重试';
    } finally {
      chatSend.disabled = false;
      chatInput?.focus();
    }
  };

  if (chatOpen && chatPanel) {
    restoreSession();
    chatOpen.addEventListener('click', () => {
      const opening = !chatPanel.classList.contains('open');
      setPanel(chatPanel, opening);
      if (opening) {
        chatInput?.focus();
        startPolling();
      } else {
        clearInterval(pollTimer);
      }
    });
    chatSend?.addEventListener('click', sendMessage);
    chatInput?.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });
  }
  wechatOpen?.addEventListener('click', () => setPanel(wechatPanel, !wechatPanel?.classList.contains('open')));
  document.querySelectorAll('.support-close').forEach((button) => {
    button.addEventListener('click', () => {
      setPanel(button.closest('.support-panel,.wechat-panel'), false);
      clearInterval(pollTimer);
    });
  });

  // Light hero carousel
  const slides = [...document.querySelectorAll('.hero-slide')];
  const dots = [...document.querySelectorAll('.hero-dots button')];
  if (slides.length > 1) {
    let idx = 0;
    const show = (n) => {
      idx = (n + slides.length) % slides.length;
      slides.forEach((s, i) => s.classList.toggle('is-active', i === idx));
      dots.forEach((d, i) => d.classList.toggle('is-active', i === idx));
    };
    dots.forEach((d) => d.addEventListener('click', () => show(Number(d.dataset.slide || 0))));
    setInterval(() => show(idx + 1), 6000);
  }

  // Category filters
  document.querySelectorAll('.filter-bar').forEach((bar) => {
    const items = bar.parentElement.querySelectorAll('.filter-item');
    bar.querySelectorAll('.filter-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        bar.querySelectorAll('.filter-chip').forEach((c) => c.classList.remove('is-active'));
        chip.classList.add('is-active');
        const key = chip.dataset.filter;
        items.forEach((item) => {
          const show = key === 'all' || item.dataset.filter === key;
          item.style.display = show ? '' : 'none';
        });
      });
    });
  });

  // Scroll reveal (lightweight)
  const reveals = document.querySelectorAll('.card, .case-card, .kb-item, .values-card, .content-block, .faq-item');
  if ('IntersectionObserver' in window && reveals.length) {
    reveals.forEach((el) => el.classList.add('reveal'));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach((el) => io.observe(el));
  }
});
