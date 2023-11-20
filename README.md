
# Download satellite images from Google Earth Engine API to Google Drive with Google Cloud platform
This repo helps in using Google Cloud instruments: Google Earth Engine API and Google Drive API

To create APIs on Google Cloud, please refer to this link:

https://developers.google.com/earth-engine/cloud

You can use parser (gee_download_parser.py) from linux command line.
Parser usage example:
<pre><code> python gee_download_parser.py -b 142.707 53.454 142.797 53.494 -f sakhalin --min_date 2022-06-01 --max_date 2022-08-01 --clouds 1 <code><pre>

