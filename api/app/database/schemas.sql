-- schema.sql
CREATE TABLE IF NOT EXISTS anonimo (
    id_anonimo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres VARCHAR(45) NOT NULL,
    telefono VARCHAR(16) NOT NULL,
    chat TEXT NOT NULL,
    correo_admin VARCHAR(45) NOT NULL
);