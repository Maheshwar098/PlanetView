# PlanetView 🌎🛰️

PlanetView is a web-app providing Semantic Segmentation of Satellite Images. Users can obtain Land-use pattern Segmentation Masks of any location in any given duration.

## Legend

- ![#000000](https://placehold.co/15x15/000000/000000.png) Black - Unmarked
- ![#202099](https://placehold.co/15x15/202099/202099.png) Blue - Water 
- ![#208040](https://placehold.co/15x15/208040/208040.png) Green - Trees
- ![#707010](https://placehold.co/15x15/707010/707010.png) Yellow - Flooded Vegetation 
- ![#000000](https://placehold.co/15x15/501060/501060.png) Purple - Crops
- ![#202099](https://placehold.co/15x15/abaaaa/aaaaaa.png) Grey - Scrub 
- ![#208040](https://placehold.co/15x15/600000/600000.png) Maroon - Built Area
- ![#304025](https://placehold.co/15x15/304025/304025.png) Olive - Bare ground
- ![#505050](https://placehold.co/15x15/505050/505090.png) Grey - Snow/Ice 
- ![#208040](https://placehold.co/15x15/009090/009090.png) Teal - Cloud

## Setup

1. Clone Repo 
```
git clone https://github.com/Maheshwar098/PlanetView.git
cd PLANETVIEW
```
2. Obtain  OpenCage GeoEncode API Key
3. Create GCP Service Account and obtain serive key json
4. Update .env file
5. Create venv and install libs

```
python -m venv venv
venv/Scripts/Activate
pip install -r requirements.txt
```

## Run App
```
venv/Scripts/Activate
flask --app  App.py run
```

