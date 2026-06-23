import os
import logging
import pandas as pd
from email.message import EmailMessage
import smtplib
from datetime import datetime
from rpt_config import validate_date, validate_path, validate_file_path
import shutil
import rpt_db_connect


def replace_in_text(to_parse : str, replace : dict, log_name : str):
    # check if parse words are known or throw an error
    for key, value in replace.items():
        if "{" + key + "}" in to_parse:
            to_parse = to_parse.replace("{" + key + "}", value)
    if (to_parse.count("{") + to_parse.count("}")) > 0: 
        raise Exception(f"Error reading {{}} parameters in parameter {log_name}")
    return to_parse


def send_emails(config: dict, perso_info_extract):

    if config["accdb_over_xlsx"].get_value():
        logging.info(f"Using {config["accdb_path"].get_value()} file as database")
        db_path = validate_file_path(config["accdb_path"].get_value(), "accdb_path")
        import_method = rpt_db_connect.access2pd
    else:
        logging.info(f"Using {config["xlsx_path"].get_value()} file as database")
        db_path = validate_file_path(config["xlsx_path"].get_value(), "xlsx_path")
        import_method = rpt_db_connect.xlsx2pd
    
    validate_path(config["to_send_folder_path"].get_value(), "to_send_folder_path")
    copy_after_send_path = validate_path(config["copy_after_send_path"].get_value(), "copy_after_send_path", none_allowed=True)
    
    if copy_after_send_path is None:
        logging.info("copy_after_send_path not defined, will not copy")

    db_data = rpt_db_connect.DbData(
        db_path = db_path,
        column_names = {k: v.get_value() for k, v in config.items() if k.startswith("colonne_")},
        import_method = import_method
    )
    
    files = []


    for f in os.listdir(config["to_send_folder_path"].get_value()):
        if f.endswith('.pdf'):
            files.append(os.path.join(config["to_send_folder_path"].get_value(), f))
    logging.info(f"{len(files)} pdf files found")
    
    count = 0
    for f in files:
        
        count += 1
        try:
            pdict = perso_info_extract(db_data, f)

            ## check this log_name thing and pdf_info not always generated


            msg = EmailMessage()
            msg["to"] = pdict[config['colonne_mail'].get_value()]
            msg["from"] = config["sender_email"].get_value()
            
            msg["subject"] = replace_in_text(
                    to_parse = config["mail_subject"].get_value(),
                    replace = {
                        "date_in_xlsx" : pdict[config['colonne_date_in'].get_value()],
                        "date_out_xlsx" : pdict[config['colonne_date_out'].get_value()],
                        "barcode" : pdict[config['colonne_barcode'].get_value()],
                        "date_in" : pdict["date_in"] if pdict.get("date_in") else None,
                        "date_out" : pdict["date_out"] if pdict.get("date_out") else None
                    },
                    log_name = "mail_subject")
                    
            msg.set_content(
                replace_in_text(
                    to_parse = config["mail_body"].get_value(),
                    replace = {
                        "prenom" : pdict[config['colonne_prenom'].get_value()].lower().capitalize(),
                        "date_in_xlsx" : pdict[config['colonne_date_in'].get_value()],
                        "date_out_xlsx" : pdict[config['colonne_date_out'].get_value()]
                    },
                    log_name = "mail_body")
                .replace("\\n", "\n")
            )
            

            with open(f, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(f)
            )
            logging.info(f"{count}/{len(files)} Sending to {pdict[config['colonne_prenom'].get_value()]} {pdict[config['colonne_nom'].get_value()]} ({pdict[config['colonne_mail'].get_value()]})")    
            with smtplib.SMTP_SSL(config["smtp_server"].get_value(), config["smtp_port"].get_value()) as server:
                # server.set_debuglevel(1)
                if config["enable_starttls"].get_value():
                    server.starttls()
                server.login(config['sender_email'].get_value(), config['sender_pwd'].get_value())
                server.send_message(msg)

            if copy_after_send_path is not None:
                logging.info(f"Copying {f}")
                shutil.copy(f, os.path.join(copy_after_send_path , os.path.basename(f)))

            if config["delete_after_sent"].get_value():
                # os.remove(f)
                logging.info(f"Deleting {f}")
                os.remove(f)

        except Exception as e:
            logging.debug(e)            
            logging.warning(f"{count}/{len(files)} Operation aborted for {f}")