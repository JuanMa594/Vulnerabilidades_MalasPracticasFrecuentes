-- Datos de ejemplo: el inventario de una ferretería de barrio.
-- Generado por scratchpad/descargar_imagenes.py (imágenes en static/img).
-- Todo es ficticio y solo vive en el contenedor local.

CREATE TABLE IF NOT EXISTS productos (
    id        SERIAL PRIMARY KEY,
    sku       TEXT UNIQUE NOT NULL,
    nombre    TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio    NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock     INTEGER NOT NULL CHECK (stock >= 0),
    imagen    TEXT NOT NULL DEFAULT ''
);

INSERT INTO productos (sku, nombre, categoria, precio, stock, imagen) VALUES
    ('FE-001', 'Martillo de carpintero', 'Herramientas', 25000.00, 40, 'FE-001.jpg'),
    ('FE-002', 'Destornillador de estrella', 'Herramientas', 8500.00, 120, 'FE-002.jpg'),
    ('FE-003', 'Taladro percutor 650W', 'Eléctricas', 189000.00, 15, 'FE-003.jpg'),
    ('FE-004', 'Caja de tornillos 3/4x100', 'Fijaciones', 12000.00, 300, 'FE-004.jpg'),
    ('FE-005', 'Pintura blanca 1 galón', 'Pinturas', 78000.00, 25, 'FE-005.jpg'),
    ('FE-006', 'Cinta métrica 5m', 'Medición', 9900.00, 80, 'FE-006.jpg'),
    ('FE-007', 'Guantes de nitrilo (par)', 'Seguridad', 6500.00, 200, 'FE-007.jpg'),
    ('FE-008', 'Llave inglesa 10"', 'Herramientas', 22000.00, 35, 'FE-008.jpg'),
    ('FE-009', 'Alicate universal', 'Herramientas', 18000.00, 45, 'FE-009.jpg'),
    ('FE-010', 'Nivel de burbuja 40cm', 'Medición', 15000.00, 30, 'FE-010.jpg'),
    ('FE-011', 'Serrucho 20"', 'Herramientas', 27000.00, 20, 'FE-011.jpg'),
    ('FE-012', 'Cinta aislante negra', 'Electricidad', 3500.00, 250, 'FE-012.jpg'),
    ('FE-013', 'Bombillo LED 9W', 'Electricidad', 8900.00, 150, 'FE-013.jpg'),
    ('FE-014', 'Brocha 3 pulgadas', 'Pinturas', 7200.00, 90, 'FE-014.jpg'),
    ('FE-015', 'Casco de seguridad', 'Seguridad', 32000.00, 25, 'FE-015.jpg'),
    ('FE-016', 'Llave de tubo 14"', 'Plomería', 45000.00, 18, 'FE-016.jpg'),
    ('FE-017', 'Manguera de jardín 15m', 'Jardín', 52000.00, 22, 'FE-017.jpg'),
    ('FE-018', 'Candado de acero 50mm', 'Seguridad', 19000.00, 60, 'FE-018.jpg');

-- Movimientos de inventario: la versión segura los registra dentro de una
-- transacción (ACID); la insegura cambia el stock sin transacción ni registro.
CREATE TABLE IF NOT EXISTS movimientos (
    id          SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad    INTEGER NOT NULL,
    motivo      TEXT NOT NULL,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Usuarios de la caja (para las demos de login y comparación).
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
