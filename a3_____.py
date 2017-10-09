"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil

import tkinter as tk
from tkinter.messagebox import showinfo
import os
import random

try:
    from PIL import ImageTk, Image 
    HAS_PIL = True
except:
    HAS_PIL = False

from view import GridView
from game import DotGame, ObjectiveManager
from dot import BasicDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = "Yuhao Meng (s4429722)"
__email__ = "y.meng@uqconnect.edu.au"
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
load_image = load_image_pil if HAS_PIL else load_image_tk



# Define your classes here

class App(object):

    def __init__(self, master):

        self.dotsapp = DotsApp(master)  #important, make the window shows the DotsApp, and can use the method inside DotsApp class

        path = "useless.gif"
        self.img = tk.PhotoImage(file=path)
        panel = tk.Label(master, image = self.img)
        panel.pack(side=tk.LEFT)

        self._master=master
        self._master.title("Dots & Co")
        self._master.geometry("600x600")


        self._infopanel = InfoPanel(master, self)  #for the frame
        self._infopanel.pack(side=tk.LEFT)

        self._intervalbar = IntervalBar(master, self)  #for the canvas
        self._intervalbar.pack(side=tk.LEFT)
            


        menubar = tk.Menu(master)
        master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self.restart)
        filemenu.add_command(label="Exit Game", command=self.exit)


        


    def exit(self) :

        ans = tk.messagebox.askokcancel('Verify exit', 'Really quit?')
        if ans:

            #showinfo.msgbox(title='Results', message='{}'.foramt(self.dotsapp.check_game_over()))
            #tk.messagebox(title='Results', message=self.dotsapp.check_game_over())
            result = tk.messagebox.showinfo(title='Results', message='win ?')
            #self.dotsapp.check_game_over()  #doesn't work
            self._master.destroy()


    def restart(self):

        self.dotsapp.reset()

    def current_score(self):

        self._infopanel.set_score(self.dotsapp._game.get_score())

            
#######################################################################################################                         

class InfoPanel(tk.Frame):

    def __init__(self, master,parent):
        super().__init__(master)



        labelfont1 = ('times',25,'bold')  #socre
        self._remain_moves_label = tk.Label(self, text="20", fg="blue", font=labelfont1).pack(side=tk.LEFT)

        labelfont2 = ('times', 20, 'bold')  #remained moves
        self._score_label = tk.Label(self, text="0", fg="black", font=labelfont2).pack(side=tk.LEFT)


    def set_score(self,score):

        current_score="{}".format(score)
        self._score_label.config(text=current_score)

############################################################################################################


class IntervalBar(tk.Canvas):

    def __init__(self, master, parent):
        super().__init__(master)


        #progress=tk.Progressbar(self,orient=HORIZONTAL,length=100,mode='determinate')



##########################################################################################################






#for part 3, https://stackoverflow.com/questions/41943823/circular-progress-bar-using-tkinter circle bar may be useful
##############################################################################################################


# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """
        self._master = master

        self._playing = True

        self._image_manager = ImageManager('images/dots/', loader=load_image)

        # Game
        counts = [10, 15, 25, 25]
        random.shuffle(counts)
        # randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], counts)

        self._objectives = ObjectiveManager(objectives)

        # Game
        dead_cells = {(2, 2), (2, 3), (2, 4),
                      (3, 2), (3, 3), (3, 4),
                      (4, 2), (4, 3), (4, 4),
                      (0, 7), (1, 7), (6, 7), (7, 7)}
        self._game = DotGame({BasicDot: 1}, objectives=self._objectives, kinds=(1, 2, 3, 4), size=(8, 8),
                             dead_cells=dead_cells)

        # Grid View
        self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
        self._grid_view.pack()
        self._grid_view.draw(self._game.grid)
        self.draw_grid_borders()

        # Events
        self.bind_events()

        # Set initial score again to trigger view update automatically
        self._score(self._game.get_score())

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
        raise NotImplementedError()

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
        # Need to check whether the game is over
        raise NotImplementedError()  # no mercy for stooges

    def _score(self, score):  # pylint: disable=no-self-use
        """Handles change in score

        Parameters:
            score (int): The new score
        """

        # Normally, this should raise the following error:
        # raise NotImplementedError()
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information
        # Sometimes I believe Python ignores all my comments :(
        print("Score is now {}.".format(score))

        # Note: # score can also be retrieved through self._game.get_score()
####################################################################################################



#######################################################################################################
def main():
    """Sets-up the GUI for Dots & Co"""
    # TODO: Write your GUI instantiation code here

    root = tk.Tk()
    def ask_quit():

        if tk.messagebox.askokcancel("Quit","You want to quit now? "):

            root.destroy()

    root.protocol("WM_DELETE_WINDOW", ask_quit)
    app = App(root)
    root.mainloop()


    pass

if __name__ == "__main__":
    main()
    
