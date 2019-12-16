
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Property_Data_Scrapy.items import PropertyDataScrapyItem,GeoItem,ElevatorItem,PriceItem,UrlItem
from scrapy.exporters import CsvItemExporter
from scrapy.conf import settings
import pymongo

# 输出本地csv文件
class PropertyDataScrapyCSVPipeline(object):

    def __init__(self):
        self.dir = ".\data\\"
        self.file = open(self.dir+"information.csv", "wb")
        self.fields_order = [
            'item_id', 'item_name', 'province_name', 'city_name', 'county_name',
            'item_district', 'item_address', 'price_month', 'YOY', 'chain_last_month',
            'on_sale_number', 'in_rent_number', 'developer', 'building_year',
            'architectural_area', 'floor_area', 'plot_ratio', 'green_ratio',
            'architectural_structure', 'architectural_type', 'building_number',
            'total_floors', 'households_number', 'efficiency_rate', 'deliver_criterion',
            'office_level', 'loop_position', 'decorate_situation', 'is_division',
            'is_involed', 'property_describe', 'property_format', 'property_management_company',
            'property_office_address', 'property_office_tel', 'residential_management_fee',
            'building_entrance', 'building_facility', 'elevator_number',
            'parking_space_number', 'item_feature', 'kindergarten', 'middle_primary_school',
            'university', 'hospital', 'bank', 'mall', 'hotel', 'restaurant', 'house',
            'office', 'post_office', 'post_code', 'inner_supporting', 'other_supporting',
            'addtion_information', 'cleaning_service', 'security_management', 'tele_equipment',
            'elevator_service', 'air_conditon', 'gas_supply', 'water_supply',
            'power_supply', 'item_url', 'remark'
            ]
        self.exporter = CsvItemExporter(self.file, encoding='utf-8', fields_to_export=self.fields_order)

    def process_item(self, item, spider):
        if isinstance(item, PropertyDataScrapyItem):
            self.exporter.export_item(item)
        return item

class CoordinateCSVPipeline(object):

    def __init__(self):
        self.dir = ".\data\\"
        self.file = open(self.dir+"Coordinate.csv", "wb")
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')

    def process_item(self, item, spider):
        if isinstance(item, GeoItem):
            self.exporter.export_item(item)
        return item

class ElevatorCSVPipeline(object):

    def __init__(self):
        self.dir = ".\data\\"
        self.file = open(self.dir+"Elevator.csv", "wb")
        self.fields_order = ["item_id", "elevator_number_new"]
        self.exporter = CsvItemExporter(self.file, encoding='utf-8', fields_to_export=self.fields_order)

    def process_item(self, item, spider):
        if isinstance(item, ElevatorItem):
            self.exporter.export_item(item)
        return item

class PriceCSVPipeline(object):

    def __init__(self):
        self.dir = ".\data\\"
        self.file = open(self.dir+"Price.csv", "wb")
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')

    def process_item(self, item, spider):
        if isinstance(item, PriceItem):
            self.exporter.export_item(item)
        return item

# 将数据存入MongoDB数据库
class DataBasePipeline(object):

    def __init__(self):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        dbNAME = settings["MONGODB_DBNAME"]
        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[dbNAME]

    def process_item(self,item,spider):
        if isinstance(item, PropertyDataScrapyItem):
            Sheet1 = self.db[settings["MONGODB_DOCNAME"][0]]
            Sheet1.insert_one(dict(item))
        elif isinstance(item, GeoItem):
            Sheet2 = self.db[settings["MONGODB_DOCNAME"][1]]
            Sheet2.insert_one(dict(item))
        elif isinstance(item, PriceItem):
            Sheet3 = self.db[settings["MONGODB_DOCNAME"][2]]
            Sheet3.insert_one(dict(item))
        elif isinstance(item, ElevatorItem):
            Sheet4 = self.db[settings["MONGODB_DOCNAME"][3]]
            Sheet4.insert_one(dict(item))
        return item

class CiytUrlPipeline(object):
    def __init__(self):
        self.dir = ".\data\\"
        self.file = open(self.dir+"City_url.csv", "wb")
        self.exporter = CsvItemExporter(self.file, encoding='gbk')
    def process_item(self, item, spider):
        if isinstance(item, UrlItem):
            if item['province_name'] != '其他':
                self.exporter.export_item(item)
        return item