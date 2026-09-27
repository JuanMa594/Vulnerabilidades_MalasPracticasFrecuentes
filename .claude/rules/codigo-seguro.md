---
paths:
  - "seguro/**"
---

# Código de la app segura

Es la versión que los estudiantes deben imitar.

- Mismos archivos, funciones y rutas que en `inseguro/`, para que `git diff --no-index inseguro seguro` muestre solo las correcciones.
- Cada corrección lleva un comentario:
  `# SEGURO V04: consulta parametrizada; el driver separa el dato de la instrucción SQL.`
- Sin secretos en el código: todo sale de variables de entorno.
- Prohibido `# noqa`: si ruff o ty marcan algo, se corrige.
- Si la corrección cambia algo visible (un mensaje de error, un código HTTP), explícalo en el comentario.
