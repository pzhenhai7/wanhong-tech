#!/usr/bin/env python3
"""
Batch process product photos:
1. Remove background with rembg
2. Paste onto white background
3. Save as JPG to wanhong-tech/assets/
4. Generate products.json entries from OCR data
"""

import os
import json
import io
from pathlib import Path
from PIL import Image
from rembg import remove
import numpy as np

SOURCE_DIR = "/Users/Admin/Desktop/product photo"
TARGET_DIR = "/Users/Admin/wanhong-tech/assets"
WHITE = (255, 255, 255)

# Product data extracted from OCR
# Format: filename -> {model, name, specs}
OCR_DATA = {
    "0088ec7bb4fc2a059e61390b3544d91e.jpg": {
        "model": "HGB17350R",
        "voltage": "3.7V",
        "capacity": "850mAh",
        "energy": "3.15Wh",
        "series": "17系列",
    },
    "026b3a9190d4d9110c5ac52d661a73ad.jpg": {
        "model": "GSP18350P",
        "voltage": "3.7V",
        "capacity": "1000mAh",
        "energy": "3.70Wh",
        "series": "18系列",
    },
    "068eabc0c243b45f18c69b39f18c67c3.jpg": {
        "model": "13400",
        "voltage": "3.7V",
        "capacity": "550mAh",
        "energy": "2.04Wh",
        "series": "13系列",
    },
    "091200ae8992775242dae89fcf204d43.jpg": {
        "model": "SJD16600",
        "voltage": "3.7V",
        "capacity": "1300mAh",
        "energy": "4.81Wh",
        "series": "16系列",
    },
    "17f2e152a87d7314d4dfa7e044595f3e.jpg": {
        "model": "08500",
        "voltage": "3.7V",
        "capacity": "260mAh",
        "energy": "0.96Wh",
        "series": "08系列",
    },
    "25658e225369326750ca437a3b9553c2.jpg": {
        "model": "GSP18350P",
        "voltage": "3.7V",
        "capacity": "1000mAh",
        "energy": "3.70Wh",
        "series": "18系列",
    },
    "283f10cf7277ee106f553729f8a57085.jpg": {
        "model": "18500",
        "voltage": "3.7V",
        "capacity": "1500mAh",
        "energy": "5.55Wh",
        "series": "18系列",
    },
    "2a6d8eae1b04af523c2e11247c870e2d.jpg": {
        "model": "18350",
        "voltage": "3.7V",
        "capacity": "950mAh",
        "energy": "3.52Wh",
        "series": "18系列",
    },
    "381419812aa9d9cf4fe7fefe0790c6d0.jpg": {
        "model": "601444",
        "voltage": "3.7V",
        "capacity": "350mAh",
        "energy": "1.30Wh",
        "series": "软包系列",
    },
    "447629f48e79cd685cb7fef8c09d0883.jpg": {
        "model": "13350",
        "voltage": "3.7V",
        "capacity": "500mAh",
        "energy": "1.85Wh",
        "series": "13系列",
    },
    "497274570b4c4e7d66506ca0e75d4572.jpg": {
        "model": "17350",
        "voltage": "3.7V",
        "capacity": "850mAh",
        "energy": "3.15Wh",
        "series": "17系列",
    },
    "4fb182f44a1a1057127307b9fce29388.jpg": {
        "model": "451645",
        "voltage": "3.7V",
        "capacity": "240mAh",
        "energy": "0.89Wh",
        "series": "软包系列",
    },
    "5999bf51a1964d96722aa6f9c6b8eef5.jpg": {
        "model": "HQD 08570",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "08系列",
    },
    "5999bf51a1964d96722aa6f9c6b8eef5 2.jpg": {
        "model": "HQD 08570",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "08系列",
    },
    "5999bf51a1964d96722aa6f9c6b8eef5 3.jpg": {
        "model": "HQD 08570",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "08系列",
    },
    "5999bf51a1964d96722aa6f9c6b8eef5 4.jpg": {
        "model": "HQD 08570",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "08系列",
    },
    "6527078148953dd3cead41982561093b.jpg": {
        "model": "601444",
        "voltage": "3.7V",
        "capacity": "350mAh",
        "energy": "1.30Wh",
        "series": "软包系列",
    },
    "74981791285bdba51c2229777c7d52e5.jpg": {
        "model": "XSH09430",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "09系列",
    },
    "77359a30032ce62cfa40d60c0b908d1b.jpg": {
        "model": "EVE 801437",
        "voltage": "3.7V",
        "capacity": "350mAh",
        "energy": "1.30Wh",
        "series": "软包系列",
    },
    "7c01027d9a4fa1118f83cb529d2626bd.jpg": {
        "model": "10系列/12系列",
        "voltage": "3.7V",
        "capacity": "180mAh",
        "energy": "0.67Wh",
        "series": "10系列",
    },
    "826fddd83dc6c307f86a9b7829ef1bba.jpg": {
        "model": "651545",
        "voltage": "3.7V",
        "capacity": "370mAh",
        "energy": "1.37Wh",
        "series": "软包系列",
    },
    "836db275780801d38523ded89cd6d0bf.jpg": {
        "model": "13300",
        "voltage": "3.7V",
        "capacity": "360mAh",
        "energy": "1.33Wh",
        "series": "13系列",
    },
    "88149f2a5251d626a989fae765897e78.jpg": {
        "model": "501447",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "软包系列",
    },
    "8815e03fb78d5ce3a0ba6108caa40a7e.jpg": {
        "model": "13400",
        "voltage": "3.7V",
        "capacity": "550mAh",
        "energy": "2.04Wh",
        "series": "13系列",
    },
    "932842e553645e272bae19d5519a32ae.jpg": {
        "model": "CSP18350P",
        "voltage": "3.7V",
        "capacity": "1000mAh",
        "energy": "3.70Wh",
        "series": "18系列",
    },
    "9337914dddf92e63ed19380d896799dd.jpg": {
        "model": "112040",
        "voltage": "3.7V",
        "capacity": "950mAh",
        "energy": "3.52Wh",
        "series": "软包系列",
    },
    "957c8dad343abbb797e6e8b62d2e4a03.jpg": {
        "model": "GSP18500P",
        "voltage": "3.7V",
        "capacity": "1500mAh",
        "energy": "5.55Wh",
        "series": "18系列",
    },
    "9daac70be3320dc37c911635144aedfb.jpg": {
        "model": "501447",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "软包系列",
    },
    "a6c1e4743dc8aad26b5726102a5053ed.jpg": {
        "model": "18系列/21系列/26系列",
        "voltage": "3.7V",
        "capacity": "多规格",
        "energy": "多规格",
        "series": "多系列",
    },
    "b9659633030fb29e4e7d6bf4a2cae2dd.jpg": {
        "model": "18350",
        "voltage": "3.7V",
        "capacity": "1000mAh",
        "energy": "3.70Wh",
        "series": "18系列",
    },
    "c819c8321e9cc1ce4f43c75b83588c02.jpg": {
        "model": "801640",
        "voltage": "3.7V",
        "capacity": "500mAh",
        "energy": "1.85Wh",
        "series": "软包系列",
    },
    "d220387b15a5b54b8730311eb9fdb776.jpg": {
        "model": "173040",
        "voltage": "3.7V",
        "capacity": "2500mAh",
        "energy": "9.25Wh",
        "series": "17系列",
    },
    "df839dfe2386a648043dd514d0bd75d3.jpg": {
        "model": "16350/16450/17350/18350/18500",
        "voltage": "3.7V",
        "capacity": "650-1500mAh",
        "energy": "多规格",
        "series": "多系列",
    },
    "ed4e4098f4d1ff5aab6c56c315c3637f.jpg": {
        "model": "全系列电子烟电芯",
        "voltage": "3.7V",
        "capacity": "可定制",
        "energy": "可定制",
        "series": "全系列",
    },
    "f1d869f3a3809370df492b35c35730d2.jpg": {
        "model": "21350",
        "voltage": "3.7V",
        "capacity": "1300mAh",
        "energy": "4.81Wh",
        "series": "21系列",
    },
    "f78e1e5d888074bcc0f7a0efd5cb3715.jpg": {
        "model": "173040",
        "voltage": "3.7V",
        "capacity": "2500mAh",
        "energy": "9.25Wh",
        "series": "17系列",
    },
    "fb6e534e45a3bc471cabdc255d4ecad5.jpg": {
        "model": "501447",
        "voltage": "3.7V",
        "capacity": "280mAh",
        "energy": "1.04Wh",
        "series": "软包系列",
    },
    "fe615da475955ad55348cb4f8a72f010.jpg": {
        "model": "08570",
        "voltage": "3.7V",
        "capacity": "300mAh",
        "energy": "1.11Wh",
        "series": "08系列",
    },
}

# Product definitions (unique models, deduplicated)
PRODUCTS = [
    # 08系列
    {"id": "08500", "name": "08500 电子烟电池", "subtitle": "260mAh · 3.7V · 0.96Wh", "category": "电子烟电池", "image": "assets/product-photo-17f2e152.jpg", "specs": {"容量": "260mAh", "标称电压": "3.7V", "能量": "0.96Wh", "型号": "08500"}, "applications": ["电子烟", "POD小烟"], "description": "08500 规格锂电池，260mAh容量，3.7V标称电压，适用于小型电子烟设备。"},
    {"id": "08570", "name": "08570 电子烟电池", "subtitle": "280-300mAh · 3.7V · 1.04Wh", "category": "电子烟电池", "image": "assets/product-photo-fe615da4.jpg", "specs": {"容量": "280-300mAh", "标称电压": "3.7V", "能量": "1.04Wh", "型号": "08570"}, "applications": ["电子烟", "POD小烟"], "description": "08570 规格锂电池，280-300mAh容量，3.7V标称电压。HQD品牌电芯，品质稳定，适用于电子烟、POD小烟等设备。"},
    {"id": "09430", "name": "XSH09430 电子烟电池", "subtitle": "280mAh · 3.7V · 1.04Wh", "category": "电子烟电池", "image": "assets/product-photo-74981791.jpg", "specs": {"容量": "280mAh", "标称电压": "3.7V", "能量": "1.04Wh", "型号": "XSH09430"}, "applications": ["电子烟", "POD小烟"], "description": "XSH09430 规格锂电池，280mAh容量，3.7V标称电压，1.04Wh能量。适用于小型电子烟设备。"},

    # 13系列
    {"id": "13300", "name": "13300 电子烟电池", "subtitle": "360mAh · 3.7V · 1.33Wh", "category": "电子烟电池", "image": "assets/product-photo-836db275.jpg", "specs": {"容量": "360mAh", "标称电压": "3.7V", "能量": "1.33Wh", "型号": "13300"}, "applications": ["电子烟", "POD小烟"], "description": "13300 规格锂电池，360mAh容量，3.7V标称电压，1.33Wh能量。适用于电子烟、POD小烟等便携设备。"},
    {"id": "13350", "name": "13350 电子烟电池", "subtitle": "500mAh · 3.7V · 1.85Wh", "category": "电子烟电池", "image": "assets/product-photo-447629f4.jpg", "specs": {"容量": "500mAh", "标称电压": "3.7V", "能量": "1.85Wh", "型号": "13350"}, "applications": ["电子烟", "POD小烟"], "description": "13350 规格锂电池，500mAh容量，3.7V标称电压，1.85Wh能量。适用于电子烟、POD小烟等设备。"},
    {"id": "13400", "name": "13400 电子烟电池", "subtitle": "550mAh · 3.7V · 2.04Wh", "category": "电子烟电池", "image": "assets/product-photo-068eabc0.jpg", "specs": {"容量": "550mAh", "标称电压": "3.7V", "能量": "2.04Wh", "型号": "13400"}, "applications": ["电子烟", "POD小烟"], "description": "13400 规格锂电池，550mAh容量，3.7V标称电压，2.04Wh能量。适用于电子烟、POD小烟等设备。"},

    # 16系列
    {"id": "16350", "name": "16350 电子烟电池", "subtitle": "650mAh · 3.7V · 2.41Wh", "category": "电子烟电池", "image": "assets/product-photo-df839dfe.jpg", "specs": {"容量": "650mAh", "标称电压": "3.7V", "能量": "2.41Wh", "型号": "HGB16350R"}, "applications": ["电子烟", "POD小烟", "便携设备"], "description": "16350 规格锂电池，采用HGB16350R电芯，650mAh容量，3.7V标称电压。适用于电子烟、POD小烟等便携设备。"},
    {"id": "16600", "name": "16600 电子烟电池", "subtitle": "1300mAh · 3.7V · 4.81Wh", "category": "电子烟电池", "image": "assets/product-photo-091200ae.jpg", "specs": {"容量": "1300mAh", "标称电压": "3.7V", "能量": "4.81Wh", "型号": "SJD16600"}, "applications": ["电子烟", "大烟雾设备"], "description": "16600 规格锂电池，采用SJD16600电芯，1300mAh容量，3.7V标称电压。大容量设计，适用于大烟雾电子烟设备。"},

    # 17系列
    {"id": "17350", "name": "17350 电子烟电池", "subtitle": "850mAh · 3.7V · 3.15Wh", "category": "电子烟电池", "image": "assets/product-photo-49727457.jpg", "specs": {"容量": "850mAh", "标称电压": "3.7V", "能量": "3.15Wh", "型号": "17350"}, "applications": ["电子烟", "POD小烟"], "description": "17350 规格锂电池，850mAh容量，3.7V标称电压，3.15Wh能量。适用于电子烟、POD小烟等设备，性能稳定。"},
    {"id": "173040", "name": "173040 电子烟电池", "subtitle": "2500mAh · 3.7V · 9.25Wh", "category": "电子烟电池", "image": "assets/product-photo-d220387b.jpg", "specs": {"容量": "2500mAh", "标称电压": "3.7V", "能量": "9.25Wh", "型号": "173040"}, "applications": ["电子烟", "大烟雾设备", "便携电源"], "description": "173040 规格大容量锂电池，2500mAh容量，3.7V标称电压，9.25Wh能量。采用高纯度钴+三元材料，适用于大烟雾电子烟、便携电源等设备。"},

    # 18系列
    {"id": "18350-950", "name": "18350 电子烟电池 (950mAh)", "subtitle": "950mAh · 3.7V · 3.52Wh", "category": "电子烟电池", "image": "assets/product-photo-2a6d8eae.jpg", "specs": {"容量": "950mAh", "标称电压": "3.7V", "能量": "3.52Wh", "型号": "18350"}, "applications": ["电子烟", "POD小烟", "便携设备"], "description": "18350 规格锂电池，950mAh容量，3.7V标称电压。适用于电子烟、POD小烟等设备。"},
    {"id": "18350-1000", "name": "18350 电子烟电池 (1000mAh)", "subtitle": "1000mAh · 3.7V · 3.70Wh", "category": "电子烟电池", "image": "assets/product-photo-b9659633.jpg", "specs": {"容量": "1000mAh", "标称电压": "3.7V", "能量": "3.70Wh", "型号": "18350"}, "applications": ["电子烟", "大烟雾设备", "便携设备"], "description": "18350 规格锂电池，1000mAh容量，3.7V标称电压，3.70Wh能量。适用于大烟雾电子烟等设备，续航表现优异。"},
    {"id": "18500", "name": "18500 电子烟电池", "subtitle": "1500mAh · 3.7V · 5.55Wh", "category": "电子烟电池", "image": "assets/product-photo-283f10cf.jpg", "specs": {"容量": "1500mAh", "标称电压": "3.7V", "能量": "5.55Wh", "型号": "GSP18500P"}, "applications": ["电子烟", "大烟雾设备", "手电筒"], "description": "18500 规格锂电池，采用GSP18500P电芯，1500mAh容量，3.7V标称电压。适用于大烟雾电子烟、手电筒等设备。"},

    # 21系列
    {"id": "21350", "name": "21350 电子烟电池", "subtitle": "1300mAh · 3.7V · 4.81Wh", "category": "电子烟电池", "image": "assets/product-photo-f1d869f3.jpg", "specs": {"容量": "1300mAh", "标称电压": "3.7V", "能量": "4.81Wh", "型号": "21350"}, "applications": ["电子烟", "大烟雾设备"], "description": "21350 规格大容量锂电池，1300mAh容量，3.7V标称电压。21系列大尺寸电芯，支持高倍率放电，适用于大功率电子烟设备。"},

    # 软包系列
    {"id": "451645", "name": "451645 软包锂电池", "subtitle": "240mAh · 3.7V · 0.89Wh", "category": "软包电池", "image": "assets/product-photo-4fb182f4.jpg", "specs": {"容量": "240mAh", "标称电压": "3.7V", "能量": "0.89Wh", "型号": "ZHR 451645"}, "applications": ["电子烟", "POD小烟", "迷你设备"], "description": "451645 软包锂电池，240mAh容量，3.7V标称电压。ZHR品牌，体积小巧，适用于小型电子烟设备。"},
    {"id": "501447", "name": "501447 软包锂电池", "subtitle": "280mAh · 3.7V · 1.04Wh", "category": "软包电池", "image": "assets/product-photo-fb6e534e.jpg", "specs": {"容量": "280mAh", "标称电压": "3.7V", "能量": "1.04Wh", "型号": "SD501447"}, "applications": ["电子烟", "POD小烟"], "description": "501447 软包锂电池，280mAh容量，3.7V标称电压。超薄设计，适用于电子烟、POD小烟等便携设备。"},
    {"id": "601444", "name": "601444 软包锂电池", "subtitle": "350mAh · 3.7V · 1.30Wh", "category": "软包电池", "image": "assets/product-photo-38141981.jpg", "specs": {"容量": "350mAh", "标称电压": "3.7V", "能量": "1.30Wh", "型号": "GF 601444"}, "applications": ["电子烟", "POD小烟"], "description": "601444 软包锂电池，采用GF电芯，350mAh容量，3.7V标称电压。适用于电子烟、POD小烟等设备，品质稳定。"},
    {"id": "651545", "name": "651545 软包锂电池", "subtitle": "370mAh · 3.7V · 1.37Wh", "category": "软包电池", "image": "assets/product-photo-826fddd8.jpg", "specs": {"容量": "370mAh", "标称电压": "3.7V", "能量": "1.37Wh", "型号": "LVS 651545"}, "applications": ["电子烟", "POD小烟"], "description": "651545 软包锂电池，采用LVS电芯，370mAh容量，3.7V标称电压。适用于电子烟、POD小烟等设备。"},
    {"id": "801437", "name": "801437 软包锂电池", "subtitle": "350mAh · 3.7V · 1.30Wh", "category": "软包电池", "image": "assets/product-photo-77359a30.jpg", "specs": {"容量": "350mAh", "标称电压": "3.7V", "能量": "1.30Wh", "型号": "EVE 801437"}, "applications": ["电子烟", "POD小烟", "便携设备"], "description": "801437 软包锂电池，采用EVE亿纬锂能电芯，350mAh容量，3.7V标称电压。品质稳定，一致性好，适用于电子烟、POD小烟等便携设备。"},
    {"id": "112040", "name": "112040 软包锂电池", "subtitle": "950mAh · 3.7V · 3.52Wh", "category": "软包电池", "image": "assets/product-photo-9337914d.jpg", "specs": {"容量": "950mAh", "标称电压": "3.7V", "能量": "3.52Wh", "型号": "112040"}, "applications": ["电子烟", "POD小烟", "便携设备"], "description": "112040 软包锂电池，950mAh容量，3.7V标称电压，3.52Wh能量。大容量软包设计，适用于电子烟、POD小烟等设备。"},

    # 全系列展示（作为产品类别展示）
    {"id": "series-overview", "name": "电子烟全系列电芯", "subtitle": "08~26系列 · 全规格覆盖 · 支持定制", "category": "OEM/ODM定制", "image": "assets/product-photo-ed4e4098.jpg", "specs": {"产品系列": "08系列 / 10系列 / 13系列 / 16系列 / 17系列 / 18系列 / 20系列 / 21系列 / 26系列", "电压": "3.7V (可定制)", "容量范围": "180mAh - 2500mAh", "特性": "钴+三元材料 · 支持OEM/ODM定制"}, "applications": ["电子烟", "POD小烟", "大烟雾设备", "一次性电子烟", "换弹式电子烟"], "description": "万鸿科技提供电子烟全系列电芯，从08系列到26系列，覆盖180mAh到2500mAh全容量范围。采用高纯度钴+三元正极材料，支持OEM/ODM定制。所有产品通过CE、FCC等国际认证。"},
]

# File mapping: which source file maps to which product ID
PRODUCT_IMAGE_MAP = {
    "17f2e152a87d7314d4dfa7e044595f3e.jpg": "08500",
    "fe615da475955ad55348cb4f8a72f010.jpg": "08570",
    "74981791285bdba51c2229777c7d52e5.jpg": "09430",
    "836db275780801d38523ded89cd6d0bf.jpg": "13300",
    "447629f48e79cd685cb7fef8c09d0883.jpg": "13350",
    "068eabc0c243b45f18c69b39f18c67c3.jpg": "13400",
    "df839dfe2386a648043dd514d0bd75d3.jpg": "16350",
    "091200ae8992775242dae89fcf204d43.jpg": "16600",
    "497274570b4c4e7d66506ca0e75d4572.jpg": "17350",
    "d220387b15a5b54b8730311eb9fdb776.jpg": "173040",
    "2a6d8eae1b04af523c2e11247c870e2d.jpg": "18350-950",
    "b9659633030fb29e4e7d6bf4a2cae2dd.jpg": "18350-1000",
    "283f10cf7277ee106f553729f8a57085.jpg": "18500",
    "f1d869f3a3809370df492b35c35730d2.jpg": "21350",
    "4fb182f44a1a1057127307b9fce29388.jpg": "451645",
    "fb6e534e45a3bc471cabdc255d4ecad5.jpg": "501447",
    "381419812aa9d9cf4fe7fefe0790c6d0.jpg": "601444",
    "826fddd83dc6c307f86a9b7829ef1bba.jpg": "651545",
    "77359a30032ce62cfa40d60c0b908d1b.jpg": "801437",
    "9337914dddf92e63ed19380d896799dd.jpg": "112040",
    "ed4e4098f4d1ff5aab6c56c315c3637f.jpg": "series-overview",
}


def process_image(src_path, dst_name):
    """Remove background, place on white, save as JPG."""
    dst_path = os.path.join(TARGET_DIR, dst_name)

    # Skip if already done
    if os.path.exists(dst_path):
        print(f"  SKIP (exists): {dst_name}")
        return dst_path

    try:
        img = Image.open(src_path)

        # Resize to reasonable size (max 800px)
        w, h = img.size
        if max(w, h) > 800:
            scale = 800 / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        # Convert RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Remove background
        print(f"  Removing bg: {dst_name} ({img.size[0]}x{img.size[1]})...")
        img_no_bg = remove(img, alpha_matting=True, alpha_matting_foreground_threshold=240)

        # Create white background
        bg = Image.new('RGBA', img_no_bg.size, (255, 255, 255, 255))
        bg.paste(img_no_bg, (0, 0), img_no_bg)

        # Convert to RGB and save as JPG
        final = bg.convert('RGB')
        final.save(dst_path, 'JPEG', quality=90)
        print(f"  DONE: {dst_name}")
        return dst_path
    except Exception as e:
        print(f"  ERROR processing {src_path}: {e}")
        # Fallback: just copy with resize
        try:
            img = Image.open(src_path)
            w, h = img.size
            if max(w, h) > 800:
                scale = 800 / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            if img.mode == 'RGBA':
                bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                bg.paste(img, (0, 0), img)
                img = bg.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(dst_path, 'JPEG', quality=90)
            print(f"  FALLBACK SAVED: {dst_name}")
            return dst_path
        except Exception as e2:
            print(f"  DOUBLE ERROR: {e2}")
            return None


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Process images that have a mapping
    print("=== Processing product images ===")
    processed = {}

    for src_file, product_id in PRODUCT_IMAGE_MAP.items():
        src = os.path.join(SOURCE_DIR, src_file)
        if not os.path.exists(src):
            print(f"  MISSING: {src_file}")
            continue
        dst_name = f"product-photo-{src_file.split('.')[0][:8]}.jpg"
        result = process_image(src, dst_name)
        if result:
            processed[product_id] = dst_name

    # Generate products.json
    print(f"\n=== Generating products.json ({len(PRODUCTS)} products) ===")

    products_json = []
    for i, p in enumerate(PRODUCTS):
        price = 0
        if p["category"] == "软包电池":
            price = 12.00
        elif p["category"] == "OEM/ODM定制":
            price = 0
        elif "2500" in p.get("subtitle", ""):
            price = 22.00
        elif "1500" in p.get("subtitle", ""):
            price = 16.00
        elif "1300" in p.get("subtitle", ""):
            price = 15.00
        elif "1000" in p.get("subtitle", ""):
            price = 14.00
        elif "950" in p.get("subtitle", ""):
            price = 13.50
        elif "850" in p.get("subtitle", ""):
            price = 13.00
        elif "650" in p.get("subtitle", ""):
            price = 12.50
        elif "550" in p.get("subtitle", ""):
            price = 12.00
        elif "500" in p.get("subtitle", ""):
            price = 11.50
        elif "360" in p.get("subtitle", ""):
            price = 11.00
        elif "350" in p.get("subtitle", ""):
            price = 10.50
        elif "280" in p.get("subtitle", "") or "300" in p.get("subtitle", ""):
            price = 10.00
        elif "260" in p.get("subtitle", ""):
            price = 9.50
        elif "240" in p.get("subtitle", ""):
            price = 9.00
        else:
            price = 13.00

        badge = "新品" if i < 5 else ("热销" if "2500" in p.get("subtitle", "") or "1000" in p.get("subtitle", "") else None)

        product = {
            "id": p["id"],
            "name": p["name"],
            "subtitle": p["subtitle"],
            "fullName": f'{p["name"]}<br>{p["subtitle"]}',
            "category": p["category"],
            "price": price,
            "priceDesc": "单价 / 含税含运费，批量价格另议",
            "image": p["image"],
            "tag": badge,
            "tagColor": "orange",
            "badge": badge,
            "badgeType": "new" if badge == "新品" else "hot",
            "featured": i < 4,
            "specs": p["specs"],
            "features": [f'{k}: {v}' for k, v in list(p["specs"].items())[:4]],
            "applications": p["applications"],
            "description": p["description"],
            "fullDescription": f'<p>{p["description"]}</p><p>所有产品通过CE、FCC等国际认证，内置过充、过放、短路多重保护。支持OEM/ODM定制，欢迎询价。</p>',
            "specList": [{"label": k, "value": v} for k, v in p["specs"].items()],
            "createdAt": "2026-06-04"
        }
        products_json.append(product)

    # Write products.json
    json_path = os.path.join(os.path.dirname(TARGET_DIR), "data", "products.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    data = {
        "products": products_json,
        "settings": {
            "companyName": "惠州市万鸿科技有限公司",
            "companyNameEn": "Huizhou Wanhong Technology Co., Ltd",
            "phone": "13682629862",
            "email": "info@wanhong-tech.com",
            "contactPerson": "廖万欣",
            "contactTitle": "总经理",
            "address": "广东省惠州市仲恺高新区惠风路8号",
            "footerDesc": "专注电子烟电池 · 无人机电池研发制造",
            "githubRepo": "pzhenhai7/wanhong-tech",
            "githubToken": ""
        }
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Written {len(products_json)} products to {json_path}")

    # Print summary
    print("\n=== PRODUCT CATALOG ===")
    for p in products_json:
        print(f"  [{p['category']}] {p['name']} - {p['subtitle']} (¥{p['price']:.2f})")


if __name__ == '__main__':
    main()
