import re
import json
from slpp import slpp as lua
import datetime as dt
import logging
import pandas as pd
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

params = {
  "equip_types":["head","neck","ring","chest","hands","shoulders","one-handed","two-handed","off","waist","feet","legs"],
  "traits":["healthy","arcane","robust","bloodthirsty","harmony","infused","triune","protective","swift","sturdy","impenetrable","reinforced","well-fitted","training","invigorating","divines","powered","charged","precise","defending","sharpened","decisive","nirnhoned","intricate","ornate","prolific","shattering","bolstered","soothing","focused","quickened","augmented","aggressive","vigorous"]
  }

def esoWeek(d):
    while d.weekday()!=1:
        d+=dt.timedelta(1)
    d = d.replace(hour=12, minute=00, second=00)
    return(d+dt.timedelta(-7), d)

def getHeaderData(dataFolder, dataFile, header, server="NA", start_timestamp=0):
    data = open(dataFolder+dataFile, 'r').read()
    decodedData = lua.decode(data.partition(header)[2])
    ignored=0
    cnt=0
    results = []
    try:
        for value in decodedData.values():
            for value1 in value.values():
                for v in value1['sales'].values():
                    v['esoServer'] = server
                    v['itemName'] = value1['itemDesc']
                    v['itemDetail'] = value1['itemAdderText']
                    if v['timestamp'] > start_timestamp:
                        cnt+=1
                        results.append(v)
                    else:
                        ignored+=1
    except Exception as e:
        logger.error('{}: {}'.format(dataFile, e))
    logger.info('Data file "{}": {} new records, {} old records.'.format(dataFile[1:], cnt, ignored))
    return({'results':results,'ignored':ignored,'count':cnt})

def getListingsData(dataFolder, server="NA", start_timestamp=0):
    if server == "NA":
        header = '["listingsna"] = \n'
    else:
        header = '["listingsnaeu"] = \n'
    datafiles = [f'\GS{i:02}Data.lua' for i in range(16)]
    listings = []
    logger.info('GS Datafile Directory: "{}"'.format(dataFolder))
    truncate_cnt=0
    for datafile in datafiles:
        data = getHeaderData(dataFolder, datafile, header, start_timestamp=start_timestamp)
        for listing in data['results']:
            listings.append(listing)
        truncate_cnt+=data['ignored']
    logger.info('{} new records captured from {} total records in data files.'.format(len(listings), truncate_cnt))
    return listings

def getSalesData(dataFolder, server="NA", start_timestamp=0):
    if server == "NA":
        header = '["datana"] = \n'
    else:
        header = '["dataeu"] = \n'
    datafiles = [f'\GS{i:02}Data.lua' for i in range(16)]
    sales = []
    logger.info('GS Datafile Directory: "{}"'.format(dataFolder))
    truncate_cnt=0
    for datafile in datafiles:
        data = getHeaderData(dataFolder, datafile, header, start_timestamp=start_timestamp)
        for sale in data['results']:
            sales.append(sale)
        truncate_cnt+=data['ignored']
    logger.info('{} new records captured from {} total records in data files.'.format(len(sales), truncate_cnt))
    return sales

def getPurchasesData(dataFolder, server="NA", start_timestamp=0):
    if server == "NA":
        header = '["purchasena"] = \n'
    else:
        header = '["purchaseeu"] = \n'
    datafile = '\GS17Data.lua'
    purchases = []
    logger.info('GS Datafile Directory: "{}"'.format(dataFolder))
    truncate_cnt=0
    data = getHeaderData(dataFolder, datafile, header, start_timestamp=start_timestamp)
    for purchase in data['results']:
        purchases.append(purchase)
    truncate_cnt+=data['ignored']
    logger.info('{} new records captured.'.format(len(purchases)))
    return purchases

def enrichSalesData(dataFolder, salesData):
    logger.info('Enriching Sales Data for {} records...'.format(len(salesData)))
    logger.info('Parsing "GS16Data.lua" data file for guild names, item links, and account names.')
    GS16 = open(dataFolder+'\GS16Data.lua','r').read()
    guilds = [(k,v) for k,v in lua.decode(GS16.partition('["guildNames"] = \n')[2]).items()]
    itemLinks = [(k,v) for k,v in lua.decode(GS16.partition('["itemLink"] = \n')[2]).items()]
    users = [(k,v) for k,v in lua.decode(GS16.partition('["accountNames"] = \n')[2]).items()]
    guildsDf = pd.DataFrame(guilds, columns=['guild','id']).set_index('id')
    itemLinksDf = pd.DataFrame(itemLinks, columns=['link','id']).set_index('id')
    usersDf = pd.DataFrame(users, columns=['user','id']).set_index('id')

    logger.info('Converting transaction timestamp to datetime & adding pricing details...')
    for sale in salesData:
        sale['dateTime_UTC'] = dt.datetime.fromtimestamp(sale['timestamp'])
        esoWk = esoWeek(sale['dateTime_UTC'])
        sale['esoWeekStart'] = esoWk[0]
        sale['esoWeekEnd'] = esoWk[1]
        sale['unitPrice'] = sale['price'] / sale['quant']
        sale['guildTax'] = round(sale['price']*.035,2)
        sale['zosTax'] = round(sale['price']*0.035,2)
        sale['listingFee'] = round(sale['price']*.01,2)
        sale['netSalePrice'] = round(sale['price'] - (sale['price']*.07),2)
        sale['netSaleProfit'] = round(sale['price'] - (sale['price']*.08),2)

    logger.info('Parsing item level, color, quality...')
    for sale in salesData:
        dimensions = sale['itemDetail'].split(' ')
        sale['itemLevel'] = dimensions[0].replace('rr','').upper()
        if sale['itemName'] == 'Spoiled Food':
            sale['itemColor'] = 'n/a'
            sale['itemQuality'] = 'n/a'
        else:
            sale['itemColor'] = dimensions[1].title()
            sale['itemQuality'] = dimensions[2].title()

    logger.info('Parsing item type, trait, equip type...')
    for sale in salesData:
        dimensions = sale['itemDetail'].split(' ')
        # Apparel, Consumable, and Furnishings have 2 word descriptions, this will account for that
        if 'apparel' in dimensions or 'consumable' in dimensions or 'furnishings' in dimensions:
            try:
                sale['itemType'] = '{} {}'.format(dimensions[3].title(), dimensions[4].title())
            except IndexError:
                sale['itemType'] = '{} {}'.format(dimensions[2].title(), dimensions[3].title())
        else:
            sale['itemType'] = dimensions[3].title()
        # Materials could have 1 to three words
        if 'materials' in dimensions:
            if len(dimensions) == 7:
                sale['itemType'] = '{} {} {}'.format(dimensions[3].title(), dimensions[4].title(), dimensions[5].title())
                sale['itemTrait'] = dimensions[-1].title()
            elif len(dimensions) == 6:
                sale['itemType'] = '{} {} {}'.format(dimensions[3].title(), dimensions[4].title(), dimensions[5].title())
            elif len(dimensions) == 5:
                sale['itemType'] = '{} {}'.format(dimensions[3].title(), dimensions[4].title())
            else:
                sale['itemType'] = dimensions[3].title()

        if 'apparel' in dimensions or 'weapon' in dimensions:
            for trait in params['traits']:
                if trait == dimensions[-1]:
                    sale['itemTrait'] = dimensions[-1].title()
                    break
                else:
                    sale['itemTrait'] = 'None'

        if dimensions[-1] == 'glyph':
            sale['itemType'] = '{} {}'.format(dimensions[-2].title(), dimensions[-1].title())
            sale['itemTrait'] = 'n/a'

            for type in params['equip_types']:
                if type in dimensions:
                    if type == 'off':
                        sale['itemEquipType'] = 'Off Hand'
                    else:
                        sale['itemEquipType'] = type.title()
                    break
                else:
                    sale['itemEquipType'] = 'None'
        else:
            if sale.get('itemTrait') == None:
                sale['itemTrait'] = 'n/a'
            sale['itemEquipType'] = 'n/a'

    salesDataDf = pd.DataFrame(salesData)

    logger.info('Adding buyer and seller account names...')
    salesDataDf = pd.merge(salesDataDf, usersDf, how="left", left_on='seller', right_on='id')
    salesDataDf.rename(columns={'user':'sellerName'}, inplace=True)
    salesDataDf = pd.merge(salesDataDf, usersDf, how="left", left_on='buyer', right_on='id')
    salesDataDf.rename(columns={'user':'buyerName'}, inplace=True)

    logger.info('Adding guild names...')
    salesDataDf = pd.merge(salesDataDf, guildsDf, how="left", left_on='guild', right_on='id')
    salesDataDf.rename(columns={'guild_x':'guild','guild_y':'guildName'}, inplace=True)

    logger.info('Adding item links...')
    salesDataDf = pd.merge(salesDataDf, itemLinksDf, how="left", left_on='itemLink', right_on='id')
    salesDataDf.rename(columns={'itemLink':'itemId','link':'itemLink'}, inplace=True)

    salesData = salesDataDf.to_dict(orient='records')

    for sale in salesData:
        sale['hyperlink'] = 'http://esoitem.uesp.net/itemLink.php?link='+str(sale['itemId'])
        sale['itemShortId'] = int(re.search('item:(\d*)', str(sale['itemLink'])).group(1))

    logger.info('Sorting dicts...')
    for sale in salesData:
        keys = sorted(sale)
        for k in keys:
            sale[k] = sale.pop(k)

    logger.info('Data enrichment complete.')
    return salesData
