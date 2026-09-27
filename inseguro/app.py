"""App INSEGURA — demo docente de vulnerabilidades frecuentes.

Cada ruta reproduce A PROPÓSITO un fallo del catálogo (ver CLAUDE.md). Los
comentarios `# VULNERABLE Vxx` marcan dónde está cada fallo. Este código NO es un
ejemplo de cómo programar: la versión correcta está en la carpeta `seguro/`.
"""

import os

import psycopg
from flask import Flask, render_template, request

app = Flask(__name__)


def conectar():
    """Abre una conexión a Postgres. Es infraestructura, no la lección: los datos
    de conexión salen de variables de entorno (bien), lo que falla está en las rutas."""
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


# Catálogo de demos. Cada vulnerabilidad agrega aquí su tarjeta y, más abajo, su ruta.
DEMOS = [
    {
        "codigo": "V01",
        "titulo": 'Sin if __name__ == "__main__"',
        "ruta": None,  # No es una página: es un fallo de la estructura del archivo.
        "resumen": "Importar este archivo ya arranca el servidor: falta la guardia.",
        "implementado": True,
    },
    {
        "codigo": "V02",
        "titulo": "Inyección de código / comandos",
        "ruta": "/v02",
        "resumen": "Evaluar texto del usuario con eval()/os.system().",
        "implementado": True,
    },
    {
        "codigo": "V03",
        "titulo": "Secretos en el código",
        "ruta": "/v03",
        "resumen": "Una clave escrita dentro del programa.",
        "implementado": True,
    },
    {
        "codigo": "V04",
        "titulo": "SQL Injection",
        "ruta": "/v04",
        "resumen": "Buscar productos armando la consulta con el texto del usuario.",
        "implementado": True,
    },
    {
        "codigo": "V05",
        "titulo": "Deserialización insegura",
        "ruta": None,
        "resumen": "pickle.loads() sobre datos que vienen de afuera.",
        "implementado": False,
    },
    {
        "codigo": "V06",
        "titulo": "Path traversal",
        "ruta": None,
        "resumen": "Abrir un archivo usando un nombre sin validar.",
        "implementado": False,
    },
    {
        "codigo": "V07",
        "titulo": "except demasiado amplio",
        "ruta": None,
        "resumen": "Tragarse cualquier error con except: pass.",
        "implementado": False,
    },
    {
        "codigo": "V08",
        "titulo": "Mutable por defecto",
        "ruta": None,
        "resumen": "Una lista como valor por defecto que se comparte entre llamadas.",
        "implementado": False,
    },
    {
        "codigo": "V09",
        "titulo": "Comparaciones inseguras",
        "ruta": None,
        "resumen": "Comparar tokens con == o strings con is.",
        "implementado": False,
    },
]


# VULNERABLE V03 (secreto en el código): esta clave está escrita dentro del programa.
# Cualquiera con acceso al código —o al historial de git, para siempre— la ve. Lo
# correcto es leerla de una variable de entorno (ver `seguro/app.py`).
API_KEY_PASARELA = "sk-FALSO-pagos-9c8b7a6d5e4f3210"  # noqa: S105


@app.route("/")
def index():
    return render_template("index.html", demos=DEMOS, version="insegura")


@app.route("/v03")
def v03_secreto_en_codigo():
    """V03 — 'Configuración' de la pasarela de pagos que filtra la clave del código."""
    return render_template("v03.html", api_key=API_KEY_PASARELA)


@app.route("/v04")
def v04_sql_injection():
    """V04 — Buscar productos por nombre. Escribe el ataque y míralo funcionar."""
    termino = request.args.get("q", "")
    sql = ""
    filas = []
    error = ""
    if termino:
        # VULNERABLE V04 (SQL Injection): la consulta se arma pegando el texto del
        # usuario dentro del SQL. Con   ' OR '1'='1   el buscador devuelve TODO el
        # inventario, y con   '; ...   se pueden encadenar otras órdenes.
        sql = f"SELECT * FROM productos WHERE nombre ILIKE '%{termino}%'"  # noqa: S608
        try:
            with conectar() as con, con.cursor() as cur:
                cur.execute(sql)
                filas = cur.fetchall()
        except psycopg.Error as exc:
            # Mostrar el error crudo también ayuda a ver el fallo en clase.
            error = f"{type(exc).__name__}: {exc}"
    return render_template(
        "v04.html", termino=termino, sql=sql, filas=filas, error=error
    )


@app.route("/v02")
def v02_inyeccion_codigo():
    """V02 — Calculadora de descuentos que evalúa la fórmula escrita por el usuario."""
    formula = request.args.get("formula", "")
    resultado = ""
    error = ""
    if formula:
        # VULNERABLE V02 (inyección de código): eval() ejecuta CUALQUIER cosa que
        # escriba el usuario, no solo cuentas. Con
        #   __import__('subprocess').check_output(['id'])
        # se ejecutan comandos del sistema operativo.
        try:
            resultado = repr(eval(formula))  # noqa: S307
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
    return render_template(
        "v02.html", formula=formula, resultado=resultado, error=error
    )


# ---------------------------------------------------------------------------
# Arranque del servidor
# ---------------------------------------------------------------------------
# VULNERABLE V01 (sin guardia __main__): estas líneas NO están dentro de
# `if __name__ == "__main__":`, así que se ejecutan también al importar el módulo.
# Un servidor de producción o una prueba que haga `from inseguro.app import app`
# arrancaría el servidor de desarrollo y quedaría colgado ahí.
# La forma correcta está en `seguro/app.py`.
print("[inseguro] módulo cargado: arrancando el servidor de desarrollo...")
app.run(
    host=os.environ.get("HOST", "127.0.0.1"),
    port=int(os.environ.get("PORT", "8000")),
)
