import unittest
import json
from app import create_app
from app.models import db, Cliente
from config import config

class TestClienteEndpoint(unittest.TestCase):
    def setUp(self):
        """Configura un entorno de prueba con una base de datos temporal."""
        self.app = create_app(config['test'])
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Insertar un cliente de prueba
            cliente = Cliente(cedula="9999", nombre_cliente="Test User", direccion="Test Address", telefono_cliente="123456789")
            db.session.add(cliente)
            db.session.commit()
    
    def tearDown(self):
        """Elimina la base de datos de prueba después de cada test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_cliente(self):
        """Prueba el endpoint GET /api/v1/cliente con una cédula existente."""
        response = self.client.get('/api/v1/cliente', json={"cedula": "9999"})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("cedula", data["data"])
        self.assertEqual(data["data"]["cedula"], "9999")

if __name__ == '__main__':
    unittest.main()
