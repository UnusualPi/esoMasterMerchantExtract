# esoMasterMerchantExtract
A very simple utility application used to extract data from the Elder Scrolls Online add-on Master Merchant and create a CSV file.

It will also calculate your flip (purchase and resell) margins.
# Step 1:
Select your ESO "SavedVariables" folder. Usually in `C:\Users\Your User Name\Documents\Elder Scrolls Online\live`
# Step 2:
Select the folder to save the output files.
# Step 3:
Hit the "Execute" button.  This may take a while. When completed you'll have three files:
1. `salesdata_YYYY-mm-dd.csv`
1. `purchasedata_YYYY-mm-dd.csv`
1. `flipdata_YYYY-mm-dd.csv`

## How does the "flip" calculation work?
1. Order all sales and purchase data by timestamp and index by item type.
  - Each item will be assigned an index location based on the time sold.
1. Match the purchase item index to sale item index.
  - For example, if I have 3 purchases of an item and 2 sales of that item.  The first two purchases will be matched to the 2 sales.
  - If I have 3 purchases of an item and 4 sales of that item. The 3 purchases will be matched to the first 3 sales.
  - If I have 4 purchases and 16 sales. The 4 purchases will be matched to the closest sale that occurs AFTER the purchase.

### What are the limitations of the flip calculation?
1. For now, the calculation has to have the exact same quantity.
  - This means if you purchased 143 of an item, you have to sell that exact same quantity for the flip calculator to pick it up (can be a pain on flipping mats).
1. The time frame isn't limited at this time.  Meaning, you could make a purchase 500 days ago then make a sale of the same item.  Technically, it is a flip but you may not have made the purchase with the intention to flip it.
