# -*- coding: utf-8 -*-
"""
Script de prueba para validar el JSON de servicio antes de insertar en la base de datos.
Este script demuestra como la validacion detecta errores en los datos.
"""

import sys
import os

# Agregar el directorio padre al path para importar los modulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.helpers.validator_input import ValidatorInput

# JSON de ejemplo con datos incorrectos
test_data = {
    "usuario_email": "lisa@planta742.com",
    "cedula": "742742742",
    "nombre_cliente": "Homer Simpson",
    "direccion": "742 Evergreen Terrace",
    "telefono_cliente": "555-9393",  # ERROR: contiene guion
    "tipo": "Consola",
    "marca": "KrustyBrand",
    "modelo": "K2000",
    "numero_serie": "sn-4577677",
    "reporte": "Pantalla no enciende",
    "tipo_servicio": "Reparacion",
    "precio_servicio": 150800
}

print("=" * 80)
print("PRUEBA DE VALIDACION DE SERVICIO")
print("=" * 80)
print("\nJSON de entrada:")
print("-" * 80)
for key, value in test_data.items():
    print(f"{key:20} : {value}")
print("-" * 80)

# Validar los datos
is_valid, message = ValidatorInput.validate_service_input(test_data)

print("\n" + "=" * 80)
print("RESULTADO DE LA VALIDACION")
print("=" * 80)
if is_valid:
    print("[OK] Validacion exitosa: Todos los datos son correctos")
else:
    print(f"[ERROR] Error de validacion: {message}")
print("=" * 80)

# Ahora probemos con datos correctos
print("\n\n" + "=" * 80)
print("PRUEBA CON DATOS CORREGIDOS")
print("=" * 80)

test_data_correcto = {
    "usuario_email": "lisa@planta742.com",
    "cedula": "742742742",
    "nombre_cliente": "Homer Simpson",
    "direccion": "742 Evergreen Terrace",
    "telefono_cliente": "5559393",  # CORREGIDO: solo numeros
    "tipo": "Consola",
    "marca": "KrustyBrand",
    "modelo": "K2000",
    "numero_serie": "sn-4577677",
    "reporte": "Pantalla no enciende",
    "tipo_servicio": "Reparacion",
    "precio_servicio": 150800
}

print("\nJSON corregido:")
print("-" * 80)
for key, value in test_data_correcto.items():
    print(f"{key:20} : {value}")
print("-" * 80)

# Validar los datos corregidos
is_valid, message = ValidatorInput.validate_service_input(test_data_correcto)

print("\n" + "=" * 80)
print("RESULTADO DE LA VALIDACION")
print("=" * 80)
if is_valid:
    print("[OK] Validacion exitosa: Todos los datos son correctos")
else:
    print(f"[ERROR] Error de validacion: {message}")
print("=" * 80)

# Pruebas individuales de cada campo
print("\n\n" + "=" * 80)
print("PRUEBAS INDIVIDUALES DE VALIDACION")
print("=" * 80)

test_cases = [
    {
        "nombre": "Cedula con letras",
        "data": {**test_data_correcto, "cedula": "123ABC456"},
        "campo_error": "cedula"
    },
    {
        "nombre": "Nombre con numeros",
        "data": {**test_data_correcto, "nombre_cliente": "Homer123"},
        "campo_error": "nombre_cliente"
    },
    {
        "nombre": "Telefono con guiones",
        "data": {**test_data_correcto, "telefono_cliente": "555-9393"},
        "campo_error": "telefono_cliente"
    },
    {
        "nombre": "Marca con espacios",
        "data": {**test_data_correcto, "marca": "Krusty Brand"},
        "campo_error": "marca"
    },
    {
        "nombre": "Modelo con caracteres especiales",
        "data": {**test_data_correcto, "modelo": "K-2000@"},
        "campo_error": "modelo"
    },
    {
        "nombre": "Reporte con numeros (Debe pasar)",
        "data": {**test_data_correcto, "reporte": "Windows 11 instalado"},
        "campo_error": "reporte",
        "espera_exito": True
    },
    {
        "nombre": "Reporte con caracteres especiales",
        "data": {**test_data_correcto, "reporte": "Dañó la board @#$%"},
        "campo_error": "reporte",
        "espera_exito": False
    },
    {
        "nombre": "Precio con decimales",
        "data": {**test_data_correcto, "precio_servicio": "150.80"},
        "campo_error": "precio_servicio",
        "espera_exito": False
    },
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}. {test_case['nombre']}")
    print(f"   Campo: {test_case['campo_error']} = {test_case['data'][test_case['campo_error']]}")
    is_valid, message = ValidatorInput.validate_service_input(test_case['data'])
    
    espera_exito = test_case.get('espera_exito', False)
    
    if is_valid:
        if espera_exito:
            print(f"   [OK] CORRECTO: Paso la validación como se esperaba")
        else:
            print(f"   [FALLO] Se esperaba error pero paso la validacion")
    else:
        if espera_exito:
            print(f"   [FALLO] Se esperaba exito pero retorno error: {message}")
        else:
            print(f"   [OK] CORRECTO: {message}")

print("\n" + "=" * 80)
print("FIN DE LAS PRUEBAS")
print("=" * 80)
