# poe-archnemesis-scanner
Tool for Path of Exile game to automatically scan Archemesis inventory and display related information

## Features

### Settings

When you first start the program, a small settings window will pop up that will look like this:

![settings_window](docs/settings_window.png)

Here you can adjust some parameters to improve searching or change the display settings.

* 'Set scanner window' button modifies the scanning area. The format for the window position is the following `x, y, width, height`. `x` and `y` are the horizontal and vertical offset from the top left corner of the screen. `width` and `height` are horizontal and vertical size of the window.

  When you press the button, a white rectangle will pop up for a moment and then disappear. This rectangle shows the scanning window area to help with adjustments. The default value should work in most cases, but if you want to speed the search, it's recommended to adjust it.
  
* 'Set image scale' button sets the scaling factor for the source images. The current search algorithm expects the source image and the image on the screen to be the same size. Thus, we'll need to scale down/up the source images in order to get reliable results.

  The default calculated automatically based on the screen resolution and should work for most of the people. However, if you have some non-standard resolution, the search algorithm may not work properly, so you'll need to adjust this parameter manually.
  
* 'Display inventory items' checkbox turns additional display setting for scan window. The scan results will also include a list of all of your archnemesis items in the inventory.

### Controls
Once you close the setting window, two small buttons will pop up in the top left corner of your screen.

![controls](docs/controls.png)

* '[X]' button just closes the program.
* 'Scan' button does all the magic. Once you press it, the program will enter the scanning mode and the button will change to 'Scanning...'. It will scan your screen according to the scanning window area and will create a list of all possible recipes. After the scan completes, the button will change again to 'Hide'. Once you examine the scan result, click the 'Hide' button to hide them.

### Scan results
The scan result will be displayed at the top of the screen like that:

![scan_results](docs/scan_results.png)

It shows you all available recipes that you can create right now. If the text is green, then that means you already have such item in the inventory. If the text is orange, then this item doesn't exist in your inventory.

You could then hover over any of the recipes to highlight the items in your inventory that could be combined to create it:

![scan_results_highlight](docs/scan_results_highlight.png)

If you checked 'Display inventory items' box, then your scan results will also include a list of all of your items in inventory (colored in white):

![scan_results_display_inventory_items](docs/scan_results_display_inventory_items.png)

Again, hover over any items to display them in your inventory.

## Installation


### Standalone
You could download a standalone version from release page: https://github.com/4rtzel/poe-archnemesis-scanner/releases. The package was created using `pyinstaller`.

### Manual
You'll need to install Python and all project dependencies. Python could be installed from Microsoft Store and from the main site: https://www.python.org/downloads/ (doesn't include `pip`, so you'll have to install it separately).

Once the Python and pip are installed, run this command from the project directory to install all project dependencies:

```cmd
pip.exe install -r requirements.txt
```

and then start the program

```cmd
python.exe poe_arch_scanner.py
```

## Known Issues

* Doesn't work if the game is in the fullscreen.
* Only works for the primary monitor (Tk limitation).
* Occasionally hangs.
