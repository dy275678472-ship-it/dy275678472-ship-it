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

  const aiBtn = document.getElementById('ai-btn');
  const aiPanel = document.getElementById('ai-panel');
  const aiSend = document.getElementById('ai-send');
  const aiInput = document.getElementById('ai-input');
  const aiMessages = document.getElementById('ai-messages');
  if (aiBtn && aiPanel) {
    aiBtn.addEventListener('click', () => aiPanel.classList.toggle('open'));
    const send = async () => {
      const q = aiInput.value.trim();
      if (!q) return;
      aiMessages.innerHTML += `<p><strong>您：</strong>${q}</p>`;
      aiInput.value = '';
      try {
        const res = await fetch('/api/ai/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q }),
        });
        const json = await res.json();
        aiMessages.innerHTML += `<p><strong>助手：</strong>${json.answer}</p>`;
        aiMessages.scrollTop = aiMessages.scrollHeight;
      } catch {
        aiMessages.innerHTML += `<p><strong>助手：</strong>暂时无法回答，请通过联系页留言。</p>`;
      }
    };
    aiSend?.addEventListener('click', send);
    aiInput?.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
  }
});
