from functools import total_ordering
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import pygame


class LayoutDirection(Enum):
    """
    Enum for layout directions of rectangles and UI containers.

    Attributes:
        LEFT_TO_RIGHT (int): Arrange children horizontally from left to right.
        TOP_TO_BOTTOM (int): Arrange children vertically from top to bottom.
        RIGHT_TO_LEFT (int): (Reserved for future use) Arrange children horizontally from right to left.
        BOTTOM_TO_TOP (int): (Reserved for future use) Arrange children vertically from bottom to top.
        GRID (int): (Reserved for future use) Arrange children in a grid layout.
        ABSOLUTE (int): (Reserved for future use) Children are positioned absolutely, not managed by layout.
    """

    LEFT_TO_RIGHT = 0  # Horizontal layout
    TOP_TO_BOTTOM = 1  # Vertical layout
    RIGHT_TO_LEFT = 2  # Not yet implemented
    BOTTOM_TO_TOP = 3  # Not yet implemented
    GRID = 4  # Not yet implemented
    ABSOLUTE = 5  # Not yet implemented


class SizeMode(Enum):
    """
    Enum for sizing modes of rectangles and UI elements.

    Attributes:
        FIXED (int): The element uses a fixed size as specified by its 'size' attribute, regardless of its children.
        FIT (int): The element automatically resizes to fit its children, taking into account layout direction, padding, and gap.
        GROW (int): Grows to fill available space on the layout direction
    """

    FIXED = 0  # Use the specified size, ignore children
    FIT = 1  # Resize to fit children
    GROWX = 2  # Grow to fill available space horizontally
    GROWY = 3  # Grow to fill available space vertically


@total_ordering
@dataclass
class Size:
    """A Size class for storing Sizes."""

    x: int
    y: int

    def __iter__(self):
        return iter((self.x, self.y))

    def __lt__(self, other):
        if isinstance(other, Size):
            return self.x < other.x or self.y < other.y
        else:
            raise AssertionError(f"Cannot compair {type(Size)} and {type(other)}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Size):
            return self.x == other.x and self.y == other.y
        else:
            raise AssertionError(f"Cannot compair {type(Size)} and {type(other)}")


_APPLICATION: Optional["Application"] = None  # The active application


def get_application() -> Optional["Application"]:
    """Returns the current active application if one exists"""
    return _APPLICATION


class Application:
    """Base Application that UI will sit in."""

    def __init__(
        self,
        size: tuple[int, int] = (600, 400),
        title: str = "A Pygame Application",
        flags: int = 0,
    ):
        """
        Base Application that UI will sit in.

        Args:
            size (tuple[int, int]): The size of the screen.
            title (str): The title of the application
            *flags (list[int]): A list of pygame flags for the screen
        """
        if not pygame.get_init():
            raise RuntimeError(
                "Pygame must be initialized before creating an Application."
            )

        global _APPLICATION
        _APPLICATION = self  # Set the global application instance

        self.screen: pygame.SurfaceType = pygame.display.set_mode(size, flags=flags)
        pygame.display.set_caption(title)
        self.running: bool = True

        self.ui_elements: list[UI_Element] = []

    def draw(self):
        if self.ui_elements:
            self.ui_elements[0].draw()  # Draw root


class UI_Element:
    """A base UI Element Class that all UI elements follow."""

    def __init__(
        self, size: Size | tuple[int, int], position: tuple[int, int] = (0, 0)
    ) -> None:
        """A base UI Element Class that all UI elements follow."""
        if _APPLICATION := get_application():
            # Register this element with the application
            _APPLICATION.ui_elements.append(self)
        else:
            raise RuntimeError(
                "Application not initialized. Please create an Application instance first."
            )

        # Sizing
        self.min_size: Size = Size(0, 0)
        self.max_size: Optional[Size] = None
        self.size: Size = size if isinstance(size, Size) else Size(*size)

        self.position: tuple[int, int] = (
            position  # Will most likely be automatically set if it has a parent
        )

        self.visible: bool = True

    def get_rect(self):
        return pygame.Rect(*self.position, *self.size)

    def draw(self):
        raise NotImplementedError("Subclasses must implement this function.")


class Container(UI_Element):
    """A container to hold and manipulate UI Elements"""

    def __init__(
        self,
        size: Size | tuple[int, int],
        position: tuple[int, int] = (0, 0),
        color: Optional[tuple[int, int, int]] = (255, 255, 255),
        **kwargs,
    ) -> None:
        super().__init__(size, position)

        self.color: Optional[tuple[int, int, int]] = color

        # Extras
        self.size_mode: SizeMode = kwargs.get("size_mode", SizeMode.FIT)
        self.padding: tuple[int, int, int, int] = kwargs.get(
            "padding", (0, 0, 0, 0)
        )  # (left, top, right, bottom)
        if isinstance(self.padding, int):
            self.padding = (self.padding, self.padding, self.padding, self.padding)
        self.gap: int = kwargs.get("gap", 0)  # Gap between children
        self.layout_direction = kwargs.get(
            "layout_direction", LayoutDirection.LEFT_TO_RIGHT
        )
        self.border_radius: tuple[int, int, int, int] = kwargs.get(
            "border_radius", (0, 0, 0, 0)
        )
        if isinstance(self.border_radius, int):
            self.border_radius = (
                self.border_radius,
                self.border_radius,
                self.border_radius,
                self.border_radius,
            )

        self.children: list[UI_Element] = []

    def _visible_children(self) -> list[UI_Element]:
        return [child for child in self.children if child.visible]

    def calculate_size(self):
        """Calculates the sizing for this container based on children."""
        visible_children = self._visible_children()

        if self.size_mode == SizeMode.FIT:
            total_size = Size(0, 0)  # Set the total_size to 0

            # Loop through all visible children
            for child in visible_children:
                if self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                    total_size.x += child.size.x
                    total_size.y = max(total_size.y, child.size.y)
                elif self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                    total_size.y += child.size.y
                    total_size.x = max(total_size.x, child.size.x)

            if self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                total_size.x += self.gap * (len(visible_children) - 1)
            elif self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                total_size.y += self.gap * (len(visible_children) - 1)

            # Add padding to total width and height
            total_size.x += self.padding[0] + self.padding[2]
            total_size.y += self.padding[1] + self.padding[3]

            self.size = total_size

        # Clamp size to min and max
        if self.size < self.min_size:
            self.size = self.min_size
        elif self.max_size and self.size > self.max_size:
            self.size = self.max_size

    def calculate_position(self):
        """Calculates the position of each child in this container"""

        # Start the offset with some padding
        # Using Size class for easy comparison and explicit variable access
        offset = Size(self.padding[0], self.padding[1])
        for element in self._visible_children():
            # Set the elements position
            element.position = (
                self.get_rect().x + offset.x,
                self.get_rect().y + offset.y,
            )

            # Adjust offset based off
            if self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                offset.x += element.size.x
                offset.x += self.gap * 1 if element != self.children[-1] else 0
            elif self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                offset.y += element.size.y
                offset.y += self.gap * 1 if element != self.children[-1] else 0

    def add_child(self, child: UI_Element):
        self.children.append(child)
        self.calculate_size()
        self.calculate_position()

    def draw(self):
        application = get_application()
        if application is None:
            raise RuntimeError(
                "Application not initialized. Please create an Application instance first."
            )

        if not self.visible:
            return

        screen = application.screen

        if self.color:
            pygame.draw.rect(screen, self.color, self.get_rect())
        for child in self.children:
            child.draw()
