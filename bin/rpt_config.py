import os
import json
import logging
from datetime import datetime


def validate_date(date : str):
    try:
        datetime.strptime(date, "%d/%m/%Y")
    except ValueError as e:
        logging.critical(f"Invalid date : {date}", exc_info=True)

def validate_path(path: str, param_name: str = None, none_allowed = False):
    
    if none_allowed and path in [None, "None", "none", ""]:
        return None
    
    else:
        if not os.path.isdir(path):
            msg = f"Could not locate the path: {path}" if param_name is None else f"Could not locate '{param_name}': {path}"
            raise ValueError(msg)
        
        if len(path) == 0:
            msg = f"Path empty" if param_name is None else f"Empty path '{param_name}': {path}"
            raise ValueError(msg)

        return path
    
def validate_file_path(path: str, param_name: str = None):
    
    if not os.path.isfile(path):
        msg = f"Could not locate the file: {path}" if param_name is None else f"Could not locate '{param_name}': {path}"
        raise ValueError(msg)
    
    if len(path) == 0:
        msg = f"Path empty" if param_name is None else f"Empty path '{param_name}': {path}"
        raise ValueError(msg)

    return path

translate_values = {
    "True":"Oui",
    "False":"Non"
}

class ConfigElement():
    def __init__(self, value, value_type, display=None, widget=None):
        self.value = value
        self.value_type = value_type
        self.widget = widget
        self.display = display

    def get_value(self):
        return self.value
    def set_value(self, raw):

        if self.display == "Date":
            validate_date(raw)
            logging.info(f"Setting date to: {raw}")

        try:

            if isinstance(raw, self.value_type):
                value = raw

            # elif self.value_type is bool:
            #     value = (raw == "True")

            elif self.value_type is int:
                value = int(raw)

            elif self.value_type in (dict, list):
                if isinstance(raw, str):
                    value = json.loads(raw)
                else:
                    value = raw

            self.value = value

        except TypeError as e:
            logging.critical(f"Impossible to save {raw} of type {type(raw)}", exc_info=True)


    def get_value_type(self):
        return self.value_type
    def set_widget(self, widget):
        self.widget = widget

    def widget2value(self):
        # print(self.get_value(), type(self.get_value()), self.get_value_type())
        if self.get_value_type() is bool:
            self.set_value(self.widget.currentText() == translate_values.get("True"))
        else:
            self.set_value(self.widget.text())


class RptConfig():

    def __init__(self):
        self.package_path = os.path.dirname(__file__)
        if not os.path.exists(os.path.join(self.package_path , "..", "ress")):
            os.makedirs(os.path.join(self.package_path , "..", "ress"))
        self.config_path = os.path.join(self.package_path , "..", "ress", "config.json")

        self.make_config()
        if not os.path.isfile(self.config_path):
            logging.warning("No config.json found, making file with default values")
            self.export_config()
        else:
            self.import_config()


    def make_config(self):
        self.config = {
            "general_annotate" : { ##annotate general
                "date" : ConfigElement("", str, display="Date"),
                "signature_size" : ConfigElement([80,80], list, display="Taille Signature"), #better compatibility with json
                "paraphe_size" : ConfigElement([40,40], list, display="Taille Paraphe"),
                "cachet_size" : ConfigElement([150,75], list, display="Taille Cachet"),
                "signature_path" : ConfigElement("", str, display="Chemin Signature"),
                "paraphe_path" : ConfigElement("", str, display="Chemin Paraphe"),
            },
            "AnnotateContrat2Pages" : {
                "input_folder" : ConfigElement("", str, display="Dossier à traiter"),
                "output_folder" : ConfigElement("", str, display="Dossier de destination"),
                "signature_positions" : ConfigElement([], list, display="Positions Signature"),
                "paraphe_positions" : ConfigElement([], list, display="Positions Paraphe"),
                "rename_to_barcode": ConfigElement(True, bool, display="Renommer par barcode"),
                "delete_original" : ConfigElement(False, bool, display="Supprimer original"),
                "open_explorer" : ConfigElement(True, bool, display="Ouvrir Explorer"),
            },
            "TransfertContrat" : {
                "source_path" : ConfigElement("", str, display="Dossier à traiter"),
                "to_clean" : ConfigElement("", str, display=None),
                "dest" : ConfigElement("", str, display="Dossier de destination"),
                "dest_JBE" : ConfigElement("", str, display="Dossier de destination JBE"),
                "open_explorer" : ConfigElement(True, bool, display="Ouvrir Explorer"),
            },

            "AnnotateC4" : {
                "x_positions" : ConfigElement([], list, display="Positions X"), #[[page_nb, x, y],]
                "date_positions" : ConfigElement([], list, display="Position date"),
                "signature_positions" : ConfigElement([], list, display="Positions Signature"),
                "cachet_positions" : ConfigElement([], list, display="Positions Cachet"),
                "append_to_name" : ConfigElement("_signe", str, display="Suffixe renommage"),
            },

            "specific_C4Bis" : {
                "input_folder" : ConfigElement("", str, display="Dossier à traiter"),
                "output_folder" : ConfigElement("", str, display="Dossier de destination"),
                "cachet_path" : ConfigElement("", str, display="Chemin Cachet"),
                "delete_original" : ConfigElement(False, bool, display="Supprimer après traitement"),
            },

            "specific_C4Mis" : {
                "input_folder" : ConfigElement("", str, display="Dossier à traiter"),
                "output_folder" : ConfigElement("", str, display="Dossier de destination"),
                "cachet_path" : ConfigElement("", str, display="Chemin Cachet"),
                "delete_original" : ConfigElement(False, bool, display="Supprimer après traitement"),
            },

            "mail_server" : {
                "sender_email" : ConfigElement("", str, display="Adresse e-mail"),
                "sender_pwd" : ConfigElement("", str, display="Mot de passe"),
                "smtp_server" : ConfigElement("smtp.gmail.com", str, display="Serveur SMTP"),
                "smtp_port" : ConfigElement(465, int, display="Port SMTP"),
                "enable_starttls": ConfigElement(False, bool, display="Activer STARTTLS"),
            },

            "xlsx_file" : {
                "xlsx_path" : ConfigElement("", str, display="Chemin fichier Excel"),
                "colonne_nom" : ConfigElement("Nom", str, display='Colonne "Nom"'),
                "colonne_prenom" : ConfigElement("Prenom", str, display='Colonne "Prénom"'),
                "colonne_mail" : ConfigElement("EMail", str, display='Colonne "e-mail"'),
                "colonne_registre_national" : ConfigElement("RegistreNational", str, display='Colonne "Registre National"'),
                "colonne_date_in" : ConfigElement("DateIn", str, display='Colonne "date in"'),
                "colonne_barcode" : ConfigElement("Barcode", str, display='Colonne "barcode"')
            },

            "send_email_C4" : {
                "to_send_folder_path" : ConfigElement("", str, display="Dossier à traiter"),
                "copy_after_send_path" : ConfigElement("", str, display=None),
                "delete_after_sent" : ConfigElement(False, bool, display="Supprimer après envoi"),
                "mail_subject" : ConfigElement("Available fields: date_in: {date_in}, date_out: {date_out}", str, display="Sujet"),
                "mail_body" : ConfigElement("Available fields: prenom: {prenom}", str, display="Corps de texte")
            },
    
            "send_email_contract" : {
                "to_send_folder_path" : ConfigElement("", str, display="Dossier à traiter"),
                "copy_after_send_path" : ConfigElement("", str, display=None),
                "delete_after_sent" : ConfigElement(False, bool, display="Supprimer après envoi"),
                "mail_subject" : ConfigElement("Available fields: date_in_xlsx: {date_in_xlsx}", str, display="Sujet"),
                "mail_body" : ConfigElement("Available fields: prenom: {prenom}, date_in_xlsx: {date_in_xlsx}", str, display="Corps de texte")
            },
        }


    def import_config(self):
        logging.info("Importing config.json")        
        with open(self.config_path, 'r') as fp:
            configdict = json.load(fp)

        for section, fields in configdict.items():
            for key, value in fields.items():
                if key == "date":
                    self.config["general_annotate"]["date"].set_value(datetime.strftime(datetime.now(),"%d/%m/%Y"))
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
