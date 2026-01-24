"""
Módulo de utilidades y helpers para la aplicación.
Contiene funciones genéricas y reutilizables siguiendo principios DRY.
"""
import random
import json
import logging
import uuid
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
    def extract_params_servicio_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae y limpia los parámetros para el procedimiento de guardar servicio (JSON).
        No usa prefijo porque las claves van dentro de un objeto JSON.
        """
        from .const import CAMPOS_SERVICIO_JSON
        return Help.extract_params(data, list(CAMPOS_SERVICIO_JSON), prefix="")
    
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
    def map_query_results(results: list, column_list: tuple) -> list[dict]:
        """
        Mapea los resultados de una consulta SQLAlchemy a una lista de diccionarios.
        
        Args:
            results: Lista de resultados de la consulta (tuplas o filas)
            column_list: Tupla/Lista con los nombres de las columnas en orden
            
        Returns:
            Lista de diccionarios mapeados
        """
        mapped_list = []
        for row in results:
            item_dict = {
                campo: row[i] for i, campo in enumerate(column_list)
            }
            mapped_list.append(item_dict)
        return mapped_list

    @staticmethod
    def set_resource(model_method: Any, many: bool = False) -> Any:
        # ... (rest of the method remains valid, but since I am replacing until end of file or just adding, I need to be careful with context)
        """
        Decorador genérico para buscar y asignar uno o varios recursos (Servicio, etc.)
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
                
                # Si el método acepta 'many', pasarlo
                if 'many' in sig.parameters:
                    search_args['many'] = many
                
                # Ejecutar búsqueda
                resource = model_method(**search_args)
                
                if not resource:
                    return notFound()
                    
                return f(resource, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def add_default_value_to_data(data: Dict[str, Any], key: str, default_value: Any):
        """
        Agrega un valor por defecto a un campo en el diccionario de datos si no existe.
        """
        if key not in data:
            data[key] = default_value


class ChatManager:
    """
    Gestor de chats efímeros en memoria.
    Sigue el principio de responsabilidad única para el manejo del estado del chat.
    """
    _chats: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def create_chat(client_uuid: str, sid: str) -> Dict[str, Any]:
        """Crea un nuevo chat para un cliente si no existe."""
        if client_uuid not in ChatManager._chats:
            ChatManager._chats[client_uuid] = {
                "sid": sid,
                "messages": [],
                "status": "active",
                "last_activity": None
            }
        return ChatManager._chats[client_uuid]

    @staticmethod
    def get_chat(client_uuid: str) -> Optional[Dict[str, Any]]:
        """Busca un chat por el UUID del cliente."""
        return ChatManager._chats.get(client_uuid)

    @staticmethod
    def get_all_chats() -> Dict[str, Dict[str, Any]]:
        """Retorna todos los chats activos."""
        return ChatManager._chats

    @staticmethod
    def add_message(client_uuid: str, sender: str, text: str):
        """Agrega un mensaje al historial de un chat."""
        chat = ChatManager.get_chat(client_uuid)
        if chat:
            message = {
                "sender": sender,
                "text": text,
                "timestamp": None # Podría usarse datetime si se requiere
            }
            chat["messages"].append(message)

    @staticmethod
    def remove_chat_by_sid(sid: str) -> Optional[str]:
        """
        Elimina un chat basado en el SID de Socket.IO.
        Retorna el client_uuid si fue encontrado y eliminado.
        """
        uuid_to_remove = None
        for client_uuid, data in ChatManager._chats.items():
            if data.get("sid") == sid:
                uuid_to_remove = client_uuid
                break
        
        if uuid_to_remove:
            del ChatManager._chats[uuid_to_remove]
        
        return uuid_to_remove

    @staticmethod
    def generate_uuid() -> str:
        """Genera un UUID único para identificación anónima."""
        return str(uuid.uuid4())
