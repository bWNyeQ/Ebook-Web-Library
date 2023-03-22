#pip install pdf2image
import os
import tempfile
from pdf2image import convert_from_path
output_folder=os.getcwd() #current work directory

def pdf_to_png(pdf_name,source,destino):
    with tempfile.TemporaryDirectory() as path:
            images_from_path = convert_from_path(pdf_path=source+"/"+pdf_name,
            dpi=100,
            output_folder=destino,
            fmt="png",
            output_file=pdf_name[:-4],
            single_file=True)
            