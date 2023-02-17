import re
import os
from typing import Union
from werkzeug.datastructures import FileStorage
from flask_uploads import IMAGES,UploadSet
ImageSet=UploadSet("images",IMAGES)


def save_image(image:FileStorage,folder:str=None,name:str=None)-> str:
    return ImageSet.save(image,folder,name)

def get_path(filename:str=None,folder:str=None)->str:

    return ImageSet.path(filename,folder)

def find_image_any_format(filename:str,folder:str)-> Union[str,None]:
    for _format in IMAGES:
        image=f"{filename}.{_format}"
        image_path=ImageSet.path(filename=image,folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None

def _retrieve_filename(file:Union[str,FileStorage])->str:
    if isinstance(file,FileStorage):
        return file.filename
    return file

def is_filename_safe(file:Union[str,FileStorage])->bool:
    filename=_retrieve_filename(file)
    allowed_formats="|".join(IMAGES)
    regex=f"^[a-zA-Z0-9][a-zA-Z0-9.()-_\]*\.({allowed_formats})$"
    return re.match(regex,filename)

def get_basename(file:Union[str,FileStorage]):
    filename=_retrieve_filename(file)
    return os.path.split(filename)[1]

def get_extension(file:Union[str,FileStorage]):
    filename=_retrieve_filename(file)
    return os.path.splitext(filename)[1]