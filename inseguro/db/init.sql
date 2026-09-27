-- Datos de ejemplo para las demos: el inventario de una ferretería de barrio.
-- Todo es ficticio y solo vive en el contenedor local.
-- Postgres ejecuta este archivo la primera vez que se crea el volumen de datos.

-- Productos: es lo que la app deja consultar y editar (precio y stock).
CREATE TABLE IF NOT EXISTS productos (
    id        SERIAL PRIMARY KEY,
    sku       TEXT UNIQUE NOT NULL,
    nombre    TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio    NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock     INTEGER NOT NULL CHECK (stock >= 0)
);

INSERT INTO productos (sku, nombre, categoria, precio, stock) VALUES
    ('FE-001', 'Martillo de carpintero',      'Herramientas',  25000.00,  40),
    ('FE-002', 'Destornillador de estrella',  'Herramientas',   8500.00, 120),
    ('FE-003', 'Taladro percutor 650W',       'Eléctricas',    189000.00,  15),
    ('FE-004', 'Caja de tornillos 3/4" x100', 'Fijaciones',     12000.00, 300),
    ('FE-005', 'Pintura blanca 1 galón',      'Pinturas',       78000.00,  25),
    ('FE-006', 'Cinta métrica 5m',            'Medición',        9900.00,  80),
    ('FE-007', 'Guantes de nitrilo (par)',    'Seguridad',       6500.00, 200);

-- Movimientos de inventario: entradas y salidas. La versión segura los usa para
-- registrar cada cambio de stock dentro de una transacción (ACID); la insegura
-- actualiza el stock "a lo bruto", sin dejar rastro ni transacción.
CREATE TABLE IF NOT EXISTS movimientos (
    id         SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad   INTEGER NOT NULL,          -- positivo = entrada, negativo = salida
    motivo     TEXT NOT NULL,
    creado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Usuarios de la caja. Sirven para las demos de login y comparación de credenciales.
-- Contraseña en texto plano A PROPÓSITO, para poder mostrarla en clase.
CREATE TABLE IF NOT EXISTS usuarios (
    id       SERIAL PRIMARY KEY,
    nombre   TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol      TEXT NOT NULL DEFAULT 'cajero'
);

INSERT INTO usuarios (nombre, password, rol) VALUES
    ('cajero', 'cajero123',          'cajero'),
    ('admin',  'admin-secreto-demo', 'admin');
