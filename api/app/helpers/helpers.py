"""Utilidades y helpers para la aplicación."""
import random
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from .const import *

logger = logging.getLogger(__name__)

class Help:
    """Clase de utilidades con métodos estáticos."""

    @staticmethod
    def _generation_id() -> str:
        """Genera un ID aleatorio."""
        digitos = random.randint(3, 8)
        return str(random.randint(10**(digitos-1), 10**digitos - 1))

    @staticmethod
    def generator_id(obj: Any, attr: str) -> Any:
        """Asigna un ID generado a un atributo."""
        if hasattr(obj, attr):
            setattr(obj, attr, Help._generation_id())
            return obj
        raise AttributeError(f"El objeto no tiene '{attr}'")

    @staticmethod
    def extract_params(data: Dict, column_list: List, json_fields: List = None, prefix: str = "p_") -> Dict:
        """Extrae y normaliza parámetros de un diccionario."""
        res, json_fields = {}, json_fields or []
        # Lista de campos que suelen ser monetarios en este proyecto y requieren limpieza
        monetary_fields = {'precio_servicio', 'pago', 'total', 'precio_venta', 'subtotal', 'precio', 'total_compras'}
        
        for col in column_list:
            val = data.get(col)
            
            # Limpiar campo si es monetario y viene formateado como string
            if col in monetary_fields and val is not None:
                val = Help.parse_currency(val)
                
            if (col in json_fields or not json_fields) and isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            res[f"{prefix}{col}"] = val
        return res

    @staticmethod
    def extract_params_factura(data, cols): return Help.extract_params(data, cols, ["productos"])
    @staticmethod
    def extract_params_compra(data, cols): return Help.extract_params(data, cols, ["productos"])
    @staticmethod
    def extract_params_servicio_json(data): return Help.extract_params(data, list(CAMPOS_SERVICIO_JSON), prefix="")

    @staticmethod
    def add_generated_id_to_data(data: Dict, key: str) -> Dict:
        """Agrega ID generado si no existe."""
        if key not in data or not data.get(key):
            data[key] = int(Help._generation_id())
        return data

    @staticmethod
    def format_date_colombia(date_val):
        """Convierte fecha UTC a hora Colombia y formatea."""
        if not date_val: return None
        try:
            # Si es string, intentar parsear (asumiendo formato ISO si viene de JSON)
            if isinstance(date_val, str):
                from dateutil import parser
                date_val = parser.parse(date_val)
            
            # Ajustar a Colombia (UTC-5)
            # Nota: Si el servidor ya guarda en local, esto restaría 5 horas extra.
            # Asumimos que la BD guarda en UTC como se vio en el modelo Dispositivo.
            local_date = date_val - timedelta(hours=5)
            # Formato: 05/02/2026 : 05:02 pm
            return local_date.strftime('%d/%m/%Y : %I:%M %p').lower()
        except Exception:
            return str(date_val)

    @staticmethod
    def format_currency_colombia(value):
        """Formatea moneda a pesos colombianos."""
        if value is None: return "$ 0"
        try:
            val = float(value)
            # Formato: $ 300.000 (Python usa coma por defecto, reemplazamos)
            return "$ {:,.0f}".format(val).replace(",", ".")
        except:
            return str(value)

    @staticmethod
    def parse_currency(value):
        """Limpia formato de moneda para guardar en BD ($ 50.000 -> 50000)."""
        if value is None or value == "": return 0
        if isinstance(value, (int, float)): return value
        try:
            # Eliminar $, espacios y puntos (separadores de miles)
            clean_val = str(value).replace("$", "").replace(" ", "").replace(".", "")
            # Reemplazar coma por punto para decimales si existen
            clean_val = clean_val.replace(",", ".")
            return float(clean_val)
        except Exception:
            return 0

    @staticmethod
    def map_query_results(results: list, column_list: tuple) -> list[dict]:
        """Mapea resultados de SQLAlchemy a diccionarios con formato Colombia."""
        formatted_list = []
        for row in results:
            item = {}
            for i, col in enumerate(column_list):
                val = row[i]
                if col == 'fecha_ingreso':
                    val = Help.format_date_colombia(val)
                elif col == 'precio_servicio':
                    val = Help.format_currency_colombia(val)
                item[col] = val
            formatted_list.append(item)
        return formatted_list

    @staticmethod
    def set_resource(model_method: Any, many: bool = False) -> Any:
        """Decorador para inyectar recursos desde el JSON de la petición."""
        from functools import wraps
        from flask import request
        from ..database.schemas import api_search
        from ..helpers.response import notFound
        import inspect

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                params = api_search.load(request.get_json(force=True) or {})
                sig = inspect.signature(model_method)
                search_args = {k: v for k, v in params.items() if k in sig.parameters and v is not None}
                if 'many' in sig.parameters: search_args['many'] = many
                res = model_method(**search_args)
                return f(res, *args, **kwargs) if res else notFound()
            return wrapper
        return decorator

    @staticmethod
    def add_default_value_to_data(data: Dict, key: str, val: Any):
        if key not in data: data[key] = val

    @staticmethod
    def init_chat_db():
        """Inicializa SQLite para chat."""
        if not os.path.exists(os.path.dirname(CHAT_DB_PATH)):
            os.makedirs(os.path.dirname(CHAT_DB_PATH))
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            with open(CHAT_SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())

    @staticmethod
    def save_chat_message(nombres, telefono, chat, correo_admin):
        """Guarda mensaje en SQLite."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(SQL_CHAT_INSERT, (nombres, telefono, chat, correo_admin))
            return cursor.lastrowid

    @staticmethod
    def get_chat_history(user_id=None):
        """Obtiene historial de chat."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if user_id and user_id != WS_SUPPORT_ID:
                cursor.execute(SQL_CHAT_GET_BY_USER, (user_id, user_id))
            else:
                cursor.execute(SQL_CHAT_GET_ALL)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_chat_history(user_id):
        """Borra historial de un usuario."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            conn.execute(SQL_CHAT_DELETE_BY_USER, (user_id, user_id))
            return True

    @staticmethod
    def delete_chat_message(id_msg):
        """Borra un mensaje específico."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            return conn.execute(SQL_CHAT_DELETE_BY_ID, (id_msg,)).rowcount > 0

    @staticmethod
    def validate_dashboard_period(period: str) -> tuple[bool, Optional[str]]:
        """Valida periodo del dashboard."""
        p = period.lower().strip() if period else ""
        if p in PERIODOS_DASHBOARD: return True, None
        return False, f"Periodo inválido. Usar: {', '.join(PERIODOS_DASHBOARD)}"

    @staticmethod
    def get_dashboard_period_message(period: str) -> str:
        return MENSAJES_PERIODO_DASHBOARD.get(period.lower().strip(), "OK")

    @staticmethod
    def validate_status(status: str, allowed: tuple) -> bool:
        """Valida si un estado está en la lista permitida."""
        return status in allowed

    @staticmethod
    def validate_service_id(id_serv: Any) -> tuple[bool, Optional[str]]:
        try:
            if int(id_serv) > 0: return True, None
            return False, "ID debe ser positivo"
        except: return False, "ID inválido"
