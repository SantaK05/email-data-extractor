run-bolle-xc:
    @USERNAME=gekocar.mi@gmail.com \
    PASSWORD="ylpu exxn bjgw xlnb" \
    IMAP_SERVER=imap.gmail.com \
    DISTPATCHER_EMAIL=fcarsrl@sefin.it \
    EMAIL_START_DATE=01-Nov-2025 \
    EMAIL_END_DATE=01-Dic-2025 \
    python3 scripts/extract_mail.py

run-gomme:
    @USERNAME=gekocar.mi@gmail.com \
    PASSWORD="ylpu exxn bjgw xlnb" \
    IMAP_SERVER=imap.gmail.com \
    DISTPATCHER_EMAIL=noreply@francogomme.it \
    EMAIL_START_DATE=01-Sep-2025 \
    EMAIL_END_DATE=01-Dic-2025 \
    python3 scripts/extract_mail.py

# Switch to secrets.yml 