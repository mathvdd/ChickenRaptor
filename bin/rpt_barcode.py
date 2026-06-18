import logging
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode

def read_barcode(path : str) -> str:
    logging.info("Lecture du code bar")
    # covert pdf to PIL, take the first page
    img = convert_from_path(path)[0]
    detectedBarcodes = decode(img)
    if not detectedBarcodes:
        raise ValueError(f"Could not detect barcode in {path}")
    else:
        if len(detectedBarcodes) > 1:
            raise ValueError(f"Unexpected number of barcode detected: {len(detectedBarcode)}")

        else:
            barcode = detectedBarcodes[0]
            # Locate the barcode position in image
            # (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to highlight the barcode

             # cv2.rectangle(img, (x-10, y-10),
             #              (x + w+10, y + h+10),
             #              (255, 0, 0), 2)

            if barcode.data != "":

            # Print the barcode data
                # print(barcode.data)
                # print(barcode.type)
                return barcode.data.decode("utf-8")

            else:
                raise ValueError(f"Could not read barcode for {path}")