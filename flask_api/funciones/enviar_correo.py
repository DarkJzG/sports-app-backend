# flask_api/funciones/enviar_correo.py
from flask_mail import Message
from flask import current_app
from flask_api.extensiones import mail

def enviar_correo_verificacion(destinatario, nombre, token):
    """
    Envía un correo de verificación de cuenta con HTML (UTF-8) usando Flask-Mail.
    """
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
    link = f"{frontend_url}/verificar?token={token}"

    with current_app.app_context():
        msg = Message(
            subject="Verifica tu cuenta en SmartCloth",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[destinatario],
        )

        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background-color: white; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #0a3d91;">¡Hola, {nombre}!</h2>
                    <p>Gracias por registrarte en <b>SmartCloth</b>.</p>
                    <p>Para activar tu cuenta, haz clic en el siguiente botón:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{link}" 
                            style="background-color: #0a3d91; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                            Verificar mi cuenta
                        </a>
                    </div>
                    <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                    <p style="font-size: 12px; color: gray;">{link}</p>
                    <hr/>
                    <p style="font-size: 11px; color: #888;">Este enlace caduca en 24 horas.</p>
                </div>
            </body>
        </html>
        """

        mail.send(msg)
        print(f"📩 Correo de verificación enviado correctamente a {destinatario}")
        return True


def enviar_correo_reset(destinatario, nombre, token):
    """
    Envía un correo de recuperación de contraseña con HTML.
    """
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
    link = f"{frontend_url}/restablecer-contrasena?token={token}"

    with current_app.app_context():
        msg = Message(
            subject="Recuperación de contraseña - SmartCloth",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[destinatario],
        )

        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background-color: white; padding: 20px; border-radius: 10px;">
                    <h3 style="color: #0a3d91;">Hola, {nombre}</h3>
                    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                    <p>Haz clic en el siguiente botón para definir una nueva contraseña:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{link}" 
                            style="background-color: #0a3d91; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                            Restablecer contraseña
                        </a>
                    </div>
                    <p style="font-size: 12px; color: gray;">{link}</p>
                    <hr/>
                    <p style="font-size: 11px; color: #888;">Este enlace caduca en 30 minutos.</p>
                </div>
            </body>
        </html>
        """

        mail.send(msg)
        print(f"📩 Correo de recuperación enviado correctamente a {destinatario}")
        return True
