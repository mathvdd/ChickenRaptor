import os
import shutil
import logging

def transfertC4(config):
    source_path = config["source_path"].get_value()
    to_clean_path = config["to_clean"].get_value()
    dest_path = config["dest"].get_value()
    dest_JBE_path = config["dest_JBE"].get_value()

    if os.name == "nt":
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf") and os.path.join(source_path,f).startswith("C"))]
    else:
        files = [f for f in os.listdir(source_path) if (os.path.isfile(os.path.join(source_path,f)) and os.path.join(source_path,f).endswith(".pdf"))]
    files_JBE = [f for f in files if f.endswith('JBE.pdf')]

    logging.info(f"Found {len(files)} to transfer ({len(files_JBE)} JBE files)")

    for file in files_JBE:
        logging.info(f"Copy {file} in JBE repository")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_JBE_path,file))

    to_transfert = [f for f in files if not os.path.isfile(os.path.join(dest_path,f))]
    logging.info(f"{len(to_transfert)} files to transfer to main repository")

    for file in to_transfert:
        logging.info(f"Move {file} to destination repository")
        shutil.copy(os.path.join(source_path,file), os.path.join(dest_path,file))
        os.remove(os.path.join(source_path,file))

    not_transfered = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path,f))]
    if len(not_transfered) > 0:
        logging.warning(f"{len(not_transfered)} files not transfered:")
        for f in not_transfered:
            logging.warning(f"{f} not transfered")
    
    to_del = [os.path.join(to_clean_path,f) for f in os.listdir(to_clean_path) if os.path.isfile(os.path.join(to_clean_path,f)) ]
    logging.info(f"{len(to_del)} files to clean from {to_clean_path}")
    for file in to_del:
        logging.info(f"Removing {file}")
        os.remove(file)

    if config.get("open_explorer") and config["open_explorer"].get_value():
        logging.info(f"Opening {source_path} in file explorer")
        if os.name == "posix":
            os.system(f"xdg-open {source_path}")
        elif os.name == "nt":
            import subprocess
            subprocess.Popen(r'explorer "{source_path}"')
