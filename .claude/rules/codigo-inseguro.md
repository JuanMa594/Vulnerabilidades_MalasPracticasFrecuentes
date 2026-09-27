---
paths:
  - "inseguro/**"
---

# Código de la app insegura

Los fallos de esta carpeta son intencionales: son el material de clase.

- Cada fallo lleva un comentario justo encima:
  `# VULNERABLE V04 (SQL Injection): la consulta se arma con el texto del usuario.`
- Un fallo por función o ruta, y solo el que indica el catálogo de CLAUDE.md. Si encuentras un fallo que no está marcado, avisa en vez de dejarlo o corregirlo.
- El fallo debe verse a simple vista: nada de esconderlo en funciones auxiliares.
- Si ruff detecta el fallo, silencia solo esa regla y solo en esa línea (`# noqa: S608`). Así ruff sigue avisando de cualquier fallo que no sea intencional.
- Lo que no forma parte de la lección se escribe bien, igual que en `seguro/`.
