/**
 * ImmoPredictor — JavaScript principal
 * Vanilla JS, pas de dépendances externes.
 * C17 — Accessibilité, UX progressive.
 */

'use strict';

/* ─── Fermeture automatique des messages ─────────────────────── */
document.querySelectorAll('.message').forEach(function (el) {
  setTimeout(function () {
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.4s';
    setTimeout(function () { el.remove(); }, 400);
  }, 6000);
});

/* ─── Indicateur de chargement sur les formulaires ──────────────
   Prévient les doubles soumissions. */
document.querySelectorAll('form').forEach(function (form) {
  form.addEventListener('submit', function () {
    var btn = form.querySelector('[type="submit"]');
    if (!btn) return;
    btn.disabled = true;
    btn.dataset.originalText = btn.textContent;
    btn.textContent = 'Chargement…';
  });
});

/* ─── Géolocalisation auto (formulaire de prédiction) ───────────
   Remplit lat/lon si l'utilisateur autorise la géolocalisation. */
var geoBtn = document.getElementById('btn-geolocate');
if (geoBtn && navigator.geolocation) {
  geoBtn.style.display = 'inline-block';
  geoBtn.addEventListener('click', function () {
    geoBtn.textContent = 'Localisation…';
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        var latInput = document.querySelector('[name="latitude"]');
        var lngInput = document.querySelector('[name="longitude"]');
        if (latInput) latInput.value = pos.coords.latitude.toFixed(6);
        if (lngInput) lngInput.value = pos.coords.longitude.toFixed(6);
        geoBtn.textContent = '📍 Position obtenue';
      },
      function () {
        geoBtn.textContent = 'Géolocalisation refusée';
      }
    );
  });
}

/* ─── Navigation mobile (menu hamburger) ────────────────────── */
var hamburger = document.getElementById('hamburger');
var mobileMenu = document.getElementById('mobile-menu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', function () {
    var expanded = hamburger.getAttribute('aria-expanded') === 'true';
    hamburger.setAttribute('aria-expanded', String(!expanded));
    mobileMenu.hidden = expanded;
  });
}
