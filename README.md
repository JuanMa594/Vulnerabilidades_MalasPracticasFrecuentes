# Vulnerabilidades y malas prácticas frecuentes

Proyecto educativo para aprender, con una aplicación de ejemplo, cómo se manifiestan algunas
vulnerabilidades y errores comunes de programación y cómo prevenirlos.

> **Advertencia:** la versión de `inseguro/` contiene fallos intencionales. Úsala solo para
> aprendizaje en esta máquina. No la publiques ni la conectes a redes externas. Los datos y las
> credenciales incluidos son ficticios.

## Cómo funciona

El proyecto levanta dos versiones de una tienda de ferretería en paralelo. Ambas muestran las
mismas pantallas y lecciones, pero cada una tiene su propia base de datos:

| Versión | Aplicación | pgAdmin | Propósito |
|---|---|---|---|
| Insegura | <http://127.0.0.1:8011> | <http://127.0.0.1:5051> | Demuestra los fallos intencionales |
| Segura | <http://127.0.0.1:8012> | <http://127.0.0.1:5052> | Muestra las correcciones |

En cada lección, observa el comportamiento de ambas versiones y compara sus implementaciones:

```powershell
rtk git diff --no-index inseguro/app.py seguro/app.py
```

## Lecciones

| Código | Tema |
|---|---|
| V01 | Ejecutar el servidor al importar el módulo; guardia `__main__` |
| V02 | Inyección de código y comandos |
| V03 | Secretos escritos en el código |
| V04 | Inyección SQL |
| V05 | Deserialización insegura |
| V06 | Path traversal |
| V07 | Manejo demasiado amplio de excepciones |
| V08 | Valores mutables por defecto |
| V09 | Comparaciones inseguras |

## Requisitos

- Docker con Docker Compose.
- [RTK](https://github.com/rtk-ai/rtk) para ejecutar los comandos del proyecto.
- Python 3.14 y [uv](https://docs.astral.sh/uv/) si vas a trabajar en el código fuera de Docker.

## Stack del aplicativo

| Capa | Tecnología |
|---|---|
| Lenguaje y runtime | Python 3.14 |
| Backend | Flask 3.1 o superior |
| Base de datos | PostgreSQL 18 |
| Acceso a PostgreSQL | Psycopg 3.2 o superior (`psycopg[binary]`) |
| Interfaz | HTML, CSS y JavaScript |
| Plantillas | Jinja, integradas con Flask |
| Administración de base de datos | pgAdmin 4 (imagen `dpage/pgadmin4:9.8`) |
| Contenedores y servicios | Docker y Docker Compose |
| Dependencias de Python | uv; versiones fijadas en `uv.lock` |
| Calidad y pruebas de desarrollo | Ruff (formato y lint), ty (tipos) y pytest |

Cada versión de la aplicación usa el mismo stack, pero se ejecuta en contenedores y con una base de
datos independiente. Flask también sirve la interfaz: no hay una aplicación frontend ni un proceso
de compilación separado.

## Iniciar la demo

No necesitas crear un archivo `.env`: Compose usa valores predeterminados ficticios.
Ejecuta cada comando desde la raíz del repositorio:

```powershell
rtk docker compose -f inseguro/compose.yml up -d --build
rtk docker compose -f seguro/compose.yml up -d --build
```

Abre la lección en la versión insegura y repite la misma acción en la versión segura. Los puertos
de PostgreSQL no se publican en el equipo; cada base de datos solo es accesible desde su red interna
de Docker.

### pgAdmin

Las credenciales predeterminadas de pgAdmin son ficticias:

- Correo: `admin@ferreteria.com`
- Contraseña: `pgadmin_de_demo`

Para conectar pgAdmin a la base de datos de su versión, usa el host `db`, el puerto `5432`, la base
`demo`, el usuario `demo` y la contraseña `clave_de_demo`.

### Detener la demo

```powershell
rtk docker compose -f inseguro/compose.yml down
rtk docker compose -f seguro/compose.yml down
```

Para borrar también los datos persistidos de una versión, agrega `-v` a su comando `down`.

### Si un puerto está ocupado

Puedes cambiar los puertos sin editar los archivos. Por ejemplo, en PowerShell:

```powershell
$env:PUERTO_WEB = "8031"
rtk docker compose -f inseguro/compose.yml up -d --build
```

Los puertos publicados siguen ligados a `127.0.0.1`; **no los expongas a la red local ni a
Internet**.

## Desarrollo

Instala las dependencias del proyecto y ejecuta las comprobaciones configuradas:

```powershell
rtk uv sync
rtk uv run ruff format .
rtk uv run ruff check .
rtk uv run ty check
```

## Estructura

```text
inseguro/       App vulnerable: app.py, templates/, static/, db/, Dockerfile, compose.yml
seguro/         App corregida: app.py, templates/, static/, db/, Dockerfile, compose.yml
pyproject.toml  Dependencias y herramientas compartidas
uv.lock         Versiones bloqueadas de las dependencias
Bitacora.md     Registro de avances del proyecto
```