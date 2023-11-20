from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import io
import ee


def generate_image(
    region, 
    product= 'COPERNICUS/S2_SR_HARMONIZED', 
    min_date='2020-05-01',
    max_date='2020-09-30',
    cloud_pct=100,
    median = False
):

    """Generates cloud-filtered Sentinel-2 image  
    
    Args:
      region (ee.Geometry): The geometry of the area of interest to filter to.
      product (str): Earth Engine asset ID
        You can find the full list of ImageCollection IDs
        at https://developers.google.com/earth-engine/datasets
      min_date (str): Minimum date to acquire collection of satellite images
      max_date (str): Maximum date to acquire collection of satellite images
      cloud_pct (float): The cloud cover percent to filter by (default )
      median (bool): Median-aggregated image from min to max date

    Returns:
      ee.image.Image: Generated Sentinel-2 image clipped to the region of interest
    """
    if median == True:

        # specify and filter image collection   
        image_coll = ee.ImageCollection(product)\
            .filterBounds(region)\
            .filterDate(str(min_date), str(max_date))\
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))\
            .sort('CLOUD_COVER')\
            .median()

        image = ee.Image(image_coll)
        image_uint16 = ee.Image.uint16(image)

    if median == False:
          
          # specify and filter image collection   
        image_coll = ee.ImageCollection(product)\
            .filterBounds(region)\
            .filterDate(str(min_date), str(max_date))\
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))\
            .sort('CLOUD_COVER')\

        #turn image collection to list and get img names
        collection_list = image_coll.toList(image_coll.size())
        list_item = ee.Image(collection_list.get(1))
        img_name = list_item.get('system:index').getInfo()
        
        #choose one image from image collection
        image_coll2 = image_coll\
                      .filter(ee.Filter.eq('system:index', img_name))     
        image = ee.Image(image_coll2.median())
        image_uint16 = ee.Image.uint16(image) 


    return image_uint16.clip(region)



def export_image(image, filename, region, folder, product, proj):
    """Export Image to Google Drive.
    
    Args:
      image (ee.image.Image): Generated Sentinel-2 image
      filename (str): Name of image, without the file extension
      geometry (ee.geometry.Geometry): The geometry of the area of 
        interest to filter to.
      folder (str): The destination folder in your Google Drive.
      proj (str): Desired geoprojection 

    Returns:
      ee.batch.Task: A task instance
    """

    print('Exporting to {}.tif ...'.format(filename))


    if proj == None:

        myProj =  ee.ImageCollection(f"""{product}""")\
                    .filterBounds(region)\
                    .first()\
                    .select(1)\
                    .projection()

        myScale = myProj.nominalScale()

        task = ee.batch.Export.image.toDrive(
          image=image,
          driveFolder=folder,
          region=region,
          description=filename,
          scale= myScale.getInfo(),
          fileFormat='GeoTIFF',
          crs=myProj.getInfo()['crs'],
          maxPixels=900000000
        )
        task.start()

    else:

        task = ee.batch.Export.image.toDrive(
          image=image,
          driveFolder=folder,
          region=region,
          description=filename,
          scale= 10,
          fileFormat='GeoTIFF',
          crs=proj,
          maxPixels=900000000
        )
        task.start()

    
    return task

def download_file(real_file_id, credentials_grive, fileoutname):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
    Returns : IO object with location.
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=credentials_grive)

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=real_file_id)
  
        # export_media
        file = io.FileIO('./results/'+fileoutname+'.tiff',mode='wb')
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return 