import logging
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
import os



def read_barcode_dpi(path : str, dpi : int) -> str:
    logging.info(f"Reading barcode at {dpi} dpi")

    try:
        img = convert_from_path(path, dpi = dpi)[0]
    except:
        raise RuntimeError(f"Could not convert at dpi {dpi}")

    w_img, h_img = img.size

    crop = img.crop((
            int(w_img * 0.66),
            int(h_img * 0.04),
            int(w_img * 0.95),
            int(h_img * 0.14),
        ))

    detectedBarcodes = decode(crop)
 
    if not detectedBarcodes:
        raise ValueError(f"Could not detect barcode in {path}")
    else:
        if len(detectedBarcodes) > 1:
            raise ValueError(f"Unexpected number of barcode detected: {len(detectedBarcodes)}")

        else:
            barcode = detectedBarcodes[0]

            if barcode.data:

                return barcode.data.decode("utf-8")

            else:
                raise ValueError(f"Could not read barcode for {path}")


def read_barcode_dpis(path: str, dpis = [200, 400, 600]) -> str:
    barcode = os.path.splitext(os.path.basename(path))[0]
    for dpi in dpis:
        try:
            barcode = read_barcode_dpi(path, dpi)
            break
        except Exception as e:
            logging.debug(e)          
    
    if barcode == os.path.splitext(os.path.basename(path))[0]:
        logging.warning(f'Could not read codebar, using original name for {os.path.splitext(os.path.basename(path))[0]}]')
    return barcode

def read_barcode(path : str) -> str:
    logging.info("Reading barcode")

    img = convert_from_path(path)[0]

    w_img, h_img = img.size

    crop = img.crop((
        int(w_img * 0.66),
        int(h_img * 0.04),
        int(w_img * 0.95),
        int(h_img * 0.14),
    ))

    # import os
    # name = os.path.splitext(os.path.basename(path))[0]
    # crop.save(f"{name}_highlighted.png")
    
    detectedBarcodes = decode(crop)


    # detectedBarcodes = decode(img)
    if not detectedBarcodes:
        raise ValueError(f"Could not detect barcode in {path}")
    else:
        if len(detectedBarcodes) > 1:
            raise ValueError(f"Unexpected number of barcode detected: {len(detectedBarcodes)}")

        else:
            barcode = detectedBarcodes[0]

            # ##display the detection
            # (x, y, w, h) = barcode.rect
            # from PIL import ImageDraw
            # import os
            # name = os.path.splitext(os.path.basename(path))[0]
            # draw = ImageDraw.Draw(crop)
            # draw.rectangle(
            #     [(x, y), (x + w, y + h)],
            #     outline="red",
            #     width=10
            # )
            # crop.save(f"{name}_highlighted.png")

            if barcode.data != "":

            # Print the barcode data
                # print(barcode.data)
                # print(barcode.type)
                return barcode.data.decode("utf-8")

            else:
                raise ValueError(f"Could not read barcode for {path}")
