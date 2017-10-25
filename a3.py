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

import pygame

from companion import AbstractCompanion

try:
    from PIL import ImageTk, Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from view import GridView, ObjectivesView
from game import DotGame, ObjectiveManager, CompanionGame
from dot import BasicDot, WildcardDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = ""
__email__ = ""
__date__ = ""

__version__ = "1.1.1"

def load_image_path(image_id, size=None, prefix=None, suffix='.png'):
    """(str) Returns the filepath to an image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory)
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
    segments = []
    if prefix:
        segments.append(prefix)

    if size is not None:
        segments.append("{}x{}".format(*size))

    segments.append(image_id + suffix)

    return os.path.join(*segments)


def load_image_pil(image_id, size, prefix, suffix='.png'):
    """(ImageTk.PhotoImage) Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory)
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
    file_path = load_image_path(image_id, size=size, prefix=prefix, suffix=suffix)
    return ImageTk.PhotoImage(Image.open(file_path))


def load_image_tk(image_id, size, prefix, suffix='.gif'):
    """(tk.PhotoImage) Returns a tkinter photo image

    Parameters:
        image_id (str): The filename identifier of the image
        size (tuple<int, int>): The size of the image to load
        prefix (str): The prefix to prepend to the filepath (i.e. root directory)
        suffix (str): The suffix to append to the filepath (i.e. file extension)
    """
    file_path = load_image_path(image_id, size=size, prefix=prefix, suffix=suffix)
    return tk.PhotoImage(file=file_path)
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



# Define your classes here

class InfoPanel(tk.Frame):
    def __init__(self, master):

        self.dotsList = []
        self.infoFrame = tk.Frame(master)
        self.movesFrame = tk.Frame(self.infoFrame)

        self.companionFrame = tk.Frame(self.infoFrame)

        self.dotsFrame = tk.Frame(self.infoFrame)

        self.movesLabel = tk.Label(self.movesFrame,
                                   text="", font=(None, 30))

        # Set center image and score next to image
        self.uselessImage = tk.PhotoImage(file="images/companions/useless.gif")
        self.uselessImageLabel = tk.Label(self.companionFrame, text="",
                                          font=(None, 40),
                                          image=self.uselessImage,
                                          compound="right")

        # Packing all the frames
        self.infoFrame.pack()
        self.movesFrame.pack(side=tk.LEFT, ipadx=50)
        self.companionFrame.pack(side=tk.LEFT, expand=True)
        self.dotsFrame.pack(side=tk.LEFT, expand=True)
        self.movesLabel.pack(anchor=tk.W, expand=False)
        self.uselessImageLabel.pack(side=tk.RIGHT)

    def set_moves(self, turn):
        self.movesLabel.config(text="{}".format(turn))

    def set_score(self, score):
        self.uselessImageLabel.config(text="{}".format(score))

    def set_status(self, image_id, count, obj):

        self.statusLabel = tk.Label(self.dotsFrame,
                                    image=image_id,
                                    text=count, compound="top")
        self.statusLabel.pack(side=tk.RIGHT)

        self.dotsList.append(self.statusLabel)

    def set_remaining_dots(self, obj):
        for label,length in zip(self.dotsList, range(len(self.dotsList))):
            label.config(text=obj[length][1])



class IntervalBar(tk.Canvas):
    def __init__(self, master):

        self.canvas = tk.Canvas(master, bg="white",
                                width=500, height=30)
        
        self.canvas.pack(side=tk.TOP)
        self.rectangleCoordinates = [(80, 10, 140, 30),
                                     (140, 10, 200, 30),
                                     (200, 10, 260, 30),
                                     (260, 10, 320, 30),
                                     (320, 10, 380, 30),
                                     (380, 10, 440, 30)]
        self.draw_rectangles()

    def draw_rectangles(self):
        
        self.canvas.create_rectangle(80, 10, 140, 30)
        self.canvas.create_rectangle(140, 10, 200, 30)
        self.canvas.create_rectangle(200, 10, 260, 30)
        self.canvas.create_rectangle(260, 10, 320, 30)
        self.canvas.create_rectangle(320, 10, 380, 30)
        self.canvas.create_rectangle(380, 10, 440, 30)

    def fill_rectangle_blue(self, coordinate):
        x, y, z, w = coordinate
        self.canvas.create_rectangle(x, y, z, w, fill='#508ebf')

    def fill_rectangle_blank(self, coordinate):
        x, y, z, w = coordinate
        self.canvas.create_rectangle(x, y, z, w, fill='white')

    def charging_progress(self, charge):
        if charge == 6:
            for coordinate in self.rectangleCoordinates:
                x, y, z, w = coordinate
                self.fill_rectangle_blank(coordinate)
        else:
            for i in range(charge):
                self.fill_rectangle_blue(self.rectangleCoordinates[i])

    def fill_all_blank(self):
        for coordinate in self.rectangleCoordinates:
            x, y, z, w = coordinate
            self.fill_rectangle_blank(coordinate)


class AnchorDot(BasicDot):

    DOT_NAME = "anchor"

    def can_connect(self):
        return False
    def get_view_id(self):
        return "{}/{}".format(self.get_name(), self.get_kind())



class CompanionDot(BasicDot):
    """A companion dot"""

    DOT_NAME = "Companion"

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True

    def adjacent_activated(self, position, game, activated, activated_neighbours, has_loop=False):
        pass

    def after_resolved(self, position, game):
        pass

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), + self.get_kind())

    def can_connect(self):
        return True

class BuffaloCompanion(AbstractCompanion):
    NAME = 'Buffalo'

    def __init__(self):
        super().__init__()

    def activate(self, game):
        pass



# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("Yellow.mp3")
            pygame.mixer.music.play()
        except pygame.error:
            pass

        self._master = master
        master.title("Dots & Co")

        self._infoPanel = InfoPanel(master)
        self._intervalBar = IntervalBar(master)
        self._menuBar(master)
        self._playing = True

        self._imageManager = ImageManager('images/dots/', loader=load_image)
        # self._imageManager.

        # Game
        counts = [10, 15, 25, 25]
        random.shuffle(counts)
        # randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], counts)

        self._objectives = ObjectiveManager(objectives)
        
        self._objectivesView = ObjectivesView(master,
                                              image_manager=self._imageManager)
        for data in self._objectives.get_status():
            self._infoPanel.set_status(self._objectivesView.load_image(data[0], (20, 20)),
                                       data[1], data[0])
        self._size=(8, 8)
        # Game
        self._dead_cells = {(2, 2), (2, 3), (2, 4),
                      (3, 2), (3, 3), (3, 4),
                      (4, 2), (4, 3), (4, 4),
                      (0, 7), (1, 7), (6, 7), (7, 7)}

        self._game = CompanionGame({BasicDot: 1}, companion=BuffaloCompanion(), objectives=self._objectives,
                                        kinds=(1, 2, 3, 4), size=self._size,
                                        dead_cells=self._dead_cells)
        self.set_wildcardDots()
        self.set_anchorDots()


        # The following code may be useful when you are implementing task 2:
        # Grid View
        self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._imageManager)
        self._grid_view.pack()
        self._grid_view.draw(self._game.grid)
        self.draw_grid_borders()


        # Events
        self.bind_events()
        self._refresh_status()

    def set_wildcardDots(self):
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
            if position not in self._dead_cells:
                self._game.grid[position].set_dot(WildcardDot())

    def set_anchorDots(self):
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
            if position not in self._dead_cells:
                self._game.grid[position].set_dot(AnchorDot('anchor'))
    def isActivateAnchorDot(self):
        for data in self._game.grid.items():
            position,cell = data
            pos = position[0]

            if pos == 7 and isinstance(cell.get_dot(),AnchorDot):
                return True
        return False

    def activateAnchorDots(self):
        if self.isActivateAnchorDot():
            tempSet=[]
            for data in self._game.grid.items():
                position,cell = data
                pos = position[0]

                if pos == 7 and isinstance(cell.get_dot(),AnchorDot):
                    for num in range(8):
                        new_position = (pos, num)
                        tempSet.append(new_position)

            self.animate(self._game.activate_all(set(tempSet)))





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


        # print(list(steps))
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

        # self._grid_view.draw(self._game.grid)
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

    def remove(self, *positions):
        """Attempts to remove the tiles at the given positions
        """
        raise DeprecationWarning()


    def draw_grid(self):
        """Draws the grid"""
        self._grid_view.draw(self._game.grid)

    def reset(self):
        """Resets the game"""
        self._game.reset()
        self.set_anchorDots()
        self.draw_grid()
        self._objectives.reset()
        self._infoPanel.set_moves(self._game.get_moves())
        self._intervalBar.fill_all_blank()
        self._infoPanel.set_remaining_dots(self._objectives.get_status())

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

        self.check_game_over()

        if self._playing:
            self.activateAnchorDots()
            self._game.companion.charge()
            self._intervalBar.charging_progress(self._game.companion.get_charge())
            if self._game.companion.is_fully_charged():
                self._game.companion.reset()
                self._intervalBar.charging_progress(0)
                steps = self._game.companion.activate(self._game)
                self.set_wildcardDots()
                self._refresh_status()
                return self.animate(steps)

        else:
            if askyesno('Verify', 'Do you want to play again?'):
                self.reset()
            else:
                self._master.destroy()

        return True

    def _refresh_status(self):
        """Handles change in score"""

        self._infoPanel.set_score(self._game.get_score())
        self._infoPanel.set_moves(self._game.get_moves())
        self._infoPanel.set_remaining_dots(self._objectives.get_status())
        if self._objectives.is_complete():
            self._objectives.reset()
            self.reset()

    def _menuBar(self, master):
        
        self._menuBar = tk.Menu(master)
        master.config(menu=self._menuBar)
        self._fileMenu = tk.Menu(self._menuBar)
        self._menuBar.add_cascade(label="File", menu=self._fileMenu)
        self._fileMenu.add_command(label="New Game", command=self.reset)
        self._fileMenu.add_command(label="Music:pause ", command=self.pause)
        self._fileMenu.add_command(label="Music:play ", command=self.play)
        self._fileMenu.add_separator()
        self._fileMenu.add_command(label="Exit", command=self.exit)

    def pause(self):
        pygame.mixer.music.pause()
    def play(self):
        pygame.mixer.music.unpause()
    def exit(self):

        self._replyMessage = messagebox.askquestion(type=messagebox.YESNOCANCEL,
                                                    title="Exit game",
                                                    message="Do you want to exit?\nMake sure you save your changes")
        if self._replyMessage:
            self._master.destroy()
        else:
            return True


    def load_buffaloGame(self):
        pass


class AutoPlayingButton(tk.Frame):

    def __init__(self, master):

        self._master = master

        self.autoPlayingButton = tk.Button(master, text="AutoPlay",
                                            command=self.autoPlaying,
                                            )
        self.autoPlayingButton.pack()

    def autoPlaying(self):
        pass

def main():
    """Sets-up the GUI for Dots & Co"""
    # Write your GUI instantiation code here
    root = tk.Tk()
    app = DotsApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
