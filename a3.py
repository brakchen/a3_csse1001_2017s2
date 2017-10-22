"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil

import tkinter as tk
from tkinter import messagebox
import os
import random
from tkinter.messagebox import showinfo, askyesno

from companion import AbstractCompanion

try:
    from PIL import ImageTk, Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from view import GridView, ObjectivesView
from game import DotGame, ObjectiveManager, CompanionGame
from dot import BasicDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = ""
__email__ = ""
__date__ = ""

__version__ = "1.1.1"


def load_image_pil(image_id, size, prefix, suffix='.png'):
    """Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
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
    width, height = size
    file_path = os.path.join(prefix, f"{width}x{height}", image_id + suffix)
    return tk.PhotoImage(file=file_path)


# This allows you to simply load png images with PIL if you have it,
# otherwise will default to gifs through tkinter directly
load_image = load_image_pil if HAS_PIL else load_image_tk  # pylint: disable=invalid-name

DEFAULT_ANIMATION_DELAY = 0  # (ms)
ANIMATION_DELAYS = {
    # step_name => delay (ms)
    'ACTIVATE_ALL': 50,
    'ACTIVATE': 100,
    'ANIMATION_BEGIN': 300,
    'ANIMATION_DONE': 0,
    'ANIMATION_STEP': 200
}

companions_manager = {
    "useless.gif": "images/companions/useless.gif",
    "penguin.gif": "images/companions/penguin.gif",
    "penguin.png": "images/companions/penguin.png",
    "penguin_large.png": "images/companions/penguin_large.png",
    "buffalo_large.png": "images/companions/buffalo_large.png",
    "deer_large.png": "images/companions/deer_large.png",
    "eskimo.png": "images/companions/eskimo.png",
    "goat.png": "images/companions/goat.png",

}


# Define your classes here

class InfoPanel(tk.Frame):
    def __init__(self, master):

        self._dots_list = []
        self._info_frame = tk.Frame(master)
        self._moves_frame = tk.Frame(self._info_frame)

        self._companion_frame = tk.Frame(self._info_frame)

        self._dots_frame = tk.Frame(self._info_frame)

        self._moves_label = tk.Label(self._moves_frame,
                                     text="", font=(None, 30))

        # Set center image and score next to image
        self._image = tk.PhotoImage(file="images/companions/useless.gif")
        self._useless_image = tk.Label(self._companion_frame, text="",
                                       font=(None, 40),
                                       image=self._image,
                                       compound="right")

        # Packing all the frames
        self._info_frame.pack()
        self._moves_frame.pack(side=tk.LEFT, ipadx=50)
        self._companion_frame.pack(side=tk.LEFT, expand=True)
        self._dots_frame.pack(side=tk.LEFT, expand=True)
        self._moves_label.pack(anchor=tk.W, expand=False)
        self._useless_image.pack(side=tk.RIGHT)

    def set_turns(self, turn):
        self._moves_label.config(text="{}".format(turn))

    def set_score(self, score):
        self._useless_image.config(text="{}".format(score))

    def set_status(self, image_id, count, obj):

        self._status_label = tk.Label(self._dots_frame,
                                      image=image_id,
                                      text=count, compound="top")
        self._status_label.pack(side=tk.RIGHT)

        self._dots_list.append([obj.get_kind(),
                                obj.get_name(),
                                count,
                                self._status_label])

    def set_remaining_dots(self, obj):
        for num in range(len(self._dots_list)):
            if obj[num][1] is not self._dots_list[num][2]:
                self._dots_list[num][3].config(text=obj[num][1])
                self._dots_list[num][2] = obj[num][1]

    def reset_infopanel(self):
        self.set_turns(20)


class IntervalBar(tk.Canvas):
    def __init__(self, master):

        self._canvas = tk.Canvas(master, bg="white",
                                 width=500, height=30)
        self._canvas.pack(side=tk.TOP)
        self._canvas_coordinate = [(80, 10, 140, 30),
                                   (140, 10, 200, 30),
                                   (200, 10, 260, 30),
                                   (260, 10, 320, 30),
                                   (320, 10, 380, 30),
                                   (380, 10, 440, 30)]
        self.draw_rectangle()

    def draw_rectangle(self):
        
        self._canvas.create_rectangle(80, 10, 140, 30)
        self._canvas.create_rectangle(140, 10, 200, 30)
        self._canvas.create_rectangle(200, 10, 260, 30)
        self._canvas.create_rectangle(260, 10, 320, 30)
        self._canvas.create_rectangle(320, 10, 380, 30)
        self._canvas.create_rectangle(380, 10, 440, 30)

    def fill_rectangle_blue(self, coordinate):
        x, y, z, w = coordinate
        self._canvas.create_rectangle(x, y, z, w, fill='blue')

    def fill_rectangle_blank(self, coordinate):
        x, y, z, w = coordinate
        self._canvas.create_rectangle(x, y, z, w, fill='white')

    def changing_progress(self, charge):
        if charge == 6:
            for coordinate in self._canvas_coordinate:
                x, y, z, w = coordinate
                self.fill_rectangle_blank(coordinate)
        else:
            for i in range(charge):
                self.fill_rectangle_blue(self._canvas_coordinate[i])

    def reset_interval_bar(self):
        for coordinate in self._canvas_coordinate:
            x, y, z, w = coordinate
            self.fill_rectangle_blank(coordinate)



class BuffaloCompanion(AbstractCompanion):
    NAME = 'Buffalo'

    def __init__(self):
        super().__init__()

    def activate(self, game):
        pass
class WildcardDot(BasicDot):
    DOT_NAME = "wildcard"

    def can_connect(self):
        return False


# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """

        
        self._charge = 0
        self._infopanel = InfoPanel(master)
        self._intervalbar = IntervalBar(master)
        self.menu(master)
        
        self._master = master

        self._playing = True

        self._image_manager = ImageManager('images/dots/', loader=load_image)

        # Game
        counts = [10, 15, 25, 25]
        random.shuffle(counts)
        # randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], counts)

        self._objectives = ObjectiveManager(list(objectives))
        

        self._objectivesView = ObjectivesView(master,
                                              image_manager=self._image_manager)
        for data in self._objectives.get_status():
            self._infopanel.set_status(self._objectivesView.load_image(data[0], (20, 20)),
                                       data[1],data[0])
        
        # Game
        dead_cells = {(2, 2), (2, 3), (2, 4),
                      (3, 2), (3, 3), (3, 4),
                      (4, 2), (4, 3), (4, 4),
                      (0, 7), (1, 7), (6, 7), (7, 7)}

        self._game = CompanionGame({BasicDot: 1}, companion=BuffaloCompanion(), objectives=self._objectives,
                                   kinds=(1, 2, 3, 4), size=(8, 8),
                                   dead_cells=dead_cells)
        # The following code may be useful when you are implementing task 2:


        row_list = []
        column_list = []
        for a in range(0, 7):
            row_list.append(a)
        for b in range(0, 7):
            column_list.append(b)
        random.shuffle(row_list)
        random.shuffle(column_list)
        position_list = set(zip(row_list, column_list))

        for position in position_list:
            if position not in dead_cells:
                self._game.grid[position].set_dot(WildcardDot("wildcard"))

        # Grid View
        self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
        self._grid_view.pack()
        self._grid_view.draw(self._game.grid)
        self.draw_grid_borders()

        # Events
        self.bind_events()


        self._refresh_status()

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

        self._game.on('reset', self._refresh_status)
        self._game.on('complete', self._drop_complete)

        self._game.on('connect', self._connect)
        self._game.on('undo', self._undo)

    def _animation_step(self, step_name):
        """Runs for each step of an animation

        Parameters:
            step_name (str): The name (type) of the step
        """
        # self._drop_complete(step_name)
        # print(step_name)
        self._refresh_status()
        self.draw_grid()

    def animate(self, steps, callback=lambda: None):
        """Animates some steps (i.e. from selecting some dots, activating companion, etc.

        Parameters:
            steps (generator): Generator which yields step_name (str) for each step in the animation
        """

        if steps is None:
            steps = (None for _ in range(1))

        animation = create_animation(self._master, steps,
                                     delays=ANIMATION_DELAYS, delay=DEFAULT_ANIMATION_DELAY,
                                     step=self._animation_step, callback=callback)
        animation()

    def _drop(self, position):  # pylint: disable=unused-argument
        """Handles the dropping of the dragged connection

        Parameters:
            position (tuple<int, int>): The position where the connection was
                                        dropped
        """
        if not self._playing:
            return

        if self._game.is_resolving():
            return

        self._grid_view.clear_dragged_connections()
        self._grid_view.clear_connections()

        self.animate(self._game.drop())

    def _connect(self, start, end):
        """Draws a connection from the start point to the end point

        Parameters:
            start (tuple<int, int>): The position of the starting dot
            end (tuple<int, int>): The position of the ending dot
        """

        if self._game.is_resolving():
            return
        if not self._playing:
            return
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

        if self._game.is_resolving():
            return
        if not self._playing:
            return

        tile_position = self._grid_view.xy_to_rc(position)

        if tile_position is not None:
            cell = self._game.grid[tile_position]
            dot = cell.get_dot()

            if dot and self._game.connect(tile_position):
                self._grid_view.clear_dragged_connections()
                return

        kind = self._game.get_connection_kind()

        if not len(self._game.get_connection_path()):
            return

        start = self._game.get_connection_path()[-1]

        if start:
            self._grid_view.draw_dragged_connection(start, position, kind)

    @staticmethod
    def remove(*_):
        """Deprecated in 1.1.0"""
        raise DeprecationWarning("Deprecated in 1.1.0")

    def draw_grid(self):
        """Draws the grid"""
        self._grid_view.draw(self._game.grid)

    def reset(self):
        """Resets the game"""
        self._game.reset()

        self.draw_grid()
        self._objectives.reset()

        self._infopanel.reset_infopanel()
        self._intervalbar.reset_interval_bar()


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
        self._game.companion.charge()
        self._intervalbar.changing_progress(self._game.companion.get_charge())

        if self._playing:
            if self._game.companion.is_fully_charged():
                self._intervalbar.changing_progress(6)
                self._game.companion.reset()
                self._intervalbar.changing_progress(0)
                self._intervalbar.reset_interval_bar()
                steps = self._game.companion.activate(self._game)
                self._refresh_status()
                return self.animate(steps)
            else:
                self._intervalbar.changing_progress(self._game.companion.get_charge())

        if self._objectives.is_complete():
            if askyesno('Verify', '？？？?'):
                self._master.destroy()
            else:
                self.reset()
        return True


    def _refresh_status(self):
        """Handles change in score"""

        score = self._game.get_score()
        self._infopanel.set_score(score)
        self._infopanel.set_remaining_dots(self._objectives.get_status())
        self._infopanel.set_turns(self._game.get_moves())
        if self._objectives.is_complete():
            self._objectives.reset()
            self.reset()

    def menu(self, master):
        
        self._menu = tk.Menu(master)
        master.config(menu=self._menu)
        self._file_menu = tk.Menu(self._menu)
        self._menu.add_cascade(label="File", menu=self._file_menu)
        self._file_menu.add_command(label="New Game", command=self.reset)
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Exit", command=self.exit_game)

    def exit_game(self):
        reply = messagebox.askquestion(type=messagebox.YESNOCANCEL,
                                       title="Quit",
                                       message="Do you really want to quit?")
        if reply:
            self._master.destroy()
        else:
            return True


def main():
    """Sets-up the GUI for Dots & Co"""
    # Write your GUI instantiation code here
    root = tk.Tk()
    app = DotsApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
