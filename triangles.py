# pylint: disable=C0301,I1101,C0116,E1101
import math
import os
import pygame as pg
import pygame.gfxdraw

CURRENT_DIR = os.path.dirname('triangles.py')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BODY_COLOUR = (102, 126, 170)
TITLE_COLOUR = (85, 99, 135)
HIGHLIGHT_COLOUR = (189, 206, 224)
LOWLIGHT_COLOUR = (175, 176, 205)
SHADOW_COLOUR = (154, 156, 193)
BACKGROUND_COLOUR = (23, 24, 38)

SOHCAHTOAH = {math.asin: ['opposite', 'hypotenuse'],
              math.acos: ['adjacent', 'hypotenuse'],
              math.atan: ['opposite', 'adjacent']}

SCREEN_W = 1200
SCREEN_H = 800

pg.init()

LABEL_FONT = pg.font.Font(os.path.join(CURRENT_DIR, 'Exo2-Medium.ttf'), 16)


class Label(pg.sprite.Sprite):
    def __init__(self, display_value):
        super().__init__()
        self.image = LABEL_FONT.render(str(display_value), True, LOWLIGHT_COLOUR)


class TriangleSprite(pg.sprite.Sprite):
    def __init__(self, triangle):
        super().__init__()
        self.triangle = triangle
        self.image = pg.Surface((int(self.triangle.sides['adjacent']), int(self.triangle.sides['opposite'])), pg.SRCALPHA, 32)

        sides = self.triangle.sides
        angles = self.triangle.angles
        self.labels = {'opp': Label(sides['opposite']),
                       'adj': Label(sides['adjacent']),
                       'hyp': Label(sides['hypotenuse']),
                       'adj_angle': Label(angles['opposite']),
                       'opp_angle': Label(angles['adjacent']),
                       }
        self.label_image = pg.Surface((self.image.get_width() + 75, self.image.get_height() + 75), pg.SRCALPHA, 32)

    def update(self):
        self.draw()
        self.draw_labels()

    def get_label_image_pos(self):
        return ((SCREEN_W / 2 - self.label_image.get_width() / 2), (SCREEN_H / 2 - self.label_image.get_height() / 2))

    def draw_labels(self):
        screen = self.label_image
        screen.blit(self.labels['opp'].image, (0, screen.get_height() / 2))
        screen.blit(self.labels['adj'].image, ((screen.get_width() / 2) - (self.labels['adj'].image.get_width() / 2), (screen.get_height() - 35)))
        screen.blit(self.labels['hyp'].image, ((screen.get_width() / 2 - (self.labels['hyp'].image.get_width() / 2), screen.get_height() / 2.5)))

    def draw(self):
        # draw triangle; draws at right angle, then opposite angle, then adjacent angle coordinates
        pg.gfxdraw.aatrigon(self.image, 0, int(self.triangle.sides['opposite']), 0, 0,
                            int(self.triangle.sides['adjacent']), int(self.triangle.sides['opposite']), BACKGROUND_COLOUR)

        # fill triangle; same draw order as above
        pg.gfxdraw.filled_trigon(self.image, 0, int(self.triangle.sides['opposite']), 0, 0,
                                 int(self.triangle.sides['adjacent']), int(self.triangle.sides['opposite']), TITLE_COLOUR)

        # draw adjacent angle arc; draws a circle at adjacent point coordinates using radius 1/6th the length of the adjacent side
        pg.gfxdraw.aacircle(self.image, int(self.triangle.sides['adjacent']), int(self.triangle.sides['opposite']), int(self.triangle.sides['adjacent'] / 6), BACKGROUND_COLOUR)

        # draw opposite angle arc; same as above but for the opposite point/side
        pg.gfxdraw.aacircle(self.image, 0, 0, int(self.triangle.sides['opposite'] / 6), BACKGROUND_COLOUR)

        # draw right angle box; draws a square the size of box_size at right anglte point, coordinates offset by -1
        box_size = int(min(self.triangle.sides['opposite'] / 4.5, self.triangle.sides['adjacent'] / 4.5, 30))  # = shortest side / 4.5 or 48, whichever is smaller
        pg.gfxdraw.rectangle(self.image, (-1, int(self.triangle.sides['opposite'] - (box_size - 1)), box_size, box_size), BACKGROUND_COLOUR)


class RightAngleTriangle():
    max_degrees = 180

    def __init__(self, opp=None, adj=None, hyp=None):
        super().__init__()
        self.sides = {'opposite': opp,
                      'adjacent': adj,
                      'hypotenuse': hyp}

        self.check_sides()

        self.angles = {'adjacent': self.find_adj_angle(),
                       'opposite': None,
                       'right-angle': 90}

        self.complete_all()
        self.area = (self.sides['opposite'] * self.sides['adjacent']) / 2
        self.perimeter = round(sum(x for x in self.sides.values()), 2)
        self.sprite = TriangleSprite(self)

    def complete_all(self):
        self.angles.update({'opposite': self.find_opp_angle()})
        self.check_total_degrees()
        self.find_missing_side()

    def get_position(self):
        return ((SCREEN_W / 2 - self.sides['adjacent'] / 2), (SCREEN_H / 2 - self.sides['opposite'] / 2))

    def check_total_degrees(self):
        total = sum([x for x in self.angles.values()])
        if total != self.max_degrees:
            raise ValueError(f'Angles add up to {total}. Review trigonometry.')

    def check_sides(self):
        given_values = len([x for x in self.sides.values() if x])
        if given_values != 2:
            raise AttributeError(f'Incorrect number of attributes provided ({given_values}). Please provide 2 attributes only.')

    def find_adj_angle(self):
        given_sides = dict([[key, value] for key, value in self.sides.items() if value])

        for key, value in SOHCAHTOAH.items():
            if value == list(given_sides.keys()):
                return round(math.degrees(key(given_sides[value[0]] / given_sides[value[1]])), 2)  # given_sides[value[ints]] = names of sides of triangle = length of side (dict value); key = relevant trigonometric function

    def find_opp_angle(self):
        return self.angles['right-angle'] - self.angles['adjacent']

    def find_missing_side(self):
        if not self.sides['opposite']:
            self.sides.update({'opposite': round(math.sqrt((self.sides['hypotenuse'] ** 2) - (self.sides['adjacent'] ** 2)), 2)})
        elif not self.sides['adjacent']:
            self.sides.update({'adjacent': round(math.sqrt((self.sides['hypotenuse'] ** 2) - (self.sides['opposite'] ** 2)), 2)})
        elif not self.sides['hypotenuse']:
            self.sides.update({'hypotenuse': round(math.sqrt((self.sides['opposite'] ** 2) + (self.sides['adjacent'] ** 2)), 2)})


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_W, SCREEN_H))
        self.done = False
        self.clock = pg.time.Clock()
        self.triangle = RightAngleTriangle(opp=400, adj=400)

        for key, value in self.triangle.__dict__.items():
            print({key: value})

    def main_loop(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.screen.fill(BACKGROUND_COLOUR)
            self.screen.blit(self.triangle.sprite.image, self.triangle.get_position())
            self.screen.blit(self.triangle.sprite.label_image, self.triangle.sprite.get_label_image_pos())
            self.triangle.sprite.update()
            pg.display.update()
            self.clock.tick(30)


g = Game()
if __name__ == '__main__':
    pg.init()
    g.main_loop()
