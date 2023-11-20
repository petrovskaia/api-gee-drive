from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import geopandas as gpd
import ee

from tqdm import tqdm
import time

from tools import *

def sat_imagery_to_gdrive(bbox:list, 
                file_name:str = 'site', 
                gdrive_folder:str = 'test_gee', 
                min_date='2020-05-01', 
                max_date='2020-09-30',
                cloud_pct=10,
                proj:str = None,
                service_acc_file: str = 
                "./creds/ee-sat-imagery-nnnn.json",
                product='COPERNICUS/S2_SR_HARMONIZED',
                median:bool = False
                ):

    
    bbox = bbox 
    file_name = file_name
    folder = gdrive_folder
    proj = proj

    #build service for Google Drive
    scopes = ['https://www.googleapis.com/auth/drive']
    credentials_gdrive = Credentials.from_service_account_file(
                                        service_acc_file, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials_gdrive)

    #credentials for Google Earth Engine
    credentials_ee = Credentials.from_service_account_file(
        service_acc_file,
        scopes=['https://www.googleapis.com/auth/earthengine'])

    #initialize credentials
    ee.Initialize(credentials_ee)

    # convert bbox to Earth Engine geometry
    region = ee.Geometry.BBox(*bbox)

    #median mode
    median = median

    #generate request
    image = generate_image(
        region, 
        product = product, # Sentinel-2A 
        min_date = min_date, # Get all images within
        max_date = max_date, # the year 2020
        cloud_pct = cloud_pct, # Filter out images with cloud cover >= 10.0%
        median = median
    )

    #export image to Google Drive
    task = export_image(image, file_name, region, folder, product, proj)

    with tqdm(desc='Downloading to Drive') as pbar:
        status = 'RUNNING'
        while status!="COMPLETED":
            time.sleep(2)
            status = task.status()['state']
            if status == 'FAILED':
                print('FAILED')
                print(task.status())
                break
            pbar.update(1)
    return

def save_to_local_drive(file_name:str = 'site',
                        service_acc_file: str = 
                        "./creds/ee-sat-imagery-nnnn.json"):
    
    #build service for Google Drive
    scopes = ['https://www.googleapis.com/auth/drive']
    credentials_gdrive = Credentials.from_service_account_file(service_acc_file, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials_gdrive)
    
    #check image unique id
    files = []
    page_token = None

    while True:
        # pylint: disable=maybe-no-member
        response = service.files().list(
                                    spaces="drive",
                                    q=f"""\
                                    mimeType = 'image/tiff'\
                                    and name contains '{file_name}'\
                                    and trashed=false
                                    """,
                                    fields="files(id, name, mimeType)",).execute()
        for file in response.get('files', []):
            # Process change
            print(F'Found file: {file.get("name")}, {file.get("id")}')
            real_file_id = file.get("id")
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    #downlod image to local drive
    download_file(real_file_id = real_file_id, 
                        credentials_grive = credentials_gdrive,
                        fileoutname = file_name)
    return
