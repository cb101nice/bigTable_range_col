import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
from math import radians, cos, sin, asin, sqrt
import re
import googlemaps

new_key1 = 'AIzaSyA1yfLkwTFPMVUs6Ms8VBvHp1EarM-PL0Q'
new_key2 = 'AIzaSyDzpcg00DecOXcDrRrVw16V_yOYj8H62XM'
new_key3 = 'AIzaSyDebea1g0MYe_AM44BrW5IkEwVIQrjzof4'
new_key4 = 'AIzaSyCGQ9tGC8H2hpfwRHycKRZBic78eEfBEF0'
new_key5 = 'AIzaSyBWzTtSzpf9u9Wxki_AKKR9CrvhO_Iw0gQ'
new_key6 = 'AIzaSyDFNqrxtoAHYAQVA0QVim0nM7bAivpXm5w'
new_key7 = 'AIzaSyA2q3Zo3RDCNtYw4rzmO4rCyB41ZozJK6I'
new_key8 = 'AIzaSyDCvTAN8k57d-w_D5P8Pur2nJwHs7DNOSY'
key1 = 'AIzaSyC_vcarGfMvLtfT9Hzgn1Q8ZgUbShHDSjk'
key2 = 'AIzaSyBQlgzxJoj-bFlT1HkIY6rAYeTFrT_YcSE'
key3 = 'AIzaSyArwew-mKF3WtQ_TSOvCTJl-2PfSatDvaQ'
key4 = 'AIzaSyBnoc6s57rpUmrzXyGkeXvjteWKhXL8VKI'
key5 = 'AIzaSyDDUiVULyAhtJ_RJSyP3TUOTk_fK9ir6YI'
key6 = 'AIzaSyD5X8K0uC3aLMuJ6crbbc0djiyEIWJb9kk'
key7 = 'AIzaSyCO0xnAgE7AT1a6c29A_PZWDsQl_yXIlI8'
key8 = 'AIzaSyCoF0hPC9XSwprvJ7QTn9sRsnNceo9j-tE'

key_list = [new_key1, new_key2, new_key3, new_key4, new_key5, new_key6, new_key7, new_key8,
            key1, key2, key3, key4, key5, key6, key7, key8]

def geoc(df, key_num1):
    if 'lat' not in df.columns:
        df['lat'] = pd.Series(np.zeros(len(df)), index=df.index)
        df['lon'] = pd.Series(np.zeros(len(df)), index=df.index)
#     start_n = input("starting number ")
    print("the current key number is " + str(key_num1))
#     for i in range(int(start_n), len(df)):
    i = int(input('start from '))
    global keyStatus
    keyStatus = 1
    while i < len(df):
        addr = df['address'][i]
        url = 'https://maps.googleapis.com/maps/api/geocode/xml?address=' + addr + '&key=' + key_list[int(key_num1)]
        r = requests.get(url)
        content = r.content
        bsobj = BeautifulSoup(content, 'html.parser')
        status = bsobj.find('status').get_text()
        if status == 'OVER_QUERY_LIMIT':
            print('need to change key, the current file number is ' + str(i))
            key_num1 = int(key_num1) + 1
            print('key number has changed to ' + str(key_num1))
            i-=1
            if key_num1 > len(key_list) - 1:
                keyStatus = 0
                break
        elif status == 'OK':
            lat = bsobj.find_all('lat')[0].get_text()    
            lon = bsobj.find_all('lng')[0].get_text()
            df['lat'][i] = lat
            df['lon'][i] = lon
        else:
            print('address is not vlaid')
            lat = 0
            lon = 0
            df['lat'][i] = lat
            df['lon'][i] = lon
        if i % 500 == 0:
            print(i)
            print('緯度為: ' + str(lat))
            print('經度為: ' + str(lon))
        i+=1
        time.sleep(1)        
    return df

def state_code_compute(x):    
    scale_km = 0.5
    lat = x[0]
    lon = x[1]
    lat_to_km = lat*110.574
    lon_to_km = abs(lon*(111.320*cos(lat)))

    state_code_x = str(int(lat_to_km/scale_km))
    state_code_y = str(int(lon_to_km/scale_km))
    if len(state_code_y) == 4:
        state_code_y = '0'+state_code_y
    state_code = state_code_x+state_code_y
    return state_code

def centerProducer(state_code):
    scale_km = 0.5
    x_code = int(state_code[:4]) + 0.5
    y_code = int(state_code[4:]) + 0.5

    x_code_m_scale = x_code * scale_km
    y_code_m_scale = y_code * scale_km

    x_code_to_lat = float(x_code_m_scale) / 110.574
    cosine_ = abs(cos(x_code_to_lat))
    y_code_to_lat = float(y_code_m_scale) / (111.320 * cosine_)

    return x_code_to_lat, y_code_to_lat

class googleUClient:
    def __init__(self,key):
        self.gmaps = googlemaps.Client(key=key)
    def getInformation(self,center):
        res = self.gmaps.reverse_geocode(center,language='zh-TW')
        res_str = str(res)
        try:
            political_1 = re.findall("'(..里)", res_str)[0]
            political_2 = re.findall("'(..區)", res_str)[0]
            political_3 = re.findall("'(..市)", res_str)[0]
            print(political_3)
            return {'市': political_3,'區': political_2,'里': political_1}
        except:
            political_1 = None
            political_2 = None
            political_3 = None
            print(res)
            return {'市': political_3,'區': political_2,'里': political_1}

def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
 
    # haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 地球平均半径，单位为公里
    return c * r