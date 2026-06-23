import logging
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode

def read_barcode(path : str) -> str:
    logging.info("Reading barcode")
    # covert pdf to PIL, take the first page
    img = convert_from_path(path, dpi=600)[0]

    w_img, h_img = img.size

    crop = img.crop((
        int(w_img * 0.66),
        int(h_img * 0.04),
        int(w_img * 0.95),
        int(h_img * 0.14),
    ))

    detectedBarcodes = decode(crop)


    # detectedBarcodes = decode(img)
    if not detectedBarcodes:
        raise ValueError(f"Could not detect barcode in {path}")
    else:
        if len(detectedBarcodes) > 1:
            raise ValueError(f"Unexpected number of barcode detected: {len(detectedBarcode)}")

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
