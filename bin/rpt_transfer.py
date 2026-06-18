import os
import shutil
import logging
from rpt_config import validate_path

def transfertC4(config):
    validate_path(config["source_path"].get_value(), "source_path")
    validate_path(config["to_clean"].get_value(), "to_clean")
    validate_path(config["dest"].get_value(), "dest")
    validate_path(config["dest_JBE"].get_value(), "dest_JBE")


    source_path = config["source_path"].get_value()
    to_clean_path = config["to_clean"].get_value()
    dest_path = config["dest"].get_value()
    dest_JBE_path = config["dest_JBE"].get_value()

    if os.name == "nt":
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf") and os.path.join(source_path,f).startswith("C"))]
    else:
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf"))]
    files_JBE = [f for f in files if f.endswith('JBE.pdf')]

    logging.info(f"{len(files)} fichiers trouvés, dont ({len(files_JBE)} à copier dans le répertoire JBE)")

    count = 1
    for file in files_JBE:
        logging.info(f"{count}/{len(files_JBE)} Copie de {file} dans le répertoire JBE")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_JBE_path,file))
        count += 1

    to_transfert = [f for f in files if not os.path.isfile(os.path.join(dest_path,f))]
    logging.info(f"{len(to_transfert)} fichiers à déplacer dans le répertoire principal")

    count = 1
    for file in to_transfert:
        logging.info(f"{count}/{len(to_transfert)} Déplacement de {file}")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_path,file))
        os.remove(os.path.join(source_path,file))
        count += 1


    not_transfered = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path,f))]
    if len(not_transfered) > 0:
        logging.warning(f"{len(not_transfered)} fichiers non transférés (déjà présents dans {dest_path}):")
        for f in not_transfered:
            logging.warning(f"{f} non transféré")
    
    to_del = [os.path.join(to_clean_path,f) for f in os.listdir(to_clean_path) if os.path.isfile(os.path.join(to_clean_path,f)) ]
    logging.info(f"{len(to_del)} fichiers à supprimer de {to_clean_path}")
    for file in to_del:
        logging.info(f"Suppression de {file}")
        os.remove(file)

    if config.get("open_explorer") and config["open_explorer"].get_value():
        logging.info(f"Ouverture de {source_path} dans l'explorateur de fichier")
        if os.name == "posix":
            os.system(f"xdg-open {source_path}")
        elif os.name == "nt":
            import subprocess
            subprocess.Popen(["explorer", source_path])
