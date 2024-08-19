import logging
from models import DBInfo, DBClass

logger = logging.getLogger(__name__)

def send_email_notification(db_info : DBInfo, owner_mail : str, owners_manager_mail : str):
    logger.debug(f"sending email about {db_info.db_name} to {owners_manager_mail}, who is manager of {owner_mail}")
