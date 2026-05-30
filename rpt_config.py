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
                "p1" : "jkl",
                "p2" : 21,  
            },
            "app1" : {
                "p1" : "jkl",
                "p2" : 21,
            },
            "app2" : {
                "p1" : "jkl",
                "p2" : 21,
            },
            "app3" : {
                "p1" : "jkl",
                "p2" : 21,
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
            json.dump(self.config, fp)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    conf = RptConfig()
