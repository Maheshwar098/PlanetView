from flask import Flask, request
from flask import render_template, send_file
import sys
from opencage.geocoder import OpenCageGeocode
import ee
# import PIL
import matplotlib.pyplot as plt
import PIL
import numpy as np
import urllib
from PIL import Image
import math
import tensorflow as tf
import keras 
import matplotlib.image
import os 
import matplotlib.colors as mcolors

app = Flask(__name__)

def getCoordinateFromLocation(location):
    key = 'a4db985ec2094b609d3a7e54619e570e'
    geocoder = OpenCageGeocode(key)
    address = location

    try:
        # no need to URI encode query, module does that for you
        results = geocoder.geocode(address, no_annotations='1')

        if results and len(results):
            longitude = results[0]['geometry']['lng']
            latitude  = results[0]['geometry']['lat']
            return (latitude,longitude)
        else:
            sys.stderr.write("not found: %s\n" % address)
    except IOError:
        print('Error: File %s does not appear to exist.')

def getS2Image(location, size):
    # ee.Authenticate()
    ee.Initialize()
    lattitude = location[0]
    longitude = location[1]
    startDates = ['2019-01-01','2020-01-01','2021-01-01','2022-01-01','2023-01-01']
    endDates = ['2019-12-31','2020-12-31','2021-12-31','2022-12-31','2023-12-31']
    rgbImages = []
    for i in range (len(startDates)) : 
        try :
            startDate = startDates[i]
            endDate = endDates[i]
            point = ee.Geometry.Point(longitude, lattitude)
            collection = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(point) \
            .filterDate(startDate, endDate)\
            .sort('CLOUDY_PIXEL_PERCENTAGE')

            # Select the first image in the collection
            image = collection.first()

            # Clip the image to a 510x510 pixel area around the specified location
            image = image.clip(point.buffer(size / 2).bounds())

            # print(point.buffer(size/2).bounds())
            s2VisParams = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}

            url = image.getThumbUrl(s2VisParams)

            image_content = np.array(PIL.Image.open(urllib.request.urlopen(url)))
            resizedImg = resizeImage(512,image_content)
            rgbImages.append(resizedImg)
            img = Image.fromarray(resizedImg[:,:,:3])
            
            img.save('./static/Images/ModelImages/RGBImages/RGBImg_{}.jpg'.format(i+1))

        finally:
            pass
    
    return (rgbImages)

def resizeImage(target_dims, img):
    act_dim = target_dims
    rows = img.shape[0]
    columns = img.shape[1]

    row_margin = rows-act_dim
    col_margin = columns-act_dim
    img_arr = np.zeros((act_dim, act_dim,3))
    if (rows > act_dim):
        if (columns > act_dim):
            img_arr = img[:-row_margin,:-col_margin]
        else :
            temp = img[:-row_margin, :]
            img_arr = np.pad(temp,((0,0),(math.floor((act_dim-columns)/2),math.ceil((act_dim-columns)/2)),(0,0)), mode='constant')
    else:
        if (columns > act_dim):
            temp = img[:, :-col_margin]
            img_arr = np.pad(temp,((math.floor((act_dim-rows)/2),math.ceil((act_dim-rows)/2)),(0,0),(0,0)), mode='constant')
        else:
            img_arr = np.pad(img,((math.floor((act_dim-rows)/2),math.ceil((act_dim-rows)/2)),(math.floor((act_dim-columns)/2),math.ceil((act_dim-columns)/2)),(0,0)), mode='constant')
    return img_arr

def getRGBImg(imgArr):
  colors = [
      [0, 0, 0],          # 0: unmarked : black
      [0, 0, 255],        # 1: Water : blue
      [0, 255, 0],        # 2: Trees : green
      [255, 0, 0],        # 3: Grass : Red
      [255, 255, 0],      # 4: Flooded Vegetation : yellow
      [255, 0, 255],      # 5: Crops : purple
      [192, 192, 192],    # 6: Scrub : gray
      [128, 0, 0],        # 7: Built Area :  maroon
      [128, 128, 0],      # 8: Bare Ground :  olive
      [128, 128, 128],    # 9: Snow/Ice : gray
      [0, 128, 128]       # 10: Cloud : teal
    ]
  img = np.zeros((512,512,3))
  for i in range(11):
      img[imgArr == i] = colors[i]
  return img

# 0: unmarked 
# 1: Water 
# 2: Trees 
# 3: Grass 

# 4: Flooded Vegetation
# 5: Crops 
# 6: Scrub 
# 7: Built Area 
# 8: Bare Ground 
# 9: Snow/Ice 
# 10: Cloud 

@app.get("/")
def hello_world():
    return render_template("home.html")

@app.route("/imageexplorar")
def imgExplorar():
    return render_template("ImageExplorar.html",rgbimg="static/Images/UtilityImages/saved.jpg", segmentedimg = "static/Images/UtilityImages/predsaved.jpg")

@app.route("/aboutus")
def aboutUs():
    return render_template("aboutus.html")

@app.route("/charts")
def getCharts():
    labelDir = './static/Images/ModelImages/Labels'
    lblFiles = os.listdir(labelDir)

    pixelIntensities = []

    for File in lblFiles:
        pixelCount = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
        # filePath = labelDir + '/' + File 
        # imgArr = np.asarray(Image.open(filePath))
        # for i in range (512):
        #     for j in range (512) : 
        #         pixelCount[imgArr[i,j]] = pixelCount[imgArr[i,j]] + 1
        
        # pixelIntensities.append(pixelCount)
    
    # print(pixelIntensities)




    return render_template ("charts.html")

@app.route("/getImage", methods=['GET'])
def getImage():
    location = request.args.get('location')
    (lattitude, longitude) = getCoordinateFromLocation(location)
    inputImgs = getS2Image((lattitude,longitude),5100)

    imgDir = './static/Images/ModelImages/RGBImages'
    labelDir = './static/Images/ModelImages/Labels'
    imgFiles = os.listdir(imgDir)
    lblFiles = os.listdir(labelDir)

    pixelIntensities = []
    reconstructed_model = keras.models.load_model("./Model/model")

    for img in imgFiles :  
        inputImg = np.asarray(Image.open(imgDir+'/'+img))  
        pred = reconstructed_model.predict(inputImg.reshape(1,512, 512, 3)).reshape(512,512,11)
        pred = np.array(np.argmax(pred, axis = 2))
        pixelCount = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
        for i in range (512) : 
            for j in range (512) : 
                pixelCount[pred[i,j]] = pixelCount[pred[i,j]] + 1
        pixelIntensities.append(pixelCount)

        unique_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        num_colors = 11

        # Get the "viridis" colormap
        colormap = plt.cm.get_cmap('viridis')

        # Generate a list of colors from the colormap
        colors = [colormap(i / num_colors) for i in range(num_colors)]
    

        # Create a custom colormap with the specified colors
        cmap = mcolors.ListedColormap(colors)

        
        matplotlib.image.imsave(labelDir+'/Label_'+img[-5:], pred, cmap=cmap)   

    trees = []
    builtArea = []
    crops = []
    for i in range (len(pixelIntensities)) : 
        trees.append(pixelIntensities[i][2])
        builtArea.append(pixelIntensities[i][7])
        crops.append(pixelIntensities[i][5])
    
    piechartData = pixelIntensities[-1]

    strTrees = str(trees)
    strBuiltArea = str(builtArea)
    strCrops = str(crops)
    strpieData = str(piechartData)

    with open("./static/Js/chartdata.js", "w") as file : 
        file.write("export const histData = "+ strTrees + " ;\n")
        file.write("export const piechartData = " + strpieData + " ;\n")
        file.write("export const trees = "+ strTrees + " ;\n")
        file.write("export const builtArea = "+ strBuiltArea + " ;\n")
        file.write("export const crops = "+ strCrops + " ;\n")
        file.close()
    
    rgbImages = [imgDir[2:]+'/'+file for file in imgFiles]
    segImages = [labelDir[2:]+'/'+file for file in lblFiles]

    return render_template("ImageExplorar.html", segImages = segImages, rgbImages=rgbImages )

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        image.save('./static/uploads/rgbimg.jpg')
        reconstructed_model = keras.models.load_model("./Model/model")
        inputImg = np.asarray(Image.open('./static/uploads/rgbimg.jpg'))  
        pred = reconstructed_model.predict(inputImg.reshape(1,512, 512, 3)).reshape(512,512,11)
        pred = np.array(np.argmax(pred, axis = 2))
        num_colors = 11

        # Get the "viridis" colormap
        colormap = plt.cm.get_cmap('viridis')

        # Generate a list of colors from the colormap
        colors = [colormap(i / num_colors) for i in range(num_colors)]
    

        # Create a custom colormap with the specified colors
        cmap = mcolors.ListedColormap(colors)

        
        matplotlib.image.imsave('./static/uploads/segmimg.jpg', pred, cmap=cmap)
        
    return render_template('ImageExplorar.html',rgbimg="./static/uploads/rgbimg.jpg", segmentedimg = "./static/uploads/segmimg.jpg")

@app.route("/assets/satellite/scene.gltf", methods = ['GET'])
def getsatelliteScene():
    image_path = "./static/assets/satellite/scene.gltf"
    return send_file(image_path, as_attachment=True)

@app.route("/assets/globe.jpg", methods = ['GET'])
def getglobe():
    image_path = "./static/assets/globe.jpg"
    return send_file(image_path, as_attachment=True)

@app.route("/assets/satellite/scene.bin", methods = ['GET'])
def getsatelliteSceneBin():
    image_path = "./static/assets/satellite/scene.bin "
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/textures/lambert1_baseColor.png", methods = ['GET'])
def getsatelliteSceneBasecolor():
    image_path = "./static/assets/satellite/textures/lambert1_baseColor.png"
    return send_file(image_path, as_attachment=True)

# 
@app.route("/assets/satellite/textures/lambert1_metallicRoughness.png", methods = ['GET'])
def getsatelliteMetallicRough():
    image_path = "./static/assets/satellite/textures/lambert1_metallicRoughness.png"
    return send_file(image_path, as_attachment=True)

@app.route("/assets/satellite/textures/lambert1_emissive.jpeg" , methods = ['GET'])
def getsatelliteEmmisive():
    image_path = "./static/assets/satellite/textures/lambert1_emissive.jpeg"
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/textures/lambert1_normal.png" , methods = ['GET'])
def getsatelliteNormal():
    image_path = "./static/assets/satellite/textures/lambert1_normal.png"
    return send_file(image_path, as_attachment=True)

# flask --app test run --debug
