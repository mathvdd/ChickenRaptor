import os
import json
import logging

class ConfigElement():
    def __init__(self, value, value_type, display="", widget=None):
        self.value = value
        self.value_type = value_type
        self.widget = widget

    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = self.value_type(value)
    def get_value_type(self):
        return self.value_type
    def set_widget(self, widget):
        self.widget = widget
    def get_value_type(self):
        return self.value_type

    def widget2value(self):
        if self.get_value_type() is bool:
            self.set_value(self.widget.currentText() == "True")
        else:
            self.set_value(self.widget.text())

class RptConfig():

    def __init__(self):
        self.package_path = os.path.join(os.path.dirname(__file__)) 
        self.config_path = os.path.join(self.package_path , "ress", "config.json")

        self.make_config()
        if not os.path.isfile(self.config_path):
            logging.info("No config.json found, creating one")
            self.export_config()
        else:
            self.import_config()


    def make_config(self):
        self.config = {
            "main" : {  
            },
            "app1" : {
            },
            "app2" : {
            },
            "automail" : {
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
