import logging
import os
import pymupdf
from rpt_barcode import read_barcode_dpis
from rpt_config import validate_path, validate_file_path
from rpt_db_connect import NRExtractor
import zipfile
import uuid

class pdfAnnotater():
    def __init__(self, pdf_path:str):
        self.pdf_path = pdf_path
        self.file_handle = pymupdf.open(self.pdf_path)
        self.r_w = self.file_handle[0].rect.width
        self.r_h = self.file_handle[0].rect.height
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def add_x(self):
        pass

    def add_image(self, page, pos, size, im):
    # pymupdf uses coordinates of a box (top left and bottom right corners)

        pos_x = int(pos[0]*self.r_w)
        pos_y = int(pos[1]*self.r_h)
        p1 = pymupdf.Point(pos_x, pos_y)
        p2 = pymupdf.Point(pos_x+size[0], pos_y+size[1])
        # first_page.insert_image(pymupdf.Rect(p1,p2), filename= paraphe)
        with pymupdf.open(im) as img_doc:
            page.show_pdf_page(pymupdf.Rect(p1, p2),img_doc,0)

    def add_images(self, poss, impath, imsize):
        #dict of type {page_nb:[(x1,y1),(x2,y2)]}
        for pos in poss:
            self.add_image(self.file_handle[pos[0]-1], pos[1:3], imsize, impath)

    def add_text(self, page, pos, text):
        pos_x = int(pos[0]*self.r_w)
        pos_y = int(pos[1]*self.r_h)
        
        page.insert_text(
            pymupdf.Point(pos_x, pos_y),
            text,
            # fontsize=fontsize,
            # color=(0, 0, 0),
        )
    
    def add_texts(self, poss, text):
        for pos in poss:
            self.add_text(self.file_handle[pos[0]-1], pos[1:3], text)

    
    def resize(self, page_size='a4'):
        r_w, r_h = pymupdf.paper_size(page_size)

        if (abs(self.r_w - r_w) > 2) or (abs(self.r_h - r_h) > 2):
            logging.info("Resizing pdf")
            self.file_handle.bake()
            newdoc = pymupdf.open()

            for page in self.file_handle:

                newpage = newdoc.new_page(width=r_w, height=r_h)
                newpage.show_pdf_page(newpage.rect, self.file_handle, page.number)

            self.file_handle.close()
            self.file_handle = newdoc
            self.r_h = r_h
            self.r_w = r_w
    
    def save(self, path):
        self.file_handle.save(path)

def rename_C4(output_path, paramdict):
    head, tail = os.path.split(output_path)
    root, ext = os.path.splitext(tail)
    new_name = os.path.join( head, f"{paramdict['name'][:].replace(' ', '_')}_{paramdict['date_out'].replace('/','_')}_{paramdict['hash'][:4]}{ext}".replace('__','_'))
    return new_name

def make_all_annotations(config: dict, rename = None):
    validate_path(config["input_folder"].get_value(), "input_folder")
    validate_path(config["output_folder"].get_value(), "output_folder")


    folder = config["input_folder"].get_value()
    to_unzip = [f for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder,f)) and os.path.join(folder,f).endswith(".zip"))]
    logging.info(f"{len(to_unzip)} zip found")
    for zip_file in to_unzip:
        with zipfile.ZipFile(os.path.join(folder, zip_file)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue

                _, ext = os.path.splitext(info.filename)

                new_name = f"{uuid.uuid4().hex[:10]}{ext}"
                output_path = os.path.join(folder, new_name)

                with zf.open(info) as src, open(output_path, "wb") as dst:
                    dst.write(src.read())

                logging.info(f"Unzipping {info.filename} to {new_name}")
        os.remove(os.path.join(folder, zip_file))


    files = [f for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder,f)) and os.path.join(folder,f).endswith(".pdf"))]
    
    # for f in os.listdir(config["input_folder"].get_value()):
    #     if f.endswith('.pdf'):
    #         files.append(f)

    logging.info(f"{len(files)} pdf files found")

    count = 0
    for fil in files:
        count += 1

        input_file = os.path.join(config["input_folder"].get_value(), fil)
        if config.get("rename_to_barcode") and config["rename_to_barcode"].get_value():
            output_file = os.path.join(config["output_folder"].get_value(), read_barcode_dpis(input_file) + '.pdf')
        elif config.get("append_to_name") is not None:
            output_file = os.path.join(config["output_folder"].get_value(),  fil[:-4] + config.get("append_to_name").get_value() + '.pdf')
        else:
            output_file = os.path.join(config["output_folder"].get_value(), fil)
        if rename is not None:        
            output_file = rename(output_file, NRExtractor(input_file).extract(get_hash=True))

        logging.info(f"{count}/{len(files)} Annotating and moving {os.path.basename(input_file)} ({os.path.basename(output_file)})")

        with pdfAnnotater(input_file) as ann:
            ann.resize()
            #add the signature
            if config.get("signature_positions") is not None:  
                validate_file_path(config["signature_path"].get_value(), "signature_path")              
                ann.add_images(
                    config["signature_positions"].get_value(),
                    config["signature_path"].get_value(),
                    config["signature_size"].get_value(),
                    )
            
            if config.get("paraphe_positions") is not None:
                validate_file_path(config["paraphe_path"].get_value(), "paraphe_path")
                ann.add_images(
                    config["paraphe_positions"].get_value(),
                    config["paraphe_path"].get_value(),
                    config["paraphe_size"].get_value(),
                    )

            if config.get("cachet_positions") is not None:
                validate_file_path(config["cachet_path"].get_value(), "cachet_path")
                ann.add_images(
                    config["cachet_positions"].get_value(),
                    config["cachet_path"].get_value(),
                    config["cachet_size"].get_value(),
                    )
            
            if config.get("x_positions") is not None:
                ann.add_texts(
                    config["x_positions"].get_value(),
                    'x'
                    )

            if config.get("date_positions") is not None:
                ann.add_texts(
                    config["date_positions"].get_value(),
                    config["date"].get_value()
                    )


            ann.save(output_file)
        

        if config.get("delete_original").get_value() is True:
            logging.info(f"Deleting {fil}")
            os.remove(input_file)

         

    if config.get("open_explorer") and config["open_explorer"].get_value():
        logging.info(f"Opening {config['output_folder'].get_value()} in the file explorer")
        if os.name == "posix":
            os.system(f"xdg-open {config['output_folder'].get_value()}")
        elif os.name == "nt":
            import subprocess
            subprocess.Popen(["explorer", config["output_folder"].get_value()])

if __name__ == "__main__":
    pass



# vectorisation signature:
# need to go to some to make a bmp
# potrace ...bmp ...svg
# in inskape: select, edit -> resize page to selection
#  save a copy as
# or simply tdo it in inkscape
# or magick file.png -crop 400x180+40+50 +repage -fuzz 15% -transparent white cropped.pdf
