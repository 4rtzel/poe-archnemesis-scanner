from dataclasses import dataclass
from typing import Any, List


@dataclass
class RecipeItemNode:
    item: str
    components: List[Any]


@dataclass
class PoeWindowInfo:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    client_width: int = 0
    client_height: int = 0
    title_bar_height: int = 0