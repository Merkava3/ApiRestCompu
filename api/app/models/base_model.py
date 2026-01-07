"""
Modelo base con funcionalidad común para todos los modelos.
Aplica el patrón Mixin para eliminar código duplicado.
Debe usarse con herencia múltiple junto a db.Model.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseModelMixin:
    """
    Clase base abstracta para todos los modelos.
    Proporciona métodos comunes como save, delete y create_from_dict.
    """
    
    def save(self) -> bool:
        """
        Guarda el objeto en la base de datos.
        
        Returns:
            bool: True si se guardó exitosamente, False en caso contrario
        """
        from . import db
        try:
            db.session.add(self)
            db.session.commit()
            logger.debug(f"Objeto {self.__class__.__name__} guardado exitosamente")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al guardar {self.__class__.__name__}: {e}", exc_info=True)
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al guardar {self.__class__.__name__}: {e}", exc_info=True)
            return False
    
    def delete(self) -> bool:
        """
        Elimina el objeto de la base de datos.
        
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        from . import db
        try:
            db.session.delete(self)
            db.session.commit()
            logger.debug(f"Objeto {self.__class__.__name__} eliminado exitosamente")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al eliminar {self.__class__.__name__}: {e}", exc_info=True)
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al eliminar {self.__class__.__name__}: {e}", exc_info=True)
            return False
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[list] = None) -> None:
        """
        Actualiza los atributos del objeto desde un diccionario.
        
        Args:
            data: Diccionario con los valores a actualizar
            exclude: Lista de claves a excluir de la actualización
        """
        exclude = exclude or []
        for key, value in data.items():
            if hasattr(self, key) and key not in exclude:
                setattr(self, key, value)
    
    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Crea una nueva instancia del modelo desde un diccionario.
        
        Args:
            data: Diccionario con los valores iniciales
        
        Returns:
            Instancia del modelo creada
        """
        return cls(**data)
    
    @classmethod
    def new(cls, kwargs: Dict[str, Any]) -> 'BaseModel':
        """
        Alias para create_from_dict para compatibilidad con código existente.
        
        Args:
            kwargs: Diccionario con los valores iniciales
        
        Returns:
            Instancia del modelo creada
        """
        return cls.create_from_dict(kwargs)
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """
        Convierte el objeto a un diccionario.
        
        Args:
            exclude: Lista de atributos a excluir
        
        Returns:
            Dict con los atributos del objeto
        """
        exclude = exclude or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                result[column.name] = value.isoformat() if hasattr(value, 'isoformat') else value
        return result
