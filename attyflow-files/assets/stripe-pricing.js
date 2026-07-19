(function () {
  fetch('/assets/stripe-config.json')
    .then(function (r) { return r.json(); })
    .then(function (cfg) {
      var solo = document.getElementById('solo-cta');
      var team = document.getElementById('team-cta');
      if (solo && cfg.solo) { solo.href = cfg.solo; solo.textContent = 'Subscribe Solo — $69/mo'; }
      if (team && cfg.team) { team.href = cfg.team; team.textContent = 'Subscribe Team — $249/mo'; }
    })
    .catch(function () {});
})();
