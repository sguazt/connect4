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


class GameUI:
    """
    Base class for user interfaces for the Connect 4 game.
    """
    def __init__(self, game):
        self.game = game

    def show(self):
        """
        Shows the main game board.
        """
        upo.utils.raise_undefined_method()


class PyGameUI(GameUI):
    """
    User interface based on the PyGame library.
    """
    #DEFAULT_FG_COLOR = (  0,   0,   0)
    #DEFAULT_BG_COLOR = (255, 255, 255)
    DEFAULT_FPS = 30
    DEFAULT_GEOMETRY = (800, 600) # window geometry (width, height)
    DEFAULT_LAYOUT = (7, 6) # board (width, height)
    DEFAULT_TIMEOUT = 0 # maximum number of second before a timeout is triggered for an agent

    def __init__(self, game, geometry = DEFAULT_GEOMETRY, fps = DEFAULT_FPS, timeout = DEFAULT_TIMEOUT):
        GameUI.__init__(self, game)
        self.win_geometry = geometry
        self.fps = fps
        self.timeout = timeout
        self.display = None
        self.timer_font = None
        self.legend_font = None
        self.bg_color = (255, 255, 255) # white
        self.fg_color = (128, 128, 128) # gray
        self.column_highlight_color = (0, 255, 0) # green
        self.board_color = (0, 0, 0) # black
        #self.top_row_color = (0, 255, 255) # cyan
        if game.num_agents() > 2:
            # Generate a custom color palette
            self.player_colors = upo.gfx_utils.generate_color_palette(game.num_agents())
        else:
            # Use standard colors: red and yellow
            self.player_colors = [(255, 0, 0), (255, 255, 0)]
        #self.tile_geom = (geometry[0]//layout[0], geometry[1]//layout[1])
        #self.yoffs = (self.win_geometry[0]-layout[0]*self.tile_geom[0])//2
        #self.xoffs = (self.win_geometry[1]-layout[1]*self.tile_geom[1])//2
        board_cols = self.game.get_state().get_board().width()
        board_rows = self.game.get_state().get_board().height()
        self.tile_size = min(self.win_geometry)//max(board_cols, board_rows)
        self.board_dim = (self.tile_size*board_cols, self.tile_size*board_rows)
        self.xoffs = (self.get_window_width()-self.board_dim[0])//2
        self.yoffs = (self.get_window_height()-self.board_dim[1])//2
        #self.board_rect = pygame.Rect(self.xoffs, self.yoffs+self.tile_size, self.board_dim, self.board_dim)
        self.board_rect = pygame.Rect(self.xoffs, self.yoffs, self.board_dim[0], self.board_dim[1])
        self.token_radius = self.tile_size//2 - 1
        #print('Window: ', self.win_geometry, ', Board: ', self.board_dim, ', Tile: ', self.tile_size, ', Offset: ', (self.xoffs, self.yoffs))

    def get_geometry(self):
        return self.win_geometry

    def get_window_width(self):
        return self.win_geometry[0]

    def get_window_height(self):
        return self.win_geometry[1]

    def show(self):
        """
        Shows the user interface and runs the game loop.
        """
        pygame.init()

        fps_clock = pygame.time.Clock();

        self.display = pygame.display.set_mode(self.win_geometry)
        pygame.display.set_caption('Connect 4')

        # Preloads font to avoid delays during the execution
        self.legend_font = pygame.font.SysFont(pygame.font.get_default_font(), 16)
        if self.timeout > 0:
            self.timer_font = pygame.font.Font('resources/timer_font.ttf', 24)

        winning_cells = []
        game_over = False
        winning_blink = True
        winning_blink_count = 0
        WIN_BLINK_DURATION = 0.5 # number of seconds elasping between 2 successive blinking
        column_highlight = False
        column_highlight_pos = ()
        timer_count = 0
        timer_value = 0
        skip_logic = True
        while True:
            # This is the game loop

            if skip_logic:
                skip_logic = False
            else:
                wait_interaction = not game_over and self.game.get_current_agent().is_interactive()

                # Checks for interesting events in the event loop
                for event in pygame.event.get():
                    #print('Event: ', event)
                    # Checks for a quit event
                    if (event.type == pygame.QUIT
                        or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                        pygame.quit()
                        return
                    # In case of interactive agent, there are more interesting things to check
                    if wait_interaction:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            # Pushes the token on the corresponding board column
                            if self.is_inside_board(event.pos):
                                (c, r) = self.screen_to_board_coords(event.pos)
                                if self.game.get_state().is_legal_action(c):
                                    self.game.get_current_agent().set_action(c)
                                    wait_interaction = False
                        else:
                            wait_interaction = True
                            # Draws a highlight box around the column under the mouse pointer
                            if event.type == pygame.MOUSEMOTION and self.is_inside_board(event.pos):
                                column_highlight = True
                                column_highlight_pos = event.pos
                            else:
                                column_highlight = False
                # Plays the game
                if not wait_interaction:
                    if not game_over:
                        self.game.make_move()
                        game_over = self.game.is_over()
                        if game_over:
                            if self.game.get_state().is_win():
                                winning_cells = self.game.get_state().get_winner_positions()
                                winning_agent = self.game.get_agent(self.game.get_state().get_winner())
                                print("The winner is: " + winning_agent.get_name() + "!")
                            elif self.game.get_state().is_tie():
                                print("Tie!")
                        if self.timeout > 0:
                            timer_count = 0
                # Updates the timer
                if self.timeout > 0 and not game_over:
                    # Computes total seconds
                    timer_value = self.timeout - timer_count//self.fps
                    if timer_value < 0:
                        timer_value = 0
                    if timer_value == 0:
                        game_over = True
                        print("Timed out! " + self.game.get_current_agent().get_name() + " loses!")
                    timer_count += 1
 
            ## BEGIN DRAWING

            # Fills the display with the background color
            self.display.fill(self.bg_color)

            # Draws the game board
            self.draw_board()

            # Draws agents' legend
            self.draw_legend()

            # Highlights the board column under the mouse
            if not game_over and column_highlight:
                self.highlight_column(column_highlight_pos)

            # Blinks winning tokens
            if len(winning_cells) > 0:
                if winning_blink_count/self.fps >= WIN_BLINK_DURATION:
                    winning_blink = not winning_blink
                    winning_blink_count = 0
                if winning_blink:
                    self.blink_winning_tokens(winning_cells)
                winning_blink_count += 1

            # Displays a countdown timer
            if self.timeout > 0:
                self.draw_timer(timer_value)

            pygame.display.flip();

            ## END DRAWING

            fps_clock.tick(self.fps)

    def draw_board(self):
        """
        Draws the game board.
        """
        game_board = self.game.get_state().get_board()
        board_rows = game_board.height()
        board_cols = game_board.width()

        #self.display.fill(self.bg_color)
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
        """
        Draws a single token at the given board position.
        """
        game_board = self.game.get_state().get_board()
        if game_board.has_token(column, row):
            token = game_board.get_token(column, row)
            xc = self.board_rect.left + column*self.tile_size + self.tile_size//2 + 1
            yc = self.board_rect.top + row*self.tile_size + self.tile_size//2 + 1
            pygame.draw.circle(self.display, self.player_colors[token], (xc, yc), self.token_radius)

    def highlight_column(self, pos):
        """
        Highlight the board column corresponding to the given position.
        """
        (c, r) = self.screen_to_board_coords(pos)
        (x, y) = self.board_to_screen_coords((c, r))
        pygame.draw.rect(self.display, self.column_highlight_color, (x-2, self.board_rect.top-2, self.tile_size+2, self.board_rect.height+2), 2)

    def blink_winning_tokens(self, winning_cells):
        """
        Highlights winning tokens.
        """
        game_board = self.game.get_state().get_board()
        for (x,y) in winning_cells:
            if game_board.has_token(x, y):
                token = game_board.get_token(x, y)
                #col = self.player_colors[token]
                hcol = [0,0,0]
                #hcol[0] = 255-col[0]
                #hcol[1] = 255-col[1]
                #hcol[2] = 255-col[2]
                xc = self.board_rect.left + x*self.tile_size + self.tile_size//2 + 1
                yc = self.board_rect.top + y*self.tile_size + self.tile_size//2 + 1
                pygame.draw.circle(self.display, hcol, (xc, yc), self.token_radius, 2)

    def draw_legend(self):
        """
        Draws the agents' legend.
        """
        #font_col = (255-x for x in self.bg_color)
        font_col = (255-self.bg_color[0],255-self.bg_color[1],255-self.bg_color[2])
        radius = int(self.token_radius*0.20)
        for agent in self.game.get_agents():
            idx = agent.get_index()
            xc = self.board_rect.right + 10
            yc = self.board_rect.top + radius + idx*radius*4
            pygame.draw.circle(self.display, self.player_colors[idx], (xc, yc), radius)
            font_surf = self.legend_font.render(agent.get_name(), True, font_col)
            self.display.blit(font_surf, (xc+6, yc-6))

    def draw_timer(self, timer_value):
        # Gets total minutes and seconds
        (mins, secs) = divmod(timer_value, 60)
        timer_str = "{0:02}:{1:02}".format(mins, secs)
        font_col = (255-self.bg_color[0],255-self.bg_color[1],255-self.bg_color[2])
        font_timer = self.timer_font.render(timer_str, True, font_col)
        #rect = font_timer.get_rect()
        #self.display.blit(font_timer, (self.board_rect.left, self.board_rect.bottom+(self.win_geometry[1]-self.board_rect.bottom)//2))
        self.display.blit(font_timer, (self.board_rect.left, self.board_rect.bottom+font_timer.get_rect().height//2))

    def board_to_screen_coords(self, pos):
        """
        Transforms board position (column, row) into screen coordinates (x, y).
        """
        (c, r) = pos
        x = c*self.tile_size+self.board_rect.left
        y = r*self.tile_size+self.board_rect.top
        return (x, y)

    def screen_to_board_coords(self, pos):
        """
        Transforms screen position (x, y) into board coordinates (column, row).
        """
        (x, y) = pos
        c = (x-self.board_rect.left)//self.tile_size
        r = (y-self.board_rect.top)//self.tile_size
        return (c, r)

    def is_inside_board(self, pos):
        """
        Tells if the given screen position (x, y) is inside the game board.
        """
        (x, y) = pos
        return (x >= self.board_rect.left
                and x <= self.board_rect.right
                and y >= self.board_rect.top
                and y <= self.board_rect.bottom)
