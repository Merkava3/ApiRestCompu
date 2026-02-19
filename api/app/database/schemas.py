from marshmallow import Schema, EXCLUDE, pre_dump, post_dump
from marshmallow import fields as serializacion
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Cliente, Dispositivo, Servicios, Usuario
from ..helpers.const import *

# ======================== BASES Y MIXINS (SOLID, DRY & CLEAN CODE) ========================

class BaseAutoSchema(SQLAlchemyAutoSchema):
    """Esquema base para modelos SQLAlchemy con configuración común."""
    class Meta:
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

class ClientFieldsMixin:
    """Encapsula los campos de Cliente para reutilización (DRY)."""
    id_cliente = serializacion.Int(dump_only=True)
    cedula = serializacion.Str()
    nombre_cliente = serializacion.Str()
    direccion = serializacion.Str()
    telefono_cliente = serializacion.Str()

class DispositivoFieldsMixin:
    """Encapsula los campos de Dispositivo para reutilización (DRY)."""
    id_dispositivo = serializacion.Int(dump_only=True)
    cliente_id_dispositivo = serializacion.Int()
    tipo = serializacion.Str()
    marca = serializacion.Str()
    modelo = serializacion.Str()
    numero_serie = serializacion.Str()
    descripcion = serializacion.Str()
    reporte = serializacion.Str()
    fecha_ingreso = serializacion.Raw()

class ServiceBaseFieldsMixin:
    """Campos base de la tabla Servicios."""
    id_servicio = serializacion.Int(dump_only=True)
    cliente_id_servicio = serializacion.Int()
    dispositivo_id_servicio = serializacion.Int()
    usuario_id_servicio = serializacion.Int()
    tipo_servicio = serializacion.Str()
    precio_servicio = serializacion.Raw() # Raw para manejar moneda/float
    descripcion = serializacion.Str()
    estado_servicio = serializacion.Str()
    fecha_servicio = serializacion.Raw()
    fecha_entrega = serializacion.Raw()

class ServiceFlattenedMixin:
    """Mapeos de atributos aplanados para Servicios (SOLID)."""
    # Mapeos de Cliente
    cedula = serializacion.Str(attribute="cliente.cedula", dump_only=True)
    nombre_cliente = serializacion.Str(attribute="cliente.nombre_cliente", dump_only=True)
    direccion = serializacion.Str(attribute="cliente.direccion", dump_only=True)
    telefono_cliente = serializacion.Str(attribute="cliente.telefono_cliente", dump_only=True)
    
    # Mapeos de Dispositivo
    marca = serializacion.Str(attribute="dispositivo.marca", dump_only=True)
    modelo = serializacion.Str(attribute="dispositivo.modelo", dump_only=True)
    tipo = serializacion.Str(attribute="dispositivo.tipo", dump_only=True)
    numero_serie = serializacion.Str(attribute="dispositivo.numero_serie", dump_only=True)
    reporte = serializacion.Str(attribute="dispositivo.reporte", dump_only=True)
    
    # Mapeos de Usuario
    email_usuario = serializacion.Str(attribute="usuario.email_usuario", dump_only=True)
    usuario_email = serializacion.Str(attribute="usuario.email_usuario", dump_only=True) # Alias para compatibilidad
    nombre_usuario = serializacion.Str(attribute="usuario.nombre_usuario", dump_only=True)
    
    # Campos calculados / Formateo (Lógica de Negocio)
    dias = serializacion.Raw(dump_only=True)
    
    @pre_dump
    def format_dates(self, obj, **kwargs):
        """Formatea fechas antes de la serialización si son objetos datetime."""
        if hasattr(obj, 'fecha_ingreso') and hasattr(obj.fecha_ingreso, 'strftime'):
            obj.fecha_ingreso_str = obj.fecha_ingreso.strftime('%d/%m/%Y')
        # Nota: La lógica de formateo específica de fecha_ingreso de dispositivo se maneja mejor en el serializador si es necesario
        return obj

# ======================== ESQUEMAS PRINCIPALES ========================

class ClienteSchemas(BaseAutoSchema, ClientFieldsMixin):
    class Meta(BaseAutoSchema.Meta):
        model = Cliente
        fields = CAMPOS_CLIENTE

class Dispostivoschemas(BaseAutoSchema, DispositivoFieldsMixin):
    # Relación anidada
    cliente = serializacion.Nested(ClienteSchemas)
    
    # Atributos aplanados de Cliente (Explícito como en la imagen)
    cedula = serializacion.Str(attribute="cliente.cedula", dump_only=True)
    nombre_cliente = serializacion.Str(attribute="cliente.nombre_cliente", dump_only=True)
    direccion = serializacion.Str(attribute="cliente.direccion", dump_only=True)
    telefono_cliente = serializacion.Str(attribute="cliente.telefono_cliente", dump_only=True)

    class Meta(BaseAutoSchema.Meta):
        model = Dispositivo
        fields = CAMPOS_DISPOSITIVO_CON_CLIENTE

class ServiciosSchemas(BaseAutoSchema, ServiceBaseFieldsMixin):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS

class ServiciosUpdateSchemas(ServiciosSchemas):
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIO_UPDATE

class ServiciosCompletosSchemas(BaseAutoSchema, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS_COMPLETOS

class ServiciosCedulaSchemas(BaseAutoSchema, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS_CEDULA

class UsuarioSchemas(BaseAutoSchema):
    id_usuario = serializacion.Int(dump_only=True)
    email_usuario = serializacion.Str()
    nombre_usuario = serializacion.Str()
    rol = serializacion.Str()

    class Meta(BaseAutoSchema.Meta):
        model = Usuario
        fields = CAMPOS_USUARIO

# ======================== ESQUEMAS AUXILIARES ========================

class SearchSchema(Schema):
    id_servicio = serializacion.Raw(allow_none=True)
    cedula = serializacion.Str(allow_none=True)
    class Meta:
        unknown = EXCLUDE

class ServicioUltimoDetalleSchema(BaseAutoSchema, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIO_ULTIMO_DETALLE

class ServicioReporteSchema(Schema, ClientFieldsMixin, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    """Esquema para reportes (Datos suelen venir como diccionarios)."""
    class Meta:
        fields = CAMPOS_SERVICIO_REPORTE
        unknown = EXCLUDE

class ServicioTareasSchema(Schema, ClientFieldsMixin, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    """Esquema para tareas (Datos suelen venir como diccionarios)."""
    class Meta:
        fields = CAMPOS_SERVICIOS_TAREAS
        unknown = EXCLUDE

class ServicioUltimoResumenSchema(Schema, ClientFieldsMixin, ServiceBaseFieldsMixin, ServiceFlattenedMixin):
    """Esquema para resumen (Datos suelen venir como diccionarios)."""
    class Meta:
        fields = CAMPOS_LISTA_ULTIMOS
        unknown = EXCLUDE

# ======================== INSTANCIAS (SINGLETONS) ========================

api_search = SearchSchema()
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)
api_servicio = ServiciosSchemas()
api_servicios = ServiciosSchemas(many=True)
api_servicio_update = ServiciosUpdateSchemas()
api_servicios_completos = ServiciosCompletosSchemas(many=True)
api_servicio_completo = ServiciosCompletosSchemas()
api_servicio_cedula = ServiciosCedulaSchemas()
api_servicios_ultimo = ServicioUltimoResumenSchema(many=True)
api_usuario = UsuarioSchemas()
api_usuarios = UsuarioSchemas(many=True)
api_servicio_ultimo_detalle = ServicioUltimoDetalleSchema()
api_servicios_reporte = ServicioReporteSchema(many=True)
api_servicios_tareas = ServicioTareasSchema(many=True)
