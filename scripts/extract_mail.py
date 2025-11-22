import email
import imaplib
import logging
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email.header import decode_header

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
    output_dir_gomme = './data/gomme_txt'

    os.makedirs(output_dir_bolle, exist_ok=True)
    os.makedirs(output_dir_xc, exist_ok=True)
    os.makedirs(output_dir_gomme, exist_ok=True)

    logging.info(f"Created directories: {output_dir_bolle}, {output_dir_xc}, {output_dir_gomme}")

def decode_subject(subject):
    decoded_parts = decode_header(subject)
    subject_decoded = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            subject_decoded += part.decode(encoding or "utf-8", errors="ignore")
        else:
            subject_decoded += part
    return subject_decoded

def connect_to_mailbox():
    username = os.getenv('USERNAME')
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

def save_bolla_or_xc(part, content_type, content_disposition, output_dir):
    logging.info(f"Content type: {content_type}, Disposition: {content_disposition}")

    if content_type == "application/octet-stream" and "attachment" in content_disposition:
        filename = part.get_filename()

        if filename:
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                logging.info(f"PDF saved: {filepath}")
            except Exception as e:
                logging.error(f"Error while saving PDF: {e}")

def extract_gomme_data(email_msg, output_dir):
    # Get the HTML body from the email
    html_body = None
    for part in email_msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True)
            break

    if not html_body:
        logging.warning("No HTML body found in this email")
        return

    soup = BeautifulSoup(html_body, "lxml")

    # Extract all table cells (td)
    cells = [td.get_text(strip=True) for td in soup.find_all("td")]

    if not cells:
        logging.warning("No table data found")
        return

    # Try to find the value next to "Totale ordine"
    totale_ordine = None
    for i, cell in enumerate(cells):
        if "Totale ordine" in cell:
            # Get the following cell
            totale_ordine = cells[i + 1] if i + 1 < len(cells) else None
            break

    if totale_ordine is None:
        logging.warning("Totale ordine not found")
        return

    logging.info(f"Totale ordine: {totale_ordine}")

    # Save to a txt file
    output_path = f"{output_dir}/gomme_totali.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"{totale_ordine}\n")

    logging.info(f"Saved totale ordine to {output_path}")


def fetch_emails(mail): 
    logging.info("Selecting INBOX")

    mail.select("inbox")
    distpatcher = os.getenv('DISTPATCHER_EMAIL')
    start_date = os.getenv('EMAIL_START_DATE')
    end_date = os.getenv('EMAIL_END_DATE')
    search_criteria = f'(FROM "{distpatcher}" SINCE {start_date} BEFORE {end_date})'

    result, data = mail.search(None, search_criteria)
    
    if result != 'OK':
        logging.error("Failed to search emails.")
        return

    email_ids = data[0].split()
    logging.info(f"Find {len(email_ids)} emails")

    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        if result != 'OK':
            logging.error(f"Failed to fetch email ID {email_id}")
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                email_msg = email.message_from_bytes(response_part[1])

                raw_subject = email_msg["Subject"]
                subject = decode_subject(raw_subject).strip()
                logging.info(f"Email subject: {subject}")

                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if subject and subject.startswith("Invio BL-"):
                        save_bolla_or_xc(part, content_type, content_disposition, output_dir='./data/bolle_pdf')
                    elif subject and subject.startswith("Invio XC-"):
                        save_bolla_or_xc(part, content_type, content_disposition, output_dir='./data/xc_pdf')
                        
                if subject and subject.startswith("Notifica ordine cliente (201614 G)"):
                    extract_gomme_data(email_msg, output_dir='./data/gomme_txt')

def main():
    create_data_directory()
    mail = connect_to_mailbox()
    fetch_emails(mail)
    mail.logout()

if __name__ == "__main__":
    main()
