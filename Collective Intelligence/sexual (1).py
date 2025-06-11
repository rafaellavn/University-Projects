import random
from enum import Enum, auto
from vi import Agent, Simulation, Config, Window, HeadlessSimulation, Matrix
from vi.config import Config, dataclass, deserialize
from typing import Optional
import polars as pl
from random import choice
from polars import col, lit
from pygame import Vector2
import pygame as pg
from random import randrange
import numpy as np


FRAME_DURATION = 5000

RABBIT_COUNT = 30
FOX_COUNT = 30
GRASS_COUNT = 90

RABBIT_LIMIT = 600
FOX_LIMIT = 600

FOX_REPRODUCTION_P = 0.7
RABBIT_REPRODUCTION_P = 0.8

FOX_SEX_TIMER = 360
RABBIT_SEX_TIMER = 35


FOX_ENERGY = 4.0
RABBIT_ENERGY = 1.2
FOX_ENERGY_LOSS = 0.0085
RABBIT_ENERGY_LOSS = 0.004
ENERGY_FROM_GRASS = 0.75


RABBIT_TO_REPRODUCE = 0.8
RABBIT_AGE_TO_REPRODUCE = 240
FOX_TO_REPRODUCE = 3.0
FOX_AGE_TO_REPRODUCE = 720
FOX_TO_EAT = 4.0


FOX_EATING_P = 0.6

GRASS_TIMER_SPRING = 120
GRASS_TIMER_WINTER = 80
GRASS_IMAGE = 0

MAX_VEL = 3

SPRING_BOOST = random.uniform(1,1.1)
WINTER_NERF = random.uniform(0.9,1)
SEASONAL_TIMER = 240

TOTAL_RABBITS_EATEN = 0
TOTAL_FOX_DIED = 0
TOTAL_RABBITS_STARVED = 0
TOTAL_FOX_CHILDREN = 0
TOTAL_RABBIT_CHILDREN = 0

TOTAL_RABBITS_EATEN_SPRING = 0
TOTAL_FOX_DIED_SPRING = 0
TOTAL_RABBITS_STARVED_SPRING = 0
TOTAL_FOX_CHILDREN_SPRING = 0
TOTAL_RABBIT_CHILDREN_SPRING = 0

TOTAL_RABBITS_EATEN_WINTER = 0
TOTAL_FOX_DIED_WINTER = 0
TOTAL_RABBITS_STARVED_WINTER = 0
TOTAL_FOX_CHILDREN_WINTER = 0
TOTAL_RABBIT_CHILDREN_WINTER = 0


SEASON = 0


GRASS_VOTE = 0

config = Config(
    radius=19,
    visualise_chunks=True,
    window=Window.square(1500)
)


class Grass(Agent):
    timer: int = 0
    s_timer: int = 0
    eaten_counter: int = 0
    s_timer_limit: int = SEASONAL_TIMER
    imagee: int = 0

    def on_spawn(self):
        self.freeze_movement()

    def rabbit_check(self):

        rabbit = (
            self.in_proximity_accuracy()
            .without_distance()
            .filter_kind(Rabbit)
            .first()
        )

        return rabbit

    def update(self):
        global GRASS_IMAGE
        global SEASON
        global GRASS_VOTE
        global SPRING_BOOST
        global WINTER_NERF

        self.on_spawn()

        if self.rabbit_check() is not None:
            GRASS_IMAGE = 1
            self.change_image(GRASS_IMAGE)
            self.imagee = 1
            self.eaten_counter += 1

        if GRASS_IMAGE == 1:
            self.timer += 1
        
        self.s_timer += 1

        if SEASON == 0 and self.timer >= GRASS_TIMER_SPRING:
            GRASS_IMAGE = 0
            self.change_image(GRASS_IMAGE)
            self.timer = 0
            self.imagee = 0

        if SEASON == 1 and self.timer >= GRASS_TIMER_WINTER:
            GRASS_IMAGE = 0
            self.change_image(GRASS_IMAGE)
            self.timer = 0
            self.imagee = 0

        if self.s_timer >= self.s_timer_limit:
            GRASS_VOTE +=1
            self.s_timer = 0
        
        if GRASS_VOTE == GRASS_COUNT:
            if SEASON == 0:
                SEASON = 1
                SPRING_BOOST = random.uniform(1,1.15)
                WINTER_NERF = random.uniform (0.85, 1)
            else:
                SEASON = 0
                SPRING_BOOST = random.uniform(1,1.15)
                WINTER_NERF = random.uniform (0.85, 1)
            GRASS_COUNT

        self.save_data('Type', 'Grass')
        self.save_data('Energy', 0.0)
        self.save_data('Eating times', self.eaten_counter)
        self.save_data('Number of Children', 0.0)
        self.save_data('Season', SEASON)
        self.save_data('Age', 0)
        self.save_data('Boost', SPRING_BOOST)
        self.save_data('Nerf', WINTER_NERF)

    
class Rabbit(Agent):

    global RABBIT_COUNT, FOX_COUNT, TOTAL_RABBITS_STARVED, TOTAL_RABBIT_CHILDREN
    #energy_count: float = RABBIT_ENERGY
    sex_timer: int = 0
    kill_counter: int = 0
    children_counter: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age = random.randint(180, 300)  # Age of the rabbit, every time step corresponds to 12 hours
        self.gender = random.randint(0,1)
        self.energy_count = random.uniform(1, 1.4)

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()

        # Define the weight of the random component
        randomWeight = 0.2

        # Continue in the same direction
        self.move = self.move.normalize() * 3 #velocity!

        # Add a small random component
        randomNoise = Vector2(random.uniform(-1,1), random.uniform(-1,1)) * randomWeight
        self.move += randomNoise

        # Get nearby rabbits and foxes
        nearby_rabbits = list(self.in_proximity_accuracy().filter_kind(Rabbit))
        nearby_foxes = list(self.in_proximity_accuracy().filter_kind(Fox))
        nearby_grass = list(self.in_proximity_accuracy().filter_kind(Grass))

        if nearby_rabbits:
            # Calculate the average position of nearby rabbits
            avg_pos = sum((rabbit.pos for rabbit, distance in nearby_rabbits), Vector2()) / len(nearby_rabbits)

            # Calculate the cohesion force (towards the average position)
            cohesionForce = (avg_pos - self.pos).normalize() * 0.5 

            # Calculate the separation force (away from too close rabbits)
            separationForce = sum(((self.pos - rabbit.pos + Vector2(random.uniform(-1,1), random.uniform(-1,1)) * 0.01).normalize() / (distance + 0.01) for rabbit, distance in nearby_rabbits if distance < 0.5), Vector2())

            # Add the cohesion and separation forces to the movement
            self.move += cohesionForce + separationForce

        if nearby_foxes:
            # Calculate the average position of nearby foxes
            avg_pos = sum((fox.pos for fox, distance in nearby_foxes), Vector2()) / len(nearby_foxes)

            # Calculate the avoidance force (away from the average position of foxes)
            avoidanceForce = (self.pos - avg_pos).normalize() * 0.5

            # Add the avoidance force to the movement
            self.move += avoidanceForce
        
        if nearby_grass:
            # Pick the nearest rabbit to chase
            nearest_grass = choice(nearby_grass)  # x[1] is assumed to be the distance

            # Calculate the direction towards the chosen rabbit
            chase_force = (nearest_grass[0].pos - self.pos).normalize()

            # Add the chase force to the movement
            self.move += chase_force

        self.pos += self.move

        # Limit the speed
        if self.move.length() > 5:
            self.move = self.move.normalize() * 5

        # Update the position
        self.pos += self.move
    
    def not_hiding(self):
        if self.on_site() == False:
            return True

    def should_reproduce(self):
        p_rep = random.uniform(0, 1)
        if SEASON == 0:
            mod = SPRING_BOOST
            mod2 = WINTER_NERF
        else:
            mod = WINTER_NERF
            mod2 = SPRING_BOOST
        
        if p_rep < RABBIT_REPRODUCTION_P*mod and self.energy_count > (RABBIT_TO_REPRODUCE*(mod2)) and RABBIT_COUNT <= RABBIT_LIMIT and self.age > RABBIT_AGE_TO_REPRODUCE and self.sex_timer == 0:
            return True

    def do_they_reproduce_check(self):
        rabbit = (
            self.in_proximity_accuracy()
            .without_distance()
            .filter_kind(Rabbit)
            .first()
        )

        return rabbit


    def update(self):
        global RABBIT_COUNT, GRASS_IMAGE, TOTAL_RABBITS_STARVED, TOTAL_RABBIT_CHILDREN, TOTAL_RABBIT_CHILDREN_SPRING, TOTAL_RABBIT_CHILDREN_WINTER, TOTAL_RABBITS_STARVED_SPRING, TOTAL_RABBITS_STARVED_WINTER

        self.age += 1
        
        if SEASON == 0:
            mod = SPRING_BOOST
            mod2 = WINTER_NERF
        else:
            mod = WINTER_NERF
            mod2 = SPRING_BOOST

        self.energy_count -= RABBIT_ENERGY_LOSS*mod2

        grass = (
            self.in_proximity_accuracy()
                .without_distance()
                .filter_kind(Grass)
                .first()

        )

        if grass is not None and grass.imagee == 0:
            self.energy_count += (ENERGY_FROM_GRASS*mod)
            self.kill_counter += 1

        if self.energy_count <= 0:
            self.kill()
            RABBIT_COUNT -= 1
            TOTAL_RABBITS_STARVED += 1 
            if SEASON == 0:
                TOTAL_RABBITS_STARVED_SPRING +=1 
            else:
                TOTAL_RABBITS_STARVED_WINTER +=1 

            

        if self.should_reproduce() and self.do_they_reproduce_check() is not None and self.do_they_reproduce_check().sex_timer == 0 and self.do_they_reproduce_check().age > RABBIT_AGE_TO_REPRODUCE and self.gender != self.do_they_reproduce_check().gender:
            num_children = random.randint(1, 12)  # Generate a random number of children between 1 and 12
            for _ in range(num_children):
                self.reproduce().age = 0
                self.energy_count /= 1.2
            self.sex_timer = RABBIT_SEX_TIMER*(mod2)
            self.do_they_reproduce_check().sex_timer = RABBIT_SEX_TIMER*(mod2)
            RABBIT_COUNT += num_children
            self.children_counter += num_children
            self.do_they_reproduce_check().children_counter += num_children
            TOTAL_RABBIT_CHILDREN += num_children
            if SEASON == 0:
                TOTAL_RABBIT_CHILDREN_SPRING += num_children
            else:
                TOTAL_RABBIT_CHILDREN_WINTER += num_children


        if self.sex_timer > 0:
            self.sex_timer -= 1

        
    
        self.save_data('Type', 'Rabbit')
        self.save_data('Energy', self.energy_count)
        self.save_data('Eating times', self.kill_counter)
        self.save_data('Number of Children', self.children_counter)
        self.save_data('Season', SEASON)
        self.save_data('Age', self.age)
        self.save_data('Boost', SPRING_BOOST)
        self.save_data('Nerf', WINTER_NERF)

class Fox(Agent):
    sex_timer: int = 0
    #energy_count: float = FOX_ENERGY
    target: Optional[Rabbit] = None
    kill_counter: int = 0
    children_counter: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age = random.randint(640, 800)  # Age of the rabbit, every time step corresponds to 12 hours
        self.gender = random.randint(0,1)
        self.energy_count = random.uniform(3,5)

    
    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()

        # Define the weight of the random component
        randomWeight = 0.2

        # Continue in the same direction
        self.move = self.move.normalize() * 2

        # Add a small random component
        randomNoise = Vector2(random.uniform(-1,1), random.uniform(-1,1)) * randomWeight
        self.move += randomNoise

        # Get nearby rabbits and foxes
        nearby_rabbits = list(self.in_proximity_accuracy().filter_kind(Rabbit))
        nearby_foxes = list(self.in_proximity_accuracy().filter_kind(Fox))

        if nearby_rabbits:
            # Pick the nearest rabbit to chase
            nearest_rabbit = choice(nearby_rabbits)  # x[1] is assumed to be the distance

            # Calculate the direction towards the chosen rabbit
            chase_force = (nearest_rabbit[0].pos - self.pos).normalize()*2

            # Add the chase force to the movement
            self.move += chase_force

        self.pos += self.move
        

    def should_reproduce(self):
        p_rep = random.uniform(0, 1)
        if SEASON == 0:
            mod = SPRING_BOOST
            mod2 = WINTER_NERF
        else:
            mod = WINTER_NERF
            mod2 = SPRING_BOOST
        
        if p_rep < FOX_REPRODUCTION_P*mod and self.energy_count > (FOX_TO_REPRODUCE*(mod2)) and FOX_COUNT <= FOX_LIMIT and self.age > FOX_AGE_TO_REPRODUCE and self.sex_timer == 0:
            return True

    def do_they_reproduce_check(self):
        fox = (
            self.in_proximity_accuracy()
            .without_distance()
            .filter_kind(Fox)
            .first()
        )

        return fox

    def eats(self):
        p_eats = random.uniform(0, 1)
        if self.energy_count < FOX_TO_EAT and p_eats < FOX_EATING_P:
        #if p_eats < FOX_EATING_P:
            return True
        elif self.energy_count < 0.6 and p_eats > 0:
            return True

    def update(self):
        global FOX_COUNT, RABBIT_COUNT, TOTAL_RABBITS_EATEN, TOTAL_FOX_CHILDREN, TOTAL_FOX_DIED, TOTAL_RABBITS_EATEN_SPRING, TOTAL_FOX_CHILDREN_SPRING, TOTAL_FOX_DIED_WINTER, TOTAL_RABBITS_EATEN_WINTER, TOTAL_FOX_CHILDREN_WINTER, TOTAL_FOX_DIED_SPRING

        self.age += 1
        if SEASON == 0:
            mod = SPRING_BOOST
            mod2 = WINTER_NERF
        else:
            mod = WINTER_NERF
            mod2 = SPRING_BOOST

        self.energy_count -= FOX_ENERGY_LOSS*mod2
        
        rabbit = (
            self.in_proximity_accuracy()
                .without_distance()
                .filter_kind(Rabbit)
                .first()

        )

        # If there's a rabbit, set it as the target
        if rabbit is not None:
            self.target = rabbit

        # If there's a target, move towards it
        if self.target is not None:
            self.move_towards(self.target)


        if self.eats():
            if rabbit is not None:
                if rabbit.not_hiding():
                    self.energy_count += rabbit.energy_count*mod
                    rabbit.kill()
                    RABBIT_COUNT -= 1
                    TOTAL_RABBITS_EATEN += 1
                    self.kill_counter += 1
                    if SEASON == 0:
                        TOTAL_RABBITS_EATEN_SPRING += 1
                    else:
                        TOTAL_RABBITS_EATEN_WINTER += 1

        if self.should_reproduce() and self.do_they_reproduce_check() is not None and self.do_they_reproduce_check().age > FOX_AGE_TO_REPRODUCE and self.do_they_reproduce_check().sex_timer == 0 and self.gender != self.do_they_reproduce_check().gender:
            self.reproduce().age = 0
            self.sex_timer = FOX_SEX_TIMER*(mod2)
            self.do_they_reproduce_check().sex_timer = FOX_SEX_TIMER*(mod2)
            self.energy_count /= 1.8
            FOX_COUNT += 1
            self.children_counter += 1
            TOTAL_FOX_CHILDREN += 1
            if SEASON == 0:
                TOTAL_FOX_CHILDREN_SPRING += 1
            else:
                TOTAL_FOX_CHILDREN_WINTER += 1



        if self.energy_count <= 0:
            self.kill()
            FOX_COUNT -= 1
            TOTAL_FOX_DIED += 1
            if SEASON == 0:
                TOTAL_FOX_DIED_SPRING += 1
            else:
                TOTAL_FOX_DIED_WINTER += 1

        if self.sex_timer > 0:
            self.sex_timer -= 1
        

        self.save_data('Type', 'Fox')
        self.save_data('Energy', self.energy_count)
        self.save_data('Eating times', self.kill_counter)
        self.save_data('Number of Children', self.children_counter)
        self.save_data('Season', SEASON)
        self.save_data('Age', self.age)
        self.save_data('Boost', SPRING_BOOST)
        self.save_data('Nerf', WINTER_NERF)

    def move_towards(self, target):
        direction = target.pos - self.pos
        self.velocity = direction.normalize()*1.5


class CustomBackground(Simulation):
    def init(self, config: Optional[Config] = None):
        super()._init_(config)

        # Make it green
        self._background.fill((0, 255, 0))



simulation = (
       HeadlessSimulation(Config(duration = FRAME_DURATION, seed = random))
      .batch_spawn_agents(RABBIT_COUNT, Rabbit, images=["C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/white.png"])
      .batch_spawn_agents(FOX_COUNT, Fox, images=["C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/red.png"])
      .batch_spawn_agents(GRASS_COUNT, Grass, images=["C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/grass.png", "C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/transparent.png"])
      .spawn_site('C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/site3.png',600,550)
    .spawn_site('C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/site3.png',630,500)
        .spawn_site('C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/site3.png',250,120)
        .spawn_site('C:/Users/fredd/Dropbox/My PC (LAPTOP-BRT8OLCQ)/Downloads/ABM/ABM/site3.png',150,620)
      .run()
      
)

snapshots = simulation.snapshots

path = "new_file.csv"
snapshots.write_csv(path, separator=",")
# Assume 'snapshots' is your Polars DataFrame
grouped_snapshots = snapshots.groupby(['frame', 'Type']).agg(
    pl.col('Type').count().alias('count')
)

# Convert the Polars DataFrame to a pandas DataFrame for easier manipulation
grouped_snapshots_pd = grouped_snapshots.to_pandas()

# Pivot the DataFrame to have one column per agent type
pivot_df = grouped_snapshots_pd.pivot(index='frame', columns='Type', values='count')

# Fill NaN values with 0
pivot_df = pivot_df.fillna(0)


import matplotlib.pyplot as plt


# Select only the columns for 'Fox' and 'Rabbit'
animals_df = pivot_df[['Fox', 'Rabbit']]

# Plot the data
animals_df.plot()

# Set the title and labels
plt.title('Population Over Time')
plt.xlabel('Frame')
plt.ylabel('Population')

# Show the plot
plt.show()


# Assuming 'type' column exists in your dataframe
# Filter based on type (example: 'Rabbit')
df_rabbit = snapshots.filter(snapshots['Type'] == 'Rabbit')
df_fox = snapshots.filter(snapshots['Type'] == 'Fox')



def calculate_metrics(df):
    metrics = {
        'max_foxes': df['Fox'].max(),
        'min_foxes': df['Fox'].min(),
        'max_rabbits': df['Rabbit'].max(),
        'min_rabbits': df['Rabbit'].min(),
        'total_rabbits_born': TOTAL_RABBIT_CHILDREN,
        'total_foxes_born': TOTAL_FOX_CHILDREN,
        'total_rabbits_eaten': TOTAL_RABBITS_EATEN,
        'total_rabbits_starved': TOTAL_RABBITS_STARVED,
        'total_foxes_starved': TOTAL_FOX_DIED,
        'average_energy_foxes': df_fox['Energy'].mean(),
        'average_energy_rabbits': df_rabbit['Energy'].mean(),
        'did_rabbits_take_over': 'Yes' if df['Rabbit'].iloc[-1] > df['Fox'].iloc[-1] else 'No',
        'did_everybody_die': 'Yes' if df['Rabbit'].iloc[-1] == 0 and df['Fox'].iloc[-1] == 0 else 'No',
    }
    

    # Calculate the population change from the beginning to the end of each season
    season_changes = df.diff(periods=SEASONAL_TIMER).dropna()

    # Calculate the average season deltas for non-zero changes
    average_spring_delta_foxes = season_changes[season_changes.index % (2*SEASONAL_TIMER) < SEASONAL_TIMER]['Fox'].replace(0, np.nan).mean()
    average_winter_delta_foxes = season_changes[season_changes.index % (2*SEASONAL_TIMER) >= SEASONAL_TIMER]['Fox'].replace(0, np.nan).mean()

    average_spring_delta_rabbits = season_changes[season_changes.index % (2*SEASONAL_TIMER) < SEASONAL_TIMER]['Rabbit'].replace(0, np.nan).mean()
    average_winter_delta_rabbits = season_changes[season_changes.index % (2*SEASONAL_TIMER) >= SEASONAL_TIMER]['Rabbit'].replace(0, np.nan).mean()

    # Add the average season deltas to the metrics
    metrics['average_spring_delta_foxes'] = average_spring_delta_foxes
    metrics['average_winter_delta_foxes'] = average_winter_delta_foxes
    metrics['average_spring_delta_rabbits'] = average_spring_delta_rabbits
    metrics['average_winter_delta_rabbits'] = average_winter_delta_rabbits

    return metrics



import pandas as pd



# Assume 'metrics' is the dictionary returned by the calculate_metrics function
metrics_df = pd.DataFrame(calculate_metrics(pivot_df), index=[0])

# Read the existing data
try:
    existing_data = pd.read_excel('C:/Users/fredd/OneDrive/Documenti/P_Prey_Spring.xlsx')
except FileNotFoundError:
    existing_data = pd.DataFrame()

# Append the new data
all_data = pd.concat([existing_data, metrics_df], ignore_index=True)

# Write the data back to the Excel file
with pd.ExcelWriter('C:/Users/fredd/OneDrive/Documenti/P_Prey_Spring.xlsx', engine='openpyxl') as writer:
    all_data.to_excel(writer, index=False)
