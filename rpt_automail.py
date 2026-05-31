import os
import logging
import pypdf
import pandas as pd
from email.message import EmailMessage
import smtplib
import send2trash

class NRExtractor:

    def __init__(self, pdf_path:str):
        self.pdf_path = pdf_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def extract_NR_pypdf(self) -> int:
        reader = pypdf.PdfReader(self.pdf_path)
        text = reader.pages[0].extract_text()

        found = False
        
        for line in text.split("\n"):
            if line.startswith("TRAVAILLEUR"):
                found = True
                break

        if not found:
            raise Exception("No NISS found in pdf {self.pdf_path}")

        return int(line[13:34].replace(" ",""))


class xlsxData:

    def __init__(self, xlsx_path : str, RN_column_name : str):
        self.xlsx_path = xlsx_path
        self.RN_column_name = RN_column_name
        self.tab = None 

        self.import_xlsx(self.xlsx_path)

    def import_xlsx(self, path : str):
        self.tab = pd.read_excel(path)
            
    def return_from_RN(self, RN : int) -> dict:
        res = self.tab.loc[self.tab[self.RN_column_name] == RN]

        
        if len(res) != 1:
            raise ValueError(
                f"Expected exactly one entry for {RN}, found {len(res)}"
            )
            
        return res.iloc[0].to_dict()




def send_all_emails(config : dict):
    xlsx_data = xlsxData(config["xlsx_path"], config["colonne_registre_national"])
    
    files = []
    for f in os.listdir(config["to_send_folder_path"]):
        if f.endswith('_signe.pdf'):
            files.append(os.path.join(config["to_send_folder_path"], f))
    logging.info(f"Found {len(files)} pdf")
    
    for f in files:
        with NRExtractor(f) as ext:
            NR = ext.extract_NR_pypdf()
        pdict = xlsx_data.return_from_RN(NR)
    
        with open(f, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        
        msg = EmailMessage()
        msg["to"] = pdict[config['colonne_mail']]
        msg["from"] = config["sender_email"]
        msg["subject"] = config["mail_subject"]
        msg.set_content(config["mail_body"])
        
        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(f)
        )
    
        logging.info(f"Envoi à {pdict[config['colonne_prenom']]} {pdict[config['colonne_nom']]} ({pdict[config['colonne_mail']]})")    
        with smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"]) as server:
            # server.set_debuglevel(1)
            if config["enable_starttls"]:
                server.starttls()
            server.login(config['sender_email'], config['sender_pwd'])
            # server.send_message(msg)

        if config["delete_after_sent"]:
            # os.remove(f)
            send2trash.send2trash(f)
