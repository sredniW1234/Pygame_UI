from pygame_ui import (
    Application,
    Container,
    LayoutDirection,
    SizeMode,
    MultiLineLabel,
    Label,
    Text,
)
import pygame

pygame.init()
app = Application((800, 600), flags=pygame.RESIZABLE)
screen = app.screen

rect = Container(
    (500, 500),
    color=pygame.Color(200, 200, 200),
    padding=10,
    gap=10,
    layout_direction=LayoutDirection.TOP_TO_BOTTOM,
    size_mode=SizeMode.FIXED,
    # justify=Justify.CENTER,
)
text = Text("This is a standard Text!")
rect.add_child(text)

label = Label("This is an ordinary single-line label!")
rect.add_child(label)

multiLable = MultiLineLabel(
    "This an Multi-Line Label with auto word wrapping!",
    name="My Label",
    # font=pygame.font.SysFont("arial", 15),
    padding=10,
    bg_color=(255, 0, 0),
    border_color=(0, 0, 0),
)
rect.add_child(multiLable)

running = True
while running:
    events = pygame.event.get()
    # app.update(events)
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))
    app.draw()
    pygame.display.flip()
pygame.quit()
