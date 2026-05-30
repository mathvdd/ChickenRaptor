import os
import json
import logging

class RptConfig():

    def __init__(self):
        self.package_path = os.path.join(os.path.dirname(__file__)) 
        self.config_path = os.path.join(self.package_path , "res", "config.json")

        if not os.path.isfile(self.config_path):
            logging.info("No config.json found, creating one")
            self.make_config()
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
                "to_send_folder_path" : "",
                "xlsx_path" : "",
                "delete_after_sent" : false,
                "sender_email" : "",
                "sender_pwd" : "",
                "smtp_server" : "smtp.gmail.com",
                "smtp_port" : 465,
                "enable_starttls": false,
                "mail_subject" : "",
                "mail_body" : "",
                "colonne_nom" : "Nom",
                "colonne_prenom" : "Prenom",
                "colonne_mail" : "Email",
                "colonne_registre_national" : "RegistreNational"
            },            
        }

        self.export_config()


    def import_config(self):
        logging.info("Importing config.json")        
        with open(self.config_path, 'r') as fp:
            self.config = json.load(fp)
        

    def export_config(self):
        logging.info("Exporting config.json")
        with open(self.config_path, 'w') as fp:
            json.dump(self.config, fp, indent=4)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    conf = RptConfig()
