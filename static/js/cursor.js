/* ═══════════════════════════════════════════════════════════════
   AssureX — Custom Cursor
   - Dot: sticks to mouse instantly
   - Ring: smooth lerp follow
   - Hover: ring expands on interactive elements
   - Click: ripple effect
   - Mobile: disabled automatically
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (window.matchMedia('(hover: none)').matches) return;

  const dot  = document.createElement('div');
  const ring = document.createElement('div');
  dot.id  = 'ax-cursor-dot';
  ring.id = 'ax-cursor-ring';
  document.body.appendChild(ring);
  document.body.appendChild(dot);

  let mouseX = 0, mouseY = 0;
  let ringX  = 0, ringY  = 0;

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate(calc(${mouseX}px - 50%), calc(${mouseY}px - 50%))`;
    dot.classList.remove('hidden');
    ring.classList.remove('hidden');
  });

  document.addEventListener('mouseleave', () => {
    dot.classList.add('hidden');
    ring.classList.add('hidden');
  });
  document.addEventListener('mouseenter', () => {
    dot.classList.remove('hidden');
    ring.classList.remove('hidden');
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  (function tick() {
    ringX = lerp(ringX, mouseX, 0.11);
    ringY = lerp(ringY, mouseY, 0.11);
    ring.style.transform = `translate(calc(${ringX}px - 50%), calc(${ringY}px - 50%))`;
    requestAnimationFrame(tick);
  })();

  const HOVER = 'a,button,[role="button"],input,textarea,select,label,.btn,.nav-link,.feature-card,.role-card,.ai-metric,.stat-item,.claim-list-item,.card,.sidebar-brand';

  document.addEventListener('mouseover', e => {
    if (!e.target.closest(HOVER)) return;
    dot.classList.add('hovering');
    ring.classList.add('hovering');
    const tag = e.target.closest(HOVER).tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') ring.classList.add('text-cursor');
  });
  document.addEventListener('mouseout', () => {
    dot.classList.remove('hovering', 'text-cursor');
    ring.classList.remove('hovering', 'text-cursor');
  });

  document.addEventListener('mousedown', () => {
    dot.classList.add('clicking');
    ring.classList.add('clicking');
  });
  document.addEventListener('mouseup', () => {
    dot.classList.remove('clicking');
    ring.classList.remove('clicking');
  });

  document.addEventListener('click', e => {
    const r = document.createElement('div');
    r.className = 'ax-cursor-ripple';
    r.style.cssText = `left:${e.clientX}px;top:${e.clientY}px;width:40px;height:40px;`;
    document.body.appendChild(r);
    setTimeout(() => r.remove(), 600);
  });
})();
