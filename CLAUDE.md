# Vulnerabilidades y malas prácticas frecuentes

Proyecto docente para un curso de introducción a la ciberseguridad. Muestra una aplicación
**vulnerable a propósito** y su versión **corregida**, para que los estudiantes vean cómo se
explota cada mala práctica y cómo se arregla. La idea original está en `idea_ethical_hacking.txt`.

## Público y tono
- Estudiantes que están aprendiendo a programar: nivel introductorio.
- Código, comentarios, interfaz y documentación en español.
- Código simple y explícito antes que elegante: debe entenderse leyéndolo una vez.

## Reglas de oro
- **Solo local, sin excepciones.** La demo emula el entorno en esta máquina: nada del proyecto se expone a internet ni a la red local.
  - Los puertos se publican solo en `127.0.0.1` (`"127.0.0.1:8001:8000"`), nunca en todas las interfaces.
  - Prohibido: `network_mode: host`, subir la demo a la nube o a un servidor, túneles (ngrok, cloudflared…), reenvíos de puertos (`netsh interface portproxy`) y reglas de firewall que abran puertos.
  - Si una petición requiere exponer algo, detente y avisa en lugar de hacerlo: ningún motivo lo justifica.
- Todos los secretos del proyecto son falsos y lo dicen (`sk-FALSO-...`, `clave_de_demo`).
- Todo lo que aparece en la demo lo escribimos nosotros: nada de paquetes, payloads ni herramientas de terceros.
- Los ataques de ejemplo solo apuntan a los contenedores de este proyecto.
- No corrijas código dentro de `inseguro/` salvo que se pida: los fallos son intencionales.

## Flujo de trabajo (obligatorio)
- **RTK**: todo comando de terminal lleva el prefijo `rtk` (`rtk git status`, `rtk docker compose ps`). Si rtk no tiene filtro para un comando, lo ejecuta tal cual.
- **uv** es el único gestor de Python: `rtk uv add`, `rtk uv sync`, `rtk uv run`. Prohibido `pip`, `poetry`, `pipenv`, `conda` y `python -m venv`.
- **ruff** formatea y revisa el código; **ty** revisa los tipos. No se usan black, isort, flake8, pylint ni mypy.
- **Commits**: cada avance que funciona se commitea sin esperar a que se pida, después de pasar las verificaciones de "Comandos". Un avance por commit, mensaje en español y en imperativo (`Agrega V04 en ambas versiones`). `git push` solo si se pide.
- **Bitácora**: cada avance se registra en `Bitacora.md`. La entrada nueva va arriba de todo, debajo del encabezado: lo más reciente se lee primero.

## Stack
- Python 3.14 · uv (entornos y dependencias) · ruff (formato y lint) · ty (tipos)
- PostgreSQL + pgAdmin 4
- Backend: **Flask**
- Frontend: _pendiente_
- Docker: un `Dockerfile` por app y un `compose.yml` en la raíz

## Cómo enseña la demo
Es una app real, no fragmentos sueltos. El mismo servicio corre **dos veces al mismo tiempo**, en
puertos distintos de `127.0.0.1`:

- **Versión insegura** (p. ej. `127.0.0.1:8001`): tiene los fallos del catálogo a propósito.
- **Versión segura** (p. ej. `127.0.0.1:8002`): mismas pantallas y mismas rutas, con las buenas prácticas.

Para cada vulnerabilidad, la clase sigue tres pasos:
1. **Se explota en la versión insegura** y se ve el daño (leer datos ajenos, ejecutar un comando, etc.).
2. **Se repite exactamente lo mismo contra la versión segura** y ya no funciona.
3. Se comparan los dos códigos (`git diff --no-index inseguro seguro`) para ver qué línea cambió.

El paso 2 es lo importante: el estudiante ve que la misma acción falla, no le pedimos que confíe en
que "ahora está arreglado". Esa comprobación se guarda como una prueba automatizada (ver "Pruebas").

## Pruebas
Cada vulnerabilidad `Vxx` tiene una prueba que corre el mismo intento contra las dos versiones:
- contra la insegura **debe funcionar** (si dejara de funcionar, el ejemplo se rompió);
- contra la segura **debe fallar** (si funcionara, la corrección no sirve).

Así, una sola orden demuestra ante la clase que cada arreglo cierra de verdad su fallo. Las pruebas
solo apuntan a los contenedores locales de este proyecto.

## Estructura (planeada, aún no existe)
```text
inseguro/        app vulnerable a propósito, con su Dockerfile
seguro/          la misma app corregida: mismos archivos, funciones y rutas
docs/vulns/      una ficha por vulnerabilidad para los estudiantes
tests/           una prueba por Vxx: funciona en inseguro, falla en seguro
compose.yml      postgres, pgadmin, app insegura y app segura (todo en 127.0.0.1)
.env.example     variables necesarias, sin valores reales
```

## Catálogo de vulnerabilidades
El código `Vxx` se usa en comentarios, rutas y documentos.

| Código | Tema | Tipo | Inseguro | Seguro |
|---|---|---|---|---|
| V01 | Sin `if __name__ == "__main__"` | Mala práctica | código que se ejecuta al importar | guardia `__main__` |
| V02 | Inyección de código/comandos | Seguridad | `eval`, `exec`, `os.system` con input | `ast.literal_eval`, `subprocess` con lista |
| V03 | Secretos en el código | Seguridad | `API_KEY = "..."` | variables de entorno, `.env` fuera de git |
| V04 | SQL Injection | Seguridad | f-string en la consulta | consulta parametrizada |
| V05 | Deserialización insegura | Seguridad | `pickle.loads` con datos del usuario | `json` |
| V06 | Path traversal | Seguridad | `open(f"/archivos/{nombre}")` | normalizar y validar la ruta |
| V07 | `except` demasiado amplio | Mala práctica | `except: pass` | excepciones específicas |
| V08 | Mutable por defecto | Bug | `def f(x, lista=[])` | `lista=None` |
| V09 | Comparaciones inseguras | Seguridad | `==` con tokens, `is` con strings | `hmac.compare_digest`, `==` |

Fuera de alcance: paquetes maliciosos (supply chain) y confiar en validación del lado del cliente.

## Comandos
```bash
rtk uv sync                  # instala dependencias
rtk uv run ruff format .     # formatea
rtk uv run ruff check .      # lint y reglas de seguridad
rtk uv run ty check          # tipos
```
Los tres últimos deben pasar antes de cada commit. `rtk ruff` directo no sirve: ruff vive en el entorno del proyecto.
Los comandos de Docker se agregan cuando exista `compose.yml`.

## Decisiones tomadas
- **Backend: Flask.** Framework mínimo: las rutas y las consultas se ven en el mismo archivo, sin capas que escondan el fallo. Ideal para nivel introductorio.

## Decisiones pendientes
No tomes estas decisiones por tu cuenta: pregunta.
- [ ] Frontend: ¿plantillas HTML servidas por Flask (Jinja), o una app aparte?
- [ ] Base de datos: ¿una compartida por las dos apps, o una para cada una?
- [ ] ¿Qué hacemos con `src/` y `pyproject.toml` que creó `uv init`?
- [ ] Formato de las fichas para estudiantes en `docs/vulns/`
