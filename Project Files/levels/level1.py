import random
from time import sleep
from constants import STEP_DISTANCE,WINDOW_HEIGHT,WINDOW_WIDTH
from levels.level import BaseLevel
from resources.dimension import Dimensions
from resources.sprites import Player, Box, PlayerGroup
from typing import Dict, List
from pygame import event as pg_event, quit as pg_quit, sprite, display,init
from pygame.locals import *


class Level(BaseLevel):

    def __init__(self, autoplay: bool, dimensions: Dimensions, number_of_players: int) -> None:
        super().__init__(autoplay, dimensions)

        self.player_groups: list[PlayerGroup] = [ self.spawn_player(i) for i in range(number_of_players) ]
        self.boxes= sprite.Group()
        self.human_player_group = self.player_groups[0] if not autoplay else None
        self.screen = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        for bx in range(
            STEP_DISTANCE,
            (STEP_DISTANCE * self.x_length) + STEP_DISTANCE,
            STEP_DISTANCE,
        ):
            for by in range(
                STEP_DISTANCE,
                (STEP_DISTANCE * self.y_length) + STEP_DISTANCE,
                STEP_DISTANCE,
            ):
                self.boxes.add(Box("./assets/box.png",bx, by))

    def spawn_player(self,index):
        if index == 0:
            return PlayerGroup(not self.auto_play,"./assets/user1.png", STEP_DISTANCE, STEP_DISTANCE)
        if index == 1:
            return PlayerGroup(False,"./assets/user4.png", STEP_DISTANCE*self.x_length, STEP_DISTANCE*self.y_length)
        if index == 2:
            return PlayerGroup(False,"./assets/user2.png", STEP_DISTANCE, STEP_DISTANCE*self.y_length)
        if index == 3:
            return PlayerGroup(False,"./assets/user3.png", STEP_DISTANCE*self.x_length, STEP_DISTANCE)

    
    def is_over(self) -> None:
        if len(self.player_groups) == 1:
            return True
        return False

    def make_ground(self):
        for bx in range(
            STEP_DISTANCE,
            (STEP_DISTANCE * self.x_length) + STEP_DISTANCE,
            STEP_DISTANCE,
        ):
            for by in range(
                STEP_DISTANCE,
                (STEP_DISTANCE * self.y_length) + STEP_DISTANCE,
                STEP_DISTANCE,
            ):
                self.boxes.add(Box("./assets/box.png",bx, by))

    def get_possible_routes(self, player_group: PlayerGroup):
        routes = []
        if player_group.x_coord != STEP_DISTANCE:
            routes.append('left')
        if player_group.x_coord != self.x_length*STEP_DISTANCE:
            routes.append('right')
        if player_group.y_coord != STEP_DISTANCE:
            routes.append('up')
        if player_group.y_coord != self.y_length*STEP_DISTANCE:
            routes.append('down')
        return routes

    def auto_route_if_non_human_group(self, player_group: PlayerGroup):
        if not player_group.has_human_player:
            possible_routes = self.get_possible_routes(player_group)
            chosen = random.choice(possible_routes)
            player_group.move(chosen,False)

    def route(self, player_group: PlayerGroup, direction: str):
        possible_routes = self.get_possible_routes(player_group)

        if direction in possible_routes:
            player_group.move(direction,True)


    def mergeGroups(self, player_group_list: List[PlayerGroup]) -> PlayerGroup:
        human_in_group = self.human_player_group in player_group_list
        for player_group in player_group_list[1:]:
            for player in player_group.players:
                player_group_list[0].add_player(player)
        if human_in_group:
            player_group_list[0].has_human_player = True
            self.human_player_group = player_group_list[0]
        return player_group_list[0]

    def auto_route_and_update_groups(self):
        for player_group in self.player_groups:
            self.auto_route_if_non_human_group(player_group)

        new_player_groups: list[PlayerGroup] = []
        group_coords = {}
        for player_group in self.player_groups:
            try:
                group_coords[(player_group.x_coord, player_group.y_coord)].append(player_group)
            except KeyError:
                group_coords[(player_group.x_coord, player_group.y_coord)] = [
                    player_group]

        for value in group_coords.values():
            if len(value) > 1:
                new_player_groups.append(self.mergeGroups(value))
            else:
                new_player_groups.extend(value) 

        self.player_groups = new_player_groups

    def render_screen(self) -> None:
        self.screen.fill((0,0,0))
        self.boxes.draw(self.screen)
        for player_group in self.player_groups:
            player_group.paint(self.screen)
        display.flip()

    def start(self,clock) -> int:
        running = True
        self.render_screen()
        
        while running:
            if self.is_over():
                break
            if not self.auto_play:
                
                for event_ in pg_event.get():
                    if event_.type == KEYUP and event_.key==K_ESCAPE:
                        running = False

                    if event_.type == KEYUP and event_.key == K_UP:
                        self.route(self.human_player_group, 'up')
                        self.auto_route_and_update_groups()
                        self.render_screen()

                    if event_.type == KEYUP and event_.key == K_DOWN:
                        self.route(self.human_player_group, 'down')
                        self.auto_route_and_update_groups()
                        self.render_screen()

                    if event_.type == KEYUP and event_.key == K_LEFT:
                        self.route(self.human_player_group, 'left')
                        self.auto_route_and_update_groups()
                        self.render_screen()

                    if event_.type == KEYUP and event_.key == K_RIGHT:
                        self.route(self.human_player_group, 'right')
                        self.auto_route_and_update_groups()
                        self.render_screen()

            else:
                self.render_screen()
                self.auto_route_and_update_groups()

        return 10 if self.human_player_group is None else self.human_player_group.players[0].score