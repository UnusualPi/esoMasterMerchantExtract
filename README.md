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
1. Take each purchase, then find the immediately following sale of the same itemShortId and quantity.
1. Remove the matched sale from future considerations in the event another purchase of the same item/quantity was made before the sale.

### What are the limitations of the flip calculation?
1. For now, the calculation has to have the exact same quantity.
  - This means if you purchased 143 of an item, you have to sell that exact same quantity for the flip calculator to pick it up (can be a pain on flipping mats).
1. The time frame for matching a purchase to a sale is limited to 45 days.  Meaning a sales has to occur 45 days after a purchase in order to be counted as a "flip".  This can be changed in the code, but the binaries have no way to change in the UI.
