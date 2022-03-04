"""
TITLE:          structures.py
DIRECTORY:      Reinforcement Racer project.
DESCRIPTION:    Supplemental file containing necessary 
                data structures for the completion of 
                ACS 4511's Reinforcement Racer project.
MUTABILITY:     This file contains challenges that must be
                resolved for full project completion. (NOTE:
                You may answer relevant TODOs by creating
                additional docstrings and commented segments
                that contain your respective answers.)
"""

# Relative Imports and Instantiations
import os, sys, math, random
import neat, pygame


# Minimal comments are provided for this code in order to
# assess your capabilities in reverse-engineering and 
# understanding complex AI scripting. Write additional
# comments throughout this data structure file as needed
# to clarify both your and others' understandings.

class CarAgent:
    """ Custom self-driving car object for reinforcement learning. """
    def __init__(self, agent_parameters, environment_parameters, border_color):
        """ Initialization method to configure setup parameters for agent and environment. """
        # Set State Info and Border Colors for Racetrack
        self.border_color =             border_color
        self.agent_parameters =         agent_parameters
        self.environment_parameters =   environment_parameters

        # Set Racecar Sprites
        self.sprite = pygame.image.load("assets/agents/car01.png").convert()
        self.sprite = pygame.transform.scale(self.sprite, (self.agent_parameters["X"],
                                                           self.agent_parameters["Y"]))
        self.rotated_sprite = self.sprite

        # Initialize Racecar Position on Track
        self.position = [830, 920]
        self.angle, self.speed = 0, 0

        # Disable Racecar Training Until Needed
        self.speed_set = False

        # Initialize Center of Racecar Sprite Object
        self.center = [self.position[0] + self.agent_parameters["X"] / 2,
                       self.position[1] + self.agent_parameters["Y"] / 2]

        # Setup Path Detection Algorithms for "Looking" In Front of the Racecar
        self.radars, self.drawing_radars = list(), list()

        # Set Car Survivability Variable
        self.alive = True

        # Set Distance/Time Metrics
        self.distance, self.time = 0, 0

    def __draw_radar__(self, screen):
        """ Helper method to draw sensors/radars for improved navigability. """
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def draw(self, screen):
        """ Major method to impose sprite across simulated environment screen. """
        screen.blit(self.rotated_sprite, self.position)
        self.__draw_radar__(screen)

    def detect_collision(self, environment):
        """ Major method to perform collision detection for agent across environment space. """
        self.alive = True
        for corner in self.corners:
            if environment.get_at((int(corner[0]), int(corner[1]))) == self.border_color:
                self.alive = False; break

    def __update_coordinates__(self, degree, length):
        """ Helper method to calculate updated coordinates with deltas in X and Y. """
        # Explain what the following three lines of code are doing.
        # What values are we trying to calculate and what impact does
        # that data have on our overall project?
        """ The three lines of code below calculate horizontal and vertical coordinates. 
            This is important in determining the coordinates of our radars as well as the
            coordinates of our agent's corners which determines when it hits a wall. """
        dX = math.cos(math.radians(360 - (self.angle + degree))) * length
        dY = math.sin(math.radians(360 - (self.angle + degree))) * length
        return int(self.center[0] + dX), int(self.center[1] + dY)

    def __calculate_distance__(self, X, Y):
        """ Helper method to calculate Euclidean distance between original and updated coordinates. """
        ΔX, ΔY = X - self.center[0], Y - self.center[1]
        # Utilize the `math` repository and your understanding
        # of basic algebra to complete the Euclidean distance
        # function algorithm below. (HINT: It's the basic 
        # distance function you learn in algebra!)
        distance = math.sqrt((ΔX - X) ** 2 + (ΔY - Y) ** 2)
        return distance

    def check_radar(self, degree, environment):
        """ Major method to check and validate positions of car respective to track-path borders. """
        length = 0
        # Initializing our X and Y coordinates of our radar to center of our agent
        X, Y = self.__update_coordinates__(degree, length)
        # Loop checks if the radar is still on the racetrack determined by
        # [location of radar in relation to racetrack] is not [white]
        while not environment.get_at((X, Y)) == self.border_color and length < 300:
            length += 1
            # Updates X and Y coordinates of our radar until radar is off the racetrack
            X, Y = self.__update_coordinates__(degree, length)
        # Calculates the distance of the radar to our agent
        distance = self.__calculate_distance__(X, Y)
        self.radars.append([(X, Y), distance])

    def __get_state__(self, length):
        """ Helper method to retrieve environment state data using simulation timesteps. """
        # This is a deceptively complex algorithm at play. Explain
        # what information is being created and iterated across and 
        # why this matters for our reinforcement learning algorithm.
        """ The static offset variables represent the degree values pointing to our agent's four corners
            if our agent was facing right.  We then utilize those degree values and the update_coordinates(offset, length) 
            method to calculate our X and Y coordinates of our four corners and append them to our corners list.
            The coordinates of our corners will be used to determine whether or not our agent has hit a wall. """
        TOP_LEFT_OFFSET, TOP_RIGHT_OFFSET, BOTTOM_LEFT_OFFSET, BOTTOM_RIGHT_OFFSET = 30, 150, 210, 330
        corners = list()
        for offset in [TOP_LEFT_OFFSET, TOP_RIGHT_OFFSET, BOTTOM_LEFT_OFFSET, BOTTOM_RIGHT_OFFSET]:
            X, Y = self.__update_coordinates__(offset, length)
            corners.append([X, Y])
        return corners

    def play_game(self, environment):
        """ Major method to update car-environment positions with respective state data. """
        if not self.speed_set:
            self.speed, self.speed_set = 20, True
        # rotates our agent sprite according to the angle
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        # calculates our agent's horizontal position (X)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], self.environment_parameters["WIDTH"] - 120)
        # totals the distance our agent has traveled after every action
        self.distance += self.speed; self.time += 1
        # calculates our agent's vertical position (Y)
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], self.environment_parameters["WIDTH"] - 120)
        # calculates the coordinates of the agent's center
        self.center = [int(self.position[0]) + self.agent_parameters["X"] / 2,
                       int(self.position[1]) + self.agent_parameters["Y"] / 2]
        # calculates the corners of the agent
        length = 0.5 * self.agent_parameters["X"]
        self.corners = self.__get_state__(length)
        # detects if agent has hit a wall and resets their radars
        self.detect_collision(environment); self.radars.clear()
        # recalculates radars
        for window in range(-90, 120, 45):
            self.check_radar(window, environment)

    def get_actions(self):
        """ Major method to obtain state action data for playing racecar simulation. """
        # Our `actions` object is a deceptively important data
        # structures. Explain what this object represents and 
        # how this data is interpreted/used by our learning algorithm.
        """ The actions object represents our Q-Table which is first initialized to 0, 
            and then updated to reflect the values of our agent's radars.  The different
            indexes of our actions object align with the different actions the agent can take. """
        radars, actions = self.radars, [0, 0, 0, 0, 0]
        for iteration, radar in enumerate(radars):
            actions[iteration] = int(radar[1] / 30)
        return actions
    
    def is_alive(self):
        """ Major method to manually check car survival status. """
        return self.alive

    def get_rewards(self):
        """ Major method to calculate reward schema. """
        # Explain how our rewarding schema is expressly calculated.
        """ The reward is calculated by computing the total distance the car travels
            before the agents stops due to collision or surviving over sufficient generations
            divided by half of the agent's horizontal parameter (30). """
        # Are there any other/better ways of selecting rewards for
        # our reinforcement algorithm?
        """ Rewards could also have been selected based on how many times the agent
            finishes a lap, the time it takes for the agent to finish a lap, or
            by how long the agent survives. """
        return self.distance / (self.agent_parameters["X"] / 2)

    def rotate_center(self, image, angle):
        """ Major method to rotate environmental image. """
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image
