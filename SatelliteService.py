import PIL
import numpy as np
from opencage.geocoder import OpenCageGeocode
import ee
from PIL import Image
import urllib
import os
import math
import tensorflow as tf
import keras
from typing import List, Tuple

class SatelliteService:

    def __init__(self, model_path:str, ocg_key:str, gcp_service_account:str, gcp_service_key_path:str, save_dir: str, verbose: bool = False) -> None:
        try:
            self.model = keras.models.load_model(model_path)
            self.log(f'Successfully initialized Segmentation Model at path {model_path}', 'ok')
        except Exception as e:
            self.log(f'Error initializing model at path {model_path}', 'warning')
            self.log(e, 'error')

        try:
            self.geocoder = OpenCageGeocode(ocg_key)
            self.log(f'Successfully initialized OpenCage GeoEncoder', 'ok')
        except Exception as e:
            self.log(f'Error initializing OpenCage GeoEncoder', 'warning')
            self.log(e, 'error')

        try:
            credentials = ee.ServiceAccountCredentials(gcp_service_account, gcp_service_key_path)
            self.log(f'Obtained credentials for GCP Project {credentials.project_id}', 'special')
            ee.Initialize(credentials)
            self.log(f'Successfully connected to GCP Project', 'ok')
        except Exception as e:
            self.log('Error connecting to GCP Project', 'warning')
            self.log(e, 'error')

        self.save_dir = save_dir
        self.verbose = verbose
        self.colors = [
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

    def getCoordinateFromLocation(self, location: str)->Tuple[int, int]:
        try:
            results = self.geocoder.geocode(location, no_annotations='1')
            assert results and len(results), 'Not Found'
        
            longitude = results[0]['geometry']['lng']
            latitude = results[0]['geometry']['lat']
            return (latitude, longitude)
        except Exception as e:
            if self.verbose:
                self.log('Error obtaining coords from Geocoder for location f{location}', 'error')
            raise(e)
        
    def getS2Image(self, location: Tuple[int, int], img_size: int, start_year:int = 2019, end_year=2023)->None:
        lattitude, longitude = location
        start_dates = [f"{year}-01-01" for year in range(start_year, end_year+1)]
        end_dates = [f"{year}-12-31" for year in range(start_year, end_year+1)]

        rgbImages = []
        warnings, warn_msg = 0, 'NA'
        for i, (start_date, end_date) in enumerate(zip(start_dates, end_dates)):
            try:
                point = ee.Geometry.Point(longitude, lattitude)
                collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(point) \
                .filterDate(start_date, end_date)\
                .sort('CLOUDY_PIXEL_PERCENTAGE')

                image = collection.first()
                image = image.clip(point.buffer(img_size / 2).bounds())

                s2VisParams = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
                url = image.getThumbUrl(s2VisParams)
                image_content = np.array(PIL.Image.open(urllib.request.urlopen(url)))
                resizedImg = self.resizeImage(image_content, 512)
                rgbImages.append(resizedImg)
                img = Image.fromarray(resizedImg[:, :, :3])

                img.save(os.path.join(self.save_dir, f"RGBImg_{i+1}.jpg"))

            except Exception as e:
                warnings += 1
                warn_msg = e

        if warnings > 0 and self.verbose:
            self.log(f'Retreived images from {start_date} to {end_date} with {warnings} warnings', 'warning')
            self.log(f'Recently: {warn_msg}', 'status')

    def resizeImage(self, img: np.ndarray, target_dims: Tuple[int, int])->np.ndarray:
            act_dim = target_dims
            rows = img.shape[0]
            columns = img.shape[1]

            row_margin = rows-act_dim
            col_margin = columns-act_dim
            img_arr = np.zeros((act_dim, act_dim, 3))
            if (rows > act_dim):
                if (columns > act_dim):
                    img_arr = img[:-row_margin, :-col_margin]
                else:
                    temp = img[:-row_margin, :]
                    img_arr = np.pad(temp, ((0, 0), (math.floor(
                        (act_dim-columns)/2), math.ceil((act_dim-columns)/2)), (0, 0)), mode='constant')
            else:
                if (columns > act_dim):
                    temp = img[:, :-col_margin]
                    img_arr = np.pad(temp, ((math.floor(
                        (act_dim-rows)/2), math.ceil((act_dim-rows)/2)), (0, 0), (0, 0)), mode='constant')
                else:
                    img_arr = np.pad(img, ((math.floor((act_dim-rows)/2), math.ceil((act_dim-rows)/2)),
                                    (math.floor((act_dim-columns)/2), math.ceil((act_dim-columns)/2)), (0, 0)), mode='constant')
            return img_arr
    
    def getRGBImg(self, imgArr:np.ndarray)->np.ndarray:
        img = np.zeros((512, 512, 3))
        for i in range(11):
            img[imgArr == i] = self.colors[i]
        return img
    
    def inference(self, img: np.ndarray)->np.ndarray:
        try:
            preds = self.model.predict(img.reshape(1, 512, 512, 3))
            expanded_preds = preds.reshape(512, 512, 11)
            pred = np.array(np.argmax(expanded_preds, axis=2))
            return pred
        except Exception as e:
            if type(img)==np.ndarray:
                print(f"Error in inference for input of shape {img.shape}", "warning")
            print(e)
            raise e

    def log(self, s, status):
        colors = {
            "error": "\033[31m",
            "ok": "\033[32m",
            "warning": "\033[33m",
            "special": "\033[34m",
            "status": "\033[35m",
            "log": "\033[36m",
            "reset": "\033[0m"
        }
        try:
            print(f"{colors[status]}{s}{colors['reset']}")
        except:
            print(s)
