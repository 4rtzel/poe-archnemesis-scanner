from dataclasses import dataclass
from tkinter import Image
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
    src: Image = None