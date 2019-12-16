# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#项目类：住宅、别墅
class PropertyDataScrapyItem(scrapy.Item):
	# 租售情况
	price_month = scrapy.Field()
	chain_last_month = scrapy.Field()
	YOY = scrapy.Field()
	on_sale_number = scrapy.Field()
	in_rent_number = scrapy.Field()
	# 基本信息
	province_name = scrapy.Field()
	city_name = scrapy.Field()
	county_name = scrapy.Field()
	item_id = scrapy.Field()
	item_name = scrapy.Field()
	item_url = scrapy.Field()
	item_address = scrapy.Field()
	item_district = scrapy.Field()
	post_code = scrapy.Field()
	property_describe = scrapy.Field()
	building_year = scrapy.Field()
	developer = scrapy.Field()
	architectural_structure = scrapy.Field()
	architectural_type = scrapy.Field()
	architectural_area = scrapy.Field()
	floor_area = scrapy.Field()
	households_number = scrapy.Field()
	building_number = scrapy.Field()
	property_management_company = scrapy.Field()
	green_ratio = scrapy.Field()
	plot_ratio = scrapy.Field()
	property_office_tel = scrapy.Field()
	residential_management_fee = scrapy.Field()
	property_office_address = scrapy.Field()
	property_format = scrapy.Field()
	addtion_information = scrapy.Field()
	# 基本信息____写字楼
	loop_position = scrapy.Field()
	office_level = scrapy.Field()
	total_floors = scrapy.Field()
	item_feature = scrapy.Field()
	efficiency_rate = scrapy.Field()
	is_division = scrapy.Field()
	is_involed = scrapy.Field()
	elevator_number = scrapy.Field()
	air_conditon = scrapy.Field()
	decorate_situation = scrapy.Field()
	deliver_criterion = scrapy.Field()
	building_facility = scrapy.Field()
	# 配套设施
	water_supply = scrapy.Field()
	power_supply = scrapy.Field()
	gas_supply = scrapy.Field()
	tele_equipment = scrapy.Field()
	security_management = scrapy.Field()
	cleaning_service = scrapy.Field()
	building_entrance = scrapy.Field()
	parking_space_number = scrapy.Field()
	elevator_service = scrapy.Field()
	# 周边信息
	kindergarten = scrapy.Field()
	middle_primary_school = scrapy.Field()
	university = scrapy.Field()
	mall = scrapy.Field()
	hospital = scrapy.Field()
	post_office = scrapy.Field()
	bank = scrapy.Field()
	other_supporting = scrapy.Field()
	inner_supporting = scrapy.Field()
	# 周边信息____写字楼
	house = scrapy.Field()
	hotel = scrapy.Field()
	office = scrapy.Field()
	restaurant = scrapy.Field()
	remark = scrapy.Field()
# 坐标类
class GeoItem(scrapy.Item):
	item_id = scrapy.Field()
	item_url = scrapy.Field()
	lon = scrapy.Field()
	lat = scrapy.Field()
	location = scrapy.Field()
	city = scrapy.Field()
	district = scrapy.Field()
	street = scrapy.Field()
# 价格走势类
class PriceItem(scrapy.Item):
	item_id = scrapy.Field()
	item_url = scrapy.Field()
	price_two_year = scrapy.Field()

#电梯类
class ElevatorItem(scrapy.Item):
	item_id = scrapy.Field()
	item_url = scrapy.Field()
	elevator_number_new = scrapy.Field()

class UrlItem(scrapy.Item):
	province_name = scrapy.Field()
	city_name = scrapy.Field()
	city_url = scrapy.Field()