from pygame_ui import Application, Container, LayoutDirection, SizeMode, Justify
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

rect2 = Container(
    (250, 200),
    color=pygame.Color(50, 205, 30),
    padding=10,
    # size_mode=SizeMode.GROWY,
    name="Child 2",
)
rect21 = Container((100, 100), color=pygame.Color(250, 25, 30), name="Child 2.1")
rect22 = Container((50, 50), color=pygame.Color(250, 205, 30), name="Child 2.2")
rect2.add_child(rect21)
rect2.add_child(rect22)
rect.add_child(rect2)

rect3 = Container(
    (200, 200),
    color=pygame.Color(50, 205, 30),
    padding=10,
    name="Child 3",
    size_mode=SizeMode.GROWY,
)
rect31 = Container((100, 100), color=pygame.Color(250, 25, 30), name="Child 3.1")
rect32 = Container((50, 50), color=pygame.Color(250, 205, 30), name="Child 3.2")
rect3.add_child(rect31)
rect3.add_child(rect32)
rect.add_child(rect3)

rect4 = Container(
    (150, 150),
    color=pygame.Color(50, 205, 30),
    padding=10,
    name="Child 4",
)
rect41 = Container((100, 100), color=pygame.Color(250, 25, 30), name="Child 4.1")
rect42 = Container((50, 50), color=pygame.Color(250, 205, 30), name="Child 4.2")
rect4.add_child(rect41)
rect4.add_child(rect42)
rect.add_child(rect4)

print(rect.get_child_available_space(rect4, LayoutDirection.TOP_TO_BOTTOM))

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
