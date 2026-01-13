"""
Módulo de utilidades y helpers para la aplicación.
Contiene funciones genéricas y reutilizables siguiendo principios DRY.
"""
import random
import json
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class Help:
    """Clase de utilidades con métodos estáticos para operaciones comunes."""
    
    @staticmethod
    def _generation_id() -> str:
        """
        Genera un ID numérico aleatorio.
        
        Returns:
            str: ID generado como string
        """
        digitos: int = random.randint(3, 8)
        numero: int = random.randint(10**(digitos-1), 10**digitos - 1)
        return str(numero)

    @staticmethod
    def generator_id(objeto: Any, atributo: str) -> Any:
        """
        Asigna un ID generado al atributo especificado de un objeto.

        Args:
            objeto (Any): El objeto al que se le asignará el ID.
            atributo (str): Nombre del atributo donde se guardará el ID.

        Returns:
            Any: El objeto modificado con el ID asignado.
        
        Raises:
            AttributeError: Si el objeto no tiene el atributo especificado.
        """
        if hasattr(objeto, atributo):
            setattr(objeto, atributo, Help._generation_id())
        else:
            raise AttributeError(f"El objeto no tiene el atributo '{atributo}'")
        return objeto
    
    @staticmethod
    def extract_params(data: Dict[str, Any], column_list: List[str], 
                      json_fields: Optional[List[str]] = None,
                      prefix: str = "p_") -> Dict[str, Any]:
        """
        Extrae y normaliza valores de un diccionario según una lista de claves.
        Método genérico que reemplaza a extract_params_factura, extract_params_compra, etc.
        
        Args:
            data: Diccionario con los datos fuente
            column_list: Lista de columnas a extraer
            json_fields: Lista de campos que deben convertirse a JSON (opcional)
            prefix: Prefijo para las claves del resultado (default: "p_")
        
        Returns:
            Dict con los parámetros extraídos y prefijados
        """
        extracted_data = {}
        json_fields = json_fields or []
        
        for column in column_list:
            value = data.get(column)
            
            # Convertir a JSON si el campo está en la lista de campos JSON
            if column in json_fields and isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            
            # Convertir listas/dicts a JSON por defecto si no se especificó json_fields
            elif not json_fields and isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            
            extracted_data[f"{prefix}{column}"] = value
        
        return extracted_data
    
    # Métodos de compatibilidad que usan extract_params internamente
    @staticmethod
    def extract_params_factura(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para facturas (productos se convierte a JSON)."""
        return Help.extract_params(data, column_list, json_fields=["productos"])
    
    @staticmethod
    def extract_params_compra(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para compras (productos se convierte a JSON)."""
        return Help.extract_params(data, column_list, json_fields=["productos"])
    
    @staticmethod
    def extract_params_inventario(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para inventario (productos se convierte a JSON)."""
        return Help.extract_params(data, column_list, json_fields=["productos"])
    
    @staticmethod
    def extract_params_cliente_dispositivo(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para cliente_dispositivo."""
        return Help.extract_params(data, column_list)
    
    @staticmethod
    def extract_params_servicio(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para servicio."""
        return Help.extract_params(data, column_list)
    
    @staticmethod
    def normalize_field_names(data: Dict[str, Any], 
                              field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Normaliza nombres de campos en un diccionario usando un mapeo.
        Útil para aceptar variantes de nombres de campos.
        
        Args:
            data: Diccionario con los datos
            field_mapping: Dict con mapeo {nombre_alternativo: nombre_esperado}
        
        Returns:
            Dict con los nombres normalizados
        """
        normalized = data.copy()
        
        for alt_name, expected_name in field_mapping.items():
            if alt_name in normalized and expected_name not in normalized:
                normalized[expected_name] = normalized[alt_name]
        
        return normalized
    
    @staticmethod
    def add_generated_id_to_data(data: Dict[str, Any], id_key: str) -> Dict[str, Any]:
        """
        Genera un ID aleatorio y lo agrega al diccionario si no existe o está vacío.
        
        Args:
            data: Diccionario al que se le agregará el ID generado.
            id_key: Clave del diccionario donde se guardará el ID.
        
        Returns:
            Dict: El diccionario modificado con el ID generado (si no existía).
        """
        if id_key not in data or not data.get(id_key):
            id_generado = Help._generation_id()
            data[id_key] = int(id_generado)
        return data
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], 
                                required_fields: List[str]) -> tuple[bool, Optional[List[str]]]:
        """
        Valida que todos los campos requeridos estén presentes y no sean None.
        Patrón: Strategy Pattern para validación.
        
        Args:
            data: Diccionario con los datos a validar
            required_fields: Lista de campos que son obligatorios
        
        Returns:
            Tupla (es_válido: bool, campos_faltantes: Optional[List[str]])
        """
        missing_fields = [field for field in required_fields 
                         if field not in data or data[field] is None]
        return (len(missing_fields) == 0, missing_fields if missing_fields else None)
    
    @staticmethod
    def validate_at_least_one_field(data: Dict[str, Any], 
                                   fields: List[str]) -> bool:
        """
        Valida que al menos uno de los campos especificados esté presente.
        Patrón: Strategy Pattern para validación condicional.
        
        Args:
            data: Diccionario con los datos
            fields: Lista de campos (debe haber al menos uno)
        
        Returns:
            bool: True si al menos uno está presente, False en caso contrario
        """
        return any(data.get(field) for field in fields)
    
    @staticmethod
    def extract_params_reparacion(data: Dict[str, Any], column_list: List[str]) -> Dict[str, Any]:
        """Compatibilidad: Extrae parámetros para reparación."""
        return Help.extract_params(data, column_list)

    @staticmethod
    def set_resource(model_method: Any) -> Any:
        """
        Decorador genérico para buscar y asignar un recurso (Servicio, Reparación, etc.)
        basado en los identificadores enviados en el JSON de la petición.
        Aplica principios DRY y Clean Code.
        """
        from functools import wraps
        from flask import request
        from ..database.schemas import api_search
        from ..helpers.response import notFound
        import inspect

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                json_data = request.get_json(force=True) or {}
                # Extraer criterios de búsqueda usando el esquema centralizado
                params = api_search.load(json_data)
                
                # Identificar dinámicamente qué parámetros acepta el método del modelo
                sig = inspect.signature(model_method)
                search_args = {
                    k: v for k, v in params.items() 
                    if k in sig.parameters and v is not None
                }
                
                # Ejecutar búsqueda
                resource = model_method(**search_args)
                
                if not resource:
                    return notFound()
                    
                return f(resource, *args, **kwargs)
            return wrapper
        return decorator
