"""
Módulo de utilidades y helpers centralizados.
Sigue principios Clean Code, SOLID y DRY.
"""
import random
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import wraps
from flask import request
from .const import (
    CHAT_DB_PATH, CHAT_SCHEMA_PATH, SQL_CHAT_INSERT, SQL_CHAT_GET_ALL,
    SQL_CHAT_GET_BY_USER, SQL_CHAT_DELETE_BY_USER, SQL_CHAT_DELETE_BY_ID,
    WS_SUPPORT_ID, PERIODOS_DASHBOARD, MENSAJES_PERIODO_DASHBOARD,
    CAMPOS_SERVICIO_JSON
)

logger = logging.getLogger(__name__)

class Formatter:
    """Utilidades de formateo para datos de salida y entrada."""

    @staticmethod
    def to_colombia_date(date_val: Any) -> Optional[str]:
        """Convierte fecha a zona horaria Colombia (UTC-5) y formato legible."""
        if not date_val:
            return None
        try:
            if isinstance(date_val, str):
                from dateutil import parser
                date_val = parser.parse(date_val)
            
            # Ajuste UTC-5
            local_date = date_val - timedelta(hours=5)
            return local_date.strftime('%d/%m/%Y : %I:%M %p').lower()
        except Exception:
            return str(date_val)

    @staticmethod
    def to_pesos(value: Any) -> str:
        """Formatea valor numérico a pesos colombianos ($ 1.234)."""
        if value is None:
            return "$ 0"
        try:
            return "$ {:,.0f}".format(float(value)).replace(",", ".")
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def parse_currency(value: Any) -> float:
        """Limpia formato de moneda a float puro para almacenamiento."""
        if value in (None, ""):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            clean = str(value).replace("$", "").replace(" ", "").replace(".", "").replace(",", ".")
            return float(clean)
        except (ValueError, TypeError):
            return 0.0

class Parser:
    """Encapsula la extracción y transformación de datos de peticiones."""

    @staticmethod
    def extract(data: Dict, columns: List, prefix: str = "") -> Dict:
        """Extrae campos específicos de un diccionario aplicando limpieza de moneda."""
        monetary = {'precio_servicio', 'pago', 'total'}
        result = {}
        for col in columns:
            val = data.get(col)
            if col in monetary:
                val = Formatter.parse_currency(val)
            result[f"{prefix}{col}"] = val
        return result

    @staticmethod
    def map_results(rows: List, columns: Tuple) -> List[Dict]:
        """Convierte resultados de consulta SQL a diccionarios con formato."""
        final_list = []
        for row in rows:
            item = {}
            for i, col in enumerate(columns):
                val = row[i]
                if col == 'fecha_ingreso':
                    val = Formatter.to_colombia_date(val)
                item[col] = val
            final_list.append(item)
        return final_list

class Validator:
    """Reglas de validación de negocio y estado."""

    @staticmethod
    def dashboard_period(period: str) -> Tuple[bool, Optional[str]]:
        """Valida que el período del dashboard sea permitido."""
        p = period.lower().strip() if period else ""
        if p in PERIODOS_DASHBOARD:
            return True, None
        return False, f"Periodo inválido. Permitidos: {', '.join(PERIODOS_DASHBOARD)}"

    @staticmethod
    def service_id(id_val: Any) -> Tuple[bool, Optional[str]]:
        """Valida que el ID del servicio sea un entero positivo."""
        try:
            if int(id_val) > 0:
                return True, None
            return False, "ID debe ser positivo"
        except (ValueError, TypeError):
            return False, "ID inválido"

    @staticmethod
    def status(current: str, allowed: Tuple) -> bool:
        """Verifica si un estado pertenece a los permitidos."""
        return current in allowed

class ChatPersistence:
    """Gestiona la persistencia del chat en SQLite."""

    @staticmethod
    def init_db():
        """Inicializa esquema de base de datos si no existe."""
        os.makedirs(os.path.dirname(CHAT_DB_PATH), exist_ok=True)
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            with open(CHAT_SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())

    @staticmethod
    def save(name: str, phone: str, msg: str, admin_email: str) -> int:
        """Almacena mensaje de chat."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(SQL_CHAT_INSERT, (name, phone, msg, admin_email))
            return cursor.lastrowid

    @staticmethod
    def get_history(user_id: Optional[str] = None) -> List[Dict]:
        """Recupera historial filtrado por usuario o completo."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if user_id and user_id != WS_SUPPORT_ID:
                cursor.execute(SQL_CHAT_GET_BY_USER, (user_id, user_id))
            else:
                cursor.execute(SQL_CHAT_GET_ALL)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_history(user_id: str):
        """Elimina mensajes asociados a un usuario."""
        with sqlite3.connect(CHAT_DB_PATH) as conn:
            conn.execute(SQL_CHAT_DELETE_BY_USER, (user_id, user_id))

class Help:
    """Fachada para mantener compatibilidad con el código base."""
    
    @staticmethod
    def _generation_id() -> str:
        return str(random.randint(100, 99999999))

    @staticmethod
    def add_generated_id_to_data(data: Dict, key: str) -> Dict:
        if not data.get(key):
            data[key] = int(Help._generation_id())
        return data

    @staticmethod
    def extract_params(data: Dict, cols: List, prefix: str = "p_") -> Dict:
        return Parser.extract(data, cols, prefix)

    @staticmethod
    def extract_params_servicio_json(data: Dict) -> Dict:
        return Parser.extract(data, list(CAMPOS_SERVICIO_JSON))

    # Proxies para compatibilidad
    format_date_colombia = staticmethod(Formatter.to_colombia_date)
    format_currency_colombia = staticmethod(Formatter.to_pesos)
    parse_currency = staticmethod(Formatter.parse_currency)
    map_query_results = staticmethod(Parser.map_results)
    
    init_chat_db = staticmethod(ChatPersistence.init_db)
    save_chat_message = staticmethod(ChatPersistence.save)
    get_chat_history = staticmethod(ChatPersistence.get_history)
    delete_chat_history = staticmethod(ChatPersistence.delete_history)
    
    validate_dashboard_period = staticmethod(Validator.dashboard_period)
    validate_status = staticmethod(Validator.status)
    validate_service_id = staticmethod(Validator.service_id)

    @staticmethod
    def get_dashboard_period_message(period: str) -> str:
        return MENSAJES_PERIODO_DASHBOARD.get(period.lower().strip(), "OK")

    @staticmethod
    def set_resource(model_method: Any, many: bool = False) -> Any:
        """Inyecta recursos desde el JSON a la función decorada."""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                from ..database.schemas import api_search
                from ..helpers.response import notFound
                import inspect
                
                params = api_search.load(request.get_json(force=True) or {})
                sig = inspect.signature(model_method)
                search_args = {k: v for k, v in params.items() if k in sig.parameters and v is not None}
                
                if 'many' in sig.parameters:
                    search_args['many'] = many
                
                res = model_method(**search_args)
                return f(res, *args, **kwargs) if res is not None else notFound()
            return wrapper
        return decorator

    @staticmethod
    def add_default_value_to_data(data: Dict, key: str, val: Any):
        if key not in data:
            data[key] = val
