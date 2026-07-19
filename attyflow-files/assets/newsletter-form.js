(function () {
  var form = document.getElementById('newsletter-form');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = form.querySelector('input[type=email]').value.trim();
    var consent = form.querySelector('input[name=consent]');
    if (!email || (consent && !consent.checked)) {
      alert('Please enter your email and agree to receive emails.');
      return;
    }
    fetch('/api/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, source: 'newsletter', message: 'Newsletter signup' }),
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        form.innerHTML = '<p class="note">Thanks — you are subscribed to the Contract Risk Brief.</p>';
      })
      .catch(function () {
        alert('Signup failed. Email us at contact@attyflow.com');
      });
  });
})();
