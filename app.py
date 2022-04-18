from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import json

with open('secret.json') as f:
    secret = json.load(f)

KEY = secret['KEY']
ENDPOINT = secret['ENDPOINT']

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def get_tags(filepath):
    local_image = open(filepath, "rb")

    tags_result = computervision_client.tag_image_in_stream(local_image)
    tags = tags_result.tags
    tags_name = []
    tags_conf = []
    tags_mix = []
    conf_data = 0
    mix = ''
    for tag in tags:
        tags_name.append(tag.name)
        conf_data = round(tag.confidence*100)
        conf_data = f'{conf_data}%'
        tags_conf.append(conf_data)
        mix = f'{tag.name} : {conf_data}'
        tags_mix.append(mix)
    
    return tags_name, tags_conf, tags_mix

def detect_objects(filepath):
    local_image = open(filepath, "rb")

    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    objects = detect_objects_results.objects
    
    return objects

import streamlit as st
from PIL import ImageDraw
from PIL import ImageFont

st.title('物体検出アプリ')

uploaded_file = st.file_uploader('Choose am image...', type=['jpg','png'])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_path = f'img/{uploaded_file.name}'
    img.save(img_path)
    objects = detect_objects(img_path)

    # 描画
    draw = ImageDraw.Draw(img)

    for object in objects:
        x = object.rectangle.x
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        caption = object.object_property
        size_font= int(w*0.2)
        font_info = ImageFont.truetype(font='./font/arial.ttf' ,size=size_font)
        text_w, text_h = draw.textsize(caption, font=font_info)
        size_frame = int(w*0.02)
        draw.rectangle([(x, y), (x+w, y+h)], fill=None, outline='green', width=size_frame)
        draw.rectangle([(x, y), (x+text_w, y+text_h)], fill='green')
        draw.text((x, y), caption, fil='white', font=font_info)
    
    st.image(img)

    tags_name, tags_conf, tags_mix = get_tags(img_path)
    tags_name = ', '.join(tags_name)
    tags_conf = str(", ".join(map(str, tags_conf)))
    tags_mix = str(", ".join(map(str, tags_mix)))
    st.markdown('**認識されたコンテンツタグ**')
    # st.markdown(f'> {tags_name}')
    # st.markdown(f'> {tags_conf}')
    st.markdown(f'> {tags_mix}')