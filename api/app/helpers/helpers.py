import random
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
            