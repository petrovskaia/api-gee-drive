import argparse
from gee_download import sat_imagery_to_gdrive, save_to_local_drive

parser = argparse.ArgumentParser()
parser.add_argument('-b', dest='bbox', nargs="+", type=float,
                    help='region of interest bbox')
parser.add_argument('-f', dest='file_name', type=str, 
                    default = 'site', help='output file name')
parser.add_argument('--folder', dest='gdrive_folder',type=str,
                    default = 'test_gee', help='GDrive folder')
parser.add_argument('--min_date', dest='min_date', type=str, 
                    default = '2020-05-01', help='minimum date filter, yyyy-mm-dd')
parser.add_argument('--max_date', dest='max_date', type=str, 
                    default = '2020-09-30', help='maximum date filter, yyyy-mm-dd')
parser.add_argument('--clouds', dest='cloud_pct', type=int, 
                    default = 10, help='cloud percentage filter')
parser.add_argument('--proj', dest='proj', type=str, 
                    default = None, help='EPSG code of geoprojection, EPSG:XXXX')
parser.add_argument('--sa_file', dest='service_acc_file', type=str,
                    default = './creds/ee-sat-imagery-90b7aa0dc579.json', 
                    help='path to service account file')
parser.add_argument('--product', dest='product', type=str,
                    default = 'COPERNICUS/S2_SR_HARMONIZED', help='Google Earth Engine image collection')
parser.add_argument('--median', dest='median', type=bool,
                    default = False, 
                    help='if True = median values from min to max date')
args = parser.parse_args()


sat_imagery_to_gdrive(bbox = args.bbox,
                    file_name = args.file_name, 
                    gdrive_folder = args.gdrive_folder, 
                    proj = args.proj,
                    service_acc_file = args.service_acc_file,
                    product = args.product, 
                    min_date = args.min_date, 
                    max_date = args.max_date, 
                    cloud_pct = args.cloud_pct,
                    median = args.median
                    )
                      
save_to_local_drive(file_name = args.file_name,
                    service_acc_file = args.service_acc_file)


