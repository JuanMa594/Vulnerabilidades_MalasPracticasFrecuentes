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
- Frontend: **HTML + CSS + JS**, servido por el mismo Flask (plantillas Jinja); sin app aparte
- Docker: un `Dockerfile` por app y un `compose.yml` en la raíz

## Cómo enseña la demo
Es una app real, no fragmentos sueltos. El mismo servicio corre **dos veces al mismo tiempo**, en
puertos distintos de `127.0.0.1`:

- **Versión insegura** (`127.0.0.1:8011`): tiene los fallos del catálogo a propósito.
- **Versión segura** (`127.0.0.1:8012`): mismas pantallas y mismas rutas, con las buenas prácticas.

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

## Estructura
```text
inseguro/        app vulnerable a propósito
  app.py         Flask: rutas y consultas a la vista
  templates/     HTML (Jinja)
  static/        CSS y JS
  db/init.sql    tabla y datos de ejemplo
  Dockerfile
  compose.yml    su Flask + su Postgres + su pgAdmin, todo en 127.0.0.1
  .env.example
seguro/          copia de inseguro/ con las buenas prácticas (mismos archivos y rutas)
docs/vulns/      una ficha por vulnerabilidad para los estudiantes
tests/           una prueba por Vxx: funciona contra inseguro, falla contra seguro
pyproject.toml   dependencias y herramientas (raíz, compartido)
```
Cada versión tiene **su propio `compose.yml`** y su propia base de datos: se levantan por separado
y no comparten nada. Puertos: inseguro Flask `8011` / pgAdmin `5051`; seguro Flask `8012` /
pgAdmin `5052` (8001 y 8002 estaban ocupados por otros proyectos de esta máquina). Postgres no
publica puertos (se llega por la red interna de Docker).

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

```bash
# Los valores por defecto (falsos) están en el compose: NO hace falta .env ni --env-file.
rtk docker compose -f inseguro/compose.yml up -d --build   # app 127.0.0.1:8011 · pgAdmin 5051
rtk docker compose -f seguro/compose.yml   up -d --build   # app 127.0.0.1:8012 · pgAdmin 5052
rtk docker compose -f inseguro/compose.yml down            # (con -v también borra la base)
```
Puertos fijos: inseguro `8011`/`5051`, seguro `8012`/`5052`. Si alguno estuviera ocupado, se
cambia sin editar nada: `PUERTO_WEB=8031 rtk docker compose -f inseguro/compose.yml up -d`.

## Decisiones tomadas
- **Backend: Flask.** Framework mínimo: las rutas y las consultas se ven en el mismo archivo, sin capas que escondan el fallo. Ideal para nivel introductorio.
- **Frontend: HTML + CSS + JS**, servido por el mismo Flask con plantillas Jinja; sin app aparte ni build. Condiciones para que enseñe en vez de distraer:
  - Cada pantalla deja ver el ciclo petición → Python → respuesta: un formulario y un área que muestre el resultado crudo (lo que devolvió el backend), para que el estudiante vea qué hizo Python con lo que escribió.
  - El JS no valida ni filtra nada de la lección: las vulnerabilidades son del backend y se demuestran atacando al backend. Si el JS bloqueara el payload, tapa el fallo.
  - HTML, CSS y JS iguales en `inseguro/` y `seguro/`: la única diferencia entre las dos versiones sigue siendo el Python.
- **Base de datos: una por app.** Cada versión trae su propia Postgres en su `compose.yml` ("compose aparte"): quedan aisladas y una no puede afectar a la otra.
- **`src/` se eliminó.** El `pyproject.toml` de la raíz ya no es un paquete instalable: solo declara dependencias (Flask, psycopg) y herramientas (ruff, ty, pytest), compartidas por las dos apps.
- **Dominio: inventario de una ferretería** ("Ferretería El Tornillo"). Tablas `productos` (precio y stock editables), `movimientos` y `usuarios`. Da una app real donde viven las vulnerabilidades: buscar productos (V04), editar precios/stock, login (V09).
- **ACID solo en la versión segura.** La segura registra cada cambio de stock como un `movimiento` dentro de una transacción; la insegura actualiza el stock sin transacción ni registro. El contraste es una lección extra (candidata a `V10`, aún no formalizada).

## Decisiones pendientes
No tomes estas decisiones por tu cuenta: pregunta.
- [ ] Formato de las fichas para estudiantes en `docs/vulns/`
