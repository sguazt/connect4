# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 Marco Guazzone (marco.guazzone@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pygame
import sys
import upo.connect4.game
import upo.gfx_utils

from pygame import *


class GameUI:
    def __init__(self, game):
        self.game = game

    def show(self):
        upo.utils.raise_undefined_method()


class PyGameUI(GameUI):
    #DEFAULT_FG_COLOR = (  0,   0,   0)
    #DEFAULT_BG_COLOR = (255, 255, 255)
    DEFAULT_FPS = 30
    DEFAULT_GEOMETRY = (640, 480) # window geometry (width, height)
    DEFAULT_LAYOUT = (7, 6) # board (width, height)

    def __init__(self, game, geometry = DEFAULT_GEOMETRY, fps = DEFAULT_FPS):
        GameUI.__init__(self, game)
        self.win_geometry = geometry
        self.fps = fps
        self.display = None
        self.bg_color = (255, 255, 255) # white
        self.fg_color = (128, 128, 128) # gray
        self.board_color = (0, 0, 0) # black
        #self.top_row_color = (0, 255, 255) # cyan
        if game.num_agents() > 2:
            # Generate a custom color palette
            self.player_colors = upo.gfx_utils.generate_color_palette(game.num_agents())
        else:
            # Use standard colors: red and yellow
            self.player_colors = [(255, 0, 0), (255, 255, 0)]
        #self.tile_geom = (int(geometry[0]/layout[0]), int(geometry[1]/layout[1]))
        #self.yoffs = int((self.win_geometry[0]-layout[0]*self.tile_geom[0])/2)
        #self.xoffs = int((self.win_geometry[1]-layout[1]*self.tile_geom[1])/2)
        board_cols = self.game.get_state().get_board().width()
        board_rows = self.game.get_state().get_board().height()
        self.tile_size = int(min(self.win_geometry)/max(board_cols, board_rows))
        self.board_dim = (self.tile_size*board_cols, self.tile_size*board_rows)
        self.xoffs = int((self.get_window_width()-self.board_dim[0])/2)
        self.yoffs = int((self.get_window_height()-self.board_dim[1])/2)
        #self.board_rect = pygame.Rect(self.xoffs, self.yoffs+self.tile_size, self.board_dim, self.board_dim)
        self.board_rect = pygame.Rect(self.xoffs, self.yoffs, self.board_dim[0], self.board_dim[1])
        self.token_radius = self.tile_size/2 - 1
        #print 'Window: ', self.win_geometry, ', Board: ', self.board_dim, ', Tile: ', self.tile_size, ', Offset: ', (self.xoffs, self.yoffs)

    def get_geometry(self):
        return self.win_geometry

    def get_window_width(self):
        return self.win_geometry[0]

    def get_window_height(self):
        return self.win_geometry[1]

    def show(self):
        pygame.init()

        fps_clock = pygame.time.Clock();

        self.display = pygame.display.set_mode(self.win_geometry)
        pygame.display.set_caption('Connect 4')

        #self.red_pile_rect = pygame.Rect(int(SPACE_SIZE/2), self.size[1]-int(3*SPACE_SIZE/2), SPACE_SIZE, SPACE_SIZE)

        #cur_agent = 0
        win_cells = []
        game_over = False
        win_highlight = True
        win_highlight_count = 0
        WIN_HIGHLIGHT_MAX_COUNT = 10
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    #sys.exit()
                    return

            if game_over or self.game.is_over():
                if not game_over:
                    game_over = True
                    if self.game.get_state().is_win():
                        print "Winning!"
                        win_cells = self.game.get_state().get_winner_positions()
                    elif self.game.get_state().is_tie():
                        print "Tie!"
                #elif win_cells.empty():
                #    win_cells = self.game.get_winner_cells()
            else:
                self.game.make_move()

            self.draw_board()

            self.draw_legend()

            if len(win_cells) > 0:
                if win_highlight_count == WIN_HIGHLIGHT_MAX_COUNT:
                    win_highlight = not win_highlight
                    win_highlight_count = 0
                if win_highlight:
                    self.highlight_win_tokens(win_cells)
                win_highlight_count += 1

            pygame.display.flip();

            fps_clock.tick(self.fps)

    def draw_board(self):
        game_board = self.game.get_state().get_board()
        board_rows = game_board.height()
        board_cols = game_board.width()

        self.display.fill(self.bg_color)
        ## draw top row 
        #pygame.draw.rect(self.display, self.top_row_color, [self.xoffs, self.yoffs, self.board_dim[0], self.tile_size])
        # draw board
        pygame.draw.rect(self.display, self.board_color, self.board_rect)

        # draw grid over board
        for r in range(1, board_rows):
            y = self.board_rect.top + r*self.tile_size
            start_pos = [self.board_rect.left, y]
            stop_pos = [self.board_rect.right, y]
            pygame.draw.line(self.display, self.fg_color, start_pos, stop_pos, 2)
        for c in range(1, board_cols):
            x = self.board_rect.left + c*self.tile_size
            #start_pos = [x, self.yoffs]
            start_pos = [x, self.board_rect.top]
            stop_pos = [x, self.board_rect.bottom]
            pygame.draw.line(self.display, self.fg_color, start_pos, stop_pos, 2)

        ## draw tokens
        for c in range(board_cols):
            for r in range(board_rows):
                self.draw_token(c, r)

    def draw_token(self, column, row):
        game_board = self.game.get_state().get_board()
        if game_board.has_token(column, row):
            token = game_board.get_token(column, row)
            xc = self.board_rect.left + column*self.tile_size + self.tile_size/2 + 1
            yc = self.board_rect.top + row*self.tile_size + self.tile_size/2 + 1
            pygame.draw.circle(self.display, self.player_colors[token], (xc, yc), self.token_radius)

    def highlight_win_tokens(self, win_cells):
        game_board = self.game.get_state().get_board()
        for (x,y) in win_cells:
            if game_board.has_token(x, y):
                token = game_board.get_token(x, y)
                #col = self.player_colors[token]
                hcol = [0,0,0]
                #hcol[0] = 255-col[0]
                #hcol[1] = 255-col[1]
                #hcol[2] = 255-col[2]
                xc = self.board_rect.left + x*self.tile_size + self.tile_size/2 + 1
                yc = self.board_rect.top + y*self.tile_size + self.tile_size/2 + 1
                pygame.draw.circle(self.display, hcol, (xc, yc), self.token_radius, 2)

    def draw_legend(self):
        font = pygame.font.SysFont(pygame.font.get_default_font(), 16)
        #font_col = (255-x for x in self.bg_color)
        font_col = (255-self.bg_color[0],255-self.bg_color[1],255-self.bg_color[2])
        radius = int(self.token_radius*0.20)
        for agent in self.game.get_agents():
            idx = agent.get_index()
            xc = self.board_rect.right + 10
            yc = self.board_rect.top + radius + idx*radius*4
            pygame.draw.circle(self.display, self.player_colors[idx], (xc, yc), radius)
            font_surf = font.render(agent.get_name(), True, font_col)
            self.display.blit(font_surf, (xc+6, yc-6))
