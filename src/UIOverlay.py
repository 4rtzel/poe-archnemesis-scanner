from configparser import ConfigParser
import keyboard
import tkinter as tk
import sys
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardText, CloseClipboard

from typing import Dict, List, Tuple
from DataClasses import PoeWindowInfo
from ArchnemesisItemsMap import ArchnemesisItemsMap
from ImageScanner import ImageScanner
from DataClasses import RecipeItemNode
from RecipeShopper import RecipeShopper
from constants import COLOR_BG, COLOR_FG_GREEN, COLOR_FG_LIGHT_GREEN, COLOR_FG_ORANGE, COLOR_FG_WHITE, FONT_BIG, FONT_SMALL


class UIOverlay:
    """
    Overlay window using tkinter '-topmost' property
    """
    def __init__(self, root: tk.Tk, info: PoeWindowInfo, items_map: ArchnemesisItemsMap, image_scanner: ImageScanner, recipe_shopper: RecipeShopper):
        self._window_info = info
        self._items_map = items_map
        self._image_scanner = image_scanner
        self._root = root
        self._recipe_shopper = recipe_shopper
        self._scan_results_window = None
        self._recipe_browser_window = None
        self._recipe_browser_current_root = ''
        self._tooltip_window = None
        self._highlight_windows_to_show = list()
        self._scan_results_window_saved_position = (-1, 0)


        self._settings = Settings(root, items_map, image_scanner, on_scan_hotkey=self._hotkey_pressed)

        self._create_controls()

        self._root.configure(bg='')
        self._root.geometry(f'+{info.x + 5}+{info.y + info.title_bar_height + 5}')
        if self._settings.should_run_as_overlay():
            self._root.overrideredirect(True)
            self._root.wm_attributes('-topmost', True)
        self._root.deiconify()

    @staticmethod
    def create_toplevel_window(bg=''):
        w = tk.Toplevel()
        w.configure(bg=bg)
        # Hide window outline/controls
        w.overrideredirect(True)
        # Make sure the window is always on top
        w.wm_attributes('-topmost', True)
        return w

    def _hotkey_pressed(self) -> None:
        if self._scan_label_text.get() == 'Scan':
            self._scan(None)
        elif self._scan_label_text.get() == 'Hide':
            self._hide(None)

    def _create_controls(self) -> None:
        l = tk.Button(self._root, text='[X]', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        l.bind('<Button-1>', sys.exit)
        l.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        l.grid(row=0, column=0)

        settings = tk.Button(self._root, text='Settings', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        settings.bind('<Button-1>', lambda _: self._settings.show())
        settings.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        settings.grid(row=0, column=1)

        self._scan_label_text = tk.StringVar(self._root, value='Scan')
        self._scan_label = tk.Button(self._root, textvariable=self._scan_label_text, fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        self._scan_label.bind("<Button-1>", self._scan)
        self._scan_label.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        self._scan_label.grid(row=0, column=2)

    def _drag(self, window, offset_x: int, offset_y: int, event) -> Tuple[int, int]:
        x = offset_x + event.x + window.winfo_x()
        y = offset_y + event.y + window.winfo_y()
        window.geometry(f'+{x}+{y}')
        return (x, y)

    def _scan(self, _) -> None:
        self._scan_label_text.set('Scanning...')
        self._root.update()
        results = self._image_scanner.scan()

        shopping_list_mode = self._settings.is_shopping_list_mode() is True
        desired_items = [x for x in self._settings.get_shopping_list().split(",") if x]
        shopping_list = self._recipe_shopper.get_missing_items(desired_items, results)
        print("Missing Items:", shopping_list)

        main_recipe_list = self._items_map.recipes()
        if shopping_list_mode:
            recipe_list = [x for x in self._items_map.recipes() if x[0] in self._recipe_shopper._get_full_shopping_list(desired_items)]
        else:
            recipe_list = main_recipe_list
        if len(results) > 0:
            recipes = list()
            for item, recipe in recipe_list:
                screen_items = [results.get(x) for x in recipe]
                if (all(screen_items) or self._settings.should_display_unavailable_recipes()):
                    recipes.append((item, [x[0] for x in screen_items if x is not None], item in results, all(screen_items)))

            if shopping_list_mode:
                trash_inventory = self._recipe_shopper.get_trash_inventory(desired_items, results)
                trash_recipe_items = [None] * min(4, len(trash_inventory.keys()))
                trash_recipe_items = [trash_inventory[list(trash_inventory.keys())[i]][0] for i,x in enumerate(trash_recipe_items)]
                trash_recipe = ('Trash', trash_recipe_items, False, True)
                recipes.append(trash_recipe)

            self._show_scan_results(results, recipes)

            self._scan_label_text.set('Hide')
            self._scan_label.bind('<Button-1>', self._hide)
        else:
            self._hide(None)

    def _hide(self, _) -> None:
        if self._scan_results_window is not None:
            self._scan_results_window.destroy()
        if self._recipe_browser_window is not None:
            self._recipe_browser_window.destroy()
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._clear_highlights(None)
        self._scan_label_text.set('Scan')
        self._scan_label.bind('<Button-1>', self._scan)

    def _show_scan_results(self, results: Dict[str, List[Tuple[int, int]]], recipes: List[Tuple[str, List[Tuple[int, int]], bool, bool]]) -> None:
        self._scan_results_window = UIOverlay.create_toplevel_window()
        x, y = self._scan_results_window_saved_position
        if x == -1:
            x = self._window_info.x + int(self._window_info.client_width / 3)
            y = self._window_info.y + self._window_info.title_bar_height
        self._scan_results_window.geometry(f'+{x}+{y}')

        last_column = 0
        if self._settings.should_display_inventory_items():
            last_column = self._show_inventory_list(results)
        self._show_recipes_list(results, recipes, last_column + 2)

    def _show_inventory_list(self, results: Dict[str, List[Tuple[int, int]]]) -> int:
        row = 0
        column = 0

        for item in self._items_map.items():
            inventory_items = results.get(item)
            if inventory_items is not None:
                row, column = self._show_image_and_label(item, results, inventory_items, COLOR_FG_WHITE, f'x{len(inventory_items)} {item}', True, row, column)
        return column

    def _show_recipes_list(self, results: Dict[str, List[Tuple[int, int]]], recipes: List[Tuple[str, List[Tuple[int, int]], bool, bool]], column: int) -> None:
        row = 0

        for item, inventory_items, exists_in_inventory, available in recipes:
            if exists_in_inventory:
                if available:
                    fg = COLOR_FG_GREEN
                else:
                    fg = COLOR_FG_LIGHT_GREEN
            else:
                if available:
                    fg = COLOR_FG_ORANGE
                else:
                    fg = COLOR_FG_WHITE
            row, column = self._show_image_and_label(item, results, inventory_items, fg, item, available, row, column)

    def _show_image_and_label(self, item: str, results: Dict[str, List[Tuple[int, int]]], inventory_items: Tuple[int, int], highlight_color: str, label_text: str, highlight, row: int, column: int) -> Tuple[int, int]:
        image = tk.Label(self._scan_results_window, image=self._items_map.get_display_small_image(item), bg=COLOR_BG, pady=5)
        if highlight:
            image.bind('<Enter>', lambda _, arg=inventory_items, color=highlight_color: self._highlight_items_in_inventory(arg, color))
            image.bind('<Leave>', self._clear_highlights)
        image.bind('<Button-1>', lambda _, arg1=item, arg2=results: self._show_recipe_browser_tree(arg1, arg2))
        image.bind('<B3-Motion>', self._scan_results_window_drag_and_save)
        image.grid(row=row, column=column)
        tk.Label(self._scan_results_window, text=label_text, font=FONT_BIG, fg=highlight_color, bg=COLOR_BG).grid(row=row, column=column + 1, sticky='w', padx=5)
        row += 1
        if row % 10 == 0:
            column += 2
            row = 0
        return (row, column)

    def _scan_results_window_drag_and_save(self, event) -> None:
        self._scan_results_window_saved_position = self._drag(self._scan_results_window, -5, -5, event)

    def _show_recipe_browser_tree(self, item: str, results: Dict[str, List[Tuple[int, int]]]) -> None:
        if self._recipe_browser_window is not None:
            self._recipe_browser_window.destroy()
        self._destroy_tooltip_and_clear_highlights(None)
        # If the user clicks on the current root then close the tree
        if self._recipe_browser_current_root == item:
            return
        self._recipe_browser_current_root = item
        self._recipe_browser_window = UIOverlay.create_toplevel_window()
        self._recipe_browser_window.geometry(f'+{self._scan_results_window.winfo_x()}+{self._scan_results_window.winfo_y() + self._scan_results_window.winfo_height() + 40}')

        tree = self._items_map.get_subtree_for(item)
        if self._settings.should_copy_recipe_to_clipboard():
            self._copy_tree_items_to_clipboard(tree)

        def draw_tree(node, row, column):
            children_column = column
            for c in node.components:
                children_column = draw_tree(c, row + 2, children_column)
            columnspan = max(1, children_column - column)
            if node.item in results:
                bg = COLOR_FG_GREEN
            else:
                bg = COLOR_BG
            l = tk.Label(self._recipe_browser_window, image=self._items_map.get_display_small_image(node.item), bg=bg, relief=tk.SUNKEN)
            l.bind('<Button-1>', lambda _, arg1=node.item, arg2=results: self._show_recipe_browser_tree(arg1, arg2))
            l.bind('<B3-Motion>', lambda event: self._drag(self._recipe_browser_window, -5, -5, event))
            l.bind('<Enter>', lambda _, arg1=self._recipe_browser_window, arg2=results.get(node.item), arg3=node.item: self._create_tooltip_and_highlight(arg1, arg2, arg3))
            l.bind('<Leave>', self._destroy_tooltip_and_clear_highlights)
            l.grid(row=row, column=column, columnspan=columnspan)
            if len(node.components) > 0:
                f = tk.Frame(self._recipe_browser_window, bg=COLOR_BG, width=(self._items_map.small_image_size + 4) * columnspan, height=3)
                f.grid(row=row + 1, column=column, columnspan=columnspan)
            return children_column + 1
        total_columns = draw_tree(tree, 1, 0)
        for c in range(total_columns):
            self._recipe_browser_window.grid_columnconfigure(c, minsize=self._items_map.small_image_size)
        # Show parents on row 0
        parents = [RecipeItemNode(p, []) for p in self._items_map.get_parent_recipes_for(item)]
        if len(parents) > 0:
            tk.Label(self._recipe_browser_window, text='Used in:', bg=COLOR_BG, fg=COLOR_FG_GREEN, font=FONT_BIG).grid(row=0, column=0)
            for column, p in enumerate(parents):
                # Reuse the same function for convenience
                draw_tree(p, 0, column + 1)

    def _highlight_items_in_inventory(self, inventory_items: List[Tuple[int, int]], color: str) -> None:
        self._highlight_windows_to_show = list()
        for (x, y) in inventory_items:
            x_offset, y_offset, _, _ = self._image_scanner.scanner_window_size
            x += x_offset
            y += y_offset
            width = int(self._items_map.image_size[0] * 0.7)
            height = int(self._items_map.image_size[1] * 0.7)
            w = UIOverlay.create_toplevel_window(bg=color)
            w.geometry(f'{width}x{height}+{x}+{y}')
            self._highlight_windows_to_show.append(w)

    def _clear_highlights(self, _) -> None:
        for w in self._highlight_windows_to_show:
            w.destroy()

    def _create_tooltip_and_highlight(self, window, inventory_items, text) -> None:
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._tooltip_window = UIOverlay.create_toplevel_window()
        self._tooltip_window.geometry(f'+{window.winfo_x()}+{window.winfo_y() - 40}')
        tk.Label(self._tooltip_window, text=text, font=FONT_BIG, bg=COLOR_BG, fg=COLOR_FG_GREEN).pack()

        if inventory_items is not None:
            self._highlight_items_in_inventory(inventory_items, COLOR_FG_GREEN)

    def _copy_tree_items_to_clipboard(self, tree):
        if len(tree.components) > 0:
            # leave only 4 first chars of name, poe input is limited to 50 chars
            search_string = '|'.join((str(x.item)[:4] for x in tree.components))
        else:
            search_string = tree.item

        search_string = search_string.replace(' ', '\\s')

        OpenClipboard()
        EmptyClipboard()
        SetClipboardText('^('+search_string+')')
        CloseClipboard()

    def _destroy_tooltip_and_clear_highlights(self, _) -> None:
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._clear_highlights(None)

    def run(self) -> None:
        self._root.mainloop()

class Settings:
    def __init__(self, root: tk.Tk, items_map: ArchnemesisItemsMap, image_scanner, on_scan_hotkey):
        self._root = root
        self._items_map = items_map
        self._image_scanner = image_scanner
        self._on_scan_hotkey = on_scan_hotkey
        self._window = None

        self._config = ConfigParser()
        self._config_file = 'settings.ini'

        self._config.read(self._config_file)
        if 'settings' not in self._config:
            self._config.add_section('settings')
        s = self._config['settings']

        self._items_map.scale = float(s.get('image_scale', self._items_map.scale))
        self._image_scanner.confidence_threshold = float(s.get('confidence_threshold', self._image_scanner.confidence_threshold))
        b = s.get('display_inventory_items')
        self._display_inventory_items = True if b is not None and b == 'True' else False
        b = s.get('display_unavailable_recipes')
        self._display_unavailable_recipes = True if b is not None and b == 'True' else False
        b = s.get('copy_recipe_to_clipboard')
        self._copy_recipe_to_clipboard = True if b is not None and b == 'True' else False
        b = s.get('scan_hotkey')
        self._scan_hotkey = b if b is not None else ''
        self._set_scan_hotkey()
        b = s.get('run_as_overlay')
        self._run_as_overlay = True if b is None or b == 'True' else False
        b = s.get('shopping_list_mode')
        self._shopping_list_mode = False if b is None or b == 'False' else True
        b = s.get('shopping_list')
        self._shopping_list = '' if b is None else b


    def show(self) -> None:
        if self._window is not None:
            return
        self._window = tk.Toplevel()

        self._window.geometry('+100+200')
        self._window.protocol('WM_DELETE_WINDOW', self._close)

        v = tk.DoubleVar(self._window, value=self._items_map.scale)
        self._scale_entry = tk.Entry(self._window, textvariable=v)
        self._scale_entry.grid(row=1, column=0)
        tk.Button(self._window, text='Set image scale', command=self._update_scale).grid(row=1, column=1)

        v = tk.DoubleVar(self._window, value=self._image_scanner.confidence_threshold)
        self._confidence_threshold_entry = tk.Entry(self._window, textvariable=v)
        self._confidence_threshold_entry.grid(row=2, column=0)
        tk.Button(self._window, text='Set confidence threshold', command=self._update_confidence_threshold).grid(row=2, column=1)

        v = tk.StringVar(self._window, value=self._scan_hotkey)
        self._scan_hotkey_entry = tk.Entry(self._window, textvariable=v)
        self._scan_hotkey_entry.grid(row=3, column=0)
        tk.Button(self._window, text='Set scan/hide hotkey', command=self._update_scan_hotkey).grid(row=3, column=1)

        c = tk.Checkbutton(self._window, text='Display inventory items', command=self._update_display_inventory_items)
        c.grid(row=4, column=0, columnspan=2)
        if self._display_inventory_items:
            c.select()

        c = tk.Checkbutton(self._window, text='Display unavailable recipes', command=self._update_display_unavailable_recipes)
        c.grid(row=5, column=0, columnspan=2)
        if self._display_unavailable_recipes:
            c.select()

        c = tk.Checkbutton(self._window, text='Copy recipe to clipboard', command=self._update_copy_recipe_to_clipboard)
        c.grid(row=6, column=0, columnspan=2)
        if self._copy_recipe_to_clipboard:
            c.select()

        c = tk.Checkbutton(self._window, text='Run as overlay', command=self._update_run_as_overlay)
        c.grid(row=7, column=0, columnspan=2)
        if self._run_as_overlay:
            c.select()

        c = tk.Checkbutton(self._window, text='Shopping List Mode', command=self._update_shopping_list_mode)
        c.grid(row=8, column=0, columnspan=2)
        if self._shopping_list_mode:
            c.select()

        self._shopping_list_label = tk.StringVar()
        self._shopping_list_label.set("Enter a comma separated list of items")
        c = tk.Label(self._window, textvariable=self._shopping_list_label).grid(row=9, column=0, columnspan=2)

        v = tk.StringVar(self._window, value=self._shopping_list)
        self._shopping_list_entry = tk.Entry(self._window, textvariable=v)
        self._shopping_list_entry.grid(row=10, column=0)
        tk.Button(self._window, text='Set shopping list', command=self._update_shopping_list).grid(row=10, column=1)

    def _close(self) -> None:
        if self._window is not None:
            self._window.destroy()
        self._window = None

    def _save_config(self) -> None:
        self._config['settings']['image_scale'] = str(self._items_map.scale)
        self._config['settings']['confidence_threshold'] = str(self._image_scanner.confidence_threshold)
        self._config['settings']['display_inventory_items'] = str(self._display_inventory_items)
        self._config['settings']['display_unavailable_recipes'] = str(self._display_unavailable_recipes)
        self._config['settings']['copy_recipe_to_clipboard'] = str(self._copy_recipe_to_clipboard)
        self._config['settings']['scan_hotkey'] = str(self._scan_hotkey)
        self._config['settings']['run_as_overlay'] = str(self._run_as_overlay)
        self._config['settings']['shopping_list_mode'] = str(self._shopping_list_mode)
        self._config['settings']['shopping_list'] = str(self._shopping_list)
        with open(self._config_file, 'w') as f:
            self._config.write(f)

    def _update_scale(self) -> None:
        try:
            new_scale = float(self._scale_entry.get())
        except ValueError:
            print('Unable to parse image scale parameter')
            return
        self._items_map.scale = new_scale
        self._save_config()

    def _update_confidence_threshold(self) -> None:
        try:
            new_threshold = float(self._confidence_threshold_entry.get())
        except ValueError:
            print('Unable to parse confidence threshold parameter')
            return
        self._image_scanner.confidence_threshold = new_threshold
        self._save_config()

    def _update_display_inventory_items(self) -> None:
        self._display_inventory_items = not self._display_inventory_items
        self._save_config()

    def _update_display_unavailable_recipes(self) -> None:
        self._display_unavailable_recipes = not self._display_unavailable_recipes
        self._save_config()

    def _update_copy_recipe_to_clipboard(self) -> None:
        self._copy_recipe_to_clipboard = not self._copy_recipe_to_clipboard
        self._save_config()

    def _update_scan_hotkey(self) -> None:
        try:
            keyboard.remove_hotkey(self._scan_hotkey)
        except KeyError:
            # The hotkey didn't exist or self._scan_hotkey had invalid hotkey
            pass
        self._scan_hotkey = self._scan_hotkey_entry.get()
        self._set_scan_hotkey()
        self._save_config()

    def _set_scan_hotkey(self) -> None:
        if self._scan_hotkey:
            try:
                keyboard.add_hotkey(self._scan_hotkey, self._on_scan_hotkey)
            except ValueError:
                # TODO: show the error in the ui
                print('Invalid scan hotkey!')

    def _update_run_as_overlay(self) -> None:
        self._run_as_overlay = not self._run_as_overlay
        self._save_config()

    def _update_shopping_list_mode(self) -> None:
        self._shopping_list_mode = not self._shopping_list_mode
        self._save_config()

    def _update_shopping_list(self) -> None:
        shopping_list = list(map(lambda x: x.strip(), self._shopping_list_entry.get().split(",")))
        if len(shopping_list) == 0 or len(self._shopping_list_entry.get().strip()) == 0:
            self._update_shopping_list_label("Error: Must enter at least one item")
            return
        for item in shopping_list:
            if item not in self._items_map.items():
                self._update_shopping_list_label('Error: unknown item "{0}"'.format(item))
                return
        self._update_shopping_list_label("Shopping list updated!")
        self._shopping_list = ",".join(shopping_list)
        self._save_config()

    def _update_shopping_list_label(self, value) -> None:
        self._shopping_list_label.set(value)
        self._window.update_idletasks()

    def should_display_inventory_items(self) -> bool:
        return self._display_inventory_items

    def should_display_unavailable_recipes(self) -> bool:
        return self._display_unavailable_recipes

    def should_copy_recipe_to_clipboard(self) -> bool:
        return self._copy_recipe_to_clipboard

    def should_run_as_overlay(self) -> bool:
        return self._run_as_overlay

    def is_shopping_list_mode(self) -> bool:
        return self._shopping_list_mode

    def get_shopping_list(self) -> str:
        return self._shopping_list
