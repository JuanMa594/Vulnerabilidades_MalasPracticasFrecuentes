"""App SEGURA — la misma tienda que `inseguro/`, con las buenas prácticas.

Mismos archivos, funciones y rutas que la versión insegura: así
`git diff --no-index inseguro/app.py seguro/app.py` muestra solo las correcciones.
Cada arreglo lleva un comentario `# SEGURO Vxx`.
"""

import ast
import hmac
import json
import operator
import os

import psycopg
from flask import Flask, render_template, request

app = Flask(__name__)


def conectar():
    """Abre una conexión a Postgres. Los datos salen de variables de entorno."""
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


# SEGURO V03: el secreto sale de una variable de entorno, no del código. El .env
# (con el valor) está fuera de git, igual que las credenciales de la base.
API_KEY_PASARELA = os.environ.get("API_KEY_PASARELA", "")

# Catálogo de demos. Igual que en la versión insegura.
DEMOS = [
    {
        "codigo": "V01",
        "titulo": 'Sin if __name__ == "__main__"',
        "ruta": "/v01",
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


@app.route("/")
def index():
    """Tienda: catálogo del inventario (consulta parametrizada)."""
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


@app.route("/v01")
def v01_sin_main():
    """V01 — Fallo de estructura del archivo; sin demo interactiva, solo se explica."""
    return render_template("v01.html")


# SEGURO V02: evaluador aritmético propio con `ast`. Solo acepta números y
# + - * / y paréntesis; cualquier otra cosa (llamadas, imports, nombres) se
# rechaza. Nunca ejecuta el texto como código, a diferencia de eval().
_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARIOS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluar(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, int | float):
        return nodo.value
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in _BINARIOS:
        return _BINARIOS[type(nodo.op)](_evaluar(nodo.left), _evaluar(nodo.right))
    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _UNARIOS:
        return _UNARIOS[type(nodo.op)](_evaluar(nodo.operand))
    raise ValueError("Solo se permiten números y las operaciones + - * / ( ).")


@app.route("/v02")
def v02_inyeccion_codigo():
    """V02 — Calculadora de descuentos con un evaluador aritmético seguro."""
    formula = request.args.get("formula", "")
    resultado = ""
    error = ""
    if formula:
        try:
            resultado = repr(_evaluar(ast.parse(formula, mode="eval").body))
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as exc:
            error = f"{type(exc).__name__}: {exc}"
    return render_template(
        "v02.html", formula=formula, resultado=resultado, error=error
    )


@app.route("/v03")
def v03_secreto_en_codigo():
    """V03 — Muestra que la clave viene del entorno, sin exponerla."""
    # SEGURO V03: no se muestra el secreto; solo se confirma que está cargado.
    if API_KEY_PASARELA:
        visible = f"(cargada del entorno, termina en …{API_KEY_PASARELA[-4:]})"
    else:
        visible = "(no configurada: revisa la variable de entorno)"
    return render_template("v03.html", api_key=visible)


@app.route("/v04")
def v04_sql_injection():
    """V04 — Buscar productos con consulta parametrizada."""
    termino = request.args.get("q", "")
    sql = ""
    filas = []
    error = ""
    if termino:
        # SEGURO V04: consulta parametrizada. El término viaja como dato (%s), no
        # como parte del SQL, así que ' OR '1'='1 o un UNION quedan como texto a buscar.
        sql = "SELECT * FROM productos WHERE nombre ILIKE %s"
        try:
            with conectar() as con, con.cursor() as cur:
                cur.execute(sql, (f"%{termino}%",))
                filas = cur.fetchall()
        except psycopg.Error as exc:
            error = f"{type(exc).__name__}: {exc}"
    return render_template(
        "v04.html", termino=termino, sql=sql, filas=filas, error=error
    )


@app.route("/v05", methods=["GET", "POST"])
def v05_deserializacion():
    """V05 — Restaurar un carrito con JSON (solo datos, nunca código)."""
    datos = request.form.get("datos", "")
    objeto = ""
    error = ""
    if datos:
        # SEGURO V05: JSON solo describe datos; leerlos nunca ejecuta código.
        try:
            objeto = repr(json.loads(datos))
        except (json.JSONDecodeError, ValueError) as exc:
            error = f"{type(exc).__name__}: {exc}"
    return render_template("v05.html", datos=datos, objeto=objeto, error=error)


FICHAS_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "fichas"))


@app.route("/v06")
def v06_path_traversal():
    """V06 — Descargar una ficha, validando que quede dentro de la carpeta."""
    nombre = request.args.get("archivo", "")
    ruta = ""
    contenido = ""
    error = ""
    if nombre:
        # SEGURO V06: se resuelve la ruta real y se exige que quede dentro de
        # FICHAS_DIR. Así ../../../etc/passwd se rechaza en vez de abrirse.
        candidata = os.path.realpath(os.path.join(FICHAS_DIR, nombre))
        if candidata != FICHAS_DIR and not candidata.startswith(FICHAS_DIR + os.sep):
            error = "Ruta no permitida: queda fuera de la carpeta de fichas."
        else:
            ruta = candidata
            try:
                with open(candidata, encoding="utf-8", errors="replace") as archivo:
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


@app.route("/v07", methods=["GET", "POST"])
def v07_except_amplio():
    """V07 — Cambiar el precio capturando el error específico y sin mentir."""
    mensaje = ""
    if request.method == "POST":
        sku = request.form.get("sku", "")
        nuevo = request.form.get("precio", "")
        # SEGURO V07: se captura el error concreto y solo se confirma si de verdad
        # se actualizó una fila; nada de except: pass ni mensajes falsos.
        try:
            precio = float(nuevo)
        except ValueError:
            mensaje = "El precio debe ser un número."
        else:
            try:
                with conectar() as con, con.cursor() as cur:
                    cur.execute(
                        "UPDATE productos SET precio = %s WHERE sku = %s",
                        (precio, sku),
                    )
                    actualizados = cur.rowcount
                mensaje = (
                    "Precio actualizado."
                    if actualizados
                    else f"No existe el producto {sku}."
                )
            except psycopg.Error as exc:
                mensaje = f"No se pudo guardar: {exc}"
    productos = []
    try:
        with conectar() as con, con.cursor() as cur:
            cur.execute("SELECT sku, nombre, precio FROM productos ORDER BY sku")
            productos = cur.fetchall()
    except psycopg.Error as exc:
        productos = []
        mensaje = mensaje or f"No se pudo leer el inventario: {exc}"
    return render_template("v07.html", mensaje=mensaje, productos=productos)


# SEGURO V08: el valor por defecto es None y la lista se crea dentro de la
# función, así cada llamada empieza con su propia lista vacía.
def agregar_a_cotizacion(item, cotizacion=None):
    if cotizacion is None:
        cotizacion = []
    cotizacion.append(item)
    return cotizacion


@app.route("/v08")
def v08_mutable_default():
    """V08 — Agregar a una cotización que sí empieza vacía en cada visita."""
    item = request.args.get("item", "")
    cotizacion = []
    if item:
        cotizacion = agregar_a_cotizacion(item)
    return render_template("v08.html", item=item, cotizacion=cotizacion)


@app.route("/v09", methods=["GET", "POST"])
def v09_comparaciones():
    """V09 — Login que compara el secreto en tiempo constante y el rol por valor."""
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
            # SEGURO V09: compare_digest compara en tiempo constante (sin timing
            # attack); == compara el rol por valor (is comparaba identidad).
            if hmac.compare_digest(password, guardado):
                es_admin = rol == "admin"
                mensaje = "Sesión iniciada."
            elif not mensaje:
                mensaje = "Usuario o contraseña incorrectos."
    return render_template("v09.html", mensaje=mensaje, es_admin=es_admin)


# ---------------------------------------------------------------------------
# Arranque del servidor
# ---------------------------------------------------------------------------
# SEGURO V01: el arranque va dentro de la guardia __main__. Así importar el
# módulo (una prueba, un servidor de producción) NO arranca el servidor.
if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )
