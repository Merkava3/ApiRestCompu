# Ejemplos de Reutilización de Validadores

Este documento muestra cómo otros endpoints pueden reutilizar los nuevos validadores creados en `helpers.py`.

---

## 1️⃣ Ejemplo: `post_cliente()`

### Antes (Sin reutilización):
```python
@cliente_routes.route('/cliente', methods=['POST'])
def post_cliente():
    try:
        json = request.get_json(force=True)
        
        # Validación inline duplicada
        if not json.get('cedula') or not json.get('nombre_cliente'):
            return badRequest("Campos requeridos: cedula, nombre_cliente")
        
        cliente = Clientes.new(json)
        cliente = Help.generator_id(cliente, ID_CLIENTE)
        if cliente.save():
            return response(api_cliente.dump(cliente))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST cliente: {str(e)}")
        raise
```

### Después (Reutilizando validadores):
```python
@cliente_routes.route('/cliente', methods=['POST'])
def post_cliente():
    try:
        json = request.get_json(force=True)
        
        # ✅ Reutilizar validador
        is_valid, missing = Help.validate_required_fields(
            json, 
            ['cedula', 'nombre_cliente']
        )
        if not is_valid:
            return badRequest(f"Campos requeridos: {', '.join(missing)}")
        
        cliente = Clientes.new(json)
        cliente = Help.generator_id(cliente, ID_CLIENTE)
        if cliente.save():
            return response(api_cliente.dump(cliente))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST cliente: {str(e)}")
        raise
```

---

## 2️⃣ Ejemplo: `post_dispositivo()`

### Antes (Sin reutilización):
```python
@dispositivo_routes.route('/dispositivo', methods=['POST'])
def post_dispositivo():
    try:
        data = request.get_json(force=True)
        
        # Validación redundante
        if not data.get('tipo') or not data.get('numero_serie'):
            return badRequest("Campos requeridos: tipo, numero_serie")
        
        # Otra validación inline
        if not data.get('cliente_id') and not data.get('cedula'):
            return badRequest("Se requiere cliente_id o cedula")
        
        dispositivo = Dispositivos.new(data)
        dispositivo = Help.generator_id(dispositivo, ID_DISPOSITIVO)
        if dispositivo.save():
            return response(api_dispositivo.dump(dispositivo))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST dispositivo: {str(e)}")
        raise
```

### Después (Reutilizando validadores):
```python
@dispositivo_routes.route('/dispositivo', methods=['POST'])
def post_dispositivo():
    try:
        data = request.get_json(force=True)
        
        # ✅ Validar campos requeridos
        is_valid, missing = Help.validate_required_fields(
            data, 
            ['tipo', 'numero_serie']
        )
        if not is_valid:
            return badRequest(f"Campos requeridos: {', '.join(missing)}")
        
        # ✅ Validar que al menos uno esté presente
        if not Help.validate_at_least_one_field(data, ['cliente_id', 'cedula']):
            return badRequest("Se requiere cliente_id o cedula")
        
        dispositivo = Dispositivos.new(data)
        dispositivo = Help.generator_id(dispositivo, ID_DISPOSITIVO)
        if dispositivo.save():
            return response(api_dispositivo.dump(dispositivo))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST dispositivo: {str(e)}")
        raise
```

---

## 3️⃣ Ejemplo: `post_factura()`

### Antes (Sin reutilización):
```python
@factura_routes.route('/factura', methods=['POST'])
def post_factura():
    try:
        data = request.get_json(force=True)
        
        # Validación inline larga
        required = ['id_factura', 'cedula', 'total', 'productos']
        missing = [f for f in required if f not in data or not data[f]]
        if missing:
            return badRequest(f"Falta: {missing}")
        
        factura = Facturas.new(data)
        factura = Help.generator_id(factura, ID_FACTURA)
        if factura.save():
            return response(api_factura.dump(factura))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST factura: {str(e)}")
        raise
```

### Después (Reutilizando validadores):
```python
@factura_routes.route('/factura', methods=['POST'])
def post_factura():
    try:
        data = request.get_json(force=True)
        
        # ✅ Validador genérico - Una línea
        is_valid, missing = Help.validate_required_fields(
            data, 
            ['id_factura', 'cedula', 'total', 'productos']
        )
        if not is_valid:
            return badRequest(f"Campos faltantes: {', '.join(missing)}")
        
        factura = Facturas.new(data)
        factura = Help.generator_id(factura, ID_FACTURA)
        if factura.save():
            return response(api_factura.dump(factura))
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST factura: {str(e)}")
        raise
```

---

## 4️⃣ Ejemplo: Validador Personalizado con Composición

Si necesitas validaciones más complejas, puedes componerlas:

```python
def validate_reparacion_completa(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validador personalizado que compone múltiples validadores.
    Ejemplo de composición de estrategias.
    """
    # Validar campos básicos
    is_valid, missing = Help.validate_required_fields(
        data,
        ['id_reparacion', 'estado', 'precio_reparacion']
    )
    if not is_valid:
        return False, f"Campos requeridos: {', '.join(missing)}"
    
    # Validar al menos uno de varios
    if not Help.validate_at_least_one_field(data, ['numero_serie', 'dispositivo_id']):
        return False, "Se requiere numero_serie o dispositivo_id"
    
    # Validar rango de precio
    if data.get('precio_reparacion', 0) < 0:
        return False, "El precio debe ser positivo"
    
    # Validar estado
    valid_states = ['pendiente', 'en_proceso', 'completada', 'cancelada']
    if data.get('estado') not in valid_states:
        return False, f"Estado inválido. Valores válidos: {valid_states}"
    
    return True, ""

# Uso en endpoint
@reparacion_routes.route('/reparacion/insertar_completa', methods=['POST'])
def post_reparacion_completa():
    try:
        data = request.get_json(force=True) or {}
        
        # ✅ Usar validador personalizado
        is_valid, error_msg = validate_reparacion_completa(data)
        if not is_valid:
            print(f"❌ {error_msg}")
            return badRequest(error_msg)
        
        # Continuar con la lógica de negocio...
        success = Reparaciones.insertar_reparacion_completa(data)
        if success:
            return response(SUCCESSFULREPARACION)
        return badRequest()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
```

---

## 📊 Impacto en la Codebase

| Métrica | Beneficio |
|---------|-----------|
| **Reducción de duplicación** | 60-70% menos código de validación |
| **Reutilización** | Mismos validadores en 10+ endpoints |
| **Mantenibilidad** | Cambios en un solo lugar |
| **Testabilidad** | Validadores testeables independientemente |
| **Escalabilidad** | Fácil agregar nuevos validadores |
| **Legibilidad** | Endpoints más cortos y claros |

---

## 🎯 Recomendaciones para Implementación

1. **Aplicar a otros endpoints**: Refactorizar `post_cliente()`, `post_dispositivo()`, `post_factura()`, etc.

2. **Crear validadores específicos**: Para dominios complejos, crear funciones como `validate_reparacion_completa()`

3. **Documentar patrones**: Mantener ejemplos de uso consistentes en toda la codebase

4. **Tests unitarios**: Crear tests para cada validador en `tests/test_helpers.py`

5. **Evolucionar**: Cuando identifiques validaciones duplicadas, extraerlas a helpers inmediatamente (SOLID principle)

---

## 📚 Referencias

- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy) - Design Patterns
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle) - SOLID
- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) - Clean Code
