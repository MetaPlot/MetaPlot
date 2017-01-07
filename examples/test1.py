import metaplot as mp

imageName = 'picture.jpg'

dataToinclude={'Category':'dinasor', 'size':'large'}

mp.savefig(imageName, dataToinclude)

data=mp.openfig(imageName)
print(data)
