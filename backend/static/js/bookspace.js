/**
 * Raccoon Café - utilidades de interfaz.
 */
document.addEventListener('DOMContentLoaded', function () {
  // Los mensajes de exito desaparecen solos a los 6 segundos.
  document.querySelectorAll('[data-mensaje="success"]').forEach(function (aviso) {
    setTimeout(function () {
      aviso.style.transition = 'opacity .4s ease';
      aviso.style.opacity = '0';
      setTimeout(function () { aviso.remove(); }, 400);
    }, 6000);
  });

  // Confirmacion antes de enviar formularios marcados como peligrosos.
  document.querySelectorAll('form[data-confirmar]').forEach(function (formulario) {
    formulario.addEventListener('submit', function (evento) {
      if (!window.confirm(formulario.dataset.confirmar)) {
        evento.preventDefault();
      }
    });
  });
});
