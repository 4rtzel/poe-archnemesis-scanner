import sys
from tkinter import E
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
	),
    (
        "3",
        [ "1024x768", "1280x720", "1280x800", "1280x960", "1360x768", "1366x768", "1440x900", "1536x864", "1600x900", "1680x1050", "1920x1200", "2048x1152", "2048x1536", "2560x1080", "3440x1440", "3840x1080", "3840x2160" ],
        [
            [ "Innocence-Touched", "Brine King-Touched", "Juggernaut", "Storm Strider", "Mirror Image", "Assassin", "Treant Horde", "Entangler" ],
            [ "Abberath-Touched", "Soul Conduit", "Malediction", "Abberath-Touched", "Hasted", "Permafrost", "Abberath-Touched", "Arcane Buffer" ],
            [ "Heralding Minions", "Assassin", "Juggernaut", "Gargantuan", "Bloodletter", "Arcane Buffer", "Steel-Infused", "Corrupter" ],
            [ "Opulent", "Juggernaut", "Ice Prison", "Flameweaver", "Magma Barrier", "Necromancer", "Crystal-Skinned", "Vampiric" ],
            [ "Rejuvenating", "Assassin", "Treant Horde", "Steel-Infused", "Sentinel", "Crystal-Skinned", "Gargantuan", "Chaosweaver" ],
            [ "Steel-Infused", "Frenzied", "Executioner", "Corpse Detonator", "Sentinel", "Bombardier", "Sentinel", "Toxic" ],
            [ "Bloodletter", "Trickster", "Corpse Detonator", "Toxic", "Chaosweaver", "Sentinel", "Assassin", "Assassin" ],
            [ "Overcharged", "Consecrator", "Consecrator", "Opulent", "Rejuvenating", "Permafrost", "Opulent", "Corpse Detonator" ]
        ]
    ),
    (
        "4",
        [ "1920x900", "1920x1032", "1920x1080" ],
        [
            ["Echoist", "Abberath-Touched", "Arakaali-Touched", "Tukohama-Touched", "Brine King-Touched", "Brine King-Touched", "Brine King-Touched", "Abberath-Touched"],
            ["Deadeye", "Bonebreaker", "Shakari-Touched", "Frost Strider", "Treant Horde", "Corrupter", "Hexer", "Rejuvenating"],
            ["Hexer", "Permafrost", "Berserker", "Mirror Image", "Opulent", "Frost Strider", "Mana Siphoner", "Juggernaut"],
            ["Evocationist", "Magma Barrier", "Lunaris-Touched", "Drought Bringer", "Mirror Image", "Deadeye", "Chaosweaver", "Rejuvenating"],
            ["Arakaali-Touched", "Treant Horde", "Soul Eater", "Overcharged", "Storm Strider", "Overcharged", "Flame Strider", "Consecrator"],
            ["Gargantuan", "Arcane Buffer", "Frost Strider", "Overcharged", "Gargantuan", "Treant Horde", "Soul Conduit", "Stormweaver"],
            ["Drought Bringer", "Bloodletter", "Heralding Minions", "Treant Horde", "Incendiary", "Empowered Elements", "Empowered Minions", "Deadeye"],
            ["Rejuvenating", "Heralding Minions", "Heralding Minions", "Permafrost", "Flameweaver", "Empowered Elements", "Empowered Elements", "Stormweaver"]
        ]
    )
]

def check_results(testname, found, expected) -> int:
    diffs = 8 * 8
    for x in range(8):
        for y in range(8):
            founditem = found[x][y]
            expecteditem = expected[x][y]

            if founditem is None and expecteditem is not None:
                print(f'{testname}: {x}x{y} found None expected {expecteditem}')
            elif founditem is not None and expecteditem is None:
                print(f'{testname}: {x}x{y} found {founditem[0]} expected None')
            elif founditem is not None and expecteditem is not None and expecteditem != founditem[0]:
                print(f'{testname}: {x}x{y} found {founditem[0]} expected {expecteditem} {founditem[1]}')
                if expecteditem in founditem[3]:
                    print(f'  found item was {founditem[3][expecteditem]}')
            else:
                diffs = diffs - 1

    return diffs


if __name__ == "__main__":
    items_map = ArchnemesisItemsMap()

    testing = [ x[0] for x in sys.argv[1:] if x ]
    if (len(testing) == 0):
        testing = [ x[0] for x in tests ]

    for testname, resolutions, inventory in [ x for x in tests if x[0] in testing ]:
        for resolution in resolutions:
            image_info = get_poe_image_info(f'test/{testname}_{resolution}.png')
            scanner = ImageScanner(image_info, items_map)
            check_results(f'{testname}_{resolution}', scanner.scanList(), inventory)