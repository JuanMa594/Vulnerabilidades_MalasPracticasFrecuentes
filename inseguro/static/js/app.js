// JS compartido por las dos versiones.
//
// IMPORTANTE (ver CLAUDE.md): este archivo NO valida ni filtra nada de la lección.
// Las vulnerabilidades son del backend (Python) y se demuestran enviándole el ataque.
// Si aquí bloqueáramos el texto "peligroso", taparíamos el fallo que se quiere enseñar.
//
// Su única tarea es una comodidad: marcar el botón mientras se envía el formulario,
// para que se note que la página está trabajando.

document.addEventListener("DOMContentLoaded", () => {
  for (const form of document.querySelectorAll("form.demo-form")) {
    form.addEventListener("submit", (evento) => {
      const boton = evento.target.querySelector("button[type=submit]");
      if (boton) {
        boton.disabled = true;
        boton.textContent = "Enviando...";
      }
    });
  }
});
