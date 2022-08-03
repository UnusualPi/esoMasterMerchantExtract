import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getFlipData(enrichedSalesData, enrichedPurchaseData, days=45):
    sortedPurchaseData = sorted(enrichedPurchaseData, key=lambda i: (i['itemShortId'], i['timestamp']) , reverse=True)
    sortedSalesData = sorted(enrichedSalesData, key = lambda i: (i['itemShortId'], i['timestamp']) , reverse=True)
    usr = enrichedPurchaseData[0]['buyerName']
    logger.info('Working on flip data for {}...'.format(usr))
    userSalesData = [s for s in enrichedSalesData if s['sellerName']==usr]

    logger.info('Matching purchases to sales...')
    flipLinks = []
    for purchase in enrichedPurchaseData:
        link = {'purchaseId':purchase['id'],
                'saleId': None,
                'Purchase Datetime (UTC)':purchase['dateTime_UTC'],
                'Sale Datetime (UTC)':None,
                'Days in Play': None,
                'ESO Week':None,
                'Item Name':purchase['itemName'],
                'itemType':None,
                'itemQuality':None,
                'itemTrait':None,
                'sellerName':None,
                'buyerName':None,
                'quantity':None,
                'Purchase Price':purchase['price'],
                'Sales Price':None,
                'Net Sales Price':None,
                'Profit':None,
                'Margin':None}
        for sale in userSalesData:
            if (sale['itemShortId'] == purchase['itemShortId']
                    and sale['timestamp'] > purchase['timestamp']
                    and sale['timestamp'] - purchase['timestamp'] <= 86400*days):
                link['saleId'] = sale['id']
                link['Sale Datetime (UTC)'] = sale['dateTime_UTC']
                link['Days in Play'] = (sale['dateTime_UTC'] - purchase['dateTime_UTC']).days
                link['ESO Week'] = sale['esoWeekStart']
                link['itemType'] = sale['itemType']
                link['itemQuality'] = sale['itemQuality']
                link['itemTrait'] = sale['itemTrait']
                link['sellerName'] = sale['sellerName']
                link['buyerName'] = sale['buyerName']
                link['quantity'] = sale['quant']
                link['Sales Price'] = sale['price']
                link['Net Sales Price'] = sale['netSaleProfit']
                link['Profit'] = round(sale['netSaleProfit'] - purchase['price'],2)
                if link['Profit'] >= 0:
                    link['Margin'] = round((sale['netSaleProfit'] - purchase['price']) / sale['netSaleProfit'],4)
                else:
                    link['Margin'] = round((sale['netSaleProfit'] - purchase['price']) / purchase['price'],4)
                break
        link['saleId'] = link.get('saleId')
        if link['saleId'] != None:
            flipLinks.append(link)
    return flipLinks
