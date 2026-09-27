"""App INSEGURA — demo docente de vulnerabilidades frecuentes.

Cada ruta reproduce A PROPÓSITO un fallo del catálogo (ver CLAUDE.md). Los
comentarios `# VULNERABLE Vxx` marcan dónde está cada fallo. Este código NO es un
ejemplo de cómo programar: la versión correcta está en la carpeta `seguro/`.
"""

import base64
import os
import pickle

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
        "ruta": "/v05",
        "resumen": "pickle.loads() sobre datos que vienen de afuera.",
        "implementado": True,
    },
    {
        "codigo": "V06",
        "titulo": "Path traversal",
        "ruta": "/v06",
        "resumen": "Abrir un archivo usando un nombre sin validar.",
        "implementado": True,
    },
    {
        "codigo": "V07",
        "titulo": "except demasiado amplio",
        "ruta": "/v07",
        "resumen": "Tragarse cualquier error con except: pass.",
        "implementado": True,
    },
    {
        "codigo": "V08",
        "titulo": "Mutable por defecto",
        "ruta": "/v08",
        "resumen": "Una lista como valor por defecto que se comparte entre llamadas.",
        "implementado": True,
    },
    {
        "codigo": "V09",
        "titulo": "Comparaciones inseguras",
        "ruta": "/v09",
        "resumen": "Comparar tokens con == o strings con is.",
        "implementado": True,
    },
]


# VULNERABLE V03 (secreto en el código): esta clave está escrita dentro del programa.
# Cualquiera con acceso al código —o al historial de git, para siempre— la ve. Lo
# correcto es leerla de una variable de entorno (ver `seguro/app.py`).
API_KEY_PASARELA = "sk-FALSO-pagos-9c8b7a6d5e4f3210"  # noqa: S105


@app.route("/")
def index():
    """Tienda: catálogo del inventario. Código de infraestructura, escrito bien
    (consulta parametrizada): la vitrina no es la lección, es el escenario."""
    categoria = request.args.get("categoria", "")
    categorias = []
    productos = []
    error = ""
    try:
        with conectar() as con, con.cursor() as cur:
            cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria")
            categorias = [c for (c,) in cur.fetchall()]
            if categoria:
                cur.execute(
                    "SELECT sku, nombre, categoria, precio, stock, imagen "
                    "FROM productos WHERE categoria = %s ORDER BY nombre",
                    (categoria,),
                )
            else:
                cur.execute(
                    "SELECT sku, nombre, categoria, precio, stock, imagen "
                    "FROM productos ORDER BY categoria, nombre"
                )
            productos = cur.fetchall()
    except psycopg.Error as exc:
        error = f"{type(exc).__name__}: {exc}"
    return render_template(
        "index.html",
        productos=productos,
        categorias=categorias,
        categoria=categoria,
        error=error,
    )


@app.route("/lecciones")
def lecciones():
    """Menú de las demos de vulnerabilidades (modo clase)."""
    return render_template("lecciones.html", demos=DEMOS)


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


FICHAS_DIR = os.path.join(os.path.dirname(__file__), "fichas")


@app.route("/v06")
def v06_path_traversal():
    """V06 — Descargar la ficha técnica de un producto por su nombre de archivo."""
    nombre = request.args.get("archivo", "")
    ruta = ""
    contenido = ""
    error = ""
    if nombre:
        # VULNERABLE V06 (path traversal): la ruta se arma pegando el nombre que dio
        # el usuario, sin validar que quede dentro de la carpeta de fichas. Con
        #   ../../../etc/passwd   se sale de esa carpeta y se lee cualquier archivo.
        ruta = f"{FICHAS_DIR}/{nombre}"
        try:
            with open(ruta, encoding="utf-8", errors="replace") as archivo:
                contenido = archivo.read()
        except OSError as exc:
            error = f"{type(exc).__name__}: {exc}"
    disponibles = sorted(os.listdir(FICHAS_DIR))
    return render_template(
        "v06.html",
        nombre=nombre,
        ruta=ruta,
        contenido=contenido,
        error=error,
        disponibles=disponibles,
    )


@app.route("/v05", methods=["GET", "POST"])
def v05_deserializacion():
    """V05 — Restaurar un 'carrito guardado' que llega serializado con pickle."""
    datos = request.form.get("datos", "")
    objeto = ""
    error = ""
    if datos:
        # VULNERABLE V05 (deserialización insegura): pickle.loads ejecuta lo que
        # venga dentro de los datos. Un pickle preparado corre código del sistema
        # en el momento de deserializarlo, antes de que veas ningún "carrito".
        try:
            objeto = repr(pickle.loads(base64.b64decode(datos)))  # noqa: S301
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
    return render_template("v05.html", datos=datos, objeto=objeto, error=error)


@app.route("/v07", methods=["GET", "POST"])
def v07_except_amplio():
    """V07 — Cambiar el precio de un producto; el error lo traga un except amplio."""
    mensaje = ""
    if request.method == "POST":
        sku = request.form.get("sku", "")
        nuevo = request.form.get("precio", "")
        # VULNERABLE V07 (except demasiado amplio): cualquier error queda tragado por
        # `except: pass`. Si el precio no es un número, o la base falla, la página
        # igual dice "guardado" y nadie se entera de que no se guardó nada.
        try:
            precio = float(nuevo)
            with conectar() as con, con.cursor() as cur:
                cur.execute(
                    "UPDATE productos SET precio = %s WHERE sku = %s", (precio, sku)
                )
        except:  # noqa: E722, S110
            pass
        mensaje = "Precio actualizado."  # se muestra pase lo que pase
    productos = []
    try:
        with conectar() as con, con.cursor() as cur:
            cur.execute("SELECT sku, nombre, precio FROM productos ORDER BY sku")
            productos = cur.fetchall()
    except psycopg.Error:
        pass
    return render_template("v07.html", mensaje=mensaje, productos=productos)


# VULNERABLE V08 (mutable por defecto): `cotizacion=[]` se crea UNA sola vez, al
# definir la función, y se comparte entre TODAS las llamadas. Cada petición agrega a
# la misma lista, así que una cotización "nueva" arrastra los ítems de las anteriores
# (incluso de otras personas). Lo correcto está en `seguro/app.py`.
def agregar_a_cotizacion(item, cotizacion=[]):  # noqa: B006
    cotizacion.append(item)
    return cotizacion


@app.route("/v08")
def v08_mutable_default():
    """V08 — Agregar un producto a una cotización que debería empezar vacía."""
    item = request.args.get("item", "")
    cotizacion = []
    if item:
        cotizacion = agregar_a_cotizacion(item)
    return render_template("v08.html", item=item, cotizacion=cotizacion)


@app.route("/v09", methods=["GET", "POST"])
def v09_comparaciones():
    """V09 — Iniciar sesión en la caja: compara la contraseña y decide si es admin."""
    mensaje = ""
    es_admin = False
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        password = request.form.get("password", "")
        fila = None
        try:
            with conectar() as con, con.cursor() as cur:
                cur.execute(
                    "SELECT password, rol FROM usuarios WHERE nombre = %s", (usuario,)
                )
                fila = cur.fetchone()
        except psycopg.Error as exc:
            mensaje = f"{type(exc).__name__}: {exc}"
        if fila is not None:
            guardado, rol = fila
            # VULNERABLE V09 (comparar con ==): comparar la contraseña con == deja
            # ver, por el tiempo que tarda, cuántos caracteres coinciden (timing
            # attack). Lo correcto es hmac.compare_digest (tiempo constante).
            if password == guardado:
                # VULNERABLE V09 (is en vez de ==): `is` compara identidad de objetos,
                # no valor. El rol viene de la base como un str nuevo, así que
                # `rol is "admin"` funciona solo por casualidad: casi siempre da False.
                es_admin = rol is "admin"  # noqa: F632
                mensaje = "Sesión iniciada."
            elif not mensaje:
                mensaje = "Usuario o contraseña incorrectos."
    return render_template("v09.html", mensaje=mensaje, es_admin=es_admin)


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
