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
try:
    import pygame
    HAS_PG=True
except ModuleNotFoundError:
    HAS_PG = False
    print("module not find.Please run 'pip3 install pygame' on bash")

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
        """Infor panel constructor ,init calss purpose

        Parameter:
                master(tk.Tk()):The parent farame
                _dots_list(list):list containing all dots and objectives

        """
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
        """ sets up turns
            Parameter:
                turn(int):turns remain
        """
        self.movesLabel['text'] = turn

    def set_score(self, score):
        """ sets up score
            Parameter:
                score(int):how many score needs to added
        """
        self.uselessImageLabel['text'] = score

    def set_status(self, imageId, count, obj):
        """ set up the goal frame in ordet to well display the remain dots

            Parameter:
                image_id(str):image address
                count<int>:the objective remains
                obj<BasicDot>:the basic dot object
        """

        self.statusLabel = tk.Label(self.dotsFrame,
                                    image=imageId,
                                    text=count, compound="top")
        self.statusLabel.pack(side=tk.RIGHT)

        self.dotsList.append(self.statusLabel)

    def set_remaining_dots(self, obj):
        """set up the the ramin dots

            Parameter:
                obj<BasicDot>:the basic dot object
        """
        for label,length in zip(self.dotsList, range(len(self.dotsList))):
            label["text"]=obj[length][1]



class IntervalBar(tk.Canvas):

    def __init__(self, master):
        """init interval bar class and setup some status"""
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
        """draw a interval bar retangle"""
        for coordinate in self.rectangleCoordinates:
            a, b, c, d = coordinate
            self.canvas.create_rectangle(a, b, c, d)

    def fill_rectangle_blue(self, coordinate):
        """fill the interval bar as blue
           Parameter:
                coordiante(list):the list of the coordiante

        """
        x, y, z, w = coordinate
        self.canvas.create_rectangle(x, y, z, w, fill='#508ebf')

    def fill_rectangle_blank(self, coordinate):
        """fill the interval bar as white
           Parameter:
                coordiante(list):the list of the coordiante

        """

        self.canvas.create_rectangle(coordinate[0],
                                     coordinate[1],
                                     coordinate[2],
                                     coordinate[3], fill='white')

    def charging_progress(self, fully_charge):
        """let the interval bat relate to charge
           Parameter:
                fully_charge(companion):the object of companion

        """

        if fully_charge.is_fully_charged() :
            for coordinate in self.rectangleCoordinates:
                self.fill_rectangle_blank(coordinate)
        else:
            for i in range(fully_charge.get_charge()):
                self.fill_rectangle_blue(self.rectangleCoordinates[i])

    def fill_all_blank(self):
        """fill all interal bar to white"""
        for coordinate in self.rectangleCoordinates:
            self.fill_rectangle_blank(coordinate)


class AnchorDot(BasicDot):
    """A AnchorDot dot can be activaed when it reach the bottom line"""
    DOT_NAME = "anchor"

    def can_connect(self):
        return False
    def get_view_id(self):
        return "{}/{}".format(self.get_name(), self.get_kind())



class CompanionDot(BasicDot):
    """A companion dot"""
    DOT_NAME = "Companion"

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), + self.get_kind())


class BuffaloCompanion(AbstractCompanion):
    """The companion relate to Anchor Dot"""
    NAME = 'Buffalo'

    def __init__(self):
        """init calss"""
        super().__init__()

    def activate(self, game):
        """setup activate event .The function main purpose if avoid the error occurs"""
        pass



# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """
        if HAS_PG:
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

        self._objectives = ObjectiveManager(list(objectives))
        
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

        self._game = CompanionGame({BasicDot: 1,
                                    CompanionDot: 1}, companion=BuffaloCompanion(), objectives=self._objectives,
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

    def random_generator(self,length):
        """generat the random postion

        return:
                postion_list(list(tuple(<int,int>))):list containing random positions on grid


        """
        postion_list = []
        for b in range(length):
            postion_list.append((random.randint(0,7),random.randint(0,7)))
        return postion_list

    def set_wildcardDots(self):
        """setup wildcard dots"""
        for position in self.random_generator(4):
            if position not in self._dead_cells:
                self._game.grid[position].set_dot(WildcardDot())

    def set_anchorDots(self):
        """set up anchor dots"""

        for position in self.random_generator(4):
            if position not in self._dead_cells:
                self._game.grid[position].set_dot(AnchorDot('anchor'))
    def isActivateAnchorDot(self):
        """check if anchor dot activate

            return
                bool:if the anchor dot activated
        """
        for data in self._game.grid.items():
            position,cell = data
            pos = position[0]

            if pos == 7 and isinstance(cell.get_dot(),AnchorDot):
                return True
        return False

    def activateAnchorDots(self):
        """Fisrt check is anchor activaed if activated then run function to clear the last line dots"""
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
        self._objectives.reset()
        self.set_anchorDots()
        self.set_wildcardDots()
        self.draw_grid()
        self._infoPanel.set_moves(self._game.get_moves())
        self._intervalBar.fill_all_blank()
        self._infoPanel.set_remaining_dots(self._objectives.get_status())
        self._playing=True

    def check_game_over(self):
        """Checks whether the game is over and shows an appropriate message box if so"""

        state = self._game.get_game_state()
        # print(state)
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
            self._intervalBar.charging_progress(self._game.companion)
            if self._game.companion.is_fully_charged():
                self._game.companion.reset()
                # self._intervalBar.charging_progress(self._game.companion)
                steps = self._game.companion.activate(self._game)
                self.set_wildcardDots()
                self._refresh_status()
                return self.animate(steps)

        else:
            if askyesno('Exit', 'wanna play again?'):
                self.reset()
            else:
                self._master.destroy()


    def _refresh_status(self):
        """Handles change in score"""

        self._infoPanel.set_score(self._game.get_score())
        self._infoPanel.set_moves(self._game.get_moves())
        self._infoPanel.set_remaining_dots(self._objectives.get_status())
        # if self._objectives.is_complete():
        #     self._objectives.reset()
        #     self.reset()

    def _menuBar(self, master):
        """menu setup"""
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
        """For handle music pause"""
        pygame.mixer.music.pause()
    def play(self):
        """for handle muisc replay"""
        pygame.mixer.music.unpause()
    def exit(self):
        """for handle exit event"""
        self._replyMessage = messagebox.askquestion(type=messagebox.YESNOCANCEL,
                                                    title="Exit game",
                                                    message="Do you want to exit?\nMake sure you save your changes")
        if self._replyMessage:
            self._master.destroy()






def main():
    """Sets-up the GUI for Dots & Co"""
    # Write your GUI instantiation code here
    root = tk.Tk()
    app = DotsApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
