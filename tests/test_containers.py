from pygame_ui import Application, Container, LayoutDirection
import pygame

pygame.init()
app = Application((800, 600))
screen = app.screen

rect = Container(
    (50, 50),
    color=(255, 0, 255),
    padding=2,
    gap=2,
    layout_direction=LayoutDirection.TOP_TO_BOTTOM,
)
rect2 = Container((20, 20), color=(0, 0, 0))
rect3 = Container((20, 30), color=(0, 0, 0))
rect.add_child(rect2)
rect.add_child(rect3)

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
