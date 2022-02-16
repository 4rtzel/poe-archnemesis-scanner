import unittest
import tkinter as tk

from ArchnemesisItemsMap import ArchnemesisItemsMap
from RecipeShopper import RecipeShopper

class TestStringMethods(unittest.TestCase):
    def test_owned_items(self):
      item_map = ArchnemesisItemsMap(1)
      self._shopper = RecipeShopper(item_map)
      desired_items = ["Effigy", "Corrupter"]
      inventory = {
        "Effigy": [ [1, 2] ],
        "Corrupter": [ [1, 2] ]
        }

      missing_items = self._shopper.get_missing_items(desired_items, inventory)
      self.assertListEqual(missing_items, [])

    def test_missing_simple_items(self):
      item_map = ArchnemesisItemsMap(1)
      self._shopper = RecipeShopper(item_map)
      desired_items = ["Effigy", "Berserker"]
      inventory = {
        "Effigy": [ [1, 2] ],
        }

      missing_items = self._shopper.get_missing_items(desired_items, inventory)
      self.assertListEqual(missing_items, ["Berserker"])

    def test_missing_complex_items(self):
      item_map = ArchnemesisItemsMap(1)
      self._shopper = RecipeShopper(item_map)
      desired_items = ["Effigy"]
      inventory = {}

      missing_items = self._shopper.get_missing_items(desired_items, inventory)
      self.assertListEqual(missing_items, ['Effigy', 'Hexer', 'Malediction', 'Corrupter', 'Chaosweaver', 'Echoist', 'Bloodletter', 'Chaosweaver'])

    def test_missing_complex_items_with_partial_inventory(self):
      item_map = ArchnemesisItemsMap(1)
      self._shopper = RecipeShopper(item_map)
      desired_items = ["Effigy"]
      inventory = {
        "Corrupter": [ [1, 2] ],
        "Echoist": [ [1, 2] ]
      }

      missing_items = self._shopper.get_missing_items(desired_items, inventory)
      self.assertListEqual(missing_items, ['Effigy', 'Hexer', 'Malediction', 'Chaosweaver'])

    def test_missing_requiring_duplicates_with_partial_inventory(self):
      item_map = ArchnemesisItemsMap(1)
      self._shopper = RecipeShopper(item_map)
      desired_items = ["Assassin", "Assassin"]
      inventory = {
        "Deadeye": [ [1, 2], [1, 2] ],
        "Vampiric": [ [1, 2] ]
      }

      missing_items = self._shopper.get_missing_items(desired_items, inventory)
      self.assertListEqual(missing_items, ['Assassin', 'Assassin', 'Vampiric'])

if __name__ == '__main__':
  root = tk.Tk()
  unittest.main()
