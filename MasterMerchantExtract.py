import csv
from datetime import datetime
import MasterMerchant_helper as mm
import MasterMerchant_flipCalculator as mmf
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory, asksaveasfilename
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

now = datetime.now()
today = datetime.strftime(now, '%Y-%m-%d')

def selectVariablesFolder():
    global dataFolder
    dataFolder = askdirectory()
    folderText.insert(END, "{}".format(dataFolder))
    return dataFolder

def selectSaveLocation():
    global outFolder
    outFolder = askdirectory()
    saveText.insert(END, "{}".format(outFolder))
    return outFolder

def aboutWindow():
    aboutWindow = Toplevel(window)
    aboutWindow.geometry("300x150")
    aboutWindow.wm_title("About")
    aboutLabel = Label(aboutWindow, text = "About")
    aboutLabel.pack()

def execute():
    salesData = mm.getSalesData(dataFolder)
    enrichedSalesData = mm.enrichSalesData(dataFolder, salesData)
    purchaseData = mm.getPurchasesData(dataFolder)
    enrichedPurchaseData = mm.enrichSalesData(dataFolder, purchaseData)

    for item in enrichedPurchaseData:
        window.update_idletasks()
        item.pop('listingFee')
        item.pop('guildTax')
        item.pop('zosTax')
        item.pop('netSalePrice')
        item.pop('netSaleProfit')

    logger.info('Exporting enriched sales data...')
    with open(outFolder+f'/salesdata_{today}.csv', 'w', newline='') as f:
        fields = list(enrichedSalesData[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for sale in enrichedSalesData:
            w.writerow(sale)
    logger.info('Complete.')
    logger.info('Exporting enriched purchase data...')
    with open(outFolder+f'/purchasedata_{today}.csv', 'w', newline='') as f:
        fields = list(enrichedPurchaseData[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for sale in enrichedPurchaseData:
            w.writerow(sale)
    logger.info('Complete.')

    try:
        flipData = mmf.getFlipData(enrichedSalesData, enrichedPurchaseData)
        logger.info('Exporting flip sales data...')
        with open(outFolder+'/flipdata_{}.csv'.format(today), 'w', newline='') as f:
            fields = list(flipData[0].keys())
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for flip in flipData:
                w.writerow(flip)
        logger.info('Complete.')
    except Exception as e:
        logger.error('There was an error extracing flip data: {}'.format(e))
    logger.info('All Exports Completed.')
    return True

window = ttk.Window(themename="superhero")

window.wm_title("MasterMerchant Data Extractor")
window.grid_rowconfigure(0, weight=1, minsize=20) #Top Buffer
window.grid_rowconfigure(2, weight=1, minsize=80) #Open Select Button Spacing
window.grid_rowconfigure(4, weight=1, minsize=20) #Break
window.grid_rowconfigure(6, weight=1, minsize=80) #Save select button spacing
window.grid_rowconfigure(8, weight=1, minsize=20) #Break
window.grid_rowconfigure(10, weight=1, minsize=80) #Execute select button spacing
window.grid_rowconfigure(11, weight=1, minsize=20) #Bottom Buffer
window.grid_columnconfigure(0, weight=1, minsize=20) #Left Buffer
window.grid_columnconfigure(12, weight=1, minsize=20) #Break
window.grid_columnconfigure(14, weight=1, minsize=20) #Right Buffer

openLabel = Label(window, text='1. Select your Elder Scrolls "SavedVariables" folder:')
openLabel.grid(row=1, column=1, sticky='W')
open_button=Button(window,text="Select", width=10, command=selectVariablesFolder, bootstyle=SECONDARY)
open_button.grid(row=2,column=1, rowspan=1, sticky='W')
folderText = Text(window, height=1, width=75, wrap='none')
folderText.grid(row=3, column=1, columnspan=11, sticky='NWSE')

saveLabel = Label(window, text='2. Select your save folder:')
saveLabel.grid(row=5, column=1, sticky='W')
save_button=Button(window,text="Select", width=10, command=selectSaveLocation, bootstyle=SECONDARY)
save_button.grid(row=6,column=1, rowspan=1, sticky='W')
saveText = Text(window, height=1, width=75, wrap='none')
saveText.grid(row=7, column=1, columnspan=11, sticky='NWSE')

executeLabel = Label(window, text='3. Execute:')
executeLabel.grid(row=9, column=1, sticky='W')
execute_button=Button(window,text="Execute", width=10, command=execute, style="Accent.TButton")
execute_button.grid(row=10,column=1, rowspan=1, sticky='W')

window.mainloop()
