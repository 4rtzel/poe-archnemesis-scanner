from dataclasses import dataclass


@dataclass
class RecipeItemNode:
    item: str
    components: list


@dataclass
class PoeWindowInfo:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    client_width: int = 0
    client_height: int = 0
    title_bar_height: int = 0