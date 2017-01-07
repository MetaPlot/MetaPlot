import pyexiv2
import json


def save_metaData(image,dictionary):

   metadata = pyexiv2.ImageMetadata(image)
   metadata.read()

   #userdata = {'Category':'dinasor', 'size':'large'}


   metadata['Exif.Photo.UserComment']=json.dumps(dictionary)
   metadata.write()

def load_metaData(image):

   metadata = pyexiv2.ImageMetadata(image)
   metadata.read()
   userdata=json.loads(metadata['Exif.Photo.UserComment'].value)

   return userdata
