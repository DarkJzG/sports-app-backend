from flask_mail import Message
from flask import current_app
from flask_api.extensiones import mail


def enviar_correo_verificacion(destinatario, nombre, token):
    with current_app.app_context():
        msg = Message(
            subject="Verifica tu cuenta en Johan Sports",
            recipients=[destinatario],
            html=f"""
                <h3>Hola {nombre},</h3>
                <p>Gracias por registrarte en Johan Sports.</p>
                <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                <a href="http://192.168.3.175:5000/auth/verificar?token={token}">Verificar cuenta</a>
            """
        )
        mail.send(msg)


def enviar_correo_reset(destinatario, nombre, token):
    with current_app.app_context():
        msg = Message(
            subject="Recuperación de contraseña - Johan Sports",
            recipients=[destinatario],
            html=f"""
                <h3>Hola {nombre},</h3>
                <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en este enlace para definir una nueva contraseña:</p>
                <a href="http://192.168.3.175:3000/restablecer-contrasena?token={token}">Restablecer contraseña</a>
            """
        )
        mail.send(msg)
