(function () {
  var bar = document.getElementById('sticky-cta');
  if (!bar) return;
  var shown = false;
  function onScroll() {
    if (window.scrollY > 480 && !shown) {
      bar.hidden = false;
      requestAnimationFrame(function () { bar.classList.add('visible'); });
      shown = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
})();
