"""App INSEGURA — demo docente de vulnerabilidades frecuentes.

Cada ruta reproduce A PROPÓSITO un fallo del catálogo (ver CLAUDE.md). Los
comentarios `# VULNERABLE Vxx` marcan dónde está cada fallo. Este código NO es un
ejemplo de cómo programar: la versión correcta está en la carpeta `seguro/`.
"""

import os

from flask import Flask, render_template

app = Flask(__name__)

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
        "ruta": None,
        "resumen": "Evaluar texto del usuario con eval()/os.system().",
        "implementado": False,
    },
    {
        "codigo": "V03",
        "titulo": "Secretos en el código",
        "ruta": None,
        "resumen": "Una clave escrita dentro del programa.",
        "implementado": False,
    },
    {
        "codigo": "V04",
        "titulo": "SQL Injection",
        "ruta": None,
        "resumen": "Buscar productos armando la consulta con el texto del usuario.",
        "implementado": False,
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


@app.route("/")
def index():
    return render_template("index.html", demos=DEMOS, version="insegura")


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
