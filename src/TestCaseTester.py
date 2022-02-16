from ImageScanner import ImageScanner
from ArchnemesisItemsMap import ArchnemesisItemsMap

from poe_arch_scanner import get_poe_image_info

tests = [
    (
        "1",
        [ "800x600", "1024x768", "1280x1024", "1600x1200", "1920x1080", "2560x1440" ],
        [
            # 0
            [
                "Innocence-Touched", "Brine King-Touched",
                "Treant Horde", "Rejuvenating",
                "Treant Horde", "Tukohama-Touched",
                "Incendiary", "Consecrator"
            ],
            # 1
            [
                "Malediction", "Berserker",
                "Vampiric", "Bloodletter",
                "Bloodletter", "Dynamo",
                "Steel-Infused", "Soul Conduit"
            ],
            # 2
            [
                "Steel-Infused", "Soul Conduit", 
                "Gargantuan", "Consecrator",
                "Opulent", "Bonebreaker",
                "Hasted", "Hasted"
            ],
            # 3
            [
                "Arakaali-Touched", "Storm Strider",
                "Executioner", "Flameweaver",
                "Bombardier", "Permafrost",
                "Overcharged", "Hasted"
            ],
            # 4
            [
                "Sentinel", "Steel-Infused",
                "Soul Conduit", "Flameweaver",
                "Juggernaut", "Juggernaut",
                "Overcharged", "Hasted"
            ],
            # 5
            [
                "Stormweaver", "Bonebreaker",
                "Frost Strider", "Juggernaut",
                "Juggernaut", "Juggernaut",
                "Assassin", "Soul Conduit"
            ],
            # 6
            [
                "Mirror Image", "Storm Strider",
                "Storm Strider", "Invulnerable",
                "Corpse Detonator", "Drought Bringer",
                "Flame Strider", "Flame Strider"
            ],
            # 7
            [
                "Necromancer", "Mirror Image",
                "Mirror Image", "Corrupter", 
                "Arcane Buffer", "Arcane Buffer",
                "Arcane Buffer", "Permafrost"
            ]
        ]
    ),
	
    (
        "2",
        [ "1280x1024", "1920x1080" ],
        [
            # 0
            [
                "Innocence-Touched", "Brine King-Touched",
                "Juggernaut", "Stormweaver",
                "Mirror Image", "Assassin",
                "Toxic", "Entangler"
            ],
            # 1
            [
                "Abberath-Touched", "Soul Conduit",
                None, "Abberath-Touched",
                "Steel-Infused", "Permafrost",
                "Abberath-Touched", "Arcane Buffer"
            ],
            # 2
            [
                "Heralding Minions", "Assassin",
                "Soul Conduit", "Gargantuan",
                "Bloodletter", "Arcane Buffer",
                "Steel-Infused", "Corrupter"
            ],
            # 3
            [
                "Overcharged", "Juggernaut",
                "Ice Prison", "Juggernaut",
                "Bonebreaker", "Bombardier",
                "Crystal-Skinned", "Vampiric"
            ],
            # 4
            [
                "Rejuvenating", "Assassin",
                "Treant Horde", "Steel-Infused",
                "Sentinel", "Crystal-Skinned",
                "Gargantuan", "Chaosweaver"
            ],
            # 5
            [
                "Steel-Infused", "Frenzied",
                "Executioner", "Corpse Detonator",
                "Sentinel", None,
                "Sentinel", "Toxic"
            ],
            # 6
            [
                "Arcane Buffer", "Trickster",
                "Corpse Detonator", "Toxic",
                "Chaosweaver", "Sentinel",
                "Assassin", "Assassin"
            ],
            # 7
            [
                "Overcharged", "Consecrator",
                None, "Opulent",
                "Rejuvenating", "Permafrost",
                "Opulent", "Corpse Detonator"
            ]
        ]
	)
]

def check_results(found, expected):
    for x in range(8):
        for y in range(8):
            founditem = found[x][y]
            expecteditem = expected[x][y]

            if founditem is None and expecteditem is not None:
                print(f'Diff: {x}x{y} found None expected {expecteditem}')
            elif founditem is not None and expecteditem is None:
                print(f'Diff: {x}x{y} found {founditem[0]} expected None')
            elif founditem is not None and expecteditem is not None and expecteditem != founditem[0]:
                print(f'!!!Diff: {x}x{y} found {founditem[0]} expected {expecteditem}')


if __name__ == "__main__":
    items_map = ArchnemesisItemsMap()

    for testname, resolutions, inventory in tests:
        for resolution in resolutions:
            image_info = get_poe_image_info(f'test/{testname}_{resolution}.png')
            print(f'Scanning {testname}_{resolution}')
            scanner = ImageScanner(image_info, items_map)
            check_results(scanner.scanList(), inventory)
            print('\n\n')