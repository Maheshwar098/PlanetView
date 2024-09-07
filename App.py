from flask import Flask, request
from flask import render_template, send_file
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.image
import os
import matplotlib.colors as mcolors
from dotenv import load_dotenv

from SatelliteService import SatelliteService

load_dotenv()
app = Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

satServe = SatelliteService(model_path = os.getenv('MODEL_PATH'),
                            ocg_key = os.getenv('OCG_KEY'),
                            gcp_service_account=os.getenv('GCP_SERVICE_ACCOUNT'),
                            gcp_service_key_path=os.getenv('GCP_SERVICE_KEY_PATH'),
                            save_dir=os.getenv('SAVE_DIR'),
                            verbose=app.config['DEBUG'])

@app.get("/")
def hello_world():
    return render_template("home.html")


@app.route("/imageexplorar")
def imgExplorar():
    return render_template("ImageExplorar.html", rgbimg="static/Images/UtilityImages/saved.jpg", segmentedimg="static/Images/UtilityImages/predsaved.jpg")


@app.route("/aboutus")
def aboutUs():
    return render_template("aboutus.html")


@app.route("/charts")
def getCharts():
    labelDir = './static/Images/ModelImages/Labels'
    lblFiles = os.listdir(labelDir)

    pixelIntensities = []

    for File in lblFiles:
        pixelCount = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
                      5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        # filePath = labelDir + '/' + File
        # imgArr = np.asarray(Image.open(filePath))
        # for i in range (512):
        #     for j in range (512) :
        #         pixelCount[imgArr[i,j]] = pixelCount[imgArr[i,j]] + 1
        # pixelIntensities.append(pixelCount)
    # print(pixelIntensities)

    return render_template("charts.html")


@app.route("/getImage", methods=['GET'])
def getImage():
    location = request.args.get('location')
    (lattitude, longitude) = satServe.getCoordinateFromLocation(location)
    inputImgs = satServe.getS2Image((lattitude, longitude), 5100)

    imgDir = './static/Images/ModelImages/RGBImages'
    labelDir = './static/Images/ModelImages/Labels'
    imgFiles = os.listdir(imgDir)
    lblFiles = os.listdir(labelDir)

    pixelIntensities = []

    for img in imgFiles:
        inputImg = np.asarray(Image.open(imgDir+'/'+img))
        pred = satServe.inference(inputImg)
        pixelCount = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
                      5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        for i in range(512):
            for j in range(512):
                pixelCount[pred[i, j]] = pixelCount[pred[i, j]] + 1
        pixelIntensities.append(pixelCount)

        predLst = list(pred)

        palette = {
            0: [0, 0, 0, 255],
            1: [65, 155, 223, 255],
            2: [57, 125, 73, 255],
            3: [136, 176, 83, 255],
            4: [122, 135, 198, 255],
            5: [228, 150, 53, 255],
            6: [223, 195, 90, 255],
            7: [196, 40, 27, 255],
            8: [165, 155, 143, 255],
            9: [179, 159, 225, 255],
            10: [255, 255, 255, 255]
        }

        colorImg = np.array([[palette[pixel] for pixel in row]
                            for row in predLst]).astype(np.uint8)

        # num_colors = 11
        # # Get the "viridis" colormap
        # colormap = plt.cm.get_cmap('viridis')
        # # Generate a list of colors from the colormap
        # colors = [colormap(i / num_colors) for i in range(num_colors)]
        # # Create a custom colormap with the specified colors
        # cmap = mcolors.ListedColormap(colors)

        matplotlib.image.imsave(labelDir+'/Label_'+img[-5:], colorImg)

    trees = []
    builtArea = []
    crops = []
    for i in range(len(pixelIntensities)):
        trees.append(pixelIntensities[i][2])
        builtArea.append(pixelIntensities[i][7])
        crops.append(pixelIntensities[i][5])

    piechartData = pixelIntensities[-1]

    strTrees = str(trees)
    strBuiltArea = str(builtArea)
    strCrops = str(crops)
    strpieData = str(piechartData)

    with open("./static/Js/chartdata.js", "w") as file:
        file.write("export const histData = " + strTrees + " ;\n")
        file.write("export const piechartData = " + strpieData + " ;\n")
        file.write("export const trees = " + strTrees + " ;\n")
        file.write("export const builtArea = " + strBuiltArea + " ;\n")
        file.write("export const crops = " + strCrops + " ;\n")
        file.close()

    rgbImages = [imgDir[2:]+'/'+file for file in imgFiles]
    segImages = [labelDir[2:]+'/'+file for file in lblFiles]

    return render_template("ImageExplorar.html", segImages=segImages, rgbImages=rgbImages)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        image.save('./static/uploads/rgbimg.jpg')
        inputImg = np.asarray(Image.open('./static/uploads/rgbimg.jpg'))
        pred = satServe.inference(inputImg)
        predLst = list(pred)

        palette = {
            0: [0, 0, 0, 255],
            1: [65, 155, 223, 255],
            2: [57, 125, 73, 255],
            3: [136, 176, 83, 255],
            4: [122, 135, 198, 255],
            5: [228, 150, 53, 255],
            6: [223, 195, 90, 255],
            7: [196, 40, 27, 255],
            8: [165, 155, 143, 255],
            9: [179, 159, 225, 255],
            10: [255, 255, 255, 255]
        }

        colorImg = np.array([[palette[pixel] for pixel in row] for row in predLst]).astype(np.uint8)

        # num_colors = 11
        # # Get the "viridis" colormap
        # colormap = plt.cm.get_cmap('viridis')
        # # Generate a list of colors from the colormap
        # colors = [colormap(i / num_colors) for i in range(num_colors)]
        # # Create a custom colormap with the specified colors
        # cmap = mcolors.ListedColormap(colors)

        matplotlib.image.imsave(
            './static/uploads/segmimg.jpg', colorImg)

    return render_template('ImageExplorar.html', rgbimg="./static/uploads/rgbimg.jpg", segmentedimg="./static/uploads/segmimg.jpg")


@app.route("/assets/satellite/scene.gltf", methods=['GET'])
def getsatelliteScene():
    image_path = "./static/assets/satellite/scene.gltf"
    return send_file(image_path, as_attachment=True)


@app.route("/assets/globe.jpg", methods=['GET'])
def getglobe():
    image_path = "./static/assets/globe.jpg"
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/scene.bin", methods=['GET'])
def getsatelliteSceneBin():
    image_path = "./static/assets/satellite/scene.bin "
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/textures/lambert1_baseColor.png", methods=['GET'])
def getsatelliteSceneBasecolor():
    image_path = "./static/assets/satellite/textures/lambert1_baseColor.png"
    return send_file(image_path, as_attachment=True)

@app.route("/assets/satellite/textures/lambert1_metallicRoughness.png", methods=['GET'])
def getsatelliteMetallicRough():
    image_path = "./static/assets/satellite/textures/lambert1_metallicRoughness.png"
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/textures/lambert1_emissive.jpeg", methods=['GET'])
def getsatelliteEmmisive():
    image_path = "./static/assets/satellite/textures/lambert1_emissive.jpeg"
    return send_file(image_path, as_attachment=True)


@app.route("/assets/satellite/textures/lambert1_normal.png", methods=['GET'])
def getsatelliteNormal():
    image_path = "./static/assets/satellite/textures/lambert1_normal.png"
    return send_file(image_path, as_attachment=True)

# flask --app test run --debug
