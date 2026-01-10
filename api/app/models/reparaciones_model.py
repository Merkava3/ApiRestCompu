"""
Modelo Reparaciones - Refactorizado usando BaseModelMixin.
Elimina código duplicado en métodos save/delete usando herencia múltiple.
"""
from typing import Any
from sqlalchemy import DateTime, or_, func
from sqlalchemy import text
from . import db
from .dispositivo_model import Dispositivo
from .cliente_model import Cliente
from .base_model import BaseModelMixin
from ..helpers.helpers import Help
from ..helpers.const import (
    INSERTAR_REPARACION_COMPLETA, 
    COLUMN_LIST_REPARACION_COMPLETA
)


class Reparaciones(BaseModelMixin, db.Model):
    """
    Modelo de Reparaciones con funcionalidad base proporcionada por BaseModelMixin.
    Maneja reparaciones con información de dispositivos y clientes.
    """
    __tablename__ = 'reparaciones'

    id_reparacion = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dispositivo_id_reparacion = db.Column(db.BigInteger, db.ForeignKey('dispositivos.id_dispositivo'), nullable=False)
    estado = db.Column(db.String(45), nullable=False)   
    precio_reparacion = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(DateTime, nullable=True)

    # Relación
    dispositivo = db.relationship('Dispositivo', back_populates='reparaciones')

    # Métodos de consulta
    @staticmethod
    def get_reparacion(id_reparacion):
        """Obtiene una reparación por su ID."""
        return Reparaciones.query.filter_by(id_reparacion=id_reparacion).first()

    @staticmethod
    def get_reparaciones():
        """Obtiene todas las reparaciones."""
        return Reparaciones.query.all()
    
    # Los métodos save(), delete(), new(), create_from_dict() y update_from_dict()
    # son heredados de BaseModelMixin, eliminando código duplicado
        
    @classmethod
    def get_reparaciones_con_clientes(cls):
        """
        Retorna las reparaciones con información del dispositivo y del cliente.
        """
        return db.session.query(
            Reparaciones.id_reparacion,
            Reparaciones.dispositivo_id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Reparaciones.precio_reparacion,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.numero_serie,
            Dispositivo.reporte,
            Reparaciones.descripcion,
            Reparaciones.estado,
            Dispositivo.fecha_ingreso,
            Reparaciones.fecha_entrega
        ).join(Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo) \
         .join(Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente).all()
    
    @staticmethod
    def get_reparaciones_filter(cedula=None, numero_serie=None, id_reparacion=None):
        """
        Obtiene reparaciones filtrando por cédula, número de serie o ID de reparación.
        Si todos los valores son None, devuelve None.
        """
        query = db.session.query(
            Reparaciones.id_reparacion,
            Reparaciones.dispositivo_id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Reparaciones.precio_reparacion,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Dispositivo.fecha_ingreso,
            Reparaciones.fecha_entrega
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        )        
        if cedula is not None:
            query = query.filter(Cliente.cedula == cedula)
        if numero_serie is not None:
            query = query.filter(Dispositivo.numero_serie == numero_serie)
        if id_reparacion is not None:
            query = query.filter(Reparaciones.id_reparacion == id_reparacion)

        return query.first()
    
    @classmethod
    def get_reparaciones_completas(cls):
        """
        Retorna todas las reparaciones con información completa del dispositivo y del cliente.
        Incluye: id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion, fecha_entrega, fecha_ingreso
        """
        return db.session.query(
            Reparaciones.id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Reparaciones.precio_reparacion,
            Reparaciones.descripcion,            
            func.to_char(Reparaciones.fecha_entrega, 'DD/MM/YYYY').label('fecha_entrega'),
            func.to_char(Dispositivo.fecha_ingreso, 'DD/MM/YYYY').label('fecha_ingreso'),
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        ).all()
    
    @staticmethod
    def get_reparacion_completa(id_reparacion=None, cedula=None):
        """
        Obtiene reparaciones con información completa del dispositivo y del cliente.
        Puede filtrar por id_reparacion O cedula del cliente.
        Incluye: id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion, fecha_entrega, fecha_ingreso
        
        Args:
            id_reparacion: ID de la reparación (opcional)
            cedula: Cédula del cliente (opcional)
        
        Returns:
            Primera reparación que coincida con los filtros, o None si no se encuentra
        """
        query = db.session.query(
            Reparaciones.id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Reparaciones.precio_reparacion,
            Reparaciones.descripcion,
            func.to_char(Reparaciones.fecha_entrega, 'DD/MM/YYYY').label('fecha_entrega'),
            func.to_char(Dispositivo.fecha_ingreso, 'DD/MM/YYYY').label('fecha_ingreso')
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        )
        
        # Aplicar filtros: id_reparacion OR cedula
        filters = []
        if id_reparacion is not None:
            filters.append(Reparaciones.id_reparacion == id_reparacion)
        if cedula is not None:
            filters.append(Cliente.cedula == cedula)
        
        if filters:
            # Si hay filtros, usar OR entre ellos
            query = query.filter(or_(*filters))
        
        return query.first()
    
    @classmethod
    def insertar_reparacion_completa(cls, data: dict) -> Any:
        """Inserta una reparación completa usando el procedimiento almacenado."""
        try:
            import json
            query = text(INSERTAR_REPARACION_COMPLETA)
            result = db.session.execute(query, {"p_data": json.dumps(data, ensure_ascii=False)})
            db.session.commit()
            return result.scalar()
        except Exception:
            db.session.rollback()
            raise