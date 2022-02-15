import sys
from PIL import ImageGrab

from ArchnemesisItemsMap import ArchnemesisItemsMap
from DataClasses import PoeWindowInfo
from ImageScanner import ImageScanner
from UIOverlay import UIOverlay

import win32gui
from win32clipboard import *

import tkinter as tk
from tkinter import messagebox

from PIL import ImageGrab, Image

from RecipeShopper import RecipeShopper

def show_warning(text: str) -> None:
    messagebox.showwarning('poe-archnemesis-scanner', text)

def show_error_and_die(text: str) -> None:
    # Dealing with inconveniences as Perl would
    messagebox.showerror('poe-archnemesis-scanner', text)
    sys.exit()

def get_poe_window_info() -> PoeWindowInfo:
    info = PoeWindowInfo()
    hwnd = win32gui.FindWindow(None, 'Path of Exile')
    if hwnd == 0:
        show_error_and_die('Path of Exile is not running.')

    cx0, cy0, cx1, cy1 = win32gui.GetClientRect(hwnd)
    x0, y0 = win32gui.ClientToScreen(hwnd, (cx0, cy0))
    info.x = x0
    info.y = y0
    info.width = cx1 - cx0
    info.height = cy1 - cy0
    return info

def get_poe_image_info(src: str) -> PoeWindowInfo:
    info = PoeWindowInfo()
    info.src = Image.open(src, "r")
    info.x = 0
    info.y = 0
    info.width = info.src.width
    info.height = info.src.height
    return info

# Create root as early as possible to initialize some modules (e.g. ImageTk)
root = tk.Tk()
root.withdraw()

if __name__ == "__main__":
    # Create root as early as possible to initialize some modules (e.g. ImageTk)
    root = tk.Tk()
    root.withdraw()

    if (len(sys.argv) > 1):
        info = get_poe_image_info(sys.argv[1])
    else:
        info = get_poe_window_info()

    items_map = ArchnemesisItemsMap()

    image_scanner = ImageScanner(info, items_map)

    recipe_shopper = RecipeShopper(items_map)

    overlay = UIOverlay(root, info, items_map, image_scanner, recipe_shopper)
    overlay.run()