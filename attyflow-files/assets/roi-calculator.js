(function () {
  var form = document.getElementById('roi-form');
  if (!form) return;
  function calc() {
    var contracts = parseFloat(document.getElementById('contracts').value) || 0;
    var hours = parseFloat(document.getElementById('hours').value) || 0;
    var rate = parseFloat(document.getElementById('rate').value) || 0;
    var savedPct = parseFloat(document.getElementById('saved').value) || 40;
    var plan = parseFloat(document.getElementById('plan').value) || 69;
    var hoursSaved = contracts * hours * (savedPct / 100);
    var valueSaved = hoursSaved * rate;
    var roi = plan > 0 ? ((valueSaved - plan) / plan) * 100 : 0;
    document.getElementById('hours-saved').textContent = hoursSaved.toFixed(1);
    document.getElementById('value-saved').textContent = '$' + valueSaved.toLocaleString(undefined, { maximumFractionDigits: 0 });
    document.getElementById('roi-pct').textContent = roi.toFixed(0) + '%';
    document.getElementById('net-monthly').textContent = '$' + (valueSaved - plan).toLocaleString(undefined, { maximumFractionDigits: 0 });
  }
  form.addEventListener('input', calc);
  calc();
})();
