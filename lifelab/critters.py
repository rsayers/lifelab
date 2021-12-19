from enum import Enum
import pygame
import random
from pygame.math import Vector2, Vector3
from pygame.constants import VIDEOEXPOSE
import math
from genpw import pronounceable_passwd as make_name

class AppetiteType(Enum):
    CARNIVORE = 0
    HERBIVORE = 1
    OMNIVORE = 2
    SOLAR = 3


class EatingStyle(Enum):
    PREDATOR = 0
    SCAVENGER = 1
    GRAZER = 2  # Only used for Herbivores


class Kingdom(Enum):
    PLANT = 0
    ANIMAL = 1


class Phenotype:
    def __init__(self):
        
        self.speed = 2.0
        self.calories = 1000
        self.calories_per_tick = 1
        self.color = (255, 0, 0)
        self.breed_cooldown = 400
        self.detect_radius = 100

        # On creation, a random float is generated, if the value is > ( 1 - mut_prob ), a mutation happens
        self.mutation_probability = 0.0

        self.appetite: AppetiteType = AppetiteType.OMNIVORE
        self.appetite_float = self.appetite.value

        self.eating_style: EatingStyle = EatingStyle.GRAZER
        self.eating_style_float = self.eating_style.value

        self.kingdom: Kingdom = Kingdom.PLANT
        self.kingdom_float = self.kingdom.value
        self.digestion_efficiency = 1.0

        self.cross_traits = [
            "speed",
            "calories",
            "calories_per_tick",
            "color",
            "mutation_probability",
            "appetite",
            "eating_style",
            "digestion_efficiency",
            "breed_cooldown"
        ]

        self.slow_traits = ["kingdom", "eating_style", "eating_style"]

    def radius(self):
        return int(self.calories / 100)

    def randomize(self):
        for trait_name in self.cross_traits:
            try:
                v = getattr(self, trait_name)
                v = random.uniform(v/2, v + random.uniform(-0.1, 0.1))
                setattr(self, trait_name, v)
                
            except:
                pass

        self.color = [random.randint(64,255) for x in range(3)]

        self.kingdom = Kingdom[random.choice(list(Kingdom.__members__))]
        self.kingdom_float = self.kingdom.value

        if self.kingdom == Kingdom.PLANT:
            self.appetite = AppetiteType.SOLAR
            self.color = [random.randint(0,64), 255, random.randint(0,64)]
        else:
            self.appetite = AppetiteType(random.randint(0,2))
        self.appetite_float = self.appetite.value

        if self.appetite == AppetiteType.HERBIVORE:
            self.eating_style = EatingStyle.GRAZER
        else:
            self.eating_style = EatingStyle(random.randint(0,1))
        self.eating_style_float = self.eating_style.value

    def cross(self, other):

        # t is a shorthand fn to give me a random "parent" from which to choose
        # this lets traits 
        t = lambda: random.choice([self, other])

        new_traits = Phenotype()
        for trait_name in self.cross_traits:
            setattr(new_traits, trait_name, getattr(t(), trait_name))

        for trait_name in self.slow_traits:
            setattr(new_traits, trait_name, getattr(self, trait_name))
            setattr(new_traits, f"{trait_name}_float", getattr(t(), f"{trait_name}_float"))
            

        return new_traits


class Critter:
    def __init__(self, world):
        self.world = world
        self.pos = Vector2(0, 0)
        self.dir = Vector2(0, 0)
        self.decay = 20
        self.traits: Phenotype = Phenotype()
        self.calories = self.traits.calories
        self.breed_cooldown = 0
        self._name = make_name(8)

    @property
    def name(self):
        if self.traits.kingdom == Kingdom.PLANT:
            return "A Plant"
        return self._name

    def move_to(self, x, y):
        w = self.world.window.get_width() - self.traits.radius()
        h = self.world.window.get_height() - self.traits.radius()

        if x > w:
            x = w
        if x < 0:
            x = self.traits.radius()

        if y < 0:
            y = self.traits.radius()

        if y > h:
            y = y

        self.pos = Vector2(x, y)

    def place_randomly(self):
        self.pos = Vector2(self.world.window.get_width() * random.random(), self.world.window.get_height() * random.random())

    def is_dead(self):
        return self.calories < 0

    def can_eat(self, other):
        other: Critter = other
        if self.traits.kingdom == Kingdom.PLANT:
            return False

        if self.traits.appetite in [AppetiteType.HERBIVORE, AppetiteType.OMNIVORE] and other.traits.kingdom == Kingdom.PLANT:
            return True

        if self.traits.appetite in [AppetiteType.OMNIVORE, AppetiteType.CARNIVORE]:
            if self.traits.eating_style == EatingStyle.SCAVENGER and other.is_dead():
                return True

            if self.traits.eating_style == EatingStyle.PREDATOR and other.traits.kingdom == Kingdom.ANIMAL:
                return True

    def can_breed(self, other):
        if len(self.world.critters) > self.world.LIMIT:
            return False
        other: Critter = other
        checks = [
            self.traits.kingdom == other.traits.kingdom,
            self.traits.eating_style == other.traits.eating_style,
            self.breed_cooldown < 0,
            other.breed_cooldown < 0,
            self.pos.distance_to(other.pos) < self.traits.calories + other.traits.calories
        ]
        return all(checks)
            
    def breed(self, other):

        child = Critter(self.world)
        other: Critter = other
        child.traits = self.traits.cross(other.traits)
        child.breed_cooldown = child.traits.breed_cooldown * 2

        self.breed_cooldown = self.traits.breed_cooldown * 2
        other.breed_cooldown = other.traits.breed_cooldown * 2
        child.pos = self.pos
        child.dir = self.dir * -1
        print(f"{self.name} and {other.name} have created {child.name} at {child.pos}")
        alive = [c for c in self.world.critters if not c.is_dead()]
        print(f"There are now {len(self.world.critters)} and {len(alive)} living")
        self.world.critters.append(child)

    def move(self):

        self.dir += Vector2(random.uniform(-1,1), random.uniform(-1,1))
        #self.move_towards(Vector2(400, 300))
        self.dir = Vector2(
            min(max(-self.traits.speed, self.dir.x), self.traits.speed),
            min(max(-self.traits.speed, self.dir.y), self.traits.speed)
        )

        self.pos += self.dir

        self.pos = Vector2(
            min(max(0, self.pos.x), self.world.window.get_width()),
            min(max(0, self.pos.y), self.world.window.get_height())
        )

    def move_towards(self, point: Vector2):
        t = self.world.clock.get_time()
        angle = self.pos.angle_to(point)
        move_vec = Vector2(math.sin(math.radians(angle)) / t, math.cos(math.radians(angle)) / t)
        
        self.dir += move_vec

    def eat(self, other):
        self.calories += self.traits.digestion_efficiency
        other.calories += self.traits.digestion_efficiency

    def tick(self):

        if self.traits.appetite == AppetiteType.SOLAR:
            self.calories = min(self.calories+2, self.traits.calories)
        else:
            self.calories -= self.traits.calories_per_tick

        if self.is_dead():
            self.decay -= 1
            return

        if self.breed_cooldown > 0:
            self.breed_cooldown -= 1

        if self.traits.kingdom != Kingdom.PLANT:
            self.move()
       
        for critter in self.world.critters:
            if critter.name == self.name:
                print(f"{critter.name} cant do anything to themselves")
                continue

            if critter.is_dead():
                if critter.decay < 0:
                    del critter
                    continue
            if self.can_breed(critter):
                self.breed_cooldown = self.traits.breed_cooldown
                self.breed(critter)
                break

            if self.can_eat(critter):
                self.eat(critter)

    def draw(self):
        c = self.traits.color
        if self.is_dead():
            c = [0, 0, 0]

        if self.traits.kingdom == Kingdom.PLANT:
            pygame.draw.rect(self.world.window, c, pygame.Rect(self.pos.x, self.pos.y, self.traits.radius()*2, self.traits.radius()*2))
        else:    
            pygame.draw.circle(
                self.world.window, c, self.pos, self.traits.radius()
            )
