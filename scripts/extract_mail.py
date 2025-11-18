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

def create_data_directory():
    output_dir_bolle = './data/bolle_pdf'
    output_dir_xc = './data/xc_pdf'
    output_dir_gomme = './data/gomme_pdf'

    os.makedirs(output_dir_bolle, exist_ok=True)
    os.makedirs(output_dir_xc, exist_ok=True)
    os.makedirs(output_dir_gomme, exist_ok=True)

    logging.info(f"Created directories: {output_dir_bolle}, {output_dir_xc}, {output_dir_gomme}")

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
    create_data_directory()
    mail = connect_to_mailbox()
    mail.logout()

if __name__ == "__main__":
    main()
