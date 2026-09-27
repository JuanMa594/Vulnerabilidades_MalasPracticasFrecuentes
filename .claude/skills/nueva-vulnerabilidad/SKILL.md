---
name: nueva-vulnerabilidad
description: Agrega a la demo una vulnerabilidad del catálogo con su versión insegura, su versión segura, la forma de explotarla y la ficha para estudiantes.
argument-hint: "<código Vxx>"
disable-model-invocation: true
---

# Agregar la vulnerabilidad $ARGUMENTS

1. Busca `$ARGUMENTS` en el "Catálogo de vulnerabilidades" de CLAUDE.md. Si no está, detente y pregunta.
2. **Versión insegura** en `inseguro/`, siguiendo `.claude/rules/codigo-inseguro.md`.
3. **Versión segura** en `seguro/`: mismo archivo y misma ruta, siguiendo `.claude/rules/codigo-seguro.md`.
4. **Demostración**: pasos exactos para reproducir el fallo contra `127.0.0.1` (qué escribir en el formulario o qué petición enviar) y qué se observa en cada versión.
5. **Prueba** en `tests/test_$ARGUMENTS.py`: el mismo intento contra las dos versiones locales. Debe pasar en la insegura (el fallo ocurre) y ser rechazado en la segura (la corrección lo cierra). Ver "Pruebas" en CLAUDE.md.
6. **Ficha para estudiantes** en `docs/vulns/$ARGUMENTS.md`. _Formato pendiente: ver "Decisiones pendientes" en CLAUDE.md._
7. Pide al subagente `auditor-seguridad` que revise las dos versiones y corrige lo que encuentre.
8. Ejecuta las verificaciones de la sección "Comandos" de CLAUDE.md (con `rtk`) hasta que pasen.
9. Agrega la entrada en `Bitacora.md` arriba de todo y haz el commit (`rtk git add`, `rtk git commit`).
10. Resume qué archivos cambiaron y cómo probarlo.
