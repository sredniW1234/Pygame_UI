from functools import total_ordering
from dataclasses import dataclass
from typing import Optional, Literal
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


class Justify(Enum):
    """
    Enum for justifying positioning children elements.

    Attributes:
        NORMAL (int): The default justification for positioning children.
        CENTER (int): Position children in the center.
    """

    NORMAL = 0
    CENTER = 1


class SizeMode(Enum):
    """
    Enum for sizing modes of rectangles and UI elements.

    Attributes:
        FIXED (int): The element uses a fixed size as specified by its 'size' attribute, regardless of its children.
        FIT (int): The element automatically resizes to fit its children, taking into account layout direction, padding, and gap.
        GROWX (int): Grows to fill available space on the X axis.
        GROWY (int): Grows to fill available space on the Y axis.
    """

    FIXED = 0  # Use the specified size, ignore children
    FIT = 1  # Resize to fit children
    GROWX = 2  # Grow to fill available space horizontally
    GROWY = 3  # Grow to fill available space vertically


@total_ordering
@dataclass
class Size:
    """
    Represents a 2D size with x (width) and y (height) attributes.

    Attributes:
        x (int): Width component.
        y (int): Height component.
    """

    x: int
    y: int

    def __iter__(self):
        """Allows unpacking or iteration over Size as (x, y)."""
        return iter((self.x, self.y))

    def __lt__(self, other):
        """Compares if this Size is less than another Size (by either dimension)."""
        if isinstance(other, Size):
            return self.x < other.x or self.y < other.y
        else:
            raise AssertionError(f"Cannot compare {type(Size)} and {type(other)}")

    def __eq__(self, other: object) -> bool:
        """Checks equality with another Size object."""
        if isinstance(other, Size):
            return self.x == other.x and self.y == other.y
        else:
            raise AssertionError(f"Cannot compare {type(Size)} and {type(other)}")


_APPLICATION: Optional["Application"] = None  # Stores the active application instance


def get_application() -> Optional["Application"]:
    """
    Returns the current active application instance, if one exists.
    """
    return _APPLICATION


class Application:
    """
    Main application class for the UI framework. Manages the window and root UI elements.
    """

    def __init__(
        self,
        size: tuple[int, int] = (600, 400),
        title: str = "A Pygame Application",
        flags: int = 0,
    ):
        """
        Initializes the Application window and sets up the root UI element list.

        Args:
            size (tuple[int, int]): The size of the window.
            title (str): The window title.
            flags (int): Pygame display flags.
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

        self.ui_elements: list[UIElement] = []

    def draw(self):
        """
        Draws the root UI element (if any) to the application window.
        """
        if self.ui_elements:
            self.ui_elements[0].draw(self.screen)  # Draw root


class UIElement:
    """
    Base class for all UI elements. Handles sizing, positioning, and registration with the application.
    """

    def __init__(
        self, size: Size | tuple[int, int], position: tuple[int, int] = (0, 0)
    ) -> None:
        """
        Initializes a UI element, registers it with the application, and sets up sizing and position.

        Args:
            size (Size | tuple[int, int]): Size of the element.
            position (tuple[int, int]): Initial position of the element.
        """
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
        self.surface: pygame.SurfaceType = pygame.Surface(
            tuple(self.size), pygame.SRCALPHA
        )

        self.parent: Optional["UIElement"] = None

        self.visible: bool = True

    def update_surface(self):
        """
        Updates the internal pygame surface to match the current size.
        """
        self.surface = pygame.Surface(tuple(self.size), pygame.SRCALPHA)

    def draw(self, surface: pygame.SurfaceType):
        """
        Draws the element to the given surface. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this function.")


class Container(UIElement):
    """
    Container class for holding and managing child UI elements, with layout and sizing logic.
    """

    def __init__(
        self,
        size: Size | tuple[int, int],
        position: tuple[int, int] = (0, 0),
        color: pygame.Color | tuple = pygame.Color(255, 255, 255),
        **kwargs,
    ) -> None:
        """
        A container to hold and manipulate UI Elements

        Args:
            size (Size | tuple[int, int]): The size of the container
            position (tuple[int, int]): The position of the container
            color (pygame.Color | tuple): The background color of the container
            **kwargs: Additional keyword arguments for customization
                - size_mode (SizeMode): The sizing mode of the container (default: SizeMode.FIT)
                - layout_direction (LayoutDirection): The layout direction of children (default: LayoutDirection.LEFT_TO_RIGHT)
                - padding (int | tuple[int, int, int, int]): Padding around the container's content (default: 0)
                - gap (int): Gap between children (default: 0)
                - border_color (pygame.Color): Color of the container's border (default: same as background color)
                - border_radius (int | tuple[int, int, int, int]): Border radius for rounded corners (default: 0)
                - justify (Justify): The justification for each child
        """
        super().__init__(size, position)

        self.color: pygame.Color = (
            color if isinstance(color, pygame.Color) else pygame.Color(*color)
        )

        # Extras
        self.size_mode: SizeMode = kwargs.get("size_mode", SizeMode.FIT)
        self.layout_direction = kwargs.get(
            "layout_direction", LayoutDirection.LEFT_TO_RIGHT
        )
        self.justify: Justify = kwargs.get("justify", Justify.NORMAL)

        # Positioning
        self.padding: tuple[int, int, int, int] = kwargs.get(
            "padding", (0, 0, 0, 0)
        )  # (left, top, right, bottom)
        if isinstance(self.padding, int):
            self.padding = (self.padding, self.padding, self.padding, self.padding)
        self.gap: int = kwargs.get("gap", 0)  # Gap between children

        # Border
        self.border_color: pygame.Color = kwargs.get("border_color", color)
        self.border_radius: tuple[int, int, int, int] = kwargs.get(
            "border_radius", (0, 0, 0, 0)
        )
        self.name: str = kwargs.get("name", "Container")
        if isinstance(self.border_radius, int):
            self.border_radius = (
                self.border_radius,
                self.border_radius,
                self.border_radius,
                self.border_radius,
            )

        self.children: list[UIElement] = []

    def _visible_children(self) -> list[UIElement]:
        """
        Returns a list of children that are currently visible.
        """
        return [child for child in self.children if child.visible]

    def get_child_available_space(
        self,
        child: UIElement,
        direction: Literal[
            LayoutDirection.LEFT_TO_RIGHT, LayoutDirection.TOP_TO_BOTTOM
        ],
    ) -> Size:
        # Calculate available space for a child element, considering padding and layout direction
        available_space = Size(
            self.size.x - self.padding[0] - self.padding[2],
            self.size.y - self.padding[1] - self.padding[3],
        )
        if direction == LayoutDirection.LEFT_TO_RIGHT:
            # Children ordered horizontally
            if self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                for child in self._visible_children():
                    available_space.x -= child.size.x
                # Account for gap
                available_space.x -= self.gap * (len(self.children) - 1)
            elif self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                available_space.x -= child.size.x
            available_space.y -= child.size.y
        elif direction == LayoutDirection.TOP_TO_BOTTOM:
            # Children ordered vertically
            if self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                for child in self._visible_children():
                    available_space.y -= child.size.y
                # Account for gap
                available_space.y -= self.gap * (len(self.children) - 1)
            elif self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                available_space.y -= child.size.y
            available_space.x -= child.size.x
        return available_space

    def _fit(self, visible_children):
        """
        Calculates the total size required to fit all visible children, including gap and padding.
        """
        total_size = Size(0, 0)
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
        return total_size

    def _calculate_size(self) -> None:
        print("Calculating size for:", self.name)
        """
        Calculates the size of this container based on its children and sizing mode.
        """
        visible_children = self._visible_children()
        if self.size_mode == SizeMode.FIT and visible_children:
            self.size = self._fit(visible_children)
        elif self.size_mode == SizeMode.GROWX:
            # Grow to fill available space on X axis
            if self.parent and isinstance(self.parent, Container):
                available_space = self.parent.get_child_available_space(
                    self, LayoutDirection.LEFT_TO_RIGHT
                )
                self.size.x += available_space.x // (len(visible_children) - 1)
                self.size.y = self._fit(visible_children).y  # Fit Y
        elif self.size_mode == SizeMode.GROWY:
            # Grow to fill available space on Y axis
            if self.parent and isinstance(self.parent, Container):
                available_space = self.parent.get_child_available_space(
                    self, LayoutDirection.TOP_TO_BOTTOM
                )
                self.size.y += available_space.y // (len(visible_children) - 1)
                self.size.x = self._fit(visible_children).x  # Fit X
        # Clamp size to min and max
        if self.size < self.min_size:
            self.size = self.min_size
        elif self.max_size and self.size > self.max_size:
            self.size = self.max_size

    def _calculate_position(self):
        """
        Calculates and sets the position of each child in this container based on layout direction and padding.
        """
        print("Calculating position for:", self.name)
        offset = Size(self.padding[0], self.padding[1])
        for element in self._visible_children():
            # Set the element's position
            element.position = (
                offset.x,
                offset.y,
            )
            # Adjust offset based on layout direction
            if self.layout_direction == LayoutDirection.LEFT_TO_RIGHT:
                offset.x += element.size.x
                offset.x += self.gap * 1 if element != self.children[-1] else 0
            elif self.layout_direction == LayoutDirection.TOP_TO_BOTTOM:
                offset.y += element.size.y
                offset.y += self.gap * 1 if element != self.children[-1] else 0

    def update_surface(self):
        """
        Updates the surface for this container and all child containers.
        """
        for child in self._visible_children():
            if isinstance(child, Container):
                child.update_surface()
        return super().update_surface()

    def add_child(self, child: UIElement):
        """
        Adds a child UI element to this container and recalculates layout.
        """
        print(
            "Added child:",
            child.name if isinstance(child, Container) else "",
            "to",
            self.name,
        )
        self.children.append(child)
        child.parent = self
        self.recalculate()
        print()

    def recalculate(self):
        """
        Recalculates the size and position of all children, updating layout and surfaces.
        """
        self._calculate_size()
        growable_children = []
        for child in self._visible_children():
            if isinstance(child, Container):
                if child.size_mode in (SizeMode.GROWX, SizeMode.GROWY):
                    growable_children.append(child)
                    continue
                child._calculate_size()
        # Calculate growable children after all other children have been sized
        for child in growable_children:
            child._calculate_size()
        self._calculate_position()
        for child in self._visible_children():
            if isinstance(child, Container):
                child._calculate_position()
        self.update_surface()

    def draw(self, surface: pygame.SurfaceType):
        """
        Draws the container and its children to the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the container on.
        """
        application = get_application()
        if application is None:
            raise RuntimeError(
                "Application not initialized. Please create an Application instance first."
            )
        if not self.visible:
            return
        # Draw border/background
        self.surface.fill(self.border_color)
        center_surf = self.surface.subsurface(
            pygame.Rect(
                self.padding[0],  # left
                self.padding[1],  # top
                self.size.x - self.padding[2] * 2,  # right
                self.size.y - self.padding[3] * 2,  # bottom
            )
        )
        center_surf.fill(self.color)
        # Draw children
        for child in self.children:
            child.draw(self.surface)
        surface.blit(self.surface, self.position)

    def __repr__(self) -> str:
        """
        Returns a string representation of the container for debugging.
        """
        return f"<Container size={self.size} position={self.position} children={len(self.children)}>"
