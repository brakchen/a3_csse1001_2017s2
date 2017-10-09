"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil
from copy import copy
from tkinter import *
import tkinter as tk
from tkinter.messagebox import *
import os
import random

try:
    from PIL import ImageTk, Image

    HAS_PIL = True
except:
    HAS_PIL = False

from view import GridView, ObjectivesView
from game import DotGame, ObjectiveManager
from dot import BasicDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = ""
__email__ = ""
__date__ = ""

__version__ = "1.0.0rc3"


def load_image_pil(image_id, size, prefix, suffix='.png'):
    """Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """

    print("image_id:{0}, size:{1}, prefix:{2}".format(image_id, size, prefix))

    width, height = size
    file_path = os.path.join(prefix, f"{width}x{height}", image_id + suffix)
    return ImageTk.PhotoImage(Image.open(file_path))


def load_image_tk(image_id, size, prefix, suffix='.gif'):
    """Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """

    print("image_id:{0}, size:{1}, prefix:{2}".format(image_id, size, prefix))
    width, height = size
    file_path = os.path.join(prefix, f"{width}x{height}", image_id + suffix)
    return tk.PhotoImage(file=file_path)


# This allows you to simply load png images with PIL if you have it,
# otherwise will default to gifs through tkinter directly
load_image = load_image_pil if HAS_PIL else load_image_tk



# Define your classes here




class AnchorDot(BasicDot):
    DOT_NAME = "anchor"

    def activate(self, position, game, activated):
        pass

    def adjacent_activated(self, position, game, activated, activated_neighbours):
        pass

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), self.get_kind())


class CompanionDot(BasicDot):
    DOT_NAME = "companion"

    def activate(self, position, game, activated):
        pass

    def adjacent_activated(self, position, game, activated, activated_neighbours):
        pass

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""

        return "{}/{}".format(self.get_name(), + self.get_kind())


class DotsApp(object):
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """

        self._master = master
        master.title("Dots & Co")
        # self define
        self._info_panel = InfoPanel(master)


        self._interval_bar = IntervalBar(master,60,6,(80,80))


        self._menu(master)

        self._playing = True
        self._image_manager = ImageManager('images/dots/', loader=load_image)



        self._turns = 20
        # Games
        counts = [10, 15, 25, 25]
        random.shuffle(counts)
        # randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1),
                          BasicDot(2),
                          BasicDot(3),
                          BasicDot(4),], counts)
        # objectives = zip([AnchorDot("anchor"),
        #                   AnchorDot("anchor"),
        #                   AnchorDot("anchor"),
        #                   AnchorDot("anchor"),
        #                   ], counts)
        self._objectives = ObjectiveManager(objectives)


        # --------------------------------------------------------------------------------------
        self._objectivesView = ObjectivesView(master,
                                              image_manager=self._image_manager)

        for data in self._objectives.get_status():
            self._info_panel.set_status(self._objectivesView.load_image(data[0], (20, 20)),
                                        data[1],
                                        data[0])

        dead_cells = {(2, 2), (2, 3), (2, 4),
                      (3, 2), (3, 3), (3, 4),
                      (4, 2), (4, 3), (4, 4),
                      (0, 7), (1, 7), (6, 7), (7, 7)}

        # self._game = DotGame({BasicDot: 1,AnchorDot:1},
        #                      objectives=self._objectives,
        #                      kinds=(1, 2, 3, 4,"anchor"),
        #                      size=(8, 8),
        #                      dead_cells=dead_cells)

        self._game = DotGame({BasicDot:1},
                             objectives=self._objectives,
                             kinds={1,2,3,4},
                             size=(8, 8),
                             dead_cells=dead_cells)

        #
        # self._game = DotGame({AnchorDot:1,},
        #                      objectives=self._objectives,
        #                      kinds=("anchor","anchor","anchor","anchor"),
        #                      size=(8, 8),
        #                      dead_cells=dead_cells)

        # Grid View
        self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
        self._grid_view.pack()
        self._grid_view.draw(self._game.grid)
        self.draw_grid_borders()

        # Events
        self.bind_events()
        # self._game.remove((0,0))
        # self._game.drop((0,0))



    def draw_grid_borders(self):
        """Draws borders around the game grid"""

        borders = list(self._game.grid.get_borders())

        # this is a hack that won't work well for multiple separate clusters
        outside = max(borders, key=lambda border: len(set(border)))

        for border in borders:
            self._grid_view.draw_border(border, fill=border != outside)

    def bind_events(self):
        """Binds relevant events"""
        self._grid_view.on('start_connection', self._drag)
        self._grid_view.on('move_connection', self._drag)
        self._grid_view.on('end_connection', self._drop)

        self._game.on('activate', self._score)
        self._game.on('animate', self._animate)
        self._game.on('complete', self._drop_complete)

        self._game.on('connect', self._connect)
        self._game.on('undo', self._undo)

    def _animate(self, callback=lambda: None):
        """Handles animation of the game"""

        def full_callback():
            """Function to run when animation finishes"""
            self.draw_grid()
            callback()

        animation = create_animation(self._master, self._game.animate(),
                                     func=self.draw_grid, callback=full_callback)
        animation()

    def _drop(self, position):  # pylint: disable=unused-argument
        """Handles the dropping of the dragged connection

        Parameters:
            position (tuple<int, int>): The position where the connection was
                                        dropped
        """

        if not self._playing:
            return

        self._grid_view.clear_dragged_connections()
        self._grid_view.clear_connections()

        if self._game.is_resolving():
            return

        self._game.drop()

    def _connect(self, start, end):
        """Draws a connection from the start point to the end point

        Parameters:
            start (tuple<int, int>): The position of the starting dot
            end (tuple<int, int>): The position of the ending dot
        """
        # print("start:{start}----end:{end}".format(start=start,end=end))
        self._grid_view.draw_connection(start, end,
                                        self._game.grid[start].get_dot().get_kind())

    def _undo(self, positions):
        """Removes all the given dot connections from the grid view

        Parameters:
            positions (list<tuple<int, int>>): The dot connects to remove
        """
        for _ in positions:
            self._grid_view.undo_connection()

    def _drag(self, position):
        """Attempts to connect to the given position, otherwise draws a dragged
        line from the start

        Parameters:
            position (tuple<int, int>): The position to drag to
        """
        if not self._playing:
            return

        tile_position = self._grid_view.xy_to_rc(position)

        if tile_position is not None:
            cell = self._game.grid[tile_position]
            dot = cell.get_dot()

            if dot and dot.get_kind() is not None and self._game.connect(tile_position):
                self._grid_view.clear_dragged_connections()
                return

        kind = self._game.get_connection_kind()

        if kind is None:
            return

        start = self._game.get_connection_path()[-1]

        if start:
            self._grid_view.draw_dragged_connection(start, position, kind)

    def remove(self, *positions):
        """Attempts to remove the tiles at the given positions

        Parameters:
            *positions (tuple<int, int>): Row-column position of the tile

        Raises:
            IndexError: If position cannot be activated
        """

        if len(positions) is None:
            return

        if self._game.is_resolving():
            return

        animation = create_animation(self._master, self._game.remove(*positions),
                                     func=self.draw_grid, callback=self.draw_grid)
        animation()

    def draw_grid(self):
        """Draws the grid"""
        self._grid_view.draw(self._game.grid)

    def reset(self):
        """Resets the game"""
        self._game.reset()

        self._grid_view.draw(self._game.grid)
        self._info_panel.set_turns(20)
        self._info_panel.set_image(self._info_panel.get_image("useless.gif"))


    def check_game_over(self):
        """Checks whether the game is over and shows an appropriate message box if so"""
        state = self._game.get_game_state()

        if state == self._game.GameState.WON:
            showinfo("Game Over!", "You won!!!")
            self._playing = False
        elif state == self._game.GameState.LOST:
            showinfo("Game Over!",
                     f"You didn't reach the objective(s) in time. You connected {self._game.get_score()} points")
            self._playing = False

    def _drop_complete(self):
        """Handles the end of a drop animation"""

        pass

    def _score(self, score):  # pylint: disable=no-self-use
        """Handles change in score

        Parameters:
            score (int): The new score
        """
        self._info_panel.set_score(self._game.get_score())

        self._info_panel.set_docts_step(self._objectives.get_status())
        self._info_panel.set_turns(self._game.get_moves())
        self._interval_bar.config_progress()
        print(self._game.get_connection_path())


    def _menu(self, master):
        menubar = Menu(master)
        master.config(menu=menubar)


        fileMenu = Menu(menubar)

        submenu = Menu(fileMenu)
        submenu.add_command(label="Companion",command=self.load_game)
        submenu.add_command(label="No Companion",command=self.reset)
        fileMenu.add_cascade(label='New Game', menu=submenu, underline=0)

        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline=0, command=lambda :
        self._master.destroy()
        if askyesno('Verify', 'Do you really wanna quit?')
        else showinfo('No', 'Welcome back'))

        menubar.add_cascade(label="File", underline=0, menu=fileMenu)




    def load_game(self):
        self.reset()
        self._info_panel.image_register("penguin.gif")
        self._info_panel.set_image(self._info_panel.get_image("penguin.gif"))



def main():
    """Sets-up the GUI for Dots & Co"""
    root = tk.Tk()
    app = DotsApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
