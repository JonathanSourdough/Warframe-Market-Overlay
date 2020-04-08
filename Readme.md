# Warframe Market Overlay

This is an overlay written in Python for the purpose of reading the screen in Warframe, and reporting the values from warframe.market associated with that item.

This was one of my first major projects I worked on, and never completely finished to the degree I would have liked to. Now I have decided to release this on Github so that this extremely handy tool doesnt just sit in a folder on my computer collecting e-dust.

Currently the program is full operational, however, is not highly optimized, and doesnt have all the features I had planned for it, there are a few bugs that could be worked out. Currently I plan to work on it when time allows, and I would certainly look at any pull requests brought to me.

## Prerequisites

You will need to install python (designed and tested in Python 3.7.0)
https://www.python.org/downloads/

Once python is installed you will need to install the required packages, Included in the repo is a requirements.txt to make your life easy.
```
pip install -r requirements.txt
```


You will also need to install a version of tesseract. (designed and tested using v5.0.0 Alpha.20190708 however any version should work)
https://github.com/tesseract-ocr/tesseract (Source Code)
https://digi.bib.uni-mannheim.de/tesseract/ (Assembled Binaries)

Make sure it is in your windows path variable. (for pytesseract to be able to find it)
Otherwise you will have to edit imagemethodcalc.py to find the .exe, theres a placeholder example commented out in there already.


## How to use

Once you have done the above steps all you should need to do is run the script.
```
python overlay.py
```

## How to use

<img src="ReadmeImages/RewardScreen.PNG">


Immediately on the first run it will be set up for the relic rewards screen, at 1920x1080.

The image above shows what you will see while using it, there is a "Search Window", which is movable and resizable. Paired with it is an "Info Window", which is also movable. This will tell you all the info it can find on that item.

<img src="ReadmeImages/InfoWindow.PNG">

The info Window will show you all the relevant information for the item being scanned.

"Item" The name of the item scanned.
"Accuracy" The % read accuracy. How sure the program is, that the text it was reading is what is being displayed.
"Top Seller" The name of the player who is selling this item the cheapest.
"Top Plat" What the cheapest listed price is.
"Top 10 Avg" What the average of the top 10 listings are.
"Ducats" How many ducats the item is worth.
"Efficency" The Ducat/Platinum efficency is based off of the top seller.

<img src="ReadmeImages/DropDown.PNG">

Most windows have a drop down menu that will do a variety of things.

"New" opens a new search/info window.
"Close" closes the current window.
"Setting" opens the settings window for that info window.
"Main" opens the main window.
"Close all" closes all windows and reopens the main window.

<img src="ReadmeImages/Setting.PNG">

For each of these windows there is a settings window, which can control what is displayed on each info window.

You can choose between the global settings, and on or off.
Each list item is self explanitory, given you have read the above section on the info window.

<img src="ReadmeImages/Highlight.PNG">

If you are ever having a hard time figuring out which windows are tied to eachother, you can double click and it will highlight the attached windows.

<img src="ReadmeImages/GlobalSettings.PNG">

Here you can load, save, and delete saved layouts. This feature is so you can create your own easily loadable layouts, so you dont have to reposition windows all the time if you are scanning areas other than the relic reward screen.
If you choose the "default" option on the drop down menu, and save, that will be what opens whenever you first start the program.


There is 2 new options at the top compared to what is in the individual settings windows.

"Load Background" Turning this off will unload the background picture which will save about 100MB of ram.
"Show Icons" This determines whether or not the relic, platinum, and ducat pictures are displayed on the info windows.


At the bottom you can determine which listing type is displayed.

"Sell" will show the WTS (Want To Sell) listings from warframe.market
"Buy" will show the WTB (Want To Buy) listings


You can also increase the UI scale up to 2x, using the slider at the bottom, this was mostly done to help support 4k monitors.

# Thanks

Thanks to everyone at Digital Extremes for creating and maintaining Warframe.
https://www.warframe.com/

Thanks to 42 Bytes for creating and maintaining warframe.market.
https://warframe.market/
https://www.patreon.com/42Bytes

Thanks to everyone who helped me along this coding journey.

Thanks to you the reader/user who was part of the why behind doing this.

Code by Jonathan Sourdough