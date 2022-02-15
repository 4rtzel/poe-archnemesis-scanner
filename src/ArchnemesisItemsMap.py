from typing import List
from PIL import ImageTk, Image
import cv2
import numpy as np

from DataClasses import RecipeItemNode


class ArchnemesisItemsMap:
    """
    Holds the information about all archnemesis items, recipes, images and map them together
    """
    def __init__(self):
        # Put everything into the list so we could maintain the display order
        self._arch_items = [
            ('Kitava-Touched', ['Tukohama-Touched', 'Abberath-Touched', 'Corrupter', 'Corpse Detonator']),
            ('Innocence-Touched', ['Lunaris-Touched', 'Solaris-Touched', 'Mirror Image', 'Mana Siphoner']),
            ('Shakari-Touched', ['Entangler', 'Soul Eater', 'Drought Bringer']),
            ('Abberath-Touched', ['Flame Strider', 'Frenzied', 'Rejuvenating']),
            ('Tukohama-Touched', ['Bonebreaker', 'Executioner', 'Magma Barrier']),
            ('Brine King-Touched', ['Ice Prison', 'Storm Strider', 'Heralding Minions']),
            ('Arakaali-Touched', ['Corpse Detonator', 'Entangler', 'Assassin']),
            ('Solaris-Touched', ['Invulnerable', 'Magma Barrier', 'Empowered Minions']),
            ('Lunaris-Touched', ['Invulnerable', 'Frost Strider', 'Empowered Minions']),
            ('Effigy', ['Hexer', 'Malediction', 'Corrupter']),
            ('Empowered Elements', ['Evocationist', 'Steel-Infused', 'Chaosweaver']),
            ('Crystal-Skinned', ['Permafrost', 'Rejuvenating', 'Berserker']),
            ('Invulnerable', ['Sentinel', 'Juggernaut', 'Consecrator']),
            ('Corrupter', ['Bloodletter', 'Chaosweaver']),
            ('Mana Siphoner', ['Consecrator', 'Dynamo']),
            ('Storm Strider', ['Stormweaver', 'Hasted']),
            ('Mirror Image', ['Echoist', 'Soul Conduit']),
            ('Magma Barrier', ['Incendiary', 'Bonebreaker']),
            ('Evocationist', ['Flameweaver', 'Frostweaver', 'Stormweaver']),
            ('Corpse Detonator', ['Necromancer', 'Incendiary']),
            ('Flame Strider', ['Flameweaver', 'Hasted']),
            ('Soul Eater', ['Soul Conduit', 'Necromancer', 'Gargantuan']),
            ('Ice Prison', ['Permafrost', 'Sentinel']),
            ('Frost Strider', ['Frostweaver', 'Hasted']),
            ('Treant Horde', ['Toxic', 'Sentinel', 'Steel-Infused']),
            ('Temporal Bubble', ['Juggernaut', 'Hexer', 'Arcane Buffer']),
            ('Entangler', ['Toxic', 'Bloodletter']),
            ('Drought Bringer', ['Malediction', 'Deadeye']),
            ('Hexer', ['Chaosweaver', 'Echoist']),
            ('Executioner', ['Frenzied', 'Berserker']),
            ('Rejuvenating', ['Gargantuan', 'Vampiric']),
            ('Necromancer', ['Bombardier', 'Overcharged']),
            ('Trickster', ['Overcharged', 'Assassin', 'Echoist']),
            ('Assassin', ['Deadeye', 'Vampiric']),
            ('Empowered Minions', ['Necromancer', 'Executioner', 'Gargantuan']),
            ('Heralding Minions', ['Dynamo', 'Arcane Buffer']),
            ('Arcane Buffer', []),
            ('Berserker', []),
            ('Bloodletter', []),
            ('Bombardier', []),
            ('Bonebreaker', []),
            ('Chaosweaver', []),
            ('Consecrator', []),
            ('Deadeye', []),
            ('Dynamo', []),
            ('Echoist', []),
            ('Flameweaver', []),
            ('Frenzied', []),
            ('Frostweaver', []),
            ('Gargantuan', []),
            ('Hasted', []),
            ('Incendiary', []),
            ('Juggernaut', []),
            ('Malediction', []),
            ('Opulent', []),
            ('Overcharged', []),
            ('Permafrost', []),
            ('Sentinel', []),
            ('Soul Conduit', []),
            ('Steel-Infused', []),
            ('Stormweaver', []),
            ('Toxic', []),
            ('Vampiric', []),
            ('Trash', [])
        ]

        self._multiplier_override = {
            "Malediction": 0.6
        }
        self._images = dict()
        self._small_image_size = 30
        self._crop_ratio = (0.05, 0.05, 0.05, 0.2)

    def _update_images(self, image_size):
        # To prevent borders from stopping the scan, crop a bit
        least_mask = 0
        for item, _ in self._arch_items:
            self._images[item] = dict()
            image = self._load_image(item, image_size)
            self._image_size = image.size
            self._images[item]['scan-image'] = list(self._create_scan_image(image))
            least_mask = max(least_mask, self._images[item]['scan-image'][2])
            # Convert the image to Tk image because we're going to display it
            self._images[item]['display-image'] = ImageTk.PhotoImage(image=image)
            image = image.resize((self._small_image_size, self._small_image_size))
            self._images[item]['display-small-image'] = ImageTk.PhotoImage(image=image)
        
        for item in self._images:
            value = self._images[item]
            value['scan-image'][2] = self._multiplier_override[item] if item in self._multiplier_override else value['scan-image'][2] / least_mask
            print(item, value['scan-image'][2])

    def _load_image(self, item: str, image_size: float):
        image = Image.open(f'pictures/{item}.png')
        # Scale the image according to the input parameter
        return image.resize((image_size, image_size))

    def _create_scan_image(self, image):
        width, height = image.size
        ratiol, ratiou, ratior, ratiod = self._crop_ratio
        scan_image = image.crop((
            int(width * ratiol),
            int(height * ratiou),
            int(width * (1 - ratior)),
            int(height * (1 - ratiod))
        ))
        # Remove alpha channel and replace it with predefined background color
        background = Image.new('RGBA', scan_image.size, (2, 1, 28, 255))
        image_without_alpha = Image.alpha_composite(background, scan_image)
        scan_image_array = np.asarray(scan_image)
        alpha_channel = scan_image_array.T[3]
        for x in alpha_channel:
            for y in range(x.size):
                x[y] = 255 if x[y] > 50 else 0
        scan_image_array.T[0] = scan_image_array.T[1] = scan_image_array.T[2] = scan_image_array.T[3]
        scan_mask = cv2.cvtColor(scan_image_array, cv2.COLOR_RGBA2BGR)
        scan_template = cv2.cvtColor(np.array(image_without_alpha), cv2.COLOR_RGB2BGR)

        # Image.fromarray(cv2.cvtColor(scan_template, cv2.COLOR_BGR2RGB), 'RGB').save(f'test/{item}.png')
        # Image.fromarray(scan_mask, 'RGB').save(f'test/{item}_mask.png')

        nonzero_mask = np.sum(np.count_nonzero(np.count_nonzero(scan_mask == 255, axis = 2) == 3, axis = 0))

        # Crop the image to help with scanning
        return (scan_template, scan_mask, nonzero_mask)

    def get_scan_image(self, item):
        return self._images[item]['scan-image']

    def get_display_image(self, item):
        return self._images[item]['display-image']

    def get_display_small_image(self, item):
        return self._images[item]['display-small-image']

    def items(self):
        for item, _ in self._arch_items:
            yield item

    def recipes(self):
        for item, recipe in self._arch_items:
            if recipe:
                yield (item, recipe)

    def get_subtree_for(self, item: str):
        tree = RecipeItemNode(item, [])
        nodes = [tree]
        while len(nodes) > 0:
            node = nodes.pop(0)
            children = self._get_item_components(node.item)
            if len(children) > 0:
                node.components = [RecipeItemNode(c, []) for c in children]
                nodes.extend(node.components)
        return tree

    def get_parent_recipes_for(self, item: str) -> List[str]:
        parents = list()
        for parent, components in self._arch_items:
            if item in components:
                parents.append(parent)
        return parents

    def _get_item_components(self, item) -> List[str]:
        return next(l for x, l in self._arch_items if x == item)

    @property
    def small_image_size(self):
        return self._small_image_size

    @property
    def image_size(self):
        return self._image_size

    @image_size.setter
    def image_size(self, image_size: float) -> None:
        self._update_images(image_size)

    @property
    def small_image_size(self):
        return self._small_image_size
