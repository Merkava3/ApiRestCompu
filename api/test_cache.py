"""
Script de prueba para validar el sistema de caché.
Ejecutar con: python api/test_cache.py
"""
import os
import sys
import time

# Añadir el directorio raíz al path para poder importar el paquete 'api'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.app.cache.cache_manager import (
    CacheManager, InMemoryCache, CacheKeyGenerator, cached
)
from api.app.cache.cache_config import get_ttl, CACHE_CONFIG


def test_inmemory_cache():
    """Test de caché en memoria básico."""
    print("\n" + "="*60)
    print("TEST 1: InMemoryCache - Operaciones Básicas")
    print("="*60)
    
    cache = InMemoryCache(max_size=100)
    
    # Test SET y GET
    cache.set('test_key', {'data': 'test_value'}, ttl=10)
    value = cache.get('test_key')
    assert value == {'data': 'test_value'}, "SET/GET falló"
    print("OK: SET/GET funciona")
    
    # Test EXISTS
    assert cache.exists('test_key'), "EXISTS falló"
    print("OK: EXISTS funciona")
    
    # Test DELETE
    cache.delete('test_key')
    assert not cache.exists('test_key'), "DELETE falló"
    print("OK: DELETE funciona")
    
    # Test CLEAR
    cache.set('key1', 'val1')
    cache.set('key2', 'val2')
    cache.clear()
    assert not cache.exists('key1'), "CLEAR falló"
    print("OK: CLEAR funciona")
    
    # Test TTL expiración
    cache.set('expiring_key', 'value', ttl=1)
    assert cache.get('expiring_key') == 'value', "TTL SET falló"
    time.sleep(1.1)
    assert cache.get('expiring_key') is None, "TTL expiración falló"
    print("OK: TTL expiración funciona")
    
    # Test STATS
    cache.set('key1', 'val1')
    cache.set('key2', 'val2')
    cache.set('key3', 'val3')
    stats = cache.get_stats()
    assert stats['size'] == 3, "STATS falló"
    assert stats['usage_percent'] == 3.0, "STATS porcentaje falló"
    print(f"OK: STATS funciona: {stats}")


def test_cache_key_generator():
    """Test del generador de claves."""
    print("\n" + "="*60)
    print("TEST 2: CacheKeyGenerator")
    print("="*60)
    
    # Sin parámetros
    key1 = CacheKeyGenerator.generate('servicios', 'get_all')
    assert key1 == 'servicios:get_all', "Generación sin parámetros falló"
    print(f"OK: Clave sin params: {key1}")
    
    # Con parámetros
    key2 = CacheKeyGenerator.generate(
        'servicios', 'get_by_cedula',
        {'cedula': '1234567890'}
    )
    assert 'servicios:get_by_cedula:' in key2, "Generación con parámetros falló"
    print(f"OK: Clave con params: {key2}")
    
    # Consistencia
    key3 = CacheKeyGenerator.generate(
        'servicios', 'get_by_cedula',
        {'cedula': '1234567890'}
    )
    assert key2 == key3, "Inconsistencia en generación de clave"
    print("OK: Consistencia de claves validada")


def test_cache_manager_singleton():
    """Test del patrón Singleton."""
    print("\n" + "="*60)
    print("TEST 3: CacheManager - Singleton")
    print("="*60)
    
    mgr1 = CacheManager()
    mgr2 = CacheManager()
    
    assert mgr1 is mgr2, "Singleton falló: instancias diferentes"
    print("OK: Singleton pattern funciona")
    
    # Test que comparten datos
    mgr1.set('shared_key', 'value123')
    value = mgr2.get('shared_key')
    assert value == 'value123', "Managers no comparten datos"
    print("OK: Managers comparten datos")


def test_cache_manager_operations():
    """Test de operaciones del CacheManager."""
    print("\n" + "="*60)
    print("TEST 4: CacheManager - Operaciones")
    print("="*60)
    
    CacheManager().clear()  # Limpiar para test limpio
    mgr = CacheManager()
    
    # Test set y get
    mgr.set('test_key', {'servicios': [1, 2, 3]}, ttl=300)
    value = mgr.get('test_key')
    assert value == {'servicios': [1, 2, 3]}, "CacheManager SET/GET falló"
    print("OK: CacheManager SET/GET funciona")
    
    # Test generate_key
    key = mgr.generate_key('servicios', 'get_all')
    assert key == 'servicios:get_all', "generate_key falló"
    print("OK: CacheManager generate_key funciona")
    
    # Test exists
    assert mgr.exists('test_key'), "CacheManager EXISTS falló"
    print("OK: CacheManager EXISTS funciona")
    
    # Test delete
    mgr.delete('test_key')
    assert not mgr.exists('test_key'), "CacheManager DELETE falló"
    print("OK: CacheManager DELETE funciona")


def test_cache_config():
    """Test de configuración de caché."""
    print("\n" + "="*60)
    print("TEST 5: Cache Configuration")
    print("="*60)
    
    # Test get_ttl
    ttl = get_ttl('servicios', 'get_all')
    assert ttl == 600, f"TTL servicios.get_all debería ser 600, es {ttl}"
    print(f"OK: TTL servicios:get_all = {ttl}s")
    
    ttl = get_ttl('productos', 'get_all')
    assert ttl == 1800, f"TTL productos.get_all debería ser 1800, es {ttl}"
    print(f"OK: TTL productos:get_all = {ttl}s")
    
    ttl = get_ttl('inventario', 'get_all')
    assert ttl == 300, f"TTL inventario.get_all debería ser 300, es {ttl}"
    print(f"OK: TTL inventario:get_all = {ttl}s")
    
    print("OK: Configuración de TTL validada")
    print(f"OK: Total de recursos configurados: {len(CACHE_CONFIG)}")


def test_memory_limit():
    """Test de límite de memoria."""
    print("\n" + "="*60)
    print("TEST 6: Memory Limit")
    print("="*60)
    
    cache = InMemoryCache(max_size=5)
    
    # Llenar caché más allá del límite
    for i in range(10):
        cache.set(f'key_{i}', f'value_{i}')
    
    stats = cache.get_stats()
    assert stats['size'] <= 5, "Límite de memoria no se respeta"
    print(f"OK: Límite de memoria respetado: {stats['size']}/{stats['max_size']}")


def test_thread_safety():
    """Test de thread-safety."""
    print("\n" + "="*60)
    print("TEST 7: Thread Safety")
    print("="*60)
    
    import threading
    
    cache = InMemoryCache(max_size=100)
    results = []
    
    def worker(thread_id):
        for i in range(100):
            cache.set(f'thread_{thread_id}_key_{i}', f'value_{i}')
            cache.get(f'thread_{thread_id}_key_{i}')
    
    threads = []
    for t in range(5):
        thread = threading.Thread(target=worker, args=(t,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    stats = cache.get_stats()
    print(f"OK: 5 threads con 100 operaciones cada una = {stats['size']} entries")
    print("OK: Thread-safety validado (sin crashes)")


def test_cached_decorator():
    """Test del decorador @cached."""
    print("\n" + "="*60)
    print("TEST 8: @cached Decorator")
    print("="*60)
    
    CacheManager().clear()
    
    call_count = 0
    
    @cached(namespace='test', ttl=300, key_params=['param'])
    def expensive_function(param):
        nonlocal call_count
        call_count += 1
        return f'result_{param}_{call_count}'
    
    # Primera llamada
    result1 = expensive_function(param='test')
    assert result1 == 'result_test_1', "Primera llamada falló"
    assert call_count == 1, "call_count debería ser 1"
    print("OK: Primera llamada ejecuta función")
    
    # Segunda llamada con mismo parámetro (desde caché)
    result2 = expensive_function(param='test')
    assert result2 == 'result_test_1', "Debería retornar de caché"
    assert call_count == 1, "call_count debería seguir siendo 1"
    print("OK: Segunda llamada usa caché")
    
    # Tercera llamada con parámetro diferente
    result3 = expensive_function(param='different')
    assert result3 == 'result_different_2', "Parámetro diferente falló"
    assert call_count == 2, "call_count debería ser 2"
    print("OK: Parámetro diferente ejecuta función nuevamente")


def main():
    """Ejecutar todos los tests."""
    print("\n" + "* "*20)
    print("PRUEBAS DEL SISTEMA DE CACHÉ")
    print("* "*20)
    
    try:
        test_inmemory_cache()
        test_cache_key_generator()
        test_cache_manager_singleton()
        test_cache_manager_operations()
        test_cache_config()
        test_memory_limit()
        test_thread_safety()
        test_cached_decorator()
        
        print("\n" + "="*60)
        print("OK: TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
        return 0
        
    except AssertionError as e:
        print(f"\nERROR EN TEST: {e}\n")
        return 1
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
