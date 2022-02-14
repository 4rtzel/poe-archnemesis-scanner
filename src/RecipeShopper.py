from copy import deepcopy
from typing import Dict, List, Tuple
from ArchnemesisItemsMap import ArchnemesisItemsMap

class RecipeShopper:
  def __init__(self, item_map: ArchnemesisItemsMap):
    self._item_map = item_map

  def get_missing_items(self, desired_items: List[str], current_inventory: Dict[str, List[Tuple[int, int]]]):
    missing_items = list()
    # clone the inventory, because we're going to take things out of it
    # as owned items are identified in case dupes are needed
    working_inventory = deepcopy(current_inventory)

    # identify which items are not already owned,
    # and remove owned items from the working inventory
    for item in desired_items:
      if not is_item_owned(working_inventory, item):
        missing_items.append(item)
      else:
        remove_item_from_inventory(working_inventory, item)

    # recursively call this function passing the ingredients for missing items
    complex_missing_items = list(item for item in missing_items if len(self._item_map.get_subtree_for(item).components) > 0)
    if len(complex_missing_items) > 0:
      complex_item_ingredients = list()
      for item in complex_missing_items:
        complex_item_ingredients.extend(self._item_map._get_item_components(item))
      nested_missing_items = self.get_missing_items(complex_item_ingredients, working_inventory)
      missing_items.extend(nested_missing_items)

    return missing_items

def is_item_owned(inventory: Dict[str, List[Tuple[int, int]]], item: str):
  return item in inventory.keys() and len(inventory[item]) > 0

def remove_item_from_inventory(inventory:  Dict[str, List[Tuple[int, int]]], item: str):
  return inventory[item].pop()
