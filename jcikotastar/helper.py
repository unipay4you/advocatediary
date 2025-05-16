from PIL import Image
from io import BytesIO
from django.core.files.base import File
from django.http import HttpResponse
from django.conf import settings


def compress_image(image_file, quality=75, format='JPEG'):
       """Compresses an image and returns a File object."""
       img = Image.open(image_file)
       img_io = BytesIO()
       img.save(img_io, format=format, quality=quality)
       img_io.seek(0)
       return File(img_io, name=image_file.name)





def send_msg_to_mobile(mobile, otp, msg):
    try:
        print(msg)
    except Exception as e:
        print(e)
    


def generate_otp():
    #return random.randint(100000, 999999) # for production
    return 123456 # for testing purpose




