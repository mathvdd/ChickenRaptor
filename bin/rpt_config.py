import os
import json
import logging
from datetime import datetime


def validate_date(date : str):
    try:
        datetime.strptime(date, "%d/%m/%Y")
    except ValueError as e:
        logging.critical(f"Invalid date : {date}", exc_info=True)

class ConfigElement():
    def __init__(self, value, value_type, display="", widget=None):
        self.value = value
        self.value_type = value_type
        self.widget = widget
        self.display = display

    def get_value(self):
        return self.value
    def set_value(self, raw):

        if self.display == "date":
            validate_date(raw)
            logging.info(f"Setting date to {raw}")

        try:

            if isinstance(raw, self.value_type):
                value = raw

            elif self.value_type is bool:
                value = (raw == "True")

            elif self.value_type is int:
                value = int(raw)

            elif self.value_type in (dict, list):
                if isinstance(raw, str):
                    value = json.loads(raw)
                else:
                    value = raw

            self.value = value

        except TypeError as e:
            logging.critical(f"Could not save {raw} of type {type(raw)}", exc_info=True)


    def get_value_type(self):
        return self.value_type
    def set_widget(self, widget):
        self.widget = widget

    def widget2value(self):
        # print(self.get_value(), type(self.get_value()), self.get_value_type())
        if self.get_value_type() is bool:
            self.set_value(self.widget.currentText() == "True")
        else:
            self.set_value(self.widget.text())


class RptConfig():

    def __init__(self):
        self.package_path = os.path.dirname(__file__)
        self.config_path = os.path.join(self.package_path , "..", "ress", "config.json")

        self.make_config()
        if not os.path.isfile(self.config_path):
            logging.info("No config.json found, creating one")
            self.export_config()
        else:
            self.import_config()


    def make_config(self):
        self.config = {
            "General" : {
                "date" : ConfigElement("", str, display="date"),
                "signature_size" : ConfigElement([80,80], list), #better compatibility with json
                "paraphe_size" : ConfigElement([40,40], list),
                "cachet_size" : ConfigElement([150,75], list),
                "signature_path" : ConfigElement("", str),
                "paraphe_path" : ConfigElement("", str),
            },
            "AnnotateContrat2Pages" : {
                "input_folder" : ConfigElement("", str),
                "output_folder" : ConfigElement("", str),
                "signature_positions" : ConfigElement([], list),
                "paraphe_positions" : ConfigElement([], list),
                "rename_to_barcode": ConfigElement(True, bool),
                "delete_original" : ConfigElement(False, bool),
            },
            "TransfertContrat" : {
                "source_path" : ConfigElement("", str),
                "to_clean" : ConfigElement("", str),
                "dest" : ConfigElement("", str),
                "dest_JBE" : ConfigElement("", str),
            },
            "AnnotateC4" : {
                "x_positions" : ConfigElement([], list), #[[page_nb, x, y],]
                "date_positions" : ConfigElement([], list),
                "signature_positions" : ConfigElement([], list),
                "cachet_positions" : ConfigElement([], list),
                "append_to_name" : ConfigElement("_signe", str),
            },
            "specific_C4Bis" : {
                "input_folder" : ConfigElement("", str),
                "output_folder" : ConfigElement("", str),
                "cachet_path" : ConfigElement("", str),
                "delete_original" : ConfigElement(False, bool),
            },
            "specific_C4Mis" : {
                "input_folder" : ConfigElement("", str),
                "output_folder" : ConfigElement("", str),
                "cachet_path" : ConfigElement("", str),
                "delete_original" : ConfigElement(False, bool),
            },
            "AutoMail" : {
                "to_send_folder_path" : ConfigElement("", str),
                "xlsx_path" : ConfigElement("", str),
                "delete_after_sent" : ConfigElement(False, bool),
                "sender_email" : ConfigElement("", str),
                "sender_pwd" : ConfigElement("", str),
                "smtp_server" : ConfigElement("smtp.gmail.com", str),
                "smtp_port" : ConfigElement(465, int),
                "enable_starttls": ConfigElement(False, bool),
                "mail_subject" : ConfigElement("", str),
                "mail_body" : ConfigElement("", str),
                "colonne_nom" : ConfigElement("Nom", str),
                "colonne_prenom" : ConfigElement("Prenom", str),
                "colonne_mail" : ConfigElement("Email", str),
                "colonne_registre_national" : ConfigElement("RegistreNational", str)
            },            
        }


    def import_config(self):
        logging.info("Importing config.json")        
        with open(self.config_path, 'r') as fp:
            configdict = json.load(fp)

        for section, fields in configdict.items():
            for key, value in fields.items():
                if key == "date":
                    self.config["General"]["date"].set_value(datetime.strftime(datetime.now(),"%d/%m/%Y"))
                else:
                    self.config[section][key].set_value(value)

    def export_config(self):
        logging.info("Exporting config.json")

        configdict = {}

        for section, fields in self.config.items():
            configdict[section] = {}
            for key, element in fields.items():
                configdict[section][key] = element.get_value()

        with open(self.config_path, 'w') as fp:
            json.dump(configdict, fp, indent=4)

    def sync_widget2value(self):
        for section, fields in self.config.items():
            for key, element in fields.items():
                element.widget2value()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    conf = RptConfig()
    logging.info(conf.config["General"]["paraphe_size"].get_value())