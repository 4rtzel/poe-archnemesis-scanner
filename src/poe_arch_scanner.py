import sys
import argparse
from PIL import ImageGrab

from ArchnemesisItemsMap import ArchnemesisItemsMap
from DataClasses import PoeWindowInfo
from ImageScanner import ImageScanner
from UIOverlay import UIOverlay

import win32gui
from win32clipboard import *

import tkinter as tk
from tkinter import messagebox

from PIL import ImageGrab

from RecipeShopper import RecipeShopper

import constants

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

    x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
    info.x = x0
    info.y = y0
    info.width = x1 - x0
    info.height = y1 - y0
    x0, y0, x1, y1 = win32gui.GetClientRect(hwnd)
    info.client_width = x1 - x0
    info.client_height = y1 - y0

    if info.client_width == 0 or info.client_height == 0:
        show_warning("Unable to detect Path of Exile resolution. Make sure it isn't running in the Fullscreen mode.\n\nThe tool will use your screen resolution for calculations instead.")
        screen = ImageGrab.grab()
        info.x = 0
        info.y = 0
        info.width, info.height = screen.size
        info.client_width, info.client_height = screen.size
    info.title_bar_height = info.height - info.client_height
    return info

def calculate_default_scale(info: PoeWindowInfo) -> float:
    """
    TODO: validate the math for non 16:9 resolutions (e.g. ultrawide monitors)
    """

    # Assume that all source images have 78x78 size
    source_image_height = 78.0

    # Take 0.91 as a golden standard for 2560x1440 resolution and calculate
    # scales for other resolutions based on that
    constant = 1440.0 / (source_image_height * 0.91)
    scale = info.client_height / (source_image_height * constant)
    return scale

parser = argparse.ArgumentParser(description='Path of Exile archnemesis scanner')
parser.add_argument(
    '--show-capture-image',
    help='shows the captured screen image that the program uses for scanning',
    dest='show_capture_image',
    action='store_true')

parser.add_argument('--scanner-window-x', help='x position of scanner window', dest='scanner_window_x', type=int, default=-1)
parser.add_argument('--scanner-window-y', help='y position of scanner window', dest='scanner_window_y', type=int, default=-1)
parser.add_argument('--scanner-window-width', help='width of scanner window', dest='scanner_window_width', type=int, default=-1)
parser.add_argument('--scanner-window-height', help='height of scanner window', dest='scanner_window_height', type=int, default=-1)
args = parser.parse_args()

# Create root as early as possible to initialize some modules (e.g. ImageTk)
root = tk.Tk()
root.withdraw()

info = get_poe_window_info()

items_map = ArchnemesisItemsMap(calculate_default_scale(info))

image_scanner = ImageScanner(info, items_map, args)

recipe_shopper = RecipeShopper(items_map)

overlay = UIOverlay(root, info, items_map, image_scanner, recipe_shopper)
overlay.run()
