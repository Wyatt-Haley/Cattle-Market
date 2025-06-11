# Cattle-Market
Cattle market is a project using sale barn data from the United States Department of Agriculture (USDA) Agricultural Marketing Service (AMS) MyMarketNews (MMN) API. With the end goal to produce helpful interactive sales visuals and predictive modeling.

# About
Cattle are sold in various different market structures like private treaty, contracts and local livestock markets. Larger scale cattle producers normally use the private treaty or contracts methods due to the number of head they produce, as selling at an open market like a sale barn creates a loss of efficiency. The ability to produce the volume needed for these contracts is something that most producers do not strive for as there is an easier marketing option of sale barns. Open auctions or sale barns are sales/ markets that normally happen weekly, unless on a holiday, and welcome all types of cattle from calves to mature males/ females. When selling at these places, there is a universal grading system first broken down by the type of commodity the three types are Feeder Cattle, Replacement Cattle, and Slaughter Cattle. These categories are broken down more into the classes like Heifers, Cows, Bulls, and Steers. There also is a frame score break down of Large, Large - Medium, Medium, Medium - Small, and Small. The cattle also get muscle grade scores of 1-4, where 1's are the heavier muscled and 4's being extremely light muscled. Sorting through sale price information can be confusing if never been presented before as the prices from sale barn reports are in dollars per one hundred weight ($/cwt), thus example price would be $326 cwt is the same as $3.26 per pound. 

# Files
This repository contains the python code files to pull the data from the USDA AMS MMN API, as well as the data transformation of pivoting information to create single entries for each sale. Plus there are also files for creating average price trend visualization based on the commodity, class, frame size, and muscle grade. 

"Filters and More" is a file added to break down the slug_ids and the titles of the filter data, and the available information for each tittle.

# Code 
This code allows for the user to choose the sale barns they would like to pull data from and the time frame. For the code available it pulls data from all the sale bars in Florida. To change these find the slug_ids for the markets you wish to pull and update the code. 

# Troule shooting
It is known that some sale barns do not update their numbers with the USDA AMS so work is being done to gather this additional information as the sales are happening, however the reports are not similar and for the sake of time will be revisited after the tool is more developed. 

# Thanks!
Thanks for stopping by and hope this code is helpful, please write if there are any suggestion or questions!

# Sources 
https://mymarketnews.ams.usda.gov/

# How to use
- Ensure Python and all packages used are downloaded
- Place the files where you wish to save the contents
- Edit slug_id list for selected barns and time frame
- Optain API key (this can be done by creating a account via the USDA AMS MMN)
- Open or run the api1.3.py file
- Then vis1.3.py to get the graphics
