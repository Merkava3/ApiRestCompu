#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la configuración del WebSocket.
Ejecutar desde la raíz del proyecto: python websocket_diagnostics.py
"""
import sys
import os
import subprocess
import importlib

def check_python_version():
    """Verifica la versión de Python."""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Advertencia: Se recomienda Python 3.8 o superior")
    else:
        print("✅ Versión de Python compatible")
    return True

def check_package_installation(package_name, import_name=None):
    """Verifica si un paquete está instalado y se puede importar."""
    if import_name is None:
        import_name = package_name.replace('-', '_')

    try:
        # Verificar instalación con pip
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name],
                              capture_output=True, text=True)
        installed = result.returncode == 0

        if installed:
            # Extraer versión
            lines = result.stdout.split('\n')
            version = None
            for line in lines:
                if line.startswith('Version:'):
                    version = line.split(':', 1)[1].strip()
                    break

            # Verificar importación
            try:
                importlib.import_module(import_name)
                print(f"✅ {package_name} v{version} - Instalado e importable")
                return True
            except ImportError as e:
                print(f"⚠️  {package_name} v{version} - Instalado pero no se puede importar: {e}")
                return False
        else:
            print(f"❌ {package_name} - No instalado")
            return False

    except Exception as e:
        print(f"❌ Error verificando {package_name}: {e}")
        return False

def check_websocket_dependencies():
    """Verifica todas las dependencias necesarias para WebSocket."""
    print("\n📦 Verificando dependencias WebSocket:")
    print("-" * 50)

    dependencies = [
        ('flask', 'flask'),
        ('flask-sock', 'flask_sock'),
        ('simple-websocket', 'simple_websocket'),
        ('flask-cors', 'flask_cors')
    ]

    all_ok = True
    for package, import_name in dependencies:
        if not check_package_installation(package, import_name):
            all_ok = False

    return all_ok

def check_flask_app_structure():
    """Verifica la estructura de la aplicación Flask."""
    print("\n📁 Verificando estructura del proyecto:")
    print("-" * 50)

    required_files = [
        'api/app/__init__.py',
        'api/app/websocket_config.py',
        'api/app/helpers/websocket_services.py',
        'api/app/views.py',
        'start_server.py'
    ]

    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - No encontrado")
            all_ok = False

    return all_ok

def test_websocket_imports():
    """Prueba importar los módulos WebSocket."""
    print("\n🔬 Probando importaciones WebSocket:")
    print("-" * 50)

    imports_to_test = [
        ('flask_sock', 'from flask_sock import Sock'),
        ('simple_websocket', 'import simple_websocket'),
        ('websocket_config', 'from api.app.websocket_config import init_websocket, check_websocket_health'),
        ('websocket_services', 'from api.app.helpers.websocket_services import WebSocketConnectionManager')
    ]

    all_ok = True
    for name, import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"✅ {name} - Importación exitosa")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
            all_ok = False

    return all_ok

def check_database_files():
    """Verifica archivos relacionados con la base de datos de chat."""
    print("\n💾 Verificando configuración de base de datos:")
    print("-" * 50)

    try:
        # Verificar que el directorio database existe
        db_dir = 'api/app/database'
        if os.path.exists(db_dir):
            print(f"✅ Directorio {db_dir} existe")
        else:
            print(f"⚠️  Directorio {db_dir} no existe")

        # Verificar schemas.sql
        schema_file = os.path.join(db_dir, 'schemas.sql')
        if os.path.exists(schema_file):
            print(f"✅ {schema_file} existe")
        else:
            print(f"⚠️  {schema_file} no existe")

        return True
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def test_websocket_health_endpoint():
    """Prueba el endpoint de salud del WebSocket."""
    print("\n🏥 Probando funcionalidad de diagnóstico:")
    print("-" * 50)

    try:
        from api.app.websocket_config import check_websocket_health
        health_status = check_websocket_health()

        print("Resultado del diagnóstico WebSocket:")
        for key, value in health_status.items():
            status_emoji = "✅" if value else "❌" if isinstance(value, bool) else "ℹ️"
            print(f"  {status_emoji} {key}: {value}")

        overall_healthy = health_status.get('status') == 'healthy'
        return overall_healthy

    except Exception as e:
        print(f"❌ Error ejecutando diagnóstico: {e}")
        return False

def provide_solutions():
    """Proporciona soluciones para problemas comunes."""
    print("\n🔧 Soluciones para problemas comunes:")
    print("-" * 50)
    print("1. Si flask-sock no está instalado:")
    print("   pip install flask-sock")
    print("\n2. Si simple-websocket no está instalado:")
    print("   pip install simple-websocket")
    print("\n3. Para instalar todas las dependencias:")
    print("   pip install -r requirements.txt")
    print("\n4. Para probar la conexión WebSocket manualmente:")
    print("   - Iniciar el servidor: python start_server.py")
    print("   - Abrir navegador en: http://localhost:5000/api/v1/health/websocket")
    print("\n5. Si persisten errores de conexión:")
    print("   - Verificar firewall/antivirus")
    print("   - Probar con otro puerto")
    print("   - Revisar logs del servidor para errores específicos")

def main():
    """Función principal del diagnóstico."""
    print("🔍 DIAGNÓSTICO WEBSOCKET - API REST COMPU")
    print("=" * 60)

    checks = [
        ("Versión de Python", check_python_version),
        ("Dependencias WebSocket", check_websocket_dependencies),
        ("Estructura del proyecto", check_flask_app_structure),
        ("Importaciones WebSocket", test_websocket_imports),
        ("Configuración de BD", check_database_files),
        ("Funcionalidad de diagnóstico", test_websocket_health_endpoint)
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error en {check_name}: {e}")
            results.append(False)

    # Resumen final
    print("\n📊 RESUMEN DEL DIAGNÓSTICO:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    for i, (check_name, _) in enumerate(checks):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {check_name}")

    print(f"\nResultado: {passed}/{total} verificaciones pasaron")

    if passed == total:
        print("\n🎉 ¡Todos los diagnósticos pasaron! WebSocket debería funcionar correctamente.")
        print("💡 Si aún hay problemas, verificar:")
        print("   - Que el servidor esté ejecutándose en el puerto correcto")
        print("   - Configuración del firewall/proxy")
        print("   - Logs del navegador para errores específicos")
    else:
        print(f"\n⚠️  {total - passed} verificaciones fallaron.")
        provide_solutions()

    print("\n" + "=" * 60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
