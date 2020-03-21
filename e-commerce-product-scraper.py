from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError,TooManyRedirects

import requests
import time
import csv
from lxml import html
from bs4 import BeautifulSoup
import json
import random


def csv_reader(file):

    product_urls = []

    with open(file) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            product_urls.append(row.pop())

    return product_urls


product_urls = csv_reader('product-urls.csv')


headers = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',


    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36',

}
cookie =          {

              "name": "Cookie",
              "value": ""
            }



def get_page(url):

    s = requests.Session()
    s.headers = headers
    cj = requests.utils.cookiejar_from_dict(cookie)
    s.cookies = cj


    retry = True
    while retry:

        try:
            response = s.get(url,timeout = 30)
            if response.status_code == 200:
                print('Got Page')
                retry = False

            else:
                print('Status Code Other than 200',response.status_code)
                time.sleep(random.randint(7,11))


        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError ,TooManyRedirects) as e:

            print('Did not got page  ',e)
            retry = True
            time.sleep(random.randint(7,11))

    return response

# Function to Parse Page for Product Information
def product_parser(response):

    page = BeautifulSoup(response.content,'lxml')

    item_code = page.find('div',class_='reg').text.strip()
    item_name = page.find('h1',class_='tituli').text
    item_description = page.find('div',class_='textg').text.strip()
    item_supplier = page.find('div',class_='tag catanogo').text
    item_price = page.find('td',class_='lasd-chald').text.strip()
    color_table = page.find_all('div',class_='coulor')

    # for i in colors:
    #     i.get('title')


    print(item_code,'/',item_name,'/',item_description,'/',item_supplier,'/',item_price,'\n')

    color_variants = []
    for i in color_table:
        #print(i.get('title'))
        color_variants.append(i.get('title'))

    print(color_variants)

    #print(len(color_variants))

    if len(color_variants) == 0:
        clr = page.find_all('div',class_='color-button')
        print('Getting Colors from other place')

        for i in clr:
            color_variants.append(i.get('title'))






    product_info = {

        'item_code' : item_code,
        'item_name' : item_name,
        'item_description' : item_description,
        'item_supplier' : item_supplier,
        'item_price' : item_price,
        'available_colors' : color_variants

    }

    return product_info


#Function to store info in CSV / Excel
def save_info(product_info,index,url):

    try:

        file = "products_data.csv"
        csv_file = open(file, 'a', newline="")
        writer = csv.writer(csv_file)


        writer.writerow([index,url,product_info['item_code'],product_info['item_name'],product_info['item_description'],product_info['item_supplier'],product_info['item_price']]+product_info['available_colors'])
        csv_file.close()
        print('Writing CSV Finished')

    except Exception as e:
        print('Error in save_info() ',e)
        print('Saving URL and Index in Left Out')

        left_out(index,url)



def left_out(index,url):

    file = "left_out.csv"
    csv_file = open(file, 'a', newline="")
    writer = csv.writer(csv_file)
    writer.writerow([index,url])
    csv_file.close()
    print('Saved Left Out URL')





# Function to Download Product Images
def image_downloader(response):


    base_url = 'https://www.stricker-europe.com'

    page = BeautifulSoup(response.content,'lxml')
    url = page.find('a',id='download-imagens-produto').get('href')
    item_code = page.find('div',class_='ref').text.strip()

    download_url = base_url + url

    down_res =get_page(download_url)

    with open('Images/'+item_code+'.zip', 'wb') as f:
        f.write(down_res.content)

    print('Downloaded')




def log_info(url,index):

    file = "Last_Product_Scraped.csv"
    csv_file = open(file, 'w', newline="")
    writer = csv.writer(csv_file)


    writer.writerow([index,url])

    csv_file.close()


def main(given_list):

    for url in given_list:

        print('Scraping url: ',url,' Number : ',given_list.index(url)+1+1095)
        page = get_page(url)
        prod_info=product_parser(page)
        save_info(prod_info,given_list.index(url)+1,url)

        print('Now Downloading Images , after little time')

        time.sleep(random.randint(2,5))
        image_downloader(page)

        log_info(url,given_list.index(url)+1)

        time.sleep(random.randint(4,10))



























