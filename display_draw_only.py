import pygame
import track
import trigonometrie
from algo_gen import AlgoGen
from car import *


class DisplayOnlyDraw:

    def __init__(self, track) -> None:
        super().__init__()
        # DISPLAY VALUES
        self.debug = False

        # DIPLAY INFO
        self.w = 800
        self.h = 1200
        self.bgcolor = (0xf1, 0xf2, 0xf3)
        self.fgcolor = (0, 0, 0)
        self.greencolor = (0, 0xff, 0)
        self.redcolor = (0xff, 0, 0)
        self.delay = 20
        self.key_delay = 20
        self.key_interval = 20
        self.screen = pygame.display.set_mode((self.w + 1, self.h + 1))
        self.clock = pygame.time.Clock()
        self.track = track
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Arial', 20)

    def main_loop(self):
        running = True

        pos = ''
        pos1 = ()
        i = 30

        compute = True

        while running:
            # print('while running')

            for event in pygame.event.get():
                # print('if for event')
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    print(f'event.type={event.type}')
                    print(f'event.key={event.key}')
                    if event.key == pygame.K_q:
                        running = False
                    # self.draw_all(self.track, self.cars)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos1 = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                    pos = f'line{i} = [({pygame.mouse.get_pos()[0]}, {pygame.mouse.get_pos()[1]}), '
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos2 = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                    self.track.append([pos1, pos2])
                    # self.draw_all(self.track, self.cars)
                    print(f'{pos}({pygame.mouse.get_pos()[0]}, {pygame.mouse.get_pos()[1]})]')
                    i += 1

            self.draw_all(self.track, [])
            # sleep
            self.clock.tick(self.delay)

    def draw_all(self, lines, cars: [Car]):
        self.screen.fill(self.bgcolor)
        self.draw_theta_table()
        for line in lines:
            pygame.draw.aaline(self.screen, self.fgcolor, line[0], line[1])
        for car in cars:
            self.draw_car(car.position, car.rotation, car.active)
        self.draw_text_info()
        self.draw_zones_limits()
        self.draw_zones_number()
        pygame.display.flip()

    def draw_car(self, position_vector, rotation, active):
        car_length = 50
        car_width = 25
        corner_top_left = [position_vector[0] - int(car_width / 2), position_vector[1] - int(car_length / 2)]
        corner_top_right = [position_vector[0] + int(car_width / 2), position_vector[1] - int(car_length / 2)]
        corner_bottom_right = [position_vector[0] + int(car_width / 2), position_vector[1] + int(car_length / 2)]
        corner_bottom_left = [position_vector[0] - int(car_width / 2), position_vector[1] + int(car_length / 2)]
        center = [position_vector[0], position_vector[1]]
        corners = sp.array([
            corner_top_left,
            corner_top_right,
            corner_bottom_left,
            corner_bottom_right,
        ])
        lines = Car.rotate_2d(
            corners,
            center,
            rotation
        )
        corner_top_left = (int(lines[0][0]), int(lines[0][1]))
        corner_top_right = (int(lines[1][0]), int(lines[1][1]))
        corner_bottom_right = (int(lines[2][0]), int(lines[2][1]))
        corner_bottom_left = (int(lines[3][0]), int(lines[3][1]))

        if active:
            pygame.draw.lines(self.screen, self.greencolor, True, [corner_top_left, corner_top_right, corner_bottom_left, corner_bottom_right])
        else:
            pygame.draw.lines(self.screen, self.redcolor, True, [corner_top_left, corner_top_right, corner_bottom_left, corner_bottom_right])

    def draw_zones_limits(self):
        if not self.debug:
            return
        for l in track.get_zones_limits():
            self.draw_line(l)

    def draw_line(self, line):
        pygame.draw.aaline(self.screen, self.fgcolor, line[0], line[1])

    def draw_text_info(self):
        pass
        # textsurface = self.myfont.render( f'Generation {self.gen} | Mutation Change {self.algo_gen.mutation_chance} | Mutation Rate {self.algo_gen.mutation_rate}', True, self.fgcolor)
        # self.screen.blit(textsurface, (150, 25))

    def draw_zones_number(self):
        if not self.debug:
            return
        i = 0
        for p in track.get_polygon_zones():
            textsurface = self.myfont.render(f'{i}', True, self.fgcolor)
            point = p.centroid
            self.screen.blit(textsurface, (point.coords[0][0], point.coords[0][1]))
            i += 1

    def draw_theta_table(self):
        self.draw_line([(0, 800), (800, 800)])
        # cell_width = int(760 / (input_layer_size + 1))
        # cell_height = int(360 / (first_hidden_layer_size))
        # for i in range(input_layer_size + 1):
        #     for j in range(first_hidden_layer_size):
        #         pos_x_start = 20 + (i * cell_width)
        #         pos_y_start = 820 + (j * cell_height)
        #         pygame.draw.rect(self.screen, self.fgcolor, pygame.Rect((pos_x_start, pos_y_start, cell_width, cell_height)), 1)
        #         if self.algo_gen.population[0].theta_1[j][i] > 0:
        #             textsurface = self.myfont.render(f'{self.algo_gen.population[0].theta_1[j][i]:1.3f}', True, self.greencolor)
        #         else:
        #             textsurface = self.myfont.render(f'{self.algo_gen.population[0].theta_1[j][i]:1.3f}', True, self.redcolor)
        #         self.screen.blit(textsurface, (pos_x_start + int(cell_width / 2) - 5, pos_y_start + int(cell_height / 2)))

