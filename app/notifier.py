import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_email_notification(db_name : str, owner_mail : str, owners_manager_mail : str):
    logger.debug(f"sending email about {db_name} to {owners_manager_mail}, who is manager of {owner_mail}")
    sender = 'noreply@meli.local'
    receiver = owners_manager_mail
    body = f"""
Hola!

Este mail es enviado automáticamente para recordarle que revisar la base de datos {db_name}, actualmente clasificada con criticidad ALTA, junto a su dueño: {owner_mail}.

Este correo lo recibió ya que usted está asignado como líder del dueño del activo.

Muchas gracias por su colaboración!

Equipo de MeLI :)
"""
    msg = MIMEMultipart()
    msg['Subject'] = f"Revisión de la DB {db_name}"
    msg['From'] = sender
    msg['To'] = receiver
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(os.environ['MAIL_SERVER'], os.environ['MAIL_PORT']) as server:
            server.sendmail(sender, [receiver], msg.as_string())
            logger.debug('mail sent successfully')
    except Exception as e:
        logger.error(f"Error sending mail to {owners_manager_mail} : {repr(e)}")
        return False
    return True

