from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .usuario_model import Usuario
from .cliente_model import Cliente
from .dispositivo_model import Dispositivo
from .reparaciones_model import Reparaciones
from .servicio_model import Servicios
from .producto_model import Productos
from .prooveedor_model import Proveedor
from .inventario_model import Inventario
from .facturas_model import Facturas
from .detalle_factura_model import DetalleFactura
from .compras_model import Compras
from .detalle_compra_model import DetalleCompra
