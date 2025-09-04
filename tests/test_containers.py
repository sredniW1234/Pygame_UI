from pygame_ui import Application, Container, LayoutDirection, SizeMode
import pygame

pygame.init()
app = Application((600, 600), flags=pygame.RESIZABLE)
screen = app.screen

rect = Container(
    (600, 600),
    color=pygame.Color(200, 200, 200),
    padding=10,
    gap=10,
    size_mode=SizeMode.FIXED,
    layout_direction=LayoutDirection.TOP_TO_BOTTOM,
)

rect2 = Container(
    (250, 200),
    color=pygame.Color(50, 205, 30),
    padding=10,
    size_mode=SizeMode.GROWY,
    layout_direction=LayoutDirection.BOTTOM_TO_TOP,
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
    size_mode=SizeMode.GROWX,
    layout_direction=LayoutDirection.RIGHT_TO_LEFT,
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

rect5 = Container(
    (150, 150),
    color=pygame.Color(50, 205, 30),
    padding=10,
    name="Child 5",
    size_mode=SizeMode.GROWY,
)
rect51 = Container((10, 10), color=pygame.Color(250, 25, 30), name="Child 5.1")
rect52 = Container((50, 50), color=pygame.Color(250, 205, 30), name="Child 5.2")
rect5.add_child(rect51)
rect5.add_child(rect52)
rect.add_child(rect5)
# print(rect.get_child_available_space(rect4, LayoutDirection.TOP_TO_BOTTOM))

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
