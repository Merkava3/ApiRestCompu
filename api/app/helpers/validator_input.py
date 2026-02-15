import re
from .const import ALLOWED_DOMAINS


class ValidatorInput:
    @staticmethod
    def validate_register_input(data):
        """
        Valida los datos de entrada para el registro de usuario.
        Retorna (bool, str) indicando exito y mensaje.
        """
        
        # Validar nombre_usuario (solo letras y espacios)
        nombre = data.get('nombre_usuario', '')
        if not nombre or not re.match(r"^[a-zA-Z\s]+$", nombre):
            return False, "El nombre de usuario solo debe contener letras y espacios"

        # Validar email_usuario
        email = data.get('email_usuario', '')
        if not email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return False, "El correo electrónico no es válido"
        
        domain = email.split('@')[1]
        if domain not in ALLOWED_DOMAINS:
            return False, f"Dominio de correo no permitido. Use: {', '.join(ALLOWED_DOMAINS)}"


        # Validar password (exactamente 8 caracteres)
        password = str(data.get('password', ''))
        if len(password) != 8:
            return False, "La contraseña debe tener exactamente 8 caracteres"

        return True, "Validación exitosa"

    @staticmethod
    def validate_service_input(data):
        """
        Valida los datos de entrada para la creación de servicio.
        Retorna (bool, str) indicando éxito y mensaje de error específico.
        """
        
        # Validar cedula (solo números)
        cedula = str(data.get('cedula', ''))
        if not cedula or not re.match(r"^\d+$", cedula):
            return False, "La cédula solo debe contener números"
        
        # Validar nombre_cliente (solo letras con espacios)
        nombre_cliente = data.get('nombre_cliente', '')
        if not nombre_cliente or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre_cliente):
            return False, "El nombre del cliente solo debe contener letras y espacios"
        
        # Validar telefono_cliente (solo números)
        telefono = str(data.get('telefono_cliente', ''))
        if not telefono or not re.match(r"^\d+$", telefono):
            return False, "El teléfono solo debe contener números"
        
        # Validar marca (solo letras)
        marca = data.get('marca', '')
        if not marca or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$", marca):
            return False, "La marca solo debe contener letras (sin espacios)"
        
        # Validar tipo_servicio (solo letras con espacios)
        tipo_servicio = data.get('tipo_servicio', '')
        if not tipo_servicio or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", tipo_servicio):
            return False, "El tipo de servicio solo debe contener letras y espacios"
        
        # Validar modelo (números, letras y espacios, sin caracteres especiales)
        modelo = data.get('modelo', '')
        if not modelo or not re.match(r"^[a-zA-Z0-9\s]+$", modelo):
            return False, "El modelo solo debe contener letras, números y espacios (sin caracteres especiales)"
        
        # Validar reporte (solo letras con espacios)
        reporte = data.get('reporte', '')
        if not reporte or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", reporte):
            return False, "El reporte solo debe contener letras y espacios"
        
        # Validar precio_servicio (solo números)
        precio_servicio = str(data.get('precio_servicio', ''))
        if not precio_servicio or not re.match(r"^\d+$", precio_servicio):
            return False, "El precio del servicio solo debe contener números"
        
        return True, "Validación exitosa"
