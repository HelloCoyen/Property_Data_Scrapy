# -*- coding: utf-8 -*-

import scrapy
import re
from Property_Data_Scrapy.items import PropertyDataScrapyItem,GeoItem,ElevatorItem,PriceItem
#from scrapy_redis.spiders import RedisSpider
from Property_Data_Scrapy.libs.baidu_to_gaode import bdToGaoDe

#class FangtianxiaspiderSpider(RedisSpider): # redis引擎
class FangtianxiaspiderSpider(scrapy.Spider):

    name = 'FangtianxiaSpider'
    #redis_key = "FangtianxiaSpider:start_urls" # redis起始页
    allowed_domains = ['fang.com']
    start_urls = ["https://esf.fang.com/newsecond/esfcities.aspx"]
    # 解析选定城市二手房网站，发送各城市请求
    def parse(self,response):
        select_set = ['湖北','广东','四川','湖南','直辖市']
        province_list = response.xpath('//div[@class="letterSelt"]/div[@class="outCont"]/ul/li')
        for i in range(len(province_list)):
            province_name = province_list.xpath('./strong/text()')[i].extract()
            province_list_selected = province_list[i]
            if province_name in select_set:
                city_list = province_list_selected.xpath('./a')
                for j in range(len(city_list)):
                    city_name = city_list.xpath('./text()')[j].extract()
                    city_url = city_list.xpath('./@href')[j].extract()
                    city_url = city_url.replace("http:","")
                    city_url = city_url.replace("1","")
                    city_url = city_url.replace("/","")
                    city_url = "https://" + city_url + '/housing/'
                    yield scrapy.Request(city_url,callback=self.parse_county, meta={'province_name': province_name, 'city_name': city_name})
    # 解析当前城市下区县，以区县业态为起点，查找详情页
    def parse_county(self,response):
        province_name = response.meta['province_name']
        city_name = response.meta['city_name']
        city_url = response._url
        county_list = response.xpath('//div[@class="qxName"]/a')
        for i in range(len(county_list)):
            county_name = county_list.xpath('./text()')[i].extract()
            if not county_name == '不限' or '周边' in county_name:
                county_code = county_list.xpath('./@href')[i].extract()
                county_url = city_url.replace("/housing/", county_code)
                county_url1 = county_url.replace('__0', '__1')
                county_url2 = county_url.replace('__0', '__2')
                county_url3 = county_url.replace('__0', '__3')
                county_url4 = county_url.replace('__0', '__4')
                yield scrapy.Request(county_url1,callback=self.parse_list, meta={'province_name': province_name, 'city_name': city_name, 'county_name': county_name})
                yield scrapy.Request(county_url2,callback=self.parse_list, meta={'province_name': province_name, 'city_name': city_name, 'county_name': county_name})
                yield scrapy.Request(county_url3,callback=self.parse_list, meta={'province_name': province_name, 'city_name': city_name, 'county_name': county_name})
                yield scrapy.Request(county_url4,callback=self.parse_list, meta={'province_name': province_name, 'city_name': city_name, 'county_name': county_name})
    # 解析当前城市初始信息
    def parse_list(self, response):
        request_url = response._url
        province_name = response.meta['province_name']
        city_name = response.meta['city_name']
        county_name = response.meta['county_name']
        # 获取城市短名
        city_short_name = re.search(r'^https:\/\/(.*)\.esf\.fang\.com\/housing\/.*', request_url)
        if city_short_name:
            city_short_name = city_short_name.group(1)
        else:
            city_short_name = "bj"
        # 进度提示行
        pattern = u"__(\d)_0_0_0_(\d+)_0_0_0"
        tips_list = re.search(pattern, request_url)
        Max_page = response.xpath('//span[@class="txt"]/text()').extract_first()
        if Max_page and tips_list:
            Max_page = Max_page[1: -1]
            print(f"当前爬取城市:{province_name}-{city_name}-{county_name},业态为{tips_list.group(1)},当前为第{tips_list.group(2)}页,总共{Max_page}页,进度为{int(tips_list.group(2))/int(Max_page):.2%}")
        # 获取项目列表信息
        item_list = response.xpath('//div[contains(@class, "list rel") or contains(@class, "list rel mousediv")]')
        # 取各项目详细信息界面链接，并发送请求
        mark = "house-xm"
        if '__1' in request_url or '__2' in request_url:
            for i in range(len(item_list)):
                item_id = item_list.xpath('//a[@class="plotTit"]/../a/@projcode')[i].extract()
                item_name = item_list.xpath('//a[@class="plotTit"]/text()')[i].extract()
                on_sale_number = item_list.xpath(u'//li[text()="套在售"]/a/text()')[i].extract()
                on_sale_number = int(on_sale_number)
                in_rent_number = item_list.xpath(u'//li[text()="套在租"]/a/text()')[i].extract()
                in_rent_number = int(in_rent_number)
                # 项目详情页获取项目基本信息
                item_url = 'https:' + item_list.xpath('//a[@class="plotTit"]/@href')[i].extract() + 'xiangqing/'
                item_url = item_url.replace('esf/', '')
                if mark not in item_url:
                    meta={'item_id': item_id, 'item_name': item_name,
                          'on_sale_number': on_sale_number, 'in_rent_number': in_rent_number,
                          'province_name': province_name, 'city_name': city_name,
                          'county_name': county_name}
                    yield scrapy.Request(item_url, callback=self.parse_residence_detail, meta=meta)
                    # 项目首页获取电梯数
                    item_url0 = item_url.replace('xiangqing/', '')
                    yield scrapy.Request(item_url0, callback=self.parse_elevator, meta={'item_id': item_id})
                    # 住宅项目两年价格走势
                    item_price_url = f'https://fangjia.fang.com/fangjia/common/ajaxdetailtrenddata/{city_short_name}?dataType=proj&projcode={item_id}&year=2'
                    yield scrapy.Request(item_price_url, callback=self.parse_price, meta={'item_id': item_id})
                    # 项目坐标
                    item_coordinate_url = f'https://ditu.fang.com/?c=channel&a=xiaoquNew&newcode={item_id}&city={city_short_name}&width=1200&height=455&resizePage={item_url0}/house/web/map_resize.html&category=residence&esf=1'
                    yield scrapy.Request(item_coordinate_url, callback=self.parse_map, meta={'item_id': item_id})
        else:
            for i in range(len(item_list)):
                item_id = item_list.xpath('//a[@class="plotTit"]/../a/@projcode')[i].extract()
                item_name = item_list.xpath('//a[@class="plotTit"]/text()')[i].extract()
                on_sale_number = item_list.xpath(u'//li[text()="套在售"]/a/text()')[i].extract()
                on_sale_number = int(on_sale_number)
                in_rent_number = item_list.xpath(u'//li[text()="套在租"]/a/text()')[i].extract()
                in_rent_number = int(in_rent_number)
                # 项目详情页获取项目基本信息
                item_url = 'https:' + item_list.xpath('//a[@class="plotTit"]/@href')[i].extract() + 'xiangqing/'
                item_url = item_url.replace('esf/', '')
                if mark not in item_url:
                    meta = {'item_id': item_id, 'item_name': item_name,
                            'on_sale_number': on_sale_number, 'in_rent_number': in_rent_number,
                            'province_name': province_name, 'city_name': city_name,
                            'county_name': county_name}
                    yield scrapy.Request(item_url, callback=self.parse_commerce_detail, meta=meta)
                    # 项目坐标
                    if city_short_name != "bj":
                        item_coordinate_url = f'https://{city_short_name}.esf.fang.com/newsecond/map/newhouse/ShequMap.aspx?newcode={item_id}'
                    else:
                        item_coordinate_url = f'https://esf.fang.com/newsecond/map/newhouse/ShequMap.aspx?newcode={item_id}'
                    yield scrapy.Request(item_coordinate_url, callback=self.parse_map, meta={'item_id': item_id})
        # 获取下一页
        next_page_url = response.xpath('//a[@id="PageControl1_hlk_next"]/@href').extract_first()
        if next_page_url:
            pattern = '(http.*esf\.fang\.com).*'
            city_url = re.search(pattern, request_url).group(1)
            next_page_url = city_url + response.xpath('//a[@id="PageControl1_hlk_next"]/@href').extract_first()
            yield scrapy.Request(next_page_url, callback=self.parse_list, meta={'province_name': province_name, 'city_name': city_name, 'county_name': county_name})
    # 详情页解析
    def parse_residence_detail(self, response):
        remark = [] #备注
        Fangtianxia_item = PropertyDataScrapyItem()
        # 基本信息
        item_address = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="小区地址："]/../text()').extract_first()
        item_district = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="所属区域："]/../text()').extract_first()
        post_code = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[contains(text(), "编：")]/../text()').extract_first()
        property_describe = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="产权描述："]/../text()').extract_first()
        building_year = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="建筑年代："]/../text()').extract_first()
        developer = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="开 发 商："]/../text()').extract_first()
        architectural_structure = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="建筑结构："]/../text()').extract_first()
        architectural_type = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="建筑类型："]/../text()').extract_first()
        architectural_area = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="占地面积："]/../text()').extract_first()
        floor_area = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="建筑面积："]/../text()').extract_first()
        households_number = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="房屋总数："]/../text()').extract_first()
        building_number = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="楼栋总数："]/../text()').extract_first()
        property_management_company = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="物业公司："]/../text()').extract_first()
        green_ratio = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="绿 化 率："]/../text()').extract_first()
        plot_ratio = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="容 积 率："]/../text()').extract_first()
        residential_management_fee = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="物 业 费："]/../text()').extract_first()
        property_office_tel = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="物业办公电话："]/../text()').extract_first()
        property_office_address = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="物业办公地点："]/../text()').extract_first()
        property_format = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="物业类别："]/../text()').extract_first()
        addtion_information = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="附加信息："]/../text()').extract_first()
        # 配套设施
        water_supply = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="供&nbsp;&nbsp;&nbsp;&nbsp;水："]/../span/@title').extract_first()
        power_supply = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="供&nbsp;&nbsp;&nbsp;&nbsp;电："]/../span/@title').extract_first()
        gas_supply = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="燃&nbsp;&nbsp;&nbsp;&nbsp;气："]/../span/@title').extract_first()
        tele_equipment = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="通讯设备："]/../span/@title').extract_first()
        elevator_service = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="电梯服务："]/../text()').extract_first()
        security_management = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="安全管理："]/../text()').extract_first()
        cleaning_service = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="卫生服务："]/../text()').extract_first()
        parking_space_number = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="停 车 位："]/../text()').extract_first()
        building_entrance = response.xpath(u'//div[@class="inforwrap clearfix"]/dl/dd/strong[text()="小区入口："]/../text()').extract_first()
        # 周边信息
        kindergarten = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "幼儿园：")]/text()').extract_first()
        middle_primary_school = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "中小学：")]/text()').extract_first()
        university = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "大学：")]/text()').extract_first()
        mall = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "商场：")]/text()').extract_first()
        hospital = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "医院：")]/text()').extract_first()
        post_office = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "邮局：")]/text()').extract_first()
        bank = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "银行：")]/text()').extract_first()
        other_supporting = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "其他：")]/text()').extract_first()
        inner_supporting = response.xpath(u'//dl[@class="floatl mr30"]/dt[contains(text(), "小区内部配套：")]/text()').extract_first()
        # 数据清洗
        pattern = u"[\u4E00-\u9FA5]+：(?!暂无).*?([\u4E00-\u9FA5]+.*)"
        var_Dict = {
                "kindergarten": kindergarten,
                "middle_primary_school": middle_primary_school,
                "university": university,
                "mall": mall,
                "hospital": hospital,
                "post_office": post_office,
                "bank": bank,
                "other_supporting": other_supporting,
                "inner_supporting": inner_supporting
                }
        for i in var_Dict:
            if re.search(pattern, str(var_Dict[i])):
                var_Dict[i] = re.search(pattern, str(var_Dict[i])).group(1)
            else:
                var_Dict[i] = None
        # 建筑面积
        if architectural_area:
            architectural_area = architectural_area.replace('平方米', '')
            try:
                architectural_area = float(architectural_area)
            except:
                remark.append(architectural_area)
                architectural_area = None
        # 占地面积
        if floor_area:
            floor_area = floor_area.replace('平方米', '')
            try:
                floor_area = float(floor_area)
            except:
                remark.append(floor_area)
                floor_area = None
        # 建筑年代
        if building_year:
            pattern = re.compile(r"\d\d\d\d")
            if pattern.findall(building_year):
                building_year =     pattern.findall(building_year)[0]
                try: # 建筑年代
                    building_year = int(building_year)
                except:
                    remark.append(building_year)
                    building_year = None
            else:
                building_year = None
        # 物业费
        if residential_management_fee:
            pattern = u"(\d+.*)元.*"
            if re.match(pattern, residential_management_fee):
                residential_management_fee = re.match(pattern, residential_management_fee).group(1)
                try: # 物业费
                    residential_management_fee = float(residential_management_fee)
                except:
                    remark.append(residential_management_fee)
                    residential_management_fee = None
            else:
                residential_management_fee = None
        # 租售情况
        price_month = response.xpath(u'//dl/dt[text()="本月均价"]/../dd/span/text()').extract_first()
        chain_last_month = response.xpath(u'//dl/dt[text()="环比上月"]/../dd/span/text()').extract_first()
        YOY = response.xpath(u'//dl/dt[text()="同比上年"]/../dd/span/text()').extract_first()
        if YOY:
            YOY = YOY.replace('↓ ', '-')
            YOY = YOY.replace('↑ ', '')
            YOY = YOY.replace('%', '')
        if chain_last_month:
            chain_last_month = chain_last_month.replace('↓ ', '-')
            chain_last_month = chain_last_month.replace('↑ ', '')
            chain_last_month = chain_last_month.replace('%', '')
        # 备注
        try:
            assert remark !=[]
            remark = str(remark)
        except:
            remark = None
        # 传递进类
        Fangtianxia_item['item_id'] = response.meta['item_id']
        Fangtianxia_item['item_name'] = response.meta['item_name']
        Fangtianxia_item['in_rent_number'] = response.meta['in_rent_number']
        Fangtianxia_item['on_sale_number'] = response.meta['on_sale_number']
        Fangtianxia_item['item_url'] = response._url
        Fangtianxia_item['province_name'] = response.meta['province_name']
        Fangtianxia_item['city_name'] = response.meta['city_name']
        Fangtianxia_item['county_name'] = response.meta['county_name']
        Fangtianxia_item['item_address'] = item_address
        Fangtianxia_item['item_district'] = item_district
        Fangtianxia_item['post_code'] = post_code
        Fangtianxia_item['property_describe'] = property_describe
        Fangtianxia_item['building_year'] = building_year
        Fangtianxia_item['developer'] = developer
        Fangtianxia_item['architectural_structure'] = architectural_structure
        Fangtianxia_item['architectural_type'] = architectural_type
        Fangtianxia_item['architectural_area'] = architectural_area
        Fangtianxia_item['floor_area'] = floor_area
        Fangtianxia_item['households_number'] = households_number
        Fangtianxia_item['building_number'] = building_number
        Fangtianxia_item['property_management_company'] = property_management_company
        Fangtianxia_item['green_ratio'] = green_ratio
        Fangtianxia_item['plot_ratio'] = plot_ratio
        Fangtianxia_item['residential_management_fee'] = residential_management_fee
        Fangtianxia_item['property_office_tel'] = property_office_tel
        Fangtianxia_item['property_office_address'] = property_office_address
        Fangtianxia_item['property_format'] = property_format
        Fangtianxia_item['addtion_information'] = addtion_information
        Fangtianxia_item['water_supply'] = water_supply
        Fangtianxia_item['power_supply'] = power_supply
        Fangtianxia_item['gas_supply'] = gas_supply
        Fangtianxia_item['tele_equipment'] = tele_equipment
        Fangtianxia_item['elevator_service'] = elevator_service
        Fangtianxia_item['security_management'] = security_management
        Fangtianxia_item['cleaning_service'] = cleaning_service
        Fangtianxia_item['parking_space_number'] = parking_space_number
        Fangtianxia_item['building_entrance'] = building_entrance
        Fangtianxia_item['kindergarten']  = var_Dict["kindergarten"]
        Fangtianxia_item['middle_primary_school']  = var_Dict["middle_primary_school"]
        Fangtianxia_item['university'] = var_Dict["university"]
        Fangtianxia_item['mall']  = var_Dict["mall"]
        Fangtianxia_item['hospital']  = var_Dict["hospital"]
        Fangtianxia_item['post_office']           = var_Dict["post_office"]
        Fangtianxia_item['bank']  = var_Dict["bank"]
        Fangtianxia_item['other_supporting']  = var_Dict["other_supporting"]
        Fangtianxia_item['inner_supporting']  = var_Dict["inner_supporting"]
        Fangtianxia_item['price_month'] = price_month
        Fangtianxia_item['chain_last_month'] = chain_last_month
        Fangtianxia_item['YOY'] = YOY
        Fangtianxia_item['remark'] = remark
        yield Fangtianxia_item
    # 商业解析
    def parse_commerce_detail(self,response):
        remark = []
        Fangtianxia_item = PropertyDataScrapyItem()
        # 基本信息
        item_address = response.xpath(u'//dl[@class="xiangqing"]/dd[text()="楼盘地址："]/span/text()').extract_first()
        item_district = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "所属区域：")]/text()').extract_first()
        loop_position = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "环线位置：")]/text()').extract_first()
        property_format = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "物业类别：")]/text()').extract_first()
        office_level = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "写字楼等级：")]/text()').extract_first()
        architectural_type = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "建筑类别：")]/text()').extract_first()
        developer = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "开 发 商：")]/text()').extract_first()
        total_floors = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "总 层 数：")]/text()').extract_first()
        item_feature = response.xpath('//dl[@class="xiangqing"]/comment()').extract_first()
        architectural_area = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "占地面积：")]/text()').extract_first()
        floor_area = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "建筑面积：")]/text()').extract_first()
        property_management_company = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "物业公司：")]/text()').extract_first()
        residential_management_fee = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "物 业 费：")]/text()').extract_first()
        efficiency_rate = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "得 房 率：")]/text()').extract_first()
        is_division = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "是否可分割：")]/text()').extract_first()
        is_involed = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "是否涉外：")]/text()').extract_first()
        elevator_number = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "电梯数量：")]/text()').extract_first()
        air_conditon = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "空    调：")]/text()').extract_first()
        decorate_situation = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "装修状况：")]/text()').extract_first()
        building_year = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "竣工时间：")]/text()').extract_first()
        deliver_criterion = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "开间面积：") or contains(text(), "标准层面积：")]/text()').extract_first()
        parking_space_number = response.xpath(u'//dl[@class="xiangqing"]/dd[contains(text(), "停 车 位：")]/text()').extract_first()
        building_facility = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "楼内配套：")]/text()').extract_first()
        middle_primary_school = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "中小学：")]/text()').extract_first()
        mall = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "商场：")]/text()').extract_first()
        hospital = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "医院：")]/text()').extract_first()
        post_office = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "邮局：")]/text()').extract_first()
        bank = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "银行：")]/text()').extract_first()
        other_supporting = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "其他：")]/text()').extract_first()
        house = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "住宅：")]/text()').extract_first()
        hotel = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "酒店：")]/text()').extract_first()
        office = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "写字楼：")]/text()').extract_first()
        restaurant = response.xpath(u'//dl[@class="xiangqing"]/dt[contains(text(), "餐饮：")]/text()').extract_first()
        # 数据清洗
        pattern = u"[\u4E00-\u9FA5]+：(?!暂无).*?([\u4E00-\u9FA5]+.*)"
        var_Dict = {
                "item_district": item_district,
                "loop_position": loop_position ,
                "property_format": property_format ,
                "office_level": office_level ,
                "architectural_type": architectural_type ,
                "developer": developer ,
                "property_management_company": property_management_company ,
                "efficiency_rate": efficiency_rate ,
                "is_division": is_division ,
                "is_involed": is_involed,
                "elevator_number": elevator_number ,
                "air_conditon": air_conditon ,
                "decorate_situation": decorate_situation ,
                "parking_space_number": parking_space_number,
                "building_facility": building_facility ,
                "middle_primary_school": middle_primary_school,
                "mall": mall,
                "hospital": hospital ,
                "post_office": post_office ,
                "bank" :bank ,
                "other_supporting": other_supporting,
                "house": house ,
                "hotel": hotel,
                "office": office,
                "restaurant": restaurant
                }
        for i in var_Dict:
            if re.search(pattern, str(var_Dict[i])):
                var_Dict[i] = re.search(pattern, str(var_Dict[i])).group(1)
            else:
                var_Dict[i] = None
        # 建筑年代
        if building_year:
            pattern = re.compile(r"\d\d\d\d")
            if pattern.findall(building_year):
                building_year = pattern.findall(building_year)[0]
                try: # 建筑年代
                    building_year = int(building_year)
                except:
                    remark.append(building_year)
                    building_year = None
            else:
                building_year = None
        # 项目特色
        if item_feature:
            pattern = u".*项目特色：(?!暂无).*?([\u4E00-\u9FA5]+.*[\u4E00-\u9FA5]).*"
            if re.search(pattern,item_feature):
                item_feature = re.search(pattern, item_feature).group(1)
            else:
                item_feature = None
        #开间面积=========== u".*：(?!暂无).*?(\d+\.?\d*).*"
        if deliver_criterion:
            pattern = re.compile(u".*：(?!暂无).*?(\d+\.?\d*).*")
            if pattern.findall(deliver_criterion):
                deliver_criterion = pattern.findall(deliver_criterion)[0]
                try: # 建筑面积
                    deliver_criterion = float(deliver_criterion)
                except:
                    remark.append(deliver_criterion)
                    deliver_criterion = None
            else:
                deliver_criterion = None
        # 建筑面积
        if floor_area:
            if pattern.findall(floor_area):
                floor_area =  pattern.findall(floor_area)[0]
                try: # 建筑面积
                    floor_area = float(floor_area)
                except:
                    remark.append(floor_area)
                    floor_area = None
            else:
                floor_area = None
        # 占地面积
        if architectural_area:
            if pattern.findall(architectural_area):
                architectural_area =  pattern.findall(architectural_area)[0]
                try: # 建筑面积
                    architectural_area = float(architectural_area)
                except:
                    remark.append(architectural_area)
                    architectural_area = None
            else:
                architectural_area = None
        # 总层数
        if total_floors:
            if pattern.findall(total_floors):
                total_floors = pattern.findall(total_floors)[0]
            else:
                total_floors = None
        # 物业费
        if residential_management_fee:
            pattern = u".*：(?!暂无).*?(\d+.*)元.*"
            if re.search(pattern,residential_management_fee):
                residential_management_fee = re.search(pattern, residential_management_fee).group(1)
                try: # 物业费
                    residential_management_fee = float(residential_management_fee)
                except:
                    remark.append(residential_management_fee)
                    residential_management_fee = None
            else:
                residential_management_fee = None
        # 备注
        try:
            assert remark !=[]
            remark = str(remark)
        except:
            remark = None
        # 传递进类
        Fangtianxia_item['province_name'] = response.meta['province_name']
        Fangtianxia_item['city_name'] = response.meta['city_name']
        Fangtianxia_item['county_name'] = response.meta['county_name']
        Fangtianxia_item['item_id'] = response.meta['item_id']
        Fangtianxia_item['item_name'] = response.meta['item_name']
        Fangtianxia_item['item_url'] = response._url
        Fangtianxia_item['in_rent_number'] = response.meta['in_rent_number']
        Fangtianxia_item['on_sale_number'] = response.meta['on_sale_number']
        Fangtianxia_item['item_address'] = item_address
        Fangtianxia_item['item_district'] = var_Dict["item_district"]
        Fangtianxia_item['loop_position'] = var_Dict["loop_position"]
        Fangtianxia_item['property_format'] = var_Dict["property_format"]
        Fangtianxia_item['office_level'] = var_Dict["office_level"]
        Fangtianxia_item['architectural_type'] = var_Dict["architectural_type"]
        Fangtianxia_item['developer'] = var_Dict["developer"]
        Fangtianxia_item['total_floors'] = total_floors
        Fangtianxia_item['item_feature'] = item_feature
        Fangtianxia_item['architectural_area'] = architectural_area
        Fangtianxia_item['floor_area'] = floor_area
        Fangtianxia_item['property_management_company'] = var_Dict["property_management_company"]
        Fangtianxia_item['residential_management_fee'] = residential_management_fee
        Fangtianxia_item['efficiency_rate'] = var_Dict["efficiency_rate"]
        Fangtianxia_item['is_division'] = var_Dict["is_division"]
        Fangtianxia_item['is_involed'] = var_Dict["is_involed"]
        Fangtianxia_item['elevator_number'] = var_Dict["elevator_number"]
        Fangtianxia_item['air_conditon'] = var_Dict["air_conditon"]
        Fangtianxia_item['decorate_situation'] = var_Dict["decorate_situation"]
        Fangtianxia_item['building_year'] = building_year
        Fangtianxia_item['deliver_criterion'] = deliver_criterion
        Fangtianxia_item['parking_space_number'] = var_Dict["parking_space_number"]
        Fangtianxia_item['building_facility'] = var_Dict["building_facility"]
        Fangtianxia_item['middle_primary_school']  = var_Dict["middle_primary_school"]
        Fangtianxia_item['mall']  = var_Dict["mall"]
        Fangtianxia_item['hospital']  = var_Dict["hospital"]
        Fangtianxia_item['post_office']           = var_Dict["post_office"]
        Fangtianxia_item['bank']  = var_Dict["bank"]
        Fangtianxia_item['other_supporting']  = var_Dict["other_supporting"]
        Fangtianxia_item['house'] = var_Dict["house"]
        Fangtianxia_item['hotel'] = var_Dict["hotel"]
        Fangtianxia_item['office'] = var_Dict["office"]
        Fangtianxia_item['restaurant'] = var_Dict["restaurant"]
        Fangtianxia_item['remark'] = remark
        yield Fangtianxia_item
    # 解析新房住宅电梯数量
    def parse_elevator(self,response):
        elevator = response.xpath(u'//div[@class="dongInfo"]//span[text()="电梯数"]/../text()').extract()
        pattern = re.compile(r'\d+梯')
        elevator_list = pattern.findall(str(elevator))
        if elevator_list :
            elevator_number_new = 0
            for i in range(len(elevator_list)):
                elevator_number_new += int(elevator_list[i][: -1])
            if elevator_number_new:
                Fangtianxia_item_Elevator = ElevatorItem()
                item_id = response.meta['item_id']
                Fangtianxia_item_Elevator['item_id'] = item_id
                Fangtianxia_item_Elevator['item_url'] = response._url
                Fangtianxia_item_Elevator['elevator_number_new'] = elevator_number_new
                yield Fangtianxia_item_Elevator
    # 解析项目坐标
    def parse_map(self,response):
        def AsignCity(lon,lat):
            pass
        def AsignDistrict(lon,lat):
            pass
        def AsignStreet(lon,lat):
            pass
        map_script = response.xpath('//script[contains(text(), "projName")]/text()|//script[contains(text(), "mainBuilding")]/text()').extract_first()
        pattern = re.compile(r'p[xy]:"(\d+\.\d+)"|"baidu_coord_[xy]":"(\d+\.\d+)"')
        if map_script:
            coordinate_list = pattern.findall(map_script)
            if coordinate_list:
                lon_R = coordinate_list[0][0]
                lat_R = coordinate_list[1][0]
                lon_C = coordinate_list[0][1]
                lat_C = coordinate_list[1][1]
                if lon_R or lon_C or lat_R or lat_C:
                    Fangtianxia_item_Coordinate = GeoItem()
                    if lon_R and lat_R:
                        lon = float(lon_R)
                        lat = float(lat_R)
                        lon = bdToGaoDe(lon,lat)[0]
                        lat = bdToGaoDe(lon,lat)[1]
                        location = str(lat) + ',' + str(lon)
                        city = AsignCity(lon,lat)
                        district = AsignDistrict(lon,lat)
                        street = AsignStreet(lon,lat)
                    else:
                        lon = float(lon_C)
                        lat = float(lat_C)
                        lon = bdToGaoDe(lon,lat)[0]
                        lat = bdToGaoDe(lon,lat)[1]
                        location = str(lat) + ',' + str(lon)
                        city = AsignCity(lon,lat)
                        district = AsignDistrict(lon,lat)
                        street = AsignStreet(lon,lat)
                    item_id = response.meta["item_id"]
                    Fangtianxia_item_Coordinate['item_id'] = item_id
                    Fangtianxia_item_Coordinate['item_url'] = response._url
                    Fangtianxia_item_Coordinate['lon'] = lon
                    Fangtianxia_item_Coordinate['lat'] = lat
                    Fangtianxia_item_Coordinate['location'] = location
                    Fangtianxia_item_Coordinate['city'] = city
                    Fangtianxia_item_Coordinate['district'] = district
                    Fangtianxia_item_Coordinate['street'] = street
                    yield Fangtianxia_item_Coordinate
    # 解析二手房近两年价格走势
    def parse_price(self,response):
        price_two_year = response.xpath('//text()').extract_first()
        if price_two_year:
            if price_two_year != "[]":
                Fangtianxia_item_Price = PriceItem()
                item_id = response.meta['item_id']
                Fangtianxia_item_Price['item_id'] = item_id
                Fangtianxia_item_Price['item_url'] = response._url
                Fangtianxia_item_Price['price_two_year'] = price_two_year
                yield Fangtianxia_item_Price

# 变量匹配中文名
dict_map_HandV = {
    "项目编号": "item_id",
    "项目名称": "item_name",
    "省份": "province_name",
    "城市": "city_name",
    "区县": "county_name",
    "所属区域": "item_district",
    "小区地址": "item_address",
    "邮编": "post_code",
    "经度": "lon",
    "维度": "lat",
    "坐标": "location",
    "item网址": "item_url",
    "当月均价": "price_month",
    "环比上月": "chain_last_month",
    "环比上年": "YOY",
    "在售数": "on_sale_number",
    "在租数": "in_rent_number",

    "产权描述": "property_describe",
    "建筑年代": "building_year",
    "开发商": "developer",
    "建筑结构": "architectural_structure",
    "建筑类型": "architectural_type",
    "占地面积": "architectural_area",
    "建筑面积": "floor_area",
    "房屋总数": "households_number",
    "楼栋总数": "building_number",
    "物业公司": "property_management_company",
    "绿化率": "green_ratio",
    "容积率": "plot_ratio",
    "物业类别": "property_format",
    "物业费": "residential_management_fee",
    "物业办公地点": "property_office_address",
    "物业办公电话": "property_office_tel",

    "附加信息": "addtion_information",
    "供水": "water_supply",
    "供电": "power_supply",
    "燃气": "gas_supply",
    "通讯设备": "tele_equipment",
    "电梯服务": "elevator_service",
    "安全管理": "security_management",
    "卫生服务": "cleaning_service",
    "停车位": "parking_space_number",
    "小区入口": "building_entrance",
    "幼儿园": "kindergarten",
    "中小学": "middle_primary_school",
    "大学": "university",
    "商场": "mall",
    "医院": "hospital",
    "邮局": "post_office",
    "银行": "bank",
    "其他": "other_supporting",
    "小区内部配套": "inner_supporting",

    "高德城市":"city",
    "高德区":"district",
    "高德街":"street"
    }
