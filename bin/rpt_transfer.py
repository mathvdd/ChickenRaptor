import os
import shutil
import logging
from rpt_config import validate_path

def transfer(config):
    source_path = validate_path(config["source_path"].get_value(), "source_path")
    to_clean_path = validate_path(config["to_clean"].get_value(), "to_clean", none_allowed=True)
    dest_path = validate_path(config["dest"].get_value(), "dest")
    dest_JBE_path = validate_path(config["dest_JBE"].get_value(), "dest_JBE")

    if os.name == "nt":
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf") and os.path.join(source_path,f).startswith("C"))]
    else:
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf"))]
    files_JBE = [f for f in files if f.endswith('JBE.pdf')]

    logging.info(f"{len(files)} files found, including ({len(files_JBE)} JBE files")

    count = 0
    for file in files_JBE:
        count += 1
        logging.info(f"{count}/{len(files_JBE)} Copying {file} in the JBE folder")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_JBE_path,file))
        

    to_transfert = [f for f in files if not os.path.isfile(os.path.join(dest_path,f))]
    logging.info(f"{len(to_transfert)} files to move in the main folder")

    count = 0
    for file in to_transfert:
        count += 1
        logging.info(f"{count}/{len(to_transfert)} Moving {file}")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_path,file))
        os.remove(os.path.join(source_path,file))

    not_transfered = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path,f))]
    if len(not_transfered) > 0:
        logging.warning(f"{len(not_transfered)} files not moved (already in {dest_path}):")
        for f in not_transfered:
            logging.warning(f"{f} not moved")

    if to_clean_path is not None:    
        to_del = [os.path.join(to_clean_path,f) for f in os.listdir(to_clean_path) if os.path.isfile(os.path.join(to_clean_path,f)) ]
        logging.info(f"{len(to_del)} files to clean from {to_clean_path}")
        for file in to_del:
            logging.info(f"Deleting {file}")
            os.remove(file)

    if config.get("open_explorer") and config["open_explorer"].get_value():
        logging.info(f"Opening {source_path} in the file explorer")
        if os.name == "posix":
            os.system(f"xdg-open {source_path}")
        elif os.name == "nt":
            import subprocess
            subprocess.Popen(["explorer", source_path])
