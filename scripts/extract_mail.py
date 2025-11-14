import email
import imaplib
import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def connect_to_mailbox():
    username = os.getenv('USERNAME')
    print(username)
    password = os.getenv('PASSWORD')
    imap_server = os.getenv('IMAP_SERVER')

    try:
        logging.info(f"Connection to IMAP server: {imap_server} with user: {username}")
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        
        return mail
    except imaplib.IMAP4.error as exc:
        logging.error(f"Authentication failed: {exc}")
        raise

def main():
    mail = connect_to_mailbox()
    mail.logout()

if __name__ == "__main__":
    main()
