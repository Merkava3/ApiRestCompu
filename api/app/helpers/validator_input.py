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
        
        # Se remueve la restriccion de dominios permitidos para que pueda ingresar cualquier usuario
        # domain = email.split('@')[1]
        # if domain not in ALLOWED_DOMAINS:
        #     return False, f"Dominio de correo no permitido. Use: {', '.join(ALLOWED_DOMAINS)}"


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
        cedula = str(data.get('cedula', '')).strip()
        if not cedula or not re.match(r"^\d+$", cedula):
            return False, "La cédula solo debe contener números"
        
        # Validar nombre_cliente (letras con espacios y acentos)
        nombre_cliente = str(data.get('nombre_cliente', '')).strip()
        if not nombre_cliente or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre_cliente):
            return False, "El nombre del cliente solo debe contener letras y espacios"
        
        # Validar telefono_cliente (solo números)
        telefono = str(data.get('telefono_cliente', '')).strip()
        if not telefono or not re.match(r"^\d+$", telefono):
            return False, "El teléfono solo debe contener números"
        
        # Validar marca (letras y acentos, sin espacios)
        marca = str(data.get('marca', '')).strip()
        if not marca or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$", marca):
            return False, "La marca solo debe contener letras (sin espacios)"
        
        # Validar tipo_servicio (letras, espacios y acentos)
        tipo_servicio = str(data.get('tipo_servicio', '')).strip()
        if not tipo_servicio or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", tipo_servicio):
            return False, "El tipo de servicio solo debe contener letras y espacios"
        
        # Validar modelo (letras, números, espacios y acentos)
        modelo = str(data.get('modelo', '')).strip()
        if not modelo or not re.match(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$", modelo):
            return False, "El modelo solo debe contener letras, números y espacios (sin caracteres especiales)"
        
        # Validar reporte (letras, números y espacios, sin caracteres especiales)
        # Usamos \w para soportar cualquier letra unicode + números
        reporte = str(data.get('reporte', '')).strip()
        if not reporte or not re.match(r"^[\w\sñÑáéíóúÁÉÍÓÚ]+$", reporte):
            return False, "El reporte solo debe contener letras, números y espacios"
        
        # Validar precio_servicio (solo números)
        precio_servicio = str(data.get('precio_servicio', '')).strip()
        if not precio_servicio or not re.match(r"^\d+$", precio_servicio):
            return False, "El precio del servicio solo debe contener números"
        
        return True, "Validación exitosa"
