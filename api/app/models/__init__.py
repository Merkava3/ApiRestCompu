"""
Inicialización de modelos SQLAlchemy.
Importa todos los modelos de la aplicación.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importación de modelos
from .usuario_model import Usuario
from .cliente_model import Cliente
from .dispositivo_model import Dispositivo
from .servicio_model import Servicios
from .producto_model import Productos
from .prooveedor_model import Proveedor
from .compras_model import Compras
from .detalle_compra_model import DetalleCompra
from .facturas_model import Facturas
from .detalle_factura_model import DetalleFactura
from .inventario_model import Inventario

__all__ = [
    'db',
    'Usuario',
    'Cliente',
    'Dispositivo',
    'Servicios',
    'Productos',
    'Proveedor',
    'Compras',
    'DetalleCompra',
    'Facturas',
    'DetalleFactura',
    'Inventario'
]
