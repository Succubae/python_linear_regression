import random
import operator
from multiprocessing.pool import Pool

import numpy as np
import track
from car import Car
from shapely.geometry import Point
import neural_network
from trigonometrie import get_point_in_zone_x


def get_random_posneg_value():
    v = random.random() * 0.1
    v = -v if random.random() < 50 else v
    return v


class AlgoGen:
    def __init__(self, population, population_size, selection_size, lucky_few_size, mutation_chance,
                 mutation_rate, to_regenerate, polygon_zones) -> None:
        super().__init__()
        self.population = population
        self.population_size = population_size
        self.selection_size = selection_size
        self.lucky_few_size = lucky_few_size
        self.mutation_chance = mutation_chance
        self.mutation_rate = mutation_rate
        self.to_breed = population_size - selection_size - lucky_few_size - 1 - to_regenerate
        self.to_regenerate = to_regenerate
        self.polygons = polygon_zones

    def get_ordered_population_by_fitness(self, to_print):
        val = {}
        for i in range(len(self.population)):
            val[self.population[i]] = self.calc_fitness(self.population[i])
        val = sorted(val.items(), key=operator.itemgetter(1), reverse=True)
        print([x[1] for x in val]) if to_print else ''
        return val

    def selection(self, population: [Car]):
        select = [population[0]]
        last_fitness_val = -1
        selected = 0
        for p in population:
            if selected >= self.selection_size -1:
                break
            if p.fitness_value != last_fitness_val:
                last_fitness_val = p.fitness_value
                select.append(p)
                selected += 1
        # select = population[:self.selection_size]
        luckies = []
        for i in range(self.lucky_few_size):
            luckies.append(random.choice(population))
        select.extend(luckies)
        return select

    def breed_child(self, p1: Car, p2: Car):
        child = Car(p1.start_point, p1.track)
        for i in range(len(p1.theta_1)):
            for j in range(len(p1.theta_1[i])):
                child.theta_1[i][j] = p1.theta_1[i][j] if random.random() * 100 < 50 else p2.theta_1[i][j]
        for i in range(len(p1.theta_2)):
           for j in range(len(p1.theta_2[i])):
                child.theta_2[i][j] = p1.theta_2[i][j] if random.random() * 100 < 50 else p2.theta_2[i][j]
        for i in range(len(p1.theta_3)):
            for j in range(len(p1.theta_3[i])):
                child.theta_3[i][j] = p1.theta_3[i][j] if random.random() * 100 < 50 else p2.theta_3[i][j]
        return child

    def cross_breed(self, population: [Car]):
        children = []
        print(f'to_breed: ({self.population_size - len(self.population)})' )
        for i in range(self.population_size - len(self.population)):
            # s
            children.append(self.breed_child(population[i % len(population)], population[abs(int(len(population) - i - 1)) % len(population)]))
        population.extend(children)
        return population

    def mutate(self, car: Car):
        mut = 0
        no_mut = 0
        for ti in range(len(car.theta_1)):
            for tj in range(len(car.theta_1[ti])):
                if random.random() * 100 < self.mutation_rate:
                    mut += 1
                    car.theta_1[ti][tj] += np.random.randn() / 2.
                else:
                    no_mut += 1
        for ti in range(len(car.theta_2)):
            for tj in range(len(car.theta_2[ti])):
                if random.random() * 100 < self.mutation_rate:
                    mut += 1
                    car.theta_2[ti][tj] += np.random.randn() / 2.
                else:
                    no_mut += 1
        for ti in range(len(car.theta_3)):
            for tj in range(len(car.theta_3[ti])):
                if random.random() * 100 < self.mutation_rate:
                    mut += 1
                    car.theta_3[ti][tj] += np.random.randn() / 2.
                else:
                    no_mut += 1
        print(f'MUTATED {mut} TIMES OVER {mut + no_mut}!')
        return car

    def mutate_population(self, population: [Car]):
        for i in range(len(population)):
            if random.random() * 100 < self.mutation_chance:
                population[i] = self.mutate(population[i])

    @staticmethod
    def move_car(car):
        if car.active:
            best_move = neural_network.neural_network(car.get_sensors_value(), car.theta_1, car.theta_2, car.theta_3) + 1
            car.order(best_move)

    def move_population(self):
        [self.move_car(car) for car in self.population]
        self.population = [x[0] for x in self.get_ordered_population_by_fitness(False)]

    def do_one_cycle(self):
        # print('Cycle')
        print(f'Population size for selection = {len(self.population)}')
        self.population = self.selection(self.population)
        print(f'Population size for cross_breed = {len(self.population)}')
        self.population = self.cross_breed(self.population)
        print(f'Population size for mutate_population = {len(self.population)}')
        self.mutate_population(self.population[int(self.selection_size / 2):])
        self.population = [x[0] for x in self.get_ordered_population_by_fitness(True)]
        print(f'Population size after cycle = {len(self.population)}')

    def calc_fitness(self, car: Car):
        if not car.active:
            return car.fitness_value
        car_in_zone = get_point_in_zone_x(self.polygons, car.position)
        if car_in_zone is None or car_in_zone < car.max_zone_entered:
            print(f"U-turns are BAD. You were in zone {car.max_zone_entered} but returned to {car_in_zone}")
            car.active = False
            car.fitness_value = -1
            car.max_zone_entered = car_in_zone
            return -1
        car.max_zone_entered = car_in_zone
        # return car_in_zone #* 400 + (car.position[0] * 1.3) + car.position[1]
        car.fitness_value = car_in_zone * (float(car.move_done) / float(car.default_max_move_allowed))
        return car.fitness_value #* 400 + (car.position[0] * 1.3) + car.position[1]

    def count_active_car(self):
        cnt = 0
        for c in self.population:
            if c.active:
                cnt += 1
        return cnt
