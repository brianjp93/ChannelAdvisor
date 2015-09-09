"""
channelAdvisor.py
Brian Perrett
written for Moonlight Feather Inc.
7/31/15
Channel advisor is slow af and I h8 them.
"""
from __future__ import division
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from suds.client import Client
from suds.sax.element import Element
from bs4 import BeautifulSoup
import pprint


class ChannelAdvisor():
    def __init__(self):
        self.adminurl = "https://api.channeladvisor.com/ChannelAdvisorAPI/v7/AdminService.asmx?WSDL"
        self.inventoryurl = "https://api.channeladvisor.com/ChannelAdvisorAPI/v7/InventoryService.asmx?WSDL"
        self.orderurl = "https://api.channeladvisor.com/ChannelAdvisorAPI/v7/OrderService.asmx?WSDL"
        self.devkey = self.getDevKey()
        self.pwd = self.getPwd()
        self.localID = self.getLocalId()
        self.accountID = self.getAccountId()
        self.connected = None

    def getLocalId(self):
        """
        retrieve localid from data.cookie file.
        """
        with open("data.cookie", "rb") as f:
            localid = ""
            for line in f:
                line = line.split()
                if line[0] == "localID":
                    localid = line[1].strip()
            if localid == "":
                raise Exception("Could not locate LocalID.")
        return localid

    def getDevKey(self):
        """
        retrieve devkey from data.cookie file.
        """
        with open("data.cookie", "rb") as f:
            devkey = ""
            for line in f:
                line = line.split()
                if line[0] == "devkey":
                    devkey = line[1].strip()
            if devkey == "":
                raise Exception("Could not locate developer key.")
        return devkey

    def getPwd(self):
        """
        retrieve pwd from data.cookie file.
        """
        with open("data.cookie", "rb") as f:
            pwd = ""
            for line in f:
                line = line.split()
                if line[0] == "pwd":
                    pwd = line[1].strip()
            if pwd == "":
                raise Exception("Could not locate developer key.")
        return pwd

    def getAccountId(self):
        """
        retrieve accountid from data.cookie file.
        """
        with open("data.cookie", "rb") as f:
            accountid = ""
            for line in f:
                line = line.split()
                if line[0] == "accountid":
                    accountid = line[1].strip()
            if accountid == "":
                print("Could not locate Account ID.  Please request access again.")
        return accountid

    def makeHeaders(self):
        apicreds = Element("APICredentials")
        developerkey = Element("DeveloperKey").setText(self.devkey).setPrefix("ns0")
        password = Element("Password").setText(self.pwd).setPrefix("ns0")
        apicreds.append(developerkey)
        apicreds.append(password)
        apicreds.setPrefix("ns0")
        return apicreds

    #########################
    # Admin Service Methods #
    #########################

    def connectAdmin(self):
        """
        connect to the channel advisor admin service.
        """
        if self.connected == "admin":
            return self.client
        else:
            client = Client(self.adminurl)
            self.client = client
            self.connected = "admin"
            return client

    def requestAccess(self):
        self.connectAdmin()
        headers = self.makeHeaders()
        self.client.set_options(soapheaders=headers)
        self.client.service.RequestAccess(self.localID)
        print("Please approve the request within your channel advisor account.")
        account_id = raw_input("Paste your account id here: ")
        return account_id

    #############################
    # End Admin Service Methods #
    #############################

    #############################
    # Inventory Service Methods #
    #############################

    def connectInventory(self):
        """
        connect to the channel advisor inventory service.
        """
        if self.connected == "inventory":
            return self.client
        else:
            client = Client(self.inventoryurl)
            self.client = client
            self.connected = "inventory"
            return client

    def getFilteredInventoryItemList(self,
                                     pagesize="100",
                                     pagenumber="1",
                                     labelname="All Inventory",
                                     includequantityinfo="true",
                                     includepriceinfo="true",
                                     sortfield="sku",
                                     daterangefield="",
                                     daterangestartgmt="",
                                     daterangeendgmt="",
                                     partialsku="",
                                     skustartswith="",
                                     skuendswith="",
                                     classificationname="",
                                     quantitycheckfield="",
                                     quantitychecktype="",
                                     quantitycheckvalue="",
                                     sortdirection="",
                                     includeclassificationinfo=""
                                     ):
        """
        calls channelAdvisor's GetFilteredInventoryItemList using soap
            protocol.  I made a custom xml string because the automatically
            generated one was not working for some reason.
        """
        self.connectInventory()
        headers = self.makeHeaders()
        self.client.set_options(soapheaders=headers)
        root = ET.Element("soapenv:Envelope")
        root.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        root.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(root, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        devkey = ET.SubElement(apicreds, "web:DeveloperKey").text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password").text = self.pwd
        body = ET.SubElement(root, "soapenv:Body")
        gfiil = ET.SubElement(body, "web:GetFilteredInventoryItemList")
        accountid = ET.SubElement(gfiil, "web:accountID")
        accountid.text = self.accountID
        itemcriteria = ET.SubElement(gfiil, "web:itemCriteria")
        if daterangefield != "":
            date_range_field = ET.SubElement(itemcriteria, "web:DateRangeField")
            date_range_field.text = daterangefield
        if daterangestartgmt != "":
            date_range_start_gmt = ET.SubElement(itemcriteria, "web:DateRangeStartGMT")
            date_range_start_gmt.text = daterangestartgmt
        if daterangeendgmt != "":
            date_range_end_gmt = ET.SubElement(itemcriteria, "web:DateRangeEndGMT")
            date_range_end_gmt.text = daterangeendgmt
        if partialsku != "":
            partial_sku = ET.SubElement(itemcriteria, "web:PartialSku")
            partial_sku.text = partialsku
        if skustartswith != "":
            sku_starts_with = ET.SubElement(itemcriteria, "web:SkuStartsWith")
            sku_starts_with.text = skustartswith
        if skuendswith != "":
            sku_ends_with = ET.SubElement(itemcriteria, "web:SkuEndsWith")
            sku_ends_with.text = skuendswith
        if classificationname != "":
            classification_name = ET.SubElement(itemcriteria, "web:ClassificationName")
            classification_name.text = classificationname
        if labelname != "":
            label_name = ET.SubElement(itemcriteria, "web:LabelName")
            label_name.text = labelname
        if quantitycheckfield != "":
            quantity_check_field = ET.SubElement(itemcriteria, "web:QuantityCheckField")
            quantity_check_field.text = quantitycheckfield
        if quantitychecktype != "":
            quantity_check_type = ET.SubElement(itemcriteria, "web:QuantityCheckType")
            quantity_check_type.text = quantitychecktype
        if quantitycheckvalue != "":
            quantity_check_value = ET.SubElement(itemcriteria, "web:QuantityCheckValue")
            quantity_check_value.text = quantitycheckvalue
        page_number = ET.SubElement(itemcriteria, "web:PageNumber")
        page_number.text = pagenumber
        page_size = ET.SubElement(itemcriteria, "web:PageSize")
        page_size.text = pagesize
        detail_level = ET.SubElement(gfiil, "web:detailLevel")
        include_quantity_info = ET.SubElement(detail_level, "web:IncludeQuantityInfo")
        include_quantity_info.text = includequantityinfo
        include_price_info = ET.SubElement(detail_level, "web:IncludePriceInfo")
        include_price_info.text = includepriceinfo
        if sortfield != "":
            sort_field = ET.SubElement(gfiil, "sortField")
            sort_field.text = sortfield
        if sortdirection != "":
            sort_direction = ET.SubElement(gfiil, "sortDirection")
            sort_direction.text = sortdirection
        xml = ET.tostring(root)
        self.client.service.GetFilteredInventoryItemList(__inject={'msg': xml})
        xml_data = self.client.last_received()
        # print(ET.tostring(root))
        return str(xml_data)

    def parseGfiil(self, xml):
        """
        parses one page of xml returned from getFilteredInventoryItems() method
        returns dictionary skus{sku: {title, description, weight, ...}}
        """
        # print(xml)
        skus = {}
        soup = BeautifulSoup(xml, "xml")
        # print(soup)
        envelope = soup.find("Envelope")
        body = envelope.find("Body")
        response = body.find("GetFilteredInventoryItemListResponse")
        gfiilresult = response.find("GetFilteredInventoryItemListResult")
        result_data = gfiilresult.find("ResultData")
        if result_data is None:
            return None
        # print(result_data)
        for result in result_data.find_all("InventoryItemResponse"):
            sku = result.find("Sku").string
            title = result.find("Title").string
            description = result.find("Description").string
            weight = result.find("Weight").string
            warehouse_location = result.find("WarehouseLocation").string
            tax_product_code = result.find("TaxProductCode").string
            flag_style = result.find("FlagStyle").string
            flag_description = result.find("FlagDescription").string
            is_blocked = result.find("IsBlocked").string
            block_comment = result.find("BlockComment").string
            asin = result.find("ASIN").string
            isbn = result.find("ISBN").string
            upc = result.find("UPC").string
            mpn = result.find("MPN").string
            ean = result.find("EAN").string
            manufacturer = result.find("Manufacturer").string
            brand = result.find("Brand").string
            condition = result.find("Condition").string
            warranty = result.find("Warranty").string
            product_margin = result.find("ProductMargin").string
            supplier_po = result.find("SupplierPO").string
            harmonized_code = result.find("HarmonizedCode").string
            height = result.find("Height").string
            length = result.find("Length").string
            width = result.find("Width").string
            quantity_xml = result.find("Quantity")
            quantity = quantity_xml.find("Available").string
            price_info_xml = result.find("PriceInfo")
            retail_price = price_info_xml.find("RetailPrice").string
            cost = price_info_xml.find("Cost").string
            starting_price = price_info_xml.find("StartingPrice").string
            reserve_price = price_info_xml.find("ReservePrice").string
            take_it_price = price_info_xml.find("TakeItPrice").string
            second_chance_offer_price = price_info_xml.find("SecondChanceOfferPrice").string
            store_price = price_info_xml.find("StorePrice").string
            info = {"title": title,
                    "description": description,
                    "weight": weight,
                    "warehouse_location": warehouse_location,
                    "tax_product_code": tax_product_code,
                    "flag_style": flag_style,
                    "flag_description": flag_description,
                    "is_blocked": is_blocked,
                    "block_comment": block_comment,
                    "asin": asin,
                    "isbn": isbn,
                    "upc": upc,
                    "mpn": mpn,
                    "ean": ean,
                    "manufacturer": manufacturer,
                    "brand": brand,
                    "condition": condition,
                    "warranty": warranty,
                    "product_margin": product_margin,
                    "supplier_po": supplier_po,
                    "harmonized_code": harmonized_code,
                    "height": height,
                    "length": length,
                    "width": width,
                    "quantity": quantity,
                    "retail_price": retail_price,
                    "cost": cost,
                    "starting_price": starting_price,
                    "reserve_price": reserve_price,
                    "take_it_price": take_it_price,
                    "second_chance_offer_price": second_chance_offer_price,
                    "store_price": store_price
                    }
            skus[sku] = info
        return skus

    def getFilteredSkuList(self,
                           pagesize="100",
                           pagenumber="1",
                           labelname="All Inventory",
                           sortfield="sku",
                           daterangefield="",
                           daterangestartgmt="",
                           daterangeendgmt="",
                           partialsku="",
                           skustartswith="",
                           skuendswith="",
                           classificationname="",
                           quantitycheckfield="",
                           quantitychecktype="",
                           quantitycheckvalue="",
                           sortdirection="",
                           includeclassificationinfo=""
                           ):
        """
        """
        self.connectInventory()
        headers = self.makeHeaders()
        self.client.set_options(soapheaders=headers)
        root = ET.Element("soapenv:Envelope")
        root.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        root.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(root, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        devkey = ET.SubElement(apicreds, "web:DeveloperKey").text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password").text = self.pwd
        body = ET.SubElement(root, "soapenv:Body")
        gfiil = ET.SubElement(body, "web:GetFilteredSkuList")
        accountid = ET.SubElement(gfiil, "web:accountID")
        accountid.text = self.accountID
        itemcriteria = ET.SubElement(gfiil, "web:itemCriteria")
        if daterangefield != "":
            date_range_field = ET.SubElement(itemcriteria, "web:DateRangeField")
            date_range_field.text = daterangefield
        if daterangestartgmt != "":
            date_range_start_gmt = ET.SubElement(itemcriteria, "web:DateRangeStartGMT")
            date_range_start_gmt.text = daterangestartgmt
        if daterangeendgmt != "":
            date_range_end_gmt = ET.SubElement(itemcriteria, "web:DateRangeEndGMT")
            date_range_end_gmt.text = daterangeendgmt
        if partialsku != "":
            partial_sku = ET.SubElement(itemcriteria, "web:PartialSku")
            partial_sku.text = partialsku
        if skustartswith != "":
            sku_starts_with = ET.SubElement(itemcriteria, "web:SkuStartsWith")
            sku_starts_with.text = skustartswith
        if skuendswith != "":
            sku_ends_with = ET.SubElement(itemcriteria, "web:SkuEndsWith")
            sku_ends_with.text = skuendswith
        if classificationname != "":
            classification_name = ET.SubElement(itemcriteria, "web:ClassificationName")
            classification_name.text = classificationname
        if labelname != "":
            label_name = ET.SubElement(itemcriteria, "web:LabelName")
            label_name.text = labelname
        if quantitycheckfield != "":
            quantity_check_field = ET.SubElement(itemcriteria, "web:QuantityCheckField")
            quantity_check_field.text = quantitycheckfield
        if quantitychecktype != "":
            quantity_check_type = ET.SubElement(itemcriteria, "web:QuantityCheckType")
            quantity_check_type.text = quantitychecktype
        if quantitycheckvalue != "":
            quantity_check_value = ET.SubElement(itemcriteria, "web:QuantityCheckValue")
            quantity_check_value.text = quantitycheckvalue
        page_number = ET.SubElement(itemcriteria, "web:PageNumber")
        page_number.text = pagenumber
        page_size = ET.SubElement(itemcriteria, "web:PageSize")
        page_size.text = pagesize
        if sortfield != "":
            sort_field = ET.SubElement(gfiil, "sortField")
            sort_field.text = sortfield
        if sortdirection != "":
            sort_direction = ET.SubElement(gfiil, "sortDirection")
            sort_direction.text = sortdirection
        xml = ET.tostring(root)
        self.client.service.GetFilteredSkuList(__inject={'msg': xml})
        # print(self.client.last_sent())
        xml_data = self.client.last_received()
        # print(ET.tostring(root))
        return str(xml_data)

    def parseGfsl(self, xml):
        """
        """
        skus = []
        soup = BeautifulSoup(xml, "xml")
        # print(soup)
        envelope = soup.find("Envelope")
        body = envelope.find("Body")
        response = body.find("GetFilteredSkuListResponse")
        gfiilresult = response.find("GetFilteredSkuListResult")
        result_data = gfiilresult.find("ResultData")
        # print(result_data)
        if result_data is None:
            return None
        # print(result_data)
        for string in result_data.find_all("string"):
            sku = string.string
            skus.append(sku)
        if not skus:
            return None
        return skus

    def getAllOnSale(self):
        """
        returns a set of all items in CA with the "onsale" label.
        """
        skus = set()
        pagenumber = 1
        print("Retrieving onsale skus page 1.")
        xml = self.getFilteredSkuList(pagenumber=str(pagenumber), labelname="onsale")
        # print(xml)
        while True:
            temp_skus = self.parseGfsl(xml)
            if temp_skus is None:
                break
            for sku in temp_skus:
                skus.add(sku)
            pagenumber += 1
            print("Retrieving onsale skus page {}.".format(pagenumber))
            xml = self.getFilteredSkuList(pagenumber=str(pagenumber), labelname="onsale")
        return skus

    def getAllHidden(self):
        skus = set()
        pagenumber = 1
        print("Retrieving hidden skus page 1.")
        xml = self.getFilteredSkuList(pagenumber=str(pagenumber), labelname="hide")
        # print(xml)
        while True:
            temp_skus = self.parseGfsl(xml)
            if temp_skus is None:
                break
            for sku in temp_skus:
                skus.add(sku)
            pagenumber += 1
            print("Retrieving hidden skus page {}.".format(pagenumber))
            xml = self.getFilteredSkuList(pagenumber=str(pagenumber), labelname="hide")
        return skus

    def getAllInventory(self):
        skus = {}
        pagenumber = 1
        # total = 0
        # start = time.time()
        onsale = self.getAllOnSale()
        hidden = self.getAllHidden()
        print("Retrieving Inventory Items page 1.")
        xml = self.getFilteredInventoryItemList(pagenumber=str(pagenumber))
        while True:
            temp_skus = self.parseGfiil(xml)
            # print(skus)
            if temp_skus is None:
                break
            for sku in temp_skus:
                skus[sku] = temp_skus[sku]
                if sku in onsale:
                    skus[sku]["onsale"] = "True"
                else:
                    skus[sku]["onsale"] = "False"
                if sku in hidden:
                    skus[sku]["hidden"] = "True"
                else:
                    skus[sku]["hidden"] = "False"
                # total += 1
            pagenumber += 1
            print("Retrieving Inventory Items page {}.".format(pagenumber))
            xml = self.getFilteredInventoryItemList(pagenumber=str(pagenumber))
        # end = time.time()
        # print(end-start)
        # print(total)
        return skus

    def updateInventoryItemQuantityAndPriceList(self, skus, update_type):
        """
        http://developer.channeladvisor.com/display/cadn/UpdateInventoryItemQuantityAndPriceList
        skus MUST HAVE LESS THAN 1000 ENTRIES.
        skus should be a nested dictionary with information such as
            Quantity, Cost, RetailPrice,
            StartingPrice, ReservePrice, TakeItPrice,
            SecondChanceOfferPrice, StorePrice
        update_type - [Absolute, Relative, Available, InStock, UnShipped]
        """
        self.connectInventory()
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(envelope, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        developerkey = ET.SubElement(apicreds, "web:DeveloperKey")
        developerkey.text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password")
        pwd.text = self.pwd
        body = ET.SubElement(envelope, "soapenv:Body")
        uiiqapl = ET.SubElement(body, "web:UpdateInventoryItemQuantityAndPriceList")
        accountid = ET.SubElement(uiiqapl, "web:accountID")
        accountid.text = self.accountID
        iqapl = ET.SubElement(uiiqapl, "web:itemQuantityAndPriceList")
        for sku in skus:
            iiqap = ET.SubElement(iqapl, "web:InventoryItemQuantityAndPrice")
            s = ET.SubElement(iiqap, "web:Sku")
            s.text = sku
            distribution_center_code = ET.SubElement(iiqap, "web:DistributionCenterCode")
            distribution_center_code.text = "Ventura"
            if "quantity" in skus[sku]:
                quantity = ET.SubElement(iiqap, "web:Quantity")
                quantity.text = skus[sku]["quantity"]
                updatetype = ET.SubElement(iiqap, "web:UpdateType")
                updatetype.text = update_type
                price_info = ET.SubElement(iiqap, "web:PriceInfo")
                if "cost" in skus[sku]:
                    cost = ET.SubElement(price_info, "web:Cost")
                    cost.text = skus[sku]["cost"]
                if "retailprice" in skus[sku]:
                    retailprice = ET.SubElement(price_info, "web:RetailPrice")
                    retailprice.text = skus[sku]["retailprice"]
                if "startingprice" in skus[sku]:
                    startingprice = ET.SubElement(price_info, "web:StartingPrice")
                    startingprice.text = skus[sku]["startingprice"]
                if "takeitprice" in skus[sku]:
                    takeitprice = ET.SubElement(price_info, "web:TakeItPrice")
                    takeitprice.text = skus[sku]["takeitprice"]
                if "secondchanceofferprice" in skus[sku]:
                    secondchanceofferprice = ET.SubElement(price_info, "web:SecondChanceOfferPrice")
                    secondchanceofferprice.text = skus[sku]["secondchanceofferprice"]
                if "storeprice" in skus[sku]:
                    storeprice = ET.SubElement(price_info, "web:StorePrice")
                    storeprice.text = skus[sku]["storeprice"]
        xml = ET.tostring(envelope)
        # print(xml)
        self.client.service.UpdateInventoryItemQuantityAndPriceList(__inject={'msg': xml})
        xml_data = self.client.last_received()
        return xml_data

    def batchUpdateQuantities(self, skus, update_type):
        """
        uses the above method.  Separates skus into groups of 500 and then
            sends them separately.
        skus is a dictionary with info that can include:
            quantity, cost, retailprice,
            startingprice, reserveprice, takeitprice,
            secondchanceofferprice, storeprice
        update_type - [Absolute, Relative, Available, InStock, UnShipped]
        """
        # a list of sku dictionaries
        info_list = [{}]
        counter = 0
        index = 0
        for sku in skus:
            if counter >= 500:
                counter = 0
                info_list.append({})
                index += 1
            info_list[index][sku] = skus[sku]
            counter += 1
        for new_skus in info_list:
            self.updateInventoryItemQuantityAndPriceList(new_skus, update_type)

    def getInventoryItemStoreInfo(self, sku):
        """
        retrieve info for a single sku
        returns xml data, does not parse
        """
        sku = str(sku)
        self.connectInventory()
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(envelope, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        developerkey = ET.SubElement(apicreds, "web:DeveloperKey")
        developerkey.text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password")
        pwd.text = self.pwd
        body = ET.SubElement(envelope, "soapenv:Body")
        giisi = ET.SubElement(body, "web:GetInventoryItemStoreInfo")
        accountid = ET.SubElement(giisi, "web:accountID")
        accountid.text = self.accountID
        sku_xml = ET.SubElement(giisi, "web:sku")
        sku_xml.text = sku
        xml = ET.tostring(envelope)
        # print(xml)
        self.client.service.GetInventoryItemStoreInfo(__inject={'msg': xml})
        xml_data = self.client.last_received()
        return xml_data

    def getInventoryItemList(self, skus):
        """
        skus is a list of skus.
        skus must have less than 100 items in it.
        returns xml data, does not parse
        """
        self.connectInventory()
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(envelope, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        developerkey = ET.SubElement(apicreds, "web:DeveloperKey")
        developerkey.text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password")
        pwd.text = self.pwd
        body = ET.SubElement(envelope, "soapenv:Body")
        giil = ET.SubElement(body, "web:GetInventoryItemList")
        accountid = ET.SubElement(giil, "web:accountID")
        accountid.text = self.accountID
        skulist = ET.SubElement(giil, "web:skuList")
        for sku in skus:
            sku_xml = ET.SubElement(skulist, "web:string")
            sku_xml.text = str(sku)
        xml = ET.tostring(envelope)
        # print(xml)
        self.client.set_options(timeout=3)
        self.client.service.GetInventoryItemList(__inject={'msg': xml})
        self.client.set_options(timeout=90)
        xml_data = self.client.last_received()
        return xml_data

    def getBasicInfo(self, sku):
        """
        returns title, upc, loc strings
        """
        xml = self.getInventoryItemList([str(sku)])
        xml = str(xml)
        soup = BeautifulSoup(xml, "xml")
        envelope = soup.find("Envelope")
        body = envelope.find("Body")
        response = body.find("GetInventoryItemListResponse")
        result = response.find("GetInventoryItemListResult")
        data = result.find("ResultData")
        info = data.find("InventoryItemResponse")
        title = info.find("Title").string
        try:
            upc = info.find("UPC").string
        except:
            upc = ""
        try:
            loc = info.find("WarehouseLocation").string
        except:
            loc = ""
        return title, upc, loc

    def getDetailedInfo(self, sku):
        """
        returns a dictionary of sku details.
            {sku, title, upc, bin, description, brand, condition, quantity, price}
        """
        xml = self.getInventoryItemList([str(sku)])
        xml = str(xml)
        soup = BeautifulSoup(xml, "xml")
        envelope = soup.find("Envelope")
        body = envelope.find("Body")
        response = body.find("GetInventoryItemListResponse")
        result = response.find("GetInventoryItemListResult")
        data = result.find("ResultData")
        info = data.find("InventoryItemResponse")
        title = info.find("Title").string
        try:
            upc = info.find("UPC").string
        except:
            upc = "Not Available"
        try:
            loc = info.find("WarehouseLocation").string
        except:
            loc = "Not Set"
        try:
            description = info.find("Description").string
        except:
            description = "No Description"
        brand = info.find("Brand").string
        condition = info.find("Condition").string
        centers = info.find("DistributionCenterList").find_all("DistributionCenterInfoResponse")
        ven = ""
        for center in centers:
            if center.find("DistributionCenterCode").string == "Ventura":
                ven = center
                quantity = ven.find("AvailableQuantity").string
        if ven == "":
            quantity = "not found"
        priceinfo = info.find("PriceInfo")
        price = priceinfo.find("StorePrice").string
        sku_info = {"sku": sku,
                    "title": title,
                    "upc": upc,
                    "bin": loc,
                    "description": description,
                    "brand": brand,
                    "condition": condition,
                    "quantity": quantity,
                    "price": price
                    }
        return sku_info

    def synchInventoryItem(self,
                           sku,
                           title=None,
                           subtitle=None,
                           shortdescription=None,
                           description=None,
                           weight=None,
                           suppliercode=None,
                           warehouselocation=None,
                           taxproductcode=None,
                           flagstyle=None,
                           flagdescription=None,
                           isblocked=None,
                           blockcomment=None,
                           blockexternalquantity=None,
                           asin=None,
                           isbn=None,
                           upc=None,
                           mpn=None,
                           ean=None,
                           manufacturer=None,
                           brand=None,
                           condition=None,
                           warranty=None,
                           productmargin=None,
                           supplierpo=None,
                           harmonizedcode=None,
                           height=None,
                           length=None,
                           width=None,
                           classification=None,
                           dcquantityupdatetype=None,
                           distributioncentercode=None,
                           quantity=None,
                           quantityupdatetype=None,
                           cost=None,
                           retailprice=None,
                           startingprice=None,
                           reserveprice=None,
                           takeitprice=None,
                           secondchanceprice=None,
                           storeprice=None,
                           metadescription=None):
        """
        http://developer.channeladvisor.com/display/cadn/SynchInventoryItem
        not implemented: StoreInfo, PriceInfo, AttributeList, VariationInfo,
                         ImageList, LabelList

        """
        self.connectInventory()
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        header = ET.SubElement(envelope, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        developerkey = ET.SubElement(apicreds, "web:DeveloperKey")
        developerkey.text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password")
        pwd.text = self.pwd
        body = ET.SubElement(envelope, "soapenv:Body")
        sii = ET.SubElement(body, "web:SynchInventoryItem")
        accountid = ET.SubElement(sii, "web:accountID")
        accountid.text = self.accountID
        item = ET.SubElement(sii, "web:item")
        sku_xml = ET.SubElement(item, "web:Sku")
        sku_xml.text = str(sku)
        if title is not None:
            ET.SubElement(item, "web:Title").text = title
        if subtitle is not None:
            ET.SubElement(item, "web:Subtitle").text = subtitle
        if shortdescription is not None:
            ET.SubElement(item, "web:ShortDescription").text = shortdescription
        if description is not None:
            ET.SubElement(item, "web:Description").text = description
        if weight is not None:
            ET.SubElement(item, "web:Weight").text = weight
        if suppliercode is not None:
            ET.SubElement(item, "web:SupplierCode").text = suppliercode
        if warehouselocation is not None:
            ET.SubElement(item, "web:WarehouseLocation").text = warehouselocation
        if taxproductcode is not None:
            ET.SubElement(item, "web:TaxProductCode").text = taxproductcode
        if flagstyle is not None:
            ET.SubElement(item, "web:FlagStyle").text = flagstyle
        if isblocked is not None:
            ET.SubElement(item, "web:IsBlocked").text = isblocked
        if blockcomment is not None:
            ET.SubElement(item, "web:BlockComment").text = blockcomment
        if blockexternalquantity is not None:
            ET.SubElement(item, "web:BlockExternalQuantity").text = blockexternalquantity
        if asin is not None:
            ET.SubElement(item, "web:ASIN").text = asin
        if isbn is not None:
            ET.SubElement(item, "web:ISBN").text = isbn
        if upc is not None:
            ET.SubElement(item, "web:UPC").text = upc
        if mpn is not None:
            ET.SubElement(item, "web:MPN").text = mpn
        if ean is not None:
            ET.SubElement(item, "web:EAN").text = ean
        if manufacturer is not None:
            ET.SubElement(item, "web:Manufacturer").text = manufacturer
        if brand is not None:
            ET.SubElement(item, "web:Brand").text = brand
        if condition is not None:
            ET.SubElement(item, "web:Condition").text = condition
        if warranty is not None:
            ET.SubElement(item, "web:Warranty").text = warranty
        if productmargin is not None:
            ET.SubElement(item, "web:ProductMargin").text = productmargin
        if supplierpo is not None:
            ET.SubElement(item, "web:SupplierPO").text = supplierpo
        if harmonizedcode is not None:
            ET.SubElement(item, "web:HarmonizedCode").text = harmonizedcode
        if height is not None:
            ET.SubElement(item, "web:Height").text = height
        if length is not None:
            ET.SubElement(item, "web:Length").text = length
        if width is not None:
            ET.SubElement(item, "web:Width").text = width
        if classification is not None:
            ET.SubElement(item, "web:Classification").text = classification
        if dcquantityupdatetype is not None:
            ET.SubElement(item, "web:DCQuantityUpdateType").text = dcquantityupdatetype
        if distributioncentercode is not None or quantity is not None or quantityupdatetype is not None:
            dcl_1 = ET.SubElement(item, "web:DistributionCenterList")
            dcl = ET.SubElement(dcl_1, "web:DistributionCenterInfoSubmit")
            ET.SubElement(dcl, "web:Quantity").text = str(quantity)
            ET.SubElement(dcl, "web:DistributionCenterCode").text = distributioncentercode
            ET.SubElement(dcl, "web:QuantityUpdateType").text = quantityupdatetype
        xml = ET.tostring(envelope)
        # print(xml)
        self.client.set_options(timeout=3)
        self.client.service.SynchInventoryItem(__inject={'msg': xml})
        xml_data = self.client.last_received()
        self.client.set_options(timeout=90)
        return xml_data


    #################################
    # END Inventory Service Methods #
    #################################

    ###############################
    # START Order Service Methods #
    ###############################

    def connectOrder(self):
        if self.connected == "order":
            return self.client
        else:
            client = Client(self.orderurl)
            self.client = client
            self.connected = "order"
            return client

    def getOrderList(self,
                     ordercreationfilterbegintimegmt=None,
                     ordercreationfilterendtimegmt=None,
                     statusupdatefilterbegintimegmt=None,
                     statusupdatefilterendtimegmt=None,
                     joindatefilterswithor=None,
                     detaillevel="High",
                     exportstate=None,
                     orderidlist=None,
                     clientorderidentifierlist=None,
                     orderstatefilter=None,
                     paymentstatusfilter=None,
                     checkoutstatusfilter=None,
                     shippingstatusfilter=None,
                     refundstatusfilter=None,
                     distributioncentercode=None,
                     fulfillmenttypefilter=None,
                     pagenumberfilter="1",
                     pagesize="50"):
        """
        REFERENCE -> http://developer.channeladvisor.com/display/cadn/GetOrderList

        """
        client = self.connectOrder()
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:web", "http://api.channeladvisor.com/webservices/")
        envelope.set("xmlns:ord", "http://api.channeladvisor.com/datacontracts/orders")
        header = ET.SubElement(envelope, "soapenv:Header")
        apicreds = ET.SubElement(header, "web:APICredentials")
        developerkey = ET.SubElement(apicreds, "web:DeveloperKey")
        developerkey.text = self.devkey
        pwd = ET.SubElement(apicreds, "web:Password")
        pwd.text = self.pwd
        body = ET.SubElement(envelope, "soapenv:Body")
        gol = ET.SubElement(body, "web:GetOrderList")
        accountid = ET.SubElement(gol, "web:accountID")
        accountid.text = self.accountID
        order_criteria = ET.SubElement(gol, "web:orderCriteria")
        detail_level = ET.SubElement(order_criteria, "ord:DetailLevel")
        detail_level.text = detaillevel
        ET.SubElement(order_criteria, "ord:PageNumberFilter").text = pagenumberfilter
        ET.SubElement(order_criteria, "ord:PageSize").text = pagesize
        if ordercreationfilterbegintimegmt is not None:
            ET.SubElement(order_criteria, "ord:OrderCreationFilterBeginTimeGMT").text = ordercreationfilterbegintimegmt
        if ordercreationfilterendtimegmt is not None:
            ET.SubElement(order_criteria, "ord:OrderCreationFilterEndTimeGMT").text = ordercreationfilterendtimegmt
        if statusupdatefilterbegintimegmt is not None:
            ET.SubElement(order_criteria, "ord:statusupdatefilterbegintimegmt").text = statusupdatefilterbegintimegmt
        if statusupdatefilterendtimegmt is not None:
            ET.SubElement(order_criteria, "ord:statusupdatefilterendtimegmt").text = statusupdatefilterendtimegmt
        if joindatefilterswithor is not None:
            ET.SubElement(order_criteria, "ord:JoinDateFiltersWithOr").text = joindatefilterswithor
        if exportstate is not None:
            ET.SubElement(order_criteria, "ord:ExportState").text = exportstate
        if orderidlist is not None:
            ET.SubElement(order_criteria, "ord:OrderIDList").text = orderidlist
        if clientorderidentifierlist is not None:
            ET.SubElement(order_criteria, "ord:ClientOrderIdentifierList").text = clientorderidentifierlist
        if orderstatefilter is not None:
            ET.SubElement(order_criteria, "ord:OrderStateFilter").text = orderstatefilter
        if paymentstatusfilter is not None:
            ET.SubElement(order_criteria, "ord:PaymentStatusFilter").text = paymentstatusfilter
        if checkoutstatusfilter is not None:
            ET.SubElement(order_criteria, "ord:CheckoutStatusFilter").text = checkoutstatusfilter
        if shippingstatusfilter is not None:
            ET.SubElement(order_criteria, "ord:ShippingStatusFilter").text = shippingstatusfilter
        if refundstatusfilter is not None:
            ET.SubElement(order_criteria, "ord:RefundStatusFilter").text = refundstatusfilter
        if distributioncentercode is not None:
            ET.SubElement(order_criteria, "ord:DistributionCenterCode").text = distributioncentercode
        if fulfillmenttypefilter is not None:
            ET.SubElement(order_criteria, "ord:FulfillmentTypeFilter").text = fulfillmenttypefilter
        xml = ET.tostring(envelope)
        # print(xml)
        self.client.set_options(timeout=90)
        self.client.service.GetOrderList(__inject={'msg': xml})
        xml_data = self.client.last_received()
        self.client.set_options(timeout=90)
        return str(xml_data)

    def parseOrders(self, xml):
        xml = BeautifulSoup(xml, "xml")
        envelope = xml.find("Envelope")
        body = envelope.find("Body")
        response = body.find("GetOrderListResponse")
        results = response.find("GetOrderListResult")
        data = results.find("ResultData")
        orders = {}
        oxml = data.find_all("OrderResponseItem")
        if oxml == []:
            return None
        for o in oxml:
            number_of_matches = o.find("NumberOfMatches").string
            order_time_gmt = o.find("OrderTimeGMT").string
            order_time_gmt = datetime.strptime(order_time_gmt, "%Y-%m-%dT%H:%M:%S")
            total_order_amount = o.find("TotalOrderAmount").string
            order_state = o.find("OrderState").string
            order_id = o.find("OrderID").string
            client_order_identifier = o.find("ClientOrderIdentifier").string
            buyer_email_address = o.find("BuyerEmailAddress").string
            shipping_info = o.find("ShippingInfo")
            ship_address_line_1 = shipping_info.find("AddressLine1").string
            ship_address_line_2 = shipping_info.find("AddressLine2").string
            ship_city = shipping_info.find("City").string
            ship_region = shipping_info.find("Region").string
            ship_region_description = shipping_info.find("RegionDescription").string
            ship_postal_code = shipping_info.find("PostalCode").string
            ship_country_code = shipping_info.find("CountryCode").string
            ship_first_name = shipping_info.find("FirstName").string
            ship_last_name = shipping_info.find("LastName").string
            shipment_list = shipping_info.find("ShipmentList")
            shipment = shipment_list.find("Shipment")
            shipping_carrier = shipment.find("ShippingCarrier").string
            shipping_class = shipment.find("ShippingClass").string
            tracking_number = shipment.find("TrackingNumber").string
            payment_info = o.find("PaymentInfo")
            payment_type = payment_info.find("PaymentType").string
            billing_info = o.find("BillingInfo")
            bill_address_line_1 = billing_info.find("AddressLine1").string
            bill_address_line_2 = billing_info.find("AddressLine2").string
            bill_city = billing_info.find("City").string
            bill_region = billing_info.find("Region").string
            bill_region_description = billing_info.find("RegionDescription").string
            bill_postal_code = billing_info.find("PostalCode").string
            bill_country_code = billing_info.find("CountryCode").string
            bill_first_name = billing_info.find("FirstName").string
            bill_last_name = billing_info.find("LastName").string
            shopping_cart = o.find("ShoppingCart")
            line_item_sku_list = shopping_cart.find("LineItemSKUList")
            # print(line_item_sku_list)
            item_sale_source = line_item_sku_list.find("OrderLineItemItem").find("ItemSaleSource").string
            items = {}
            for line_item in line_item_sku_list.find_all("OrderLineItemItem"):
                unit_price = line_item.find("UnitPrice").string
                quantity = line_item.find("Quantity").string
                sku = line_item.find("SKU").string
                title = line_item.find("Title").string
                warehouse_location = line_item.find("WarehouseLocation").string
                distribution_center_code = line_item.find("DistributionCenterCode").string
                item_sale_source_transaction_id = line_item.find("ItemSaleSourceTransactionID").string
                item_sale_source = line_item.find("ItemSaleSource").string
                items[sku] = {
                             "unit_price": unit_price,
                             "quantity": quantity,
                             "title": title,
                             "warehouse_location": warehouse_location,
                             "distribution_center_code": distribution_center_code,
                             "item_sale_source_transaction_id": item_sale_source_transaction_id
                             }
            orders[order_id] = {
                               "number_of_matches": number_of_matches,
                               "order_time_gmt": order_time_gmt,
                               "total_order_amount": total_order_amount,
                               "order_state": order_state,
                               "client_order_identifier": client_order_identifier,
                               "buyer_email_address": buyer_email_address,
                               "ship_address_line_1": ship_address_line_1,
                               "ship_address_line_2": ship_address_line_2,
                               "ship_city": ship_city,
                               "ship_region": ship_region,
                               "ship_region_description": ship_region_description,
                               "ship_postal_code": ship_postal_code,
                               "ship_country_code": ship_country_code,
                               "ship_first_name": ship_first_name,
                               "ship_last_name": ship_last_name,
                               "shipping_carrier": shipping_carrier,
                               "shipping_class": shipping_class,
                               "tracking_number": tracking_number,
                               "bill_address_line_1": bill_address_line_1,
                               "bill_address_line_2": bill_address_line_2,
                               "bill_city": bill_city,
                               "bill_region": bill_region,
                               "bill_region_description": bill_region_description,
                               "bill_postal_code": bill_postal_code,
                               "bill_country_code": bill_country_code,
                               "bill_first_name": bill_first_name,
                               "bill_last_name": bill_last_name,
                               "item_sale_source": item_sale_source,
                               "payment_type": payment_type,
                               "items": items
                               }
        return orders

    def getOrders(self, days):
        """
        returns orders in dictionary from <days> days ago.
        """
        d = days
        days = int(days)
        days = timedelta(days)
        x = datetime.now()
        x = x-days
        if x.month < 10:
            month = "0" + str(x.month)
        else:
            month = x.month
        day = "0" + str(x.day) if x.day < 10 else x.day
        t = "{}-{}-{}".format(x.year, month, day)
        print(t)
        page = 1
        orders = {}
        while True:
            print("Retrieving page {} of orders starting from {} days ago".format(page, d))
            xml = self.getOrderList(ordercreationfilterbegintimegmt=t, pagenumberfilter=str(page))
            parsed = self.parseOrders(xml)
            if parsed is None:
                break
            for o in parsed:
                orders[o] = parsed[o]
                # print(o)
            page += 1
        return orders


    #############################
    # END Order Service Methods #
    #############################
    def enableLogging(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)


def main():
    ca = ChannelAdvisor()
    ca.enableLogging()
    # ca.connectAdmin()
    ca.requestAccess()


def testInventoryRequest():
    ca = ChannelAdvisor()
    # ca.enableLogging()
    ca.connectInventory()
    # print(ca.client)
    xml = ca.getFilteredInventoryItemList(pagenumber="1", pagesize="2")
    # print(ca.client.last_sent())
    # print("")
    # print("")
    print(ca.client.last_received())


def testParser():
    ca = ChannelAdvisor()
    xml = ca.getFilteredInventoryItemList(pagenumber="2", pagesize="1")
    print(xml)
    info = ca.parseGfiil(xml)
    # print(info)
    for sku in info:
        print(sku)
        print(pprint.pformat(info[sku]))


def testGetAllInventory():
    ca = ChannelAdvisor()
    skus = ca.getAllInventory()
    print(skus["1131"])


def testGetFilteredSkuList():
    ca = ChannelAdvisor()
    xml = ca.getFilteredSkuList(labelname="onsale", pagesize="2")
    print(xml)


def testGetAllOnSale():
    ca = ChannelAdvisor()
    skus = ca.getAllOnSale()
    for sku in skus:
        print(sku)


def testUpdateInventory():
    skus = {}
    # should go to 27
    skus["3205"] = {"quantity":"5"}
    # should go to 30
    skus["2205"] = {"quantity":"5"}
    ca = ChannelAdvisor()
    ca.updateInventoryItemQuantityAndPriceList(skus, "Relative")
    print(ca.client.last_sent())


def testgetskuinfo():
    ca = ChannelAdvisor()
    xml = ca.getInventoryItemStoreInfo("2323")
    print(xml)


def testGetInventoryItemList():
    ca = ChannelAdvisor()
    xml = ca.getInventoryItemList(["2323"])
    print(xml)


def testGetBarcode():
    ca = ChannelAdvisor()
    title, upc, loc = ca.getBasicInfo(2323)
    print(title, upc, loc)


def testGetDetailedInfo():
    ca = ChannelAdvisor()
    info = ca.getDetailedInfo(1313)
    print(info)


def testSynchItem():
    ca = ChannelAdvisor()
    # test = ca.synchInventoryItem("1313", quantity="-2",
    #                             quantityupdatetype="Relative",
    #                             distributioncentercode="Ventura")
    ca.synchInventoryItem(1313, warehouselocation="W005")
    # print(test)


def testGetOrderList():
    ca = ChannelAdvisor()
    # x = ca.getOrderList(ordercreationfilterbegintimegmt="2015-08-22")
    x = ca.getOrderList(pagenumberfilter="1", pagesize="1")
    print(x)


def testParseOrders():
    ca = ChannelAdvisor()
    x = ca.getOrderList(pagesize="1")
    print(pprint.pformat(ca.parseOrders(x)))


def testGetOrders():
    ca = ChannelAdvisor()
    x = ca.getOrders(days=3)
    for order in x:
        print(pprint.pformat(order))

if __name__ == '__main__':
    main()
    # testInventoryRequest()
    # testParser()
    # testGetAllInventory()
    # testGetFilteredSkuList()
    # testGetAllOnSale()
    # testUpdateInventory()
    # testgetskuinfo()
    # testGetInventoryItemList()
    # testGetBarcode()
    # testGetDetailedInfo()
    # testSynchItem()
    # testGetOrderList()
    # testParseOrders()
    # testGetOrders()