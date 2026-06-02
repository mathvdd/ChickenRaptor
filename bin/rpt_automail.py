import os
import logging
import pypdf
import pandas as pd
from email.message import EmailMessage
import smtplib
from datetime import datetime
from rpt_config import validate_date

class NRExtractor:

    def __init__(self, pdf_path:str):
        self.pdf_path = pdf_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def extract(self) -> dict:
        res = {
            "RN":None,
            "date_in":None,
            "date_out":None
            }

        with open(self.pdf_path, "rb") as fp:
            reader = pypdf.PdfReader(fp)
            text = reader.pages[0].extract_text()
        
        for line in text.split("\n"):

            if line.startswith("TRAVAILLEUR"):
                res["RN"] = int(line[13:34].replace(" ",""))
            elif line.startswith("Date de début de l'occupation"):
                date = line[31:48].replace(" ","")
                validate_date(date)
                res["date_in"] = date

            elif line.startswith("Date de fin de l'occupation"):
                date = line[29:46].replace(" ","")
                validate_date(date)
                res["date_out"] = date

            if not (None in res.values()):
                return res

        raise ValueError(f"Could not extract info from {self.pdf_path}: {res}")

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
    xlsx_data = xlsxData(config["xlsx_path"].get_value(), config["colonne_registre_national"].get_value())
    
    files = []
    for f in os.listdir(config["to_send_folder_path"].get_value()):
        if f.endswith('_signe.pdf'):
            files.append(os.path.join(config["to_send_folder_path"].get_value(), f))
    logging.info(f"Found {len(files)} pdf")
    
    def replace_in_text(to_parse : str, replace : dict, log_name : str):
        # check if parse words are known or throw an error
        for key, value in replace.items():
            if "{" + key + "}" in to_parse:
                to_parse = to_parse.replace("{" + key + "}", value)
        if (to_parse.count("{") + to_parse.count("}")) > 0: 
            raise Exception(f"Error reading {{}} parameters in parameter {log_name}") 
        return to_parse

    for f in files:
        with NRExtractor(f) as ext:
            pdf_info = ext.extract()
        pdict = xlsx_data.return_from_RN(pdf_info["RN"])
        
        for item in [config['colonne_mail'].get_value(), config['colonne_nom'].get_value(), config['colonne_prenom'].get_value()]:
            if item not in pdict.keys():
                raise ValueError(f"Parameter '{item}' not found in the .xlsx")

    
        with open(f, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        msg = EmailMessage()
        msg["to"] = pdict[config['colonne_mail'].get_value()]
        msg["from"] = config["sender_email"].get_value()
        msg["subject"] = replace_in_text(
            config["mail_subject"].get_value(),
            {"date_in":pdf_info["date_in"], "date_out":pdf_info["date_out"]},
            "mail_subject")
        msg.set_content(
            replace_in_text(
            config["mail_body"].get_value(),
            {"prenom": pdict[config['colonne_prenom'].get_value()].lower().capitalize()},
            "mail_body").replace("\\n", "\n")
            )

        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(f)
        )
    
        logging.info(f"Envoi à {pdict[config['colonne_prenom'].get_value()]} {pdict[config['colonne_nom'].get_value()]} ({pdict[config['colonne_mail'].get_value()]})")    
        with smtplib.SMTP_SSL(config["smtp_server"].get_value(), config["smtp_port"].get_value()) as server:
            # server.set_debuglevel(1)
            if config["enable_starttls"].get_value():
                server.starttls()
            server.login(config['sender_email'].get_value(), config['sender_pwd'].get_value())
            server.send_message(msg)

        if config["delete_after_sent"].get_value():
            # os.remove(f)
            logging.info(f"Deleting {f}")
            os.remove(f)
