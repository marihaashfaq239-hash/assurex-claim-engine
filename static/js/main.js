/* ═══════════════════════════════════════════════════════════════
   AssureX Claim Engine — Premium JavaScript v2.0
   Features: Counter animations, page transitions, chart helpers,
             micro-interactions, particles, smooth UX
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── Utility helpers ────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const on = (el, ev, fn, opts) => el?.addEventListener(ev, fn, opts);
const sleep = ms => new Promise(r => setTimeout(r, ms));

function getCsrfToken() {
  return $('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
}

/* ═══════════════════════════════════════════════════════════════
   BOOT — runs after DOM ready
   ═══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initActiveLinks();
  initAlertAutoDismiss();
  initDropZones();
  initConfidenceBars();
  initFormLoadingState();
  initTooltips();
  initCounterAnimations();
  initPageAnimations();
  initChartDefaults();
  initRippleEffect();
  initMicroInteractions();
  initClaimStepper();
  initSearchHighlight();
  initCopyToClipboard();
  initThemeParticles();
});

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════ */
function initSidebar() {
  const toggle  = $('#sidebarToggle');
  const sidebar = $('#sidebar');
  if (!toggle || !sidebar) return;

  on(toggle, 'click', () => {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  });

  // Restore persisted state
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
  }

  // Mobile: close sidebar on link click
  if (window.innerWidth < 768) {
    $$('#sidebar .nav-link').forEach(link =>
      on(link, 'click', () => sidebar.classList.add('collapsed'))
    );
  }
}

/* ── Active link highlighting ────────────────────────────────── */
function initActiveLinks() {
  const path = window.location.pathname;
  $$('#sidebar .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   ALERTS — auto-dismiss with progress bar
   ═══════════════════════════════════════════════════════════════ */
function initAlertAutoDismiss() {
  $$('.alert-dismissible').forEach(alert => {
    const delay = 5000;

    // Add a thin progress bar
    const bar = document.createElement('div');
    bar.style.cssText = `
      position:absolute;bottom:0;left:0;height:2px;width:100%;
      background:currentColor;opacity:.3;border-radius:0 0 4px 4px;
      transition:width ${delay}ms linear;
    `;
    alert.style.position = 'relative';
    alert.style.overflow = 'hidden';
    alert.appendChild(bar);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => { bar.style.width = '0%'; });
    });

    setTimeout(() => {
      try { bootstrap.Alert.getOrCreateInstance(alert).close(); }
      catch { alert.remove(); }
    }, delay);
  });
}

/* ═══════════════════════════════════════════════════════════════
   FILE DROP ZONES
   ═══════════════════════════════════════════════════════════════ */
function initDropZones() {
  $$('.upload-zone').forEach(zone => {
    const input = zone.querySelector('input[type="file"]');

    on(zone, 'click', e => {
      if (e.target.tagName !== 'INPUT') input?.click();
    });

    ['dragenter','dragover'].forEach(ev =>
      on(zone, ev, e => { e.preventDefault(); zone.classList.add('dragover'); })
    );
    ['dragleave','dragend'].forEach(ev =>
      on(zone, ev, () => zone.classList.remove('dragover'))
    );

    on(zone, 'drop', e => {
      e.preventDefault();
      zone.classList.remove('dragover');
      if (input && e.dataTransfer.files.length) {
        // Assign files
        try {
          const dt = new DataTransfer();
          [...e.dataTransfer.files].forEach(f => dt.items.add(f));
          input.files = dt.files;
        } catch { /* Safari fallback */ }
        updateFileLabel(zone, e.dataTransfer.files);
        zone.classList.add('has-file');
      }
    });

    if (input) {
      on(input, 'change', () => {
        updateFileLabel(zone, input.files);
        if (input.files.length) zone.classList.add('has-file');
      });
    }
  });
}

function updateFileLabel(zone, files) {
  const label = zone.querySelector('.upload-label');
  if (!label || !files.length) return;
  const names = [...files].map(f => f.name).join(', ');
  label.innerHTML = `<i class="bi bi-check-circle-fill text-success me-1"></i>${names}`;
}

/* ═══════════════════════════════════════════════════════════════
   CONFIDENCE BARS — animated on scroll
   ═══════════════════════════════════════════════════════════════ */
function initConfidenceBars() {
  const animate = bar => {
    const target = parseFloat(bar.getAttribute('data-value')) || 0;
    bar.style.width = '0%';
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        bar.style.transition = 'width 0.85s cubic-bezier(.4,0,.2,1)';
        bar.style.width = Math.min(target, 100) + '%';
      })
    );
  };

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { animate(e.target); obs.unobserve(e.target); } });
    }, { threshold: 0.2 });
    $$('.confidence-fill[data-value]').forEach(b => obs.observe(b));
  } else {
    $$('.confidence-fill[data-value]').forEach(animate);
  }
}

/* ═══════════════════════════════════════════════════════════════
   FORM LOADING STATE
   ═══════════════════════════════════════════════════════════════ */
function initFormLoadingState() {
  $$('form[data-loading]').forEach(form => {
    on(form, 'submit', () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
        const original = btn.innerHTML;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing…`;
        // Safety: re-enable after 15s in case of error
        setTimeout(() => { btn.disabled = false; btn.innerHTML = original; }, 15000);
      }
    });
  });
}

/* ─── Tooltips ──────────────────────────────────────────────── */
function initTooltips() {
  $$('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el, { trigger: 'hover' }));
  $$('[data-bs-toggle="popover"]').forEach(el => new bootstrap.Popover(el));
}

/* ═══════════════════════════════════════════════════════════════
   COUNTER ANIMATIONS — stat values count up on load
   ═══════════════════════════════════════════════════════════════ */
function initCounterAnimations() {
  const easeOut = t => 1 - Math.pow(1 - t, 3);

  const animateCounter = el => {
    const target = parseFloat(el.getAttribute('data-count') || el.textContent.replace(/[^0-9.]/g, ''));
    if (isNaN(target)) return;
    const suffix   = el.getAttribute('data-suffix') || '';
    const prefix   = el.getAttribute('data-prefix') || '';
    const decimals = (String(target).split('.')[1] || '').length;
    const duration = Math.min(1200, 400 + target * 2);
    const start    = performance.now();

    const update = now => {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const current  = target * easeOut(progress);
      el.textContent = prefix + current.toFixed(decimals) + suffix;
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  };

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          animateCounter(e.target);
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });
    $$('[data-count], .stat-value').forEach(el => {
      el.setAttribute('data-count', el.textContent.replace(/[^0-9.]/g, ''));
      obs.observe(el);
    });
  }
}

/* ═══════════════════════════════════════════════════════════════
   PAGE ANIMATIONS — stagger card/row entrances
   ═══════════════════════════════════════════════════════════════ */
function initPageAnimations() {
  // Add animate-in class to stat cards and cards with delay stagger
  const targets = $$('.stat-card, .card.animate-target');
  targets.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(14px)';
    el.style.transition = `opacity 0.4s ease ${i * 0.06}s, transform 0.4s ease ${i * 0.06}s`;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      })
    );
  });
}

/* ═══════════════════════════════════════════════════════════════
   CHART.JS GLOBAL DEFAULTS — makes all charts look premium
   ═══════════════════════════════════════════════════════════════ */
function initChartDefaults() {
  if (typeof Chart === 'undefined') return;

  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = '#64748b';
  Chart.defaults.plugins.legend.labels.boxWidth  = 10;
  Chart.defaults.plugins.legend.labels.padding   = 16;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15,32,64,.92)';
  Chart.defaults.plugins.tooltip.titleColor      = '#fff';
  Chart.defaults.plugins.tooltip.bodyColor       = 'rgba(255,255,255,.8)';
  Chart.defaults.plugins.tooltip.borderColor     = 'rgba(59,130,246,.4)';
  Chart.defaults.plugins.tooltip.borderWidth     = 1;
  Chart.defaults.plugins.tooltip.padding         = 10;
  Chart.defaults.plugins.tooltip.cornerRadius    = 8;
  Chart.defaults.plugins.tooltip.displayColors   = true;
  Chart.defaults.plugins.tooltip.boxPadding      = 4;
  Chart.defaults.scale.grid.color = 'rgba(37,99,235,.06)';
  Chart.defaults.scale.border.dash = [4, 4];
  Chart.defaults.elements.line.tension  = 0.4;
  Chart.defaults.elements.line.borderWidth = 2.5;
  Chart.defaults.elements.point.radius  = 3;
  Chart.defaults.elements.point.hoverRadius = 6;
  Chart.defaults.animation.duration = 800;
  Chart.defaults.animation.easing   = 'easeOutQuart';
}

/* ── Premium gradient line chart helper ─────────────────────── */
window.AssureX = window.AssureX || {};

window.AssureX.createLineChart = (ctx, labels, data, label = '', color = '#2563eb') => {
  const canvas  = typeof ctx === 'string' ? document.getElementById(ctx) : ctx;
  if (!canvas || typeof Chart === 'undefined') return null;
  const context = canvas.getContext('2d');

  const gradient = context.createLinearGradient(0, 0, 0, canvas.offsetHeight || 200);
  gradient.addColorStop(0, color + '30');
  gradient.addColorStop(1, color + '00');

  return new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data,
        borderColor: color,
        backgroundColor: gradient,
        fill: true,
        pointBackgroundColor: '#fff',
        pointBorderColor: color,
        pointBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { precision: 0 } }
      }
    }
  });
};

window.AssureX.createDoughnutChart = (ctx, labels, data, colors) => {
  const canvas = typeof ctx === 'string' ? document.getElementById(ctx) : ctx;
  if (!canvas || typeof Chart === 'undefined') return null;

  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors || ['#2563eb','#f43f5e','#f59e0b','#10b981'],
        borderWidth: 0,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 20, usePointStyle: true, pointStyleWidth: 10 }
        }
      }
    }
  });
};

window.AssureX.createBarChart = (ctx, labels, datasets) => {
  const canvas = typeof ctx === 'string' ? document.getElementById(ctx) : ctx;
  if (!canvas || typeof Chart === 'undefined') return null;

  return new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: datasets.length > 1 } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { precision: 0 } }
      },
      borderRadius: 6,
      borderSkipped: false,
    }
  });
};

/* ═══════════════════════════════════════════════════════════════
   RIPPLE EFFECT on buttons
   ═══════════════════════════════════════════════════════════════ */
function initRippleEffect() {
  on(document, 'click', e => {
    const btn = e.target.closest('.btn');
    if (!btn || btn.disabled) return;

    const rect   = btn.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height) * 2;
    const x      = e.clientX - rect.left - size / 2;
    const y      = e.clientY - rect.top  - size / 2;

    const ripple = document.createElement('span');
    ripple.style.cssText = `
      position:absolute;border-radius:50%;pointer-events:none;
      width:${size}px;height:${size}px;left:${x}px;top:${y}px;
      background:rgba(255,255,255,.25);transform:scale(0);
      animation:ripple-anim 0.5s linear;
    `;

    if (!btn.style.position || btn.style.position === 'static') btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });

  // Inject keyframe if not present
  if (!document.getElementById('ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = '@keyframes ripple-anim{to{transform:scale(1);opacity:0}}';
    document.head.appendChild(style);
  }
}

/* ═══════════════════════════════════════════════════════════════
   MICRO-INTERACTIONS
   ═══════════════════════════════════════════════════════════════ */
function initMicroInteractions() {
  // Stat card hover — elevate sibling text
  $$('.stat-card').forEach(card => {
    on(card, 'mouseenter', () => {
      const val = card.querySelector('.stat-value');
      if (val) val.style.transform = 'scale(1.03)';
    });
    on(card, 'mouseleave', () => {
      const val = card.querySelector('.stat-value');
      if (val) val.style.transform = '';
    });
  });

  // Table row: highlight on hover with smooth bg
  $$('.table-hover tbody tr').forEach(row => {
    on(row, 'mouseenter', () => row.style.transition = 'background 0.15s');
  });

  // Sidebar link: add subtle scale to icon
  $$('#sidebar .nav-link').forEach(link => {
    on(link, 'mouseenter', () => {
      const icon = link.querySelector('i');
      if (icon) icon.style.transform = 'scale(1.15)';
    });
    on(link, 'mouseleave', () => {
      const icon = link.querySelector('i');
      if (icon) icon.style.transform = '';
    });
  });

  // Badge hover pulse
  $$('.badge-claim').forEach(badge => {
    on(badge, 'mouseenter', () => {
      badge.style.transform = 'scale(1.08)';
      badge.style.transition = 'transform 0.15s';
    });
    on(badge, 'mouseleave', () => { badge.style.transform = ''; });
  });

  // Number inputs: flash border on focus
  $$('input[type="number"]').forEach(inp => {
    on(inp, 'focus', () => inp.style.borderColor = '#2563eb');
    on(inp, 'blur',  () => inp.style.borderColor = '');
  });
}

/* ═══════════════════════════════════════════════════════════════
   CLAIM STEPPER
   ═══════════════════════════════════════════════════════════════ */
function initClaimStepper() {
  const steps    = $$('.stepper-step');
  const panels   = $$('.step-panel');
  const nextBtns = $$('[data-next-step]');
  const prevBtns = $$('[data-prev-step]');
  if (!steps.length || !panels.length) return;

  let current = 0;

  const goTo = idx => {
    steps.forEach((s, i) => {
      s.classList.remove('active', 'done');
      if (i < idx) s.classList.add('done');
      if (i === idx) s.classList.add('active');
    });
    panels.forEach((p, i) => {
      p.classList.toggle('d-none', i !== idx);
      if (i === idx) {
        p.style.opacity = '0'; p.style.transform = 'translateX(10px)';
        requestAnimationFrame(() => requestAnimationFrame(() => {
          p.style.transition = 'opacity .3s, transform .3s';
          p.style.opacity = '1'; p.style.transform = 'translateX(0)';
        }));
      }
    });
    current = idx;
  };

  nextBtns.forEach(btn => on(btn, 'click', () => { if (current < steps.length - 1) goTo(current + 1); }));
  prevBtns.forEach(btn => on(btn, 'click', () => { if (current > 0) goTo(current - 1); }));
  goTo(0);
}

/* ═══════════════════════════════════════════════════════════════
   SEARCH HIGHLIGHT — highlight query in results
   ═══════════════════════════════════════════════════════════════ */
function initSearchHighlight() {
  const searchInput = $('input[name="q"]');
  if (!searchInput || !searchInput.value.trim()) return;

  const query  = searchInput.value.trim();
  const regex  = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const cells  = $$('td');

  cells.forEach(cell => {
    if (cell.children.length === 0 && cell.textContent.match(regex)) {
      cell.innerHTML = cell.textContent.replace(regex,
        '<mark style="background:rgba(37,99,235,.15);color:inherit;padding:0 2px;border-radius:2px;">$1</mark>'
      );
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   COPY TO CLIPBOARD — for claim references, serial numbers etc.
   ═══════════════════════════════════════════════════════════════ */
function initCopyToClipboard() {
  $$('[data-copy]').forEach(el => {
    el.style.cursor = 'pointer';
    el.title = 'Click to copy';

    on(el, 'click', async () => {
      const text = el.getAttribute('data-copy') || el.textContent.trim();
      try {
        await navigator.clipboard.writeText(text);
        const orig = el.innerHTML;
        el.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> Copied!';
        await sleep(1500);
        el.innerHTML = orig;
      } catch { /* clipboard not available */ }
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   THEME PARTICLES — subtle animated dots on auth pages
   ═══════════════════════════════════════════════════════════════ */
function initThemeParticles() {
  const wrapper = $('.auth-wrapper');
  if (!wrapper) return;

  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:.4';
  wrapper.appendChild(canvas);

  const ctx  = canvas.getContext('2d');
  let w = canvas.width  = wrapper.offsetWidth;
  let h = canvas.height = wrapper.offsetHeight;

  const NUM = Math.min(50, Math.floor(w * h / 18000));
  const particles = Array.from({ length: NUM }, () => ({
    x: Math.random() * w, y: Math.random() * h,
    r: Math.random() * 1.8 + 0.4,
    dx: (Math.random() - 0.5) * 0.3,
    dy: (Math.random() - 0.5) * 0.3,
    opacity: Math.random() * 0.5 + 0.2,
  }));

  const draw = () => {
    ctx.clearRect(0, 0, w, h);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(96,165,250,${p.opacity})`;
      ctx.fill();
      p.x += p.dx; p.y += p.dy;
      if (p.x < 0 || p.x > w) p.dx *= -1;
      if (p.y < 0 || p.y > h) p.dy *= -1;
    });

    // Draw connecting lines between close particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(96,165,250,${0.12 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  };

  draw();

  window.addEventListener('resize', () => {
    w = canvas.width  = wrapper.offsetWidth;
    h = canvas.height = wrapper.offsetHeight;
  });
}

/* ═══════════════════════════════════════════════════════════════
   NOTIFICATION REAL-TIME POLL (lightweight)
   ═══════════════════════════════════════════════════════════════ */
(function initNotificationPoll() {
  const badge = $('.notification-count-badge');
  if (!badge) return;

  const update = async () => {
    try {
      const res  = await fetch('/notifications/unread-count/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (!res.ok) return;
      const data = await res.json();
      const count = data.count || 0;
      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = count > 0 ? '' : 'none';
    } catch { /* silently fail */ }
  };

  update();
  setInterval(update, 60000); // poll every 60s
})();

/* ═══════════════════════════════════════════════════════════════
   PUBLIC UTILITIES (used by inline templates)
   ═══════════════════════════════════════════════════════════════ */
window.AssureX.formatFileSize = bytes => {
  if (bytes < 1024)    return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
};

window.AssureX.getCsrfToken = getCsrfToken;

window.AssureX.showToast = (message, type = 'success', duration = 4000) => {
  let container = $('#assurex-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'assurex-toast-container';
    container.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:.5rem;';
    document.body.appendChild(container);
  }

  const icons = { success: 'check-circle-fill', danger: 'x-circle-fill', warning: 'exclamation-triangle-fill', info: 'info-circle-fill' };
  const colors = { success: '#10b981', danger: '#f43f5e', warning: '#f59e0b', info: '#0891b2' };

  const toast = document.createElement('div');
  toast.style.cssText = `
    background:#fff;border-radius:.75rem;padding:.875rem 1.125rem;
    box-shadow:0 8px 32px rgba(0,0,0,.14);border-left:4px solid ${colors[type] || colors.info};
    display:flex;align-items:center;gap:.75rem;font-size:.875rem;font-weight:500;
    min-width:280px;max-width:380px;transform:translateX(120%);
    transition:transform .35s cubic-bezier(.4,0,.2,1);color:#1e293b;
  `;
  toast.innerHTML = `
    <i class="bi bi-${icons[type] || icons.info}" style="color:${colors[type]};font-size:1.1rem;flex-shrink:0;"></i>
    <span>${message}</span>
    <button onclick="this.parentElement.remove()" style="margin-left:auto;background:none;border:none;font-size:1rem;color:#94a3b8;cursor:pointer;padding:0;">×</button>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; }));
  setTimeout(() => {
    toast.style.transform = 'translateX(120%)';
    setTimeout(() => toast.remove(), 400);
  }, duration);
};

/* ── Confirm dialog (prettier than window.confirm) ──────────── */
window.AssureX.confirm = (message, onConfirm, title = 'Confirm Action') => {
  const existing = document.getElementById('assurex-confirm-modal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'assurex-confirm-modal';
  modal.innerHTML = `
    <div class="modal fade" id="confirmModalInner" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content border-0" style="border-radius:1rem;box-shadow:0 20px 60px rgba(0,0,0,.25);">
          <div class="modal-body p-4 text-center">
            <div style="width:52px;height:52px;background:rgba(244,63,94,.1);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;">
              <i class="bi bi-exclamation-triangle-fill text-danger fs-4"></i>
            </div>
            <h6 class="fw-bold mb-2">${title}</h6>
            <p class="text-muted small mb-3">${message}</p>
            <div class="d-flex gap-2 justify-content-center">
              <button class="btn btn-outline-secondary btn-sm px-3" data-action="cancel">Cancel</button>
              <button class="btn btn-danger btn-sm px-3" data-action="confirm">Confirm</button>
            </div>
          </div>
        </div>
      </div>
    </div>`;
  document.body.appendChild(modal);

  const bsModal = new bootstrap.Modal(modal.querySelector('.modal'));
  bsModal.show();

  modal.querySelector('[data-action="confirm"]').addEventListener('click', () => {
    bsModal.hide(); onConfirm();
  });
  modal.querySelector('[data-action="cancel"]').addEventListener('click', () => bsModal.hide());
  modal.addEventListener('hidden.bs.modal', () => modal.remove());
};
