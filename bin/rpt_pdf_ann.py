import logging
import os
import pymupdf
from rpt_barcode import read_barcode
import send2trash

class pdfAnnotater():
    def __init__(self, pdf_path:str):
        self.pdf_path = pdf_path
        self.file_handle = pymupdf.open(self.pdf_path)
        self.r_w = self.file_handle[0].rect.width
        self.r_h = self.file_handle[0].rect.height
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def add_x(self):
        pass

    def add_image(self, page, pos, size, im):
    # pymupdf uses coordinates of a box (top left and bottom right corners)

        pos_x = int(pos[0]*self.r_w)
        pos_y = int(pos[1]*self.r_h)
        p1 = pymupdf.Point(pos_x, pos_y)
        p2 = pymupdf.Point(pos_x+size[0], pos_y+size[1])
        # first_page.insert_image(pymupdf.Rect(p1,p2), filename= paraphe)
        page.show_pdf_page(pymupdf.Rect(p1,p2), pymupdf.open(im),0)

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

            for page in self.pdf:

                newpage = newdoc.new_page(width=r_w, height=r_h)
                newpage.show_pdf_page(newpage.rect, self.file_handle, page.number)

            self.file_handler = newdoc
            self.r_h = r_h
            self.r_w = r_w
    
    def save(self, path):
        self.file_handle.save(path)

    
def make_all_annotations(config: dict):
    folder = config["input_folder"].get_value()
    # files = [os.path.join(folder,f) for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder,f)) and os.path.join(folder,f).endswith(".pdf"))]
    files = [f for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder,f)) and os.path.join(folder,f).endswith(".pdf"))]
    
    # for f in os.listdir(config["input_folder"].get_value()):
    #     if f.endswith('.pdf'):
    #         files.append(f)

    logging.info(f"Found {len(files)} pdf")

    for fil in files:
        input_file = os.path.join(config["input_folder"].get_value(), fil)
        if config.get("rename_to_barcode") is not None:
            output_file = os.path.join(config["output_folder"].get_value(), read_barcode(input_file) + '.pdf')
        elif config.get("append_to_name") is not None:
            output_file = os.path.join(config["output_folder"].get_value(),  fil[:-4] + config.get("append_to_name").get_value() + '.pdf')
        else:
            output_file = os.path.join(config["output_folder"].get_value(), fil)

        logging.info(f"Annotating and moving {input_file} to {output_file}")

        with pdfAnnotater(input_file) as ann:
            ann.resize()
            #add the signature
            if config.get("signature_positions") is not None:
                ann.add_images(
                    config["signature_positions"].get_value(),
                    config["signature_path"].get_value(),
                    config["signature_size"].get_value(),
                    )
            
            if config.get("paraphe_positions") is not None:
                ann.add_images(
                    config["paraphe_positions"].get_value(),
                    config["paraphe_path"].get_value(),
                    config["paraphe_size"].get_value(),
                    )

            if config.get("cachet_positions") is not None:
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
        
        if config.get("delete_original") is True:
            logging.info(f"Deleting {fil}")
            send2trash.send2trash(input_file)


if __name__ == "__main__":
    pass



# vectorisation signature:
# need to go to some to make a bmp
# potrace ...bmp ...svg
# in inskape: select, edit -> resize page to selection
#  save a copy as
# or simply tdo it in inkscape
# or magick file.png -crop 400x180+40+50 +repage -fuzz 15% -transparent white cropped.pdf
