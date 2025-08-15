import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_dir="extracted_images"):
    os.makedirs(output_dir, exist_ok=True)
    pdf = fitz.open(pdf_path)
    images = []
    for page_num, page in enumerate(pdf):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(pdf, xref)
            img_filename = f"{output_dir}/page{page_num+1}_img{img_index+1}.png"
            if pix.n < 5:  # RGB or grayscale
                pix.save(img_filename)
            else:
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save(img_filename)
                pix1 = None
            pix = None
            images.append(img_filename)
    return images

# TODO: table extraction can be done via Camelot or Tabula
