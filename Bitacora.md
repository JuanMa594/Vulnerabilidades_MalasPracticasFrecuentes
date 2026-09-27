# Bitácora del proyecto

Registro de lo que se hace en cada sesión, por qué se hizo así y qué queda pendiente.
**Las entradas nuevas van arriba de todo: lo más reciente se lee primero.**

---

## 2026-09-27 · Sesión 9: V02 (inyección de código) en la app insegura

- Ruta `/v02`: calculadora de descuentos que hace `eval()` de la fórmula del usuario
  (`# VULNERABLE V02`, `# noqa: S307`). Plantilla `v02.html` con formulario y resultado.
- Demo: `1000 * 0.9` calcula; `__import__('subprocess').check_output(['id'])` ejecuta un comando
  del sistema y muestra su salida. ruff y ty pasan.

---

## 2026-09-27 · Sesión 8: V04 (SQL Injection) en la app insegura

### Qué se hizo

- Ruta `/v04` en `inseguro/app.py`: buscador de productos por nombre. La consulta se arma con
  f-string pegando el texto del usuario (`# VULNERABLE V04 ... # noqa: S608`).
- Plantilla `templates/v04.html`: formulario, la **consulta SQL que ejecutó el backend** (para que
  se vea el ataque) y la tabla de resultados o el error crudo.
- Se agregó el ayudante `conectar()` (primera vez que se usa la base de datos) y estilos de tabla.
- La tarjeta V04 del inicio quedó activa.

### Cómo se demuestra en clase

1. Buscar `martillo` → devuelve solo ese producto.
2. Buscar `' OR '1'='1` → devuelve **todo** el inventario: el texto cambió la consulta.
3. La página muestra el SQL real ejecutado, así se ve por qué pasó.

### Detalle de la regla

`ruff` marca la línea con `S608` (SQL armado con texto). Como el fallo es **intencional**, se silencia
solo esa línea con `# noqa: S608`; así ruff sigue avisando de cualquier SQL inseguro que NO sea parte
de la lección. En la versión segura estará prohibido el `# noqa`.

### Pendiente

- Verificar con `docker compose up` que el ataque funciona de verdad (aún solo validado con ruff/ty
  y `compose config`).
- Faltan en la app insegura: V02, V03, V05, V06, V07, V08, V09.

---

## 2026-09-27 · Sesión 7: base de la app insegura + V01

### Qué se hizo

Empieza la construcción. Se resolvieron las decisiones que faltaban y se levantó la base de la app
insegura.

**Decisiones que la instrucción "compose aparte" dejó resueltas** (en [CLAUDE.md](CLAUDE.md)):
- Base de datos: **una por app**. Cada versión trae su propia Postgres en su propio `compose.yml`.
- `src/` se eliminó; el `pyproject.toml` de la raíz pasó a ser no-paquete, solo dependencias y
  herramientas compartidas (Flask, psycopg, ruff, ty, pytest).
- **Dominio: inventario de una ferretería** ("Ferretería El Tornillo"), a pedido del usuario: tablas
  `productos` (precio y stock editables), `movimientos` y `usuarios`. Da una app real donde viven
  las vulnerabilidades.
- **ACID solo en la versión segura**: la segura registrará cada cambio de stock como un `movimiento`
  dentro de una transacción; la insegura lo hará sin transacción. Contraste = lección extra
  (candidata a `V10`).

**Archivos nuevos** (`inseguro/`): `app.py` (home + catálogo de demos), `templates/` (base + index),
`static/css/estilo.css`, `static/js/app.js`, `db/init.sql` (ferretería con datos de ejemplo),
`Dockerfile`, `compose.yml` (Flask + Postgres + pgAdmin, todo en `127.0.0.1`), `.env.example`.
También `.dockerignore` en la raíz.

**V01 (sin guardia `__main__`)**: `inseguro/app.py` llama a `app.run()` en el nivel superior, sin
`if __name__ == "__main__":`. Importar el módulo arranca el servidor. Marcado `# VULNERABLE V01`.

### Por qué así, decisiones técnicas

- **Bind `0.0.0.0` sin que ruff se queje.** ruff marca el literal `"0.0.0.0"` (regla S104). Pero
  dentro del contenedor ese bind es correcto (es la red interna de Docker). Solución sin `# noqa`:
  el código usa `host=os.environ.get("HOST", "127.0.0.1")` (literal seguro) y el `0.0.0.0` se pasa
  como variable de entorno desde el `compose.yml`, donde ruff no lo ve.
- **Docker con uv.** Cada `Dockerfile` usa el contexto de build en la raíz (`context: ..`) para
  copiar `pyproject.toml` y `uv.lock`, corre `uv sync --frozen --no-dev` y luego copia el código de
  su app. Así las dos apps comparten las mismas versiones de dependencias.
- **Contención.** Postgres no publica puertos; Flask y pgAdmin solo en `127.0.0.1`; la app corre
  como usuario `app`, no root.
- **La regla `deny` de `.env` funcionó.** Al intentar `cp .env.example .env`, el permiso `deny` de
  Claude lo bloqueó (V03 aplicada a Claude). El `.env` lo crea la persona, no Claude.

### Cómo probar la base

```bash
cp inseguro/.env.example inseguro/.env
rtk docker compose -f inseguro/compose.yml up --build
# abrir http://127.0.0.1:8001  (pgAdmin en http://127.0.0.1:5051)
```
Verificado sin levantar: ruff y ty pasan; `docker compose config` valida. Falta la prueba real de
`up` (bajar imágenes `postgres:18` y `dpage/pgadmin4:9.8`; si algún tag no existe, ajustarlo).

### Pendiente

- Construir el resto de vulnerabilidades en la app insegura: V02, V03, V04, V05, V06, V07, V08, V09
  (un commit por cada una).
- Después: duplicar en `seguro/` y corregir. Formato de fichas en `docs/vulns/` sigue pendiente.

---

## 2026-09-27 · Sesión 6: frontend — HTML + CSS + JS servido por Flask

### Qué se hizo

- Decisión de frontend: **HTML + CSS + JS**, servido por el mismo Flask con plantillas Jinja, sin
  app aparte ni build. En [CLAUDE.md](CLAUDE.md) pasó a "Decisiones tomadas" con tres condiciones.
- Sigue sin escribirse código: solo se registró la decisión.

### Por qué así, y la condición que se le puso

El usuario quería HTML+CSS+JS y se eligió eso. Pero como la clase es de **Python** y las nueve
vulnerabilidades (V01–V09) son de backend, el frontend no es donde se enseña: es la ventana para
*ver* lo que hace Python. Por eso se le pusieron condiciones para que ayude en vez de estorbar:

1. **Mostrar el ciclo.** Cada pantalla tiene un formulario y un área con el resultado crudo del
   backend, para que el estudiante escriba (por ejemplo) `' OR 1=1 --` y vea qué hizo Python.
2. **El JS no valida la lección.** Los fallos se demuestran atacando al backend; si el JS filtrara
   el payload, taparía el fallo. (Además, "confiar en la validación del cliente" está fuera de
   alcance justamente por esto.)
3. **HTML/CSS/JS iguales en las dos versiones.** Así la única diferencia entre `inseguro/` y
   `seguro/` sigue siendo el código Python, y `git diff` lo deja ver de una.

### Pendiente

- Última decisión de la Lección 1: base de datos, ¿una Postgres compartida (un esquema por versión)
  o una por app? Recomendación: una compartida con dos esquemas.
- Después de eso: qué hacer con `src/` y `pyproject.toml`, y el formato de las fichas.

---

## 2026-09-27 · Sesión 5: backend elegido — Flask

### Qué se hizo

- Se decidió el backend: **Flask**. En [CLAUDE.md](CLAUDE.md) pasó de la lista de pendientes a una
  nueva sección **"Decisiones tomadas"**, y el Stack ya lo nombra.
- Todavía no se instaló ni se escribió código: solo se registró la decisión, como se acordó.

### Por qué Flask

Para enseñar, lo que importa es que el fallo se vea de un vistazo. En Flask una ruta y su consulta a
la base de datos caben en el mismo archivo, sin capas intermedias que oculten dónde está el problema.
FastAPI habría metido async, validación con Pydantic e inyección de dependencias: bueno para
producción, pero ruido para alguien que recién aprende a programar. La regla del proyecto es "código
simple y explícito antes que elegante", y Flask encaja con eso.

### Pendiente

- Siguiente decisión sugerida: frontend. Lo natural con Flask es servir plantillas Jinja desde el
  mismo backend; así no hay una segunda app que mantener y el foco queda en el fallo, no en el front.
- Instalar Flask (`rtk uv add flask`) queda para cuando se dé la orden de empezar a construir.

---

## 2026-09-27 · Sesión 4: cómo enseña la demo (lado a lado + comprobación)

### Qué se hizo

- En [CLAUDE.md](CLAUDE.md) se agregaron dos secciones:
  - **"Cómo enseña la demo"**: el mismo servicio corre dos veces a la vez, la versión insegura y la
    segura, en puertos distintos de `127.0.0.1`. Para cada `Vxx` la clase hace tres pasos: explotar
    en la insegura, repetir lo mismo en la segura (ya no funciona) y comparar los dos códigos.
  - **"Pruebas"**: cada `Vxx` tiene una prueba que corre el mismo intento contra las dos versiones;
    debe funcionar en la insegura y fallar en la segura.
- Se agregó `tests/` a la estructura planeada.
- El skill `/nueva-vulnerabilidad` ahora incluye un paso para crear esa prueba comparativa.

### Por qué así

**La comprobación es la lección, no un adorno.** Enseñar solo la versión arreglada obliga al
estudiante a creer que ya está bien. Al repetir el mismo ataque contra la versión segura y verlo
fallar, la corrección se demuestra en vez de afirmarse. Por eso la prueba de cada `Vxx` afirma las
dos cosas: en la insegura el intento **funciona** (si dejara de funcionar, el ejemplo se rompió) y
en la segura **falla** (si funcionara, el arreglo no sirve).

**Mismo servicio, dos puertos.** Las dos versiones comparten pantallas y rutas para que la única
diferencia visible sea el comportamiento ante el ataque, y la única diferencia en el código sea la
línea corregida (`git diff --no-index inseguro seguro`).

**Sigue siendo todo local.** Los dos puertos se publican en `127.0.0.1` y las pruebas solo apuntan a
los contenedores de este proyecto: la Sesión 3 se mantiene sin excepciones.

### Pendiente

- Elegir backend (Sesión 1) para poder escribir la primera prueba comparativa real.
- Decidir con qué se corren las pruebas: `pytest` es lo previsto en los permisos de `settings.json`.

---

## 2026-09-27 · Sesión 3: la demo nunca sale de esta máquina

### Qué se hizo

- En [CLAUDE.md](CLAUDE.md), la primera regla de oro ahora es **"Solo local, sin excepciones"**:
  nada del proyecto se expone a internet ni a la red local. Enumera lo prohibido (`network_mode: host`,
  nube, túneles, reenvíos de puertos, firewall) y ordena a Claude detenerse y avisar si una petición
  lo requiere.
- En [.claude/rules/docker.md](.claude/rules/docker.md) se agregaron las reglas técnicas: puertos solo en
  `127.0.0.1`, Postgres sin puertos publicados y `network_mode: host` prohibido.
- En [.claude/agents/auditor-seguridad.md](.claude/agents/auditor-seguridad.md), cualquier exposición a
  la red cuenta como ❌ aunque todo lo demás esté bien.

### Por qué así

**La app insegura permite ejecutar código** (V02, V05). Si alguien de la red pudiera alcanzarla,
tendría una puerta abierta a esta máquina. Por eso la regla no admite excepciones: ni siquiera "solo
un momento para mostrarlo en clase".

**`127.0.0.1` y `0.0.0.0` significan cosas distintas según dónde se usen:**

| Dónde | Qué se pone | Por qué |
|---|---|---|
| En el host, en `ports:` del `compose.yml` | `127.0.0.1:8001:8000` | Solo esta máquina puede entrar |
| Dentro del contenedor, donde escucha la app | `0.0.0.0` | Es la red interna de Docker; con `127.0.0.1` ni Docker podría llegar a la app |

Es un error frecuente: se ve `0.0.0.0` dentro del contenedor y se cree que la app está expuesta, o se
escribe `"8001:8000"` en `ports:` sin saber que eso la publica en todas las interfaces.

**Postgres sin puertos.** Ni pgAdmin ni las apps necesitan que Postgres esté publicado en el host:
lo alcanzan por la red interna de Docker. Un puerto que no se publica no se puede exponer por error.

### Pendiente

- Cuando exista `compose.yml`, agregar a "Comandos" una verificación que falle si algún puerto no
  está en `127.0.0.1`, y comprobar desde otra máquina que no se ve nada.
- Candidato para la lección de hooks: bloquear automáticamente un `compose.yml` que publique
  puertos fuera de `127.0.0.1`.

---

## 2026-09-27 · Sesión 2: reglas obligatorias (RTK, commits, uv, ruff, ty)

### Qué se hizo

- En [CLAUDE.md](CLAUDE.md) se agregó la sección **Flujo de trabajo (obligatorio)**:
  - RTK en todo comando;
  - uv como único gestor de Python;
  - ruff y ty como únicas herramientas de calidad;
  - commit de cada avance;
  - esta bitácora con lo más reciente arriba.
- Se instalaron ruff y ty como dependencias de desarrollo (`rtk uv add --dev ruff ty`). Quedaron en
  `pyproject.toml`, en el grupo `dev`, y sus versiones exactas en `uv.lock`: ruff 0.16.9 y ty 0.0.84.
- Se configuró ruff en `pyproject.toml` con reglas de seguridad (`S`) y de bugs frecuentes (`B`).
- Se completó la sección **Comandos** de `CLAUDE.md` con las tres verificaciones previas a cada commit.
- Se creó `.gitattributes` para que todo archivo de texto use finales de línea LF.
- Primer commit del repositorio.

### Por qué así

**RTK obliga a trabajar en WSL.** En esta máquina rtk, docker y git están en WSL; en Windows no
hay Docker. Por eso todo comando del proyecto pasa por `wsl zsh -ic "cd ... && rtk <comando>"`.
Esa forma de llamarlo depende de esta máquina, así que va en [CLAUDE.local.md](CLAUDE.local.md).
En [CLAUDE.md](CLAUDE.md), que se comparte, solo queda la regla general: "usar rtk".

**La orden se repitió en los archivos que podían contradecirla.**

| Archivo | Qué se ajustó |
|---|---|
| `CLAUDE.local.md` | Se carga junto a `CLAUDE.md` y podía contradecirlo; ahora repite que rtk es obligatorio y dice cómo llamarlo en esta máquina |
| `skills/nueva-vulnerabilidad` | Terminaba sin commit. Ahora sus últimos pasos son verificar con ruff y ty, anotar en la bitácora y hacer el commit |
| `settings.json` | Los permisos se escribieron con el prefijo `rtk` y se prohibieron `pip` y `poetry` |
| `rules/codigo-inseguro.md` | Las reglas `S` de ruff marcan los fallos intencionales; se silencian solo en su línea con `# noqa: <regla>` |
| `rules/codigo-seguro.md` | Prohibido `# noqa`: la versión segura debe pasar ruff sin excepciones |

**ruff como herramienta docente.** Con las reglas `S`, ruff detecta solo varios fallos del
catálogo (`eval`, `pickle`, SQL armado con texto, `except: pass`…). En `inseguro/` cada fallo
intencional lleva su `# noqa`, así cualquier otro fallo sigue saliendo como error. En `seguro/`
ruff tiene que pasar limpio. Se les puede mostrar a los estudiantes que una herramienta gratuita
ya detectaba el problema.

**`rtk ruff` directo no sirve.** ruff está instalado dentro del entorno del proyecto (`.venv`) y
no en el sistema. La forma correcta es `rtk uv run ruff ...`.

### Límite que conviene conocer

Las reglas de `settings.json` comparan el texto del comando. En esta máquina todo va dentro de
`wsl zsh -ic "..."`, así que esas reglas no coinciden aquí: lo que guía a Claude es `CLAUDE.md`.
La forma de *obligar* de verdad, para Claude y para cualquier persona, es un hook que ejecute ruff
y ty automáticamente. Queda para una próxima lección.

### Pendiente

- Todo lo pendiente de la Sesión 1 (Lección 1: decisiones pendientes en `CLAUDE.md`).
- Próxima lección posible: hooks para que ruff y ty se ejecuten solos.

---

## 2026-09-27 · Sesión 1: estructura de Claude Code

### Qué se hizo

A partir de `idea_ethical_hacking.txt` se creó la configuración de Claude Code del proyecto.
Todavía no hay código de la aplicación: primero se definen las reglas y después se construye.

```text
Vulnerabilidades_MalasPracticasFrecuentes/
├── CLAUDE.md                          ← se sube a git (lo comparte todo el equipo)
├── CLAUDE.local.md                    ← solo mío (está en .gitignore)
├── Bitacora.md                        ← este archivo
└── .claude/
    ├── settings.json                  ← permisos de Claude
    ├── rules/
    │   ├── codigo-inseguro.md         ← se carga al trabajar en inseguro/**
    │   ├── codigo-seguro.md           ← se carga al trabajar en seguro/**
    │   └── docker.md                  ← se carga con Dockerfile y compose*.yml
    ├── skills/nueva-vulnerabilidad/
    │   └── SKILL.md                   ← se usa con /nueva-vulnerabilidad V04
    └── agents/
        └── auditor-seguridad.md       ← subagente revisor, sin permiso para editar
```

También se agregaron al `.gitignore`: `CLAUDE.local.md`, `.claude/settings.local.json` y `.env`.

### Qué es cada pieza y cómo se llena

**[CLAUDE.md](CLAUDE.md)**: Claude lo lee al iniciar cada sesión. Va solo lo que no se puede
deducir leyendo el código: para qué es el proyecto, para quién es, las reglas que nunca se
rompen y lo que falta decidir. Se llenó con lo del `.txt`, incluido el catálogo V01–V09. Cada
vulnerabilidad tiene un código `Vxx` para que código, comentarios y fichas usen el mismo nombre.

> Regla práctica: si una línea no cambiaría lo que hace Claude, sobra. Todo lo que está aquí
> ocupa contexto en cada sesión.

**[CLAUDE.local.md](CLAUDE.local.md)**: funciona igual que `CLAUDE.md`, pero es solo mío y no se
sube a git. Sirve para datos de mi máquina, fechas de clase o qué vulnerabilidad toca en cada sesión.

**[.claude/rules/](.claude/rules/)**: reglas por tema. La cabecera `paths:` hace que cada regla
se cargue solo cuando Claude toca esos archivos, así las reglas de Docker no ocupan contexto
mientras se programa en Python. El código inseguro y el seguro tienen reglas separadas porque en
esta demo se contradicen: en una carpeta los fallos se dejan a propósito y en la otra se prohíben.

```markdown
---
paths:
  - "inseguro/**"
---
# Aquí van las reglas, en texto normal
```

**[.claude/settings.json](.claude/settings.json)** tiene tres listas de permisos:

| Lista | Significado | Ejemplos en este proyecto |
|---|---|---|
| `allow` | Claude lo ejecuta sin preguntar | ver logs, `uv sync`, correr tests |
| `ask` | Claude siempre pide permiso | `docker compose down` (con `-v` borra la base de datos), `git push` |
| `deny` | Claude no puede hacerlo | leer o editar `.env` (la lección V03 aplicada a Claude) |

La línea `$schema` le da autocompletado a VS Code al editar el archivo.
`settings.local.json` se crea solo cuando apruebo un permiso con "no volver a preguntar"; es
personal y no se sube.

**[.claude/skills/nueva-vulnerabilidad/SKILL.md](.claude/skills/nueva-vulnerabilidad/SKILL.md)**:
guarda un flujo que se va a repetir nueve veces: versión insegura, versión segura, cómo
explotarla, ficha para estudiantes y revisión. Detalles de la cabecera:

- `$ARGUMENTS` se reemplaza por lo que escriba después del comando (`/nueva-vulnerabilidad V04` → `V04`).
- `disable-model-invocation: true`: el skill solo se ejecuta cuando yo lo llamo; Claude no lo lanza solo.
- `argument-hint`: el texto de ayuda que aparece al escribir el comando.

**[.claude/agents/auditor-seguridad.md](.claude/agents/auditor-seguridad.md)**: un revisor con
contexto propio. Con `tools: Read, Grep, Glob` puede leer pero no modificar nada. Como no tiene
`model:`, usa el mismo modelo que la sesión; se puede fijar otro, por ejemplo `model: sonnet`.

### Cómo se crea cada pieza

No hay un comando que cree toda la estructura. `/init` solo genera `CLAUDE.md`, y en este
proyecto no se usó porque analiza el código y todavía no hay código.

| Pieza | Cómo se crea |
|---|---|
| `CLAUDE.md` | `/init` o a mano |
| `CLAUDE.local.md` | A mano |
| `.mcp.json` | `claude mcp add <nombre> --scope project ...` o con `/mcp` |
| `.claude/settings.json` | `/permissions`, `/config` o a mano |
| `.claude/settings.local.json` | Se crea solo al aprobar un permiso con "no volver a preguntar" |
| `.claude/rules/*.md` | A mano |
| `.claude/skills/<nombre>/SKILL.md` | A mano |
| `.claude/agents/*.md` | `/agents` (asistente guiado) o a mano |
| hooks | `/hooks`; se guardan en `settings.json`. La carpeta `.claude/hooks/` es solo una convención para los scripts |

### Lo que no se creó todavía, y por qué

- **`.mcp.json`**: conecta Claude a servicios externos. Tendrá sentido cuando Postgres esté funcionando.
- **Hooks**: necesitan comandos reales, como un formateador, y todavía no hay código.
- **`.claude/commands/`**: es el formato antiguo; los skills lo reemplazan.

Crear carpetas vacías "para tener orden" resta en lugar de sumar: cada pieza se agrega cuando
hace falta de verdad.

### Por confirmar

- En `CLAUDE.md` quedaron fuera de alcance el punto 9 del `.txt` (confiar en validación del lado
  del cliente) y el 10 (paquetes maliciosos). Así se interpretó la frase "ni confiar en
  validaciones que yo mismo no haya creado". Si la idea era excluir solo el 10, hay que corregirlo.

### Tarea: Lección 1

1. Completar **Decisiones pendientes** en [CLAUDE.md](CLAUDE.md):
   - [ ] Backend: ¿Flask, FastAPI u otro?
   - [ ] Frontend: ¿plantillas HTML servidas por el backend, o una app aparte?
   - [ ] Base de datos: ¿una compartida por las dos apps, o una para cada una?
   - [ ] ¿Qué hacer con `src/` y `pyproject.toml` que creó `uv init`?
   - [ ] Formato de las fichas para estudiantes en `docs/vulns/`
2. Abrir una conversación nueva (`CLAUDE.md` se lee al iniciar) y escribir `/memory` para ver qué archivos cargó.
3. Escribir `/` y comprobar que aparece `/nueva-vulnerabilidad`; con `/agents`, que aparece `auditor-seguridad`.

### Próxima sesión

- Lección 2: completar la sección **Comandos** de `CLAUDE.md` y definir el formato de la ficha para estudiantes.
- Todavía no hay ningún commit en el repositorio.
