import os
import zipfile
import urllib.request
from urllib.error import HTTPError

base_url = "https://github.com/jinyiabc/china_stock_data/raw/main/"


def get_data(rel_url):
    url = base_url + rel_url
    local_file = os.path.basename(url)
    try:
        urllib.request.urlretrieve(url, local_file)
    except HTTPError as err:
        print(err)
        print("Unable to download data")
        return None

    if url.endswith('.zip'):
        z = zipfile.ZipFile(local_file)
        z.extractall()
        info = z.infolist().pop(0)
        print("Downloaded {}".format(os.path.split(info.filename)[0]))
    else:
        print("Downloaded {}".format(local_file))


def get_module_1(username):
    get_data("module-{0:02n}/{1:s}.zip".format(1, username))


def get_module_2(username):
    get_data("module-{0:02n}/{1:s}.zip".format(2, username))

def get_module_3(username):
    get_data("module-{0:02n}/{1:s}".format(3, username))