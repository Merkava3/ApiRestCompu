import random
import json

class Help:
    @staticmethod
    def _generation_id() -> str:    
        digitos: int  = random.randint(3, 8)
        numero: int  = random.randint(10**(digitos-1), 10**digitos - 1)
        return str(numero)

    @staticmethod
    def generator_id(objeto: any, atributo: str) -> any:

        """Asigna un ID generado al atributo especificado de un objeto.

        Args:
            objeto (Any): El objeto al que se le asignará el ID.
            atributo (str): Nombre del atributo donde se guardará el ID.

        Returns:
            Any: El objeto modificado con el ID asignado.
        
        Raises:
            AttributeError: Si el objeto no tiene el atributo especificado.
        """

        if hasattr(objeto, atributo):  # Verifica si el objeto tiene el atributo
            setattr(objeto, atributo, Help._generation_id())  # Asigna el nuevo ID
        else:
            raise AttributeError(f"El objeto no tiene el atributo '{atributo}'")
        return objeto
    
    @staticmethod
    def extract_params_factura(data, column_list):
        """
        Extrae los valores de un diccionario según una lista de claves.
        Convierte listas o diccionarios en JSON si es necesario.
        """
        extracted_data = {}
        
        for column in column_list:
            value = data.get(column)
            
            # Asegurar que productos se almacene como JSON correctamente
            if column == "productos" and isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)  # Convertir lista a JSON
            
            extracted_data[f"p_{column}"] = value
        
        return extracted_data
    
    @staticmethod
    def extract_params_compra(data,  COLUMN_LIST_COMPRA):
        """
        Extrae los valores de un diccionario según una lista de claves.
        Convierte listas o diccionarios en JSON si es necesario.
        """
        extracted_data = {}

        for column in COLUMN_LIST_COMPRA:
            value = data.get(column)
            if column == "productos" and isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)  # Convertir lista a JSON
            
            extracted_data[f"p_{column}"] = value

        return extracted_data
    
    @staticmethod
    def extract_params_inventario(data, column_list):
        """
        Extrae los valores de un diccionario según una lista de claves.
        Convierte listas o diccionarios en JSON si es necesario.
        """
        extracted_data = {}
        
        for column in column_list:
            value = data.get(column)
            
            # Asegurar que productos se almacene como JSON correctamente
            if column == "productos" and isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)  # Convertir lista a JSON
            
            extracted_data[f"p_{column}"] = value
        
        return extracted_data
    
    @staticmethod
    def extract_params_cliente_dispositivo(data, column_list):
        """
        Extrae los valores de un diccionario según una lista de claves.
        Convierte listas o diccionarios en JSON si es necesario.
        """
        extracted_data = {}

        for column in column_list:
            value = data.get(column)

            # Si es una lista o diccionario, convertirlo a JSON
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)

            extracted_data[f"p_{column}"] = value
        return extracted_data
    
    @staticmethod
    def extract_params_servicio(data, column_list):
        """
        Extrae los valores de un diccionario según una lista de claves.
        Convierte listas o diccionarios en JSON si es necesario.
        """
        extracted_data = {}

        for column in column_list:
            value = data.get(column)

            # Si es una lista o diccionario, convertirlo a JSON
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)

            extracted_data[f"p_{column}"] = value
        return extracted_data
    
    @staticmethod
    def add_generated_id_to_data(data: dict, id_key: str) -> dict:
        """
        Genera un ID aleatorio y lo agrega al diccionario data si no existe o está vacío.
        
        Args:
            data (dict): Diccionario al que se le agregará el ID generado.
            id_key (str): Clave del diccionario donde se guardará el ID.
        
        Returns:
            dict: El diccionario modificado con el ID generado (si no existía).
        """
        if id_key not in data or not data.get(id_key):
            data[id_key] = Help._generation_id()
        return data
       

                