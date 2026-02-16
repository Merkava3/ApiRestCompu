from flask import Blueprint, request, jsonify
from ..models import db
from ..helpers.response import successfully, badRequest, serverError
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors
from ..helpers.helpers import Help
from ..models.auth_decorator import token_required
from sqlalchemy import text

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/dashboard/resumen', methods=['GET'])
@token_required
@handle_endpoint_errors
def get_dashboard_resumen():
    """
    Obtiene el resumen general del dashboard.
    Ejecuta la función fn_dashboard_resumen() que retorna:
    - ganancias_hoy: Ganancias del día actual con fecha y total
    - resumen_mensual: Resumen de clientes, servicios y ganancias por mes
    - dispositivos_por_mes: Total de dispositivos por mes
    """
    try:
        # Ejecutar la función fn_dashboard_resumen() que retorna JSONB
        query = text("SELECT fn_dashboard_resumen()")
        result = db.session.execute(query)

        # Obtener el resultado (es un JSONB que se convierte automáticamente a dict)
        row = result.fetchone()

        if row and row[0]:
            dashboard_data = dict(row[0])

            # Process data as requested
            from datetime import datetime
            current_year = datetime.now().year
            

            
            if 'dispositivos_por_mes' in dashboard_data and isinstance(dashboard_data['dispositivos_por_mes'], list):
                # Filter by current year
                dashboard_data['dispositivos_por_mes'] = [
                    item for item in dashboard_data['dispositivos_por_mes']
                    if item.get('anio') == current_year
                ]
            return successfully(dashboard_data, "Dashboard cargado exitosamente")

        return badRequest("No se pudo obtener el resumen del dashboard")

    except Exception as e:
        db.session.rollback()
        print(f"Error al obtener resumen del dashboard: {e}")
        return serverError(f"Error al obtener el resumen del dashboard: {str(e)}")


@dashboard_routes.route('/dashboard/estadisticas', methods=['GET'])
@token_required
@handle_endpoint_errors
def get_dashboard_estadisticas():
    """
    Obtiene estadísticas del dashboard por período.
    Ejecuta la función fn_dashboard_estadisticas(periodo) que retorna:
    - Datos agrupados por período (monthly, quarterly, annually)
    - Información de servicios, dispositivos y ganancias

    Query Parameters:
        periodo (str): Tipo de período - 'monthly', 'quarterly', 'annually'

    Returns:
        JSON: Estadísticas formateadas según el período solicitado
    """
    try:
        # Obtener y validar parámetro de período usando helper
        periodo = request.args.get('periodo', '')

        # Validar período usando función helper (principio DRY)
        es_valido, mensaje_error = Help.validate_dashboard_period(periodo)
        if not es_valido:
            return badRequest(mensaje_error)

        # Limpiar período para uso en consulta
        periodo_clean = periodo.lower().strip()

        # Ejecutar función de PostgreSQL con parámetro validado
        query = text("SELECT fn_dashboard_estadisticas(:periodo)")
        result = db.session.execute(query, {'periodo': periodo_clean})

        # Procesar resultado
        row = result.fetchone()

        if row and row[0]:
            estadisticas_data = row[0]

            # Obtener mensaje descriptivo usando helper
            mensaje = Help.get_dashboard_period_message(periodo_clean)

            return successfully(estadisticas_data, mensaje)

        return badRequest(f"No se pudieron obtener estadísticas para el período '{periodo}'")

    except Exception as e:
        db.session.rollback()
        print(f"Error al obtener estadísticas del dashboard: {e}")
        return serverError(f"Error al obtener estadísticas del dashboard: {str(e)}")


@dashboard_routes.route('/dashboard/pie-estado-mes', methods=['GET'])
@token_required
def get_dashboard_pie_estado_mes():
    """
    Obtiene los datos para el gráfico de torta de estados del mes actual.
    Ejecuta la función fn_dashboard_pie_estado_mes_actual() que retorna JSONB.
    """
    try:
        # Ejecutar la función directamente sin usar modelos ni helpers
        query = text("SELECT fn_dashboard_pie_estado_mes_actual()")
        result = db.session.execute(query)
        row = result.fetchone()

        if row and row[0]:
            # Retorna el JSONB directamente como un diccionario de Python
            return jsonify(row[0]), 200

        return jsonify({"error": "No se encontraron datos para el mes actual"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@dashboard_routes.route('/dashboard/bar-meses-anio', methods=['GET'])
@token_required
def get_dashboard_bar_meses_anio():
    """
    Obtiene los datos para el gráfico de barras por meses del año actual.
    Ejecuta la función fn_dashboard_bar_meses_anio_actual() que retorna JSONB.
    """
    try:
        # Ejecutar la función directamente sin usar modelos ni helpers
        query = text("SELECT fn_dashboard_bar_meses_anio_actual()")
        result = db.session.execute(query)
        row = result.fetchone()

        if row and row[0]:
            # Retorna el JSONB directamente como un diccionario de Python
            return jsonify(row[0]), 200

        return jsonify({"error": "No se encontraron datos para el año actual"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

