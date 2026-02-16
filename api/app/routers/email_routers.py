from flask import Blueprint, request
from ..email.mailer import mailer
from ..helpers.response import successfully, badRequest
from ..models.auth_decorator import token_required

email_routes = Blueprint('email_routes', __name__)

@email_routes.route('/send-email', methods=['POST'])
@token_required
def post_email():
    """
    Endpoint para enviar correos electrónicos.
    Espera un JSON con: subject, body, to
    """
    data = request.get_json(force=True)
    
    if not data:
        return badRequest("Datos JSON requeridos")

    subject = data.get('subject')
    body = data.get('body')
    to = data.get('to')

    if not subject or not body or not to:
        return badRequest("Campos 'subject', 'body' y 'to' son requeridos")

    # Depuración para ver qué se está enviando
    print(f"\n--- DEBUG EMAIL ---\nTo: {to}\nSubject: {subject}\nBody: {body}\n-------------------\n")

    if mailer.send_email(subject, body, to):
        return successfully(message="Correo enviado exitosamente")
    
    return badRequest("No se pudo enviar el correo. Verifique la configuración o los datos.")
