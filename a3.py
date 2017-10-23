"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil

import tkinter as tk
from tkinter.messagebox import showinfo, askyesno
import os
import random

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

__author__ = "Yuqi Yao"

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


# Define your classes here

class InfoPanel(tk.Frame):
	"""A class constructs moves, score, image, and objectives"""

	def __init__(self, master):
		"""Constructs information panel containing moves, score, image, and objectives

		Parameters:
			ImageContainer(dict):a dict image being key, location being value
			DotsList(list): a list that stores dots and objectives
		"""
		self.ImageContainer = {}
		self.DotsList = []
		self.InfoFrame = tk.Frame(master)
		self.InfoFrame.configure(height=10, width=1000)
		self.TurnsFrame = tk.Frame(self.InfoFrame)


		self.CompanionsFrame = tk.Frame(self.InfoFrame)


		self.DotsFrame = tk.Frame(self.InfoFrame)

		self.TurnsLabel = tk.Label(self.TurnsFrame,
								   text="", font=(None, 30))
		# Set center image and score next to image
		self.CenterImage = tk.Label(self.CompanionsFrame, text="",
									font=(None, 40),
									image=self.image_register("useless.gif").get_image("useless.gif"),
									compound="right",
									width=200,
									height=150)

		# Packing all the frames
		self.InfoFrame.pack()
		self.TurnsFrame.pack(side=tk.LEFT, ipadx=50)
		self.CompanionsFrame.pack(side=tk.LEFT, expand=True)
		self.DotsFrame.pack(side=tk.LEFT, expand=True)
		self.TurnsLabel.pack(anchor=tk.W, expand=False)
		self.CenterImage.pack(side=tk.RIGHT)

	def set_moves(self, move):
		"""Set turns after each move"""
		self.TurnsLabel.config(text="{}".format(move))

	def get_image(self, image):
		"""Return image in container. Error if no image found"""
		return self.ImageContainer.get(image, "Error")

	def config_image(self,imageId):
		"""Set the image for panel"""
		self.CenterImage.config(image=imageId)

	def set_status(self, image, move, objective):
		"""Set objectives and dots to be right side """
		self.StatusLabel = tk.Label(self.DotsFrame,
									image=image,
									text=move, compound="top")
		self.StatusLabel.pack(side=tk.RIGHT)
		self.DotsList.append([objective.get_kind(),
							  objective.get_name(),
							  move,
							  self.StatusLabel])
	def reset_status(self):
		for data in self.DotsList:
			data[-1].pack_forget()
		self.DotsList.clear()


	def set_score(self, score):
		"""Set score for playing"""
		self.CenterImage.config(text="{}".format(score))


	def set_dots_remaining(self, objective):
		"""Refresh remaining dots after each move"""

		for num in range(len(self.DotsList)):
			if objective[num][1] is not self.DotsList[num][2]:
				self.DotsList[num][3].config(text=objective[num][1])
				self.DotsList[num][2] = objective[num][1]



	# functionality
	def image_register(self, image=None, load_all=False):
		"""Register an image; raise key error if none image found"""
		images = {
			"useless.gif": "images/companions/useless.gif",
			"penguin.gif": "images/companions/penguin.gif",
			"penguin.png": "images/companions/penguin.png",
			"penguin_large.png": "images/companions/penguin_large.png",
			"buffalo_large.png": "images/companions/buffalo_large.png",
			"deer_large.png": "images/companions/deer_large.png",
			"eskimo.png": "images/companions/eskimo.png",
			"goat.png": "images/companions/goat.png"
		}

		if image is None and not load_all:
			raise KeyError("Sorry image id is important")
		else:
			if load_all:
				for name, location in images.items():
					self.ImageContainer[name] = tk.PhotoImage(file=location)
			else:
				if image.split(".")[1]=="gif":
					self.ImageContainer[image] = tk.PhotoImage(file=images[image])
				else:
					self.ImageContainer[image]=ImageTk.PhotoImage(file=images[image])
				return self


class IntervalBar(tk.Canvas):
	"""A class that constructs progress bar"""

	def __init__(self, master, length, num_of_rectangles, x=(0, 0)):
		"""Constructs canvas for progressing bar

		Parameters:
			ProgressCount(int): Number of progress after each move
			num_of_rectangles(int): An integer represents number of rectangle to draw
			length(int): Length of each small rectangle
			x(tuple):Starting point of rectangle
		"""

		self.ProgressCount = 0
		self.num_of_rectangles = num_of_rectangles
		X1, X2 = x
		Y1 = 10
		Y2 = 30
		self.canvas_coordinate = [
			(X1 + length * i, Y1, X2 + length * (i + 1), Y2)
			for i in range(0, num_of_rectangles)
		]


		self._canvas = tk.Canvas(master, bg="white",
								 width=500, height=30)
		self._canvas.pack(side=tk.TOP)

		self.draw_rectangle()


	def draw_rectangle(self):
		"""Draws rectangles at given position"""
		for coordinate in self.canvas_coordinate:
			x, y, h, l = coordinate
			self._canvas.create_rectangle(x, y, h, l)

	def blue_rectangle(self, coordinate):
		"""Fill rectangle with blue"""
		x, y, h, l = coordinate
		self._canvas.create_rectangle(x, y, h, l, fill='#508ebf')

	def white_rectangle(self, coordinate):
		"""Fill rectangle with white"""
		x, y, h, l = coordinate
		self._canvas.create_rectangle(x, y, h, l, fill='white')

	def config_progress(self, charge):
		"""Config charging progress at given charge"""
		if charge == 6:

			for coordinate in range(0, 6):
				self.white_rectangle(list(self.canvas_coordinate[coordinate]))
		else:

			for coordinate in range(charge):
				self.blue_rectangle(list(self.canvas_coordinate[coordinate]))

	def get_turn(self):
		"""(int)Return the progress move"""
		return self.ProgressCount
	def unpack_rectangle(self):
		for coordinate in self.canvas_coordinate:
			x, y, h, l = coordinate
			self._canvas.create_rectangle(x, y, h, l, fill='white')


class EskimoCompanion(AbstractCompanion):
	"""A class that builds function for EskimoCompanion"""
	NAME = 'Eskimo'

	def __init__(self):
		super().__init__()

	def activate(self, game):
		"""Activates the companion's ability

		Parameters:
			game (DotGame): The game being player

		Yield:
			None: Once for each step in an animation

		Notes:
			Typically, this method will return:
				- game.activate_all(positions): If positions need to be activated
				- None: If no animation needs to occur
		"""

		def get_companion_dot():
			"""Return generator"""
			for position, dots in game.grid.items():
				if dots.get_dot() is not None and isinstance(dots.get_dot(), SwirlDot):
					yield (position, dots.get_dot())

		positionList = []
		for pos, dts in get_companion_dot():
			for possition in game.grid.get_adjacent_cells(pos):
				try:
					game.grid[possition].set_dot(BasicDot(int(dts.get_view_id().split("/")[1])))
				except AttributeError:
					pass
			positionList.append(pos)

		return game.activate_all(set(positionList))

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


class SwirlDot(BasicDot):
	DOT_NAME = "swirl"

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

		self.charge = 0
		self.InfoPanel = InfoPanel(master)
		self.IntervalBar = IntervalBar(master, 60, 6, (80, 80))
		self.menu(master)
		self._master = master
		master.title("Dots & Co")
		self._playing = True

		self.ImageManager = ImageManager('images/dots/', loader=load_image_tk)

		# Game
		count = [10, 15, 25, 25]
		random.shuffle(count)
		# randomly pair count with each kind of dot
		objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], count)

		self._objectives = ObjectiveManager(list(objectives))
		self.ObjectivesView = ObjectivesView(master,
											 image_manager=self.ImageManager)

		# Game
		self.dead_cells = {(2, 2), (2, 3), (2, 4),
					  (3, 2), (3, 3), (3, 4),
					  (4, 2), (4, 3), (4, 4),
					  (0, 7), (1, 7), (6, 7), (7, 7)}

		self._game = CompanionGame({BasicDot: 1,
									CompanionDot: 1}, companion=EskimoCompanion(), objectives=self._objectives,
								   kinds=(1, 2, 3, 4), size=(8, 8),
								   dead_cells=self.dead_cells)
		RandomRow = [random.randint(1, 7) for num in range(4)]
		RandomColumn = [random.randint(1, 7) for num in range(4)]
		EskimoCompanionPosition = set(zip(RandomRow, RandomColumn))

		for position in EskimoCompanionPosition:
			if position not in self.dead_cells:
				self._game.grid[position].set_dot(SwirlDot(random.randint(1, 5)))
		self.reset_dots_status()

		# Grid View
		self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self.ImageManager)
		self._grid_view.pack()
		self._grid_view.draw(self._game.grid)
		self.draw_grid_borders()

		# Events
		self.bind_events()

		# Set initial score again to trigger view update automatically
		self._refresh_status()


	def reset_dots_status(self):

		for status in self._objectives.get_status():
			self.InfoPanel.set_status(self.ObjectivesView.load_image(status[0], (20, 20)),
										status[1],
										status[0])
	def reset_companion_status(self):

		RandomRow = [random.randint(1, 7) for num in range(4)]
		RandomColumn = [random.randint(1, 7) for num in range(4)]
		EskimoCompanionPosition = set(zip(RandomRow, RandomColumn))

		for position in EskimoCompanionPosition:
			if position not in self.dead_cells:
				self._game.grid[position].set_dot(SwirlDot(random.randint(1, 5)))


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
		self.reset_companion_status()
		self.draw_grid()
		self._objectives.reset()
		self.InfoPanel.reset_status()
		self.InfoPanel.set_moves(20)
		self.IntervalBar.config_progress(0)
		self.IntervalBar.unpack_rectangle()
		self.reset_dots_status()

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
		self.IntervalBar.config_progress(self._game.companion.get_charge())
		if self._playing:
			if self._game.companion.is_fully_charged():
				self.IntervalBar.config_progress(6)
				self._game.companion.reset()
				self.IntervalBar.config_progress(0)
				self.IntervalBar.unpack_rectangle()
				steps = self._game.companion.activate(self._game)

				self.reset_companion_status()
				self._refresh_status()
				return self.animate(steps)
			else:
				self.IntervalBar.config_progress(self._game.companion.get_charge())
		if self._objectives.is_complete == True:
			if askyesno('Verify', '？？？?'):
				self._master.destroy()
			else:
				self.reset()
		return True

	# Need to check whether the game is over

	def _refresh_status(self):
		"""Handles change in score"""

		self.InfoPanel.set_score(self._game.get_score())
		self.InfoPanel.set_moves(self._game.get_moves())
		self.InfoPanel.set_dots_remaining(self._objectives.get_status())
		if self._objectives.is_complete():
			self._objectives.reset()
			self.reset()

	def menu(self, master):
		"""filemenu bar on top"""
		menubar = tk.Menu(master)
		master.config(menu=menubar)
		filemenu = tk.Menu(menubar)
		menubar.add_cascade(label="File", underline=0, menu=filemenu)
		#submenu = tk.Menu(filemenu)
		filemenu.add_cascade(label='New Game', underline=0, command=self.reset)
		#submenu.add_command(label="Companion", command=self.load_game)
		#submenu.add_command(label="No Companion", command=self.reset)

		filemenu.add_separator()
		filemenu.add_command(label="Exit", underline=0, command=self.exit)

	def exit(self):

		if askyesno('!', 'Do you wanna quit?'):
			self._master.destroy()

		else:
			showinfo('No')

	def load_game(self):
		pass
	def get_companion_dot(self):
		"""Return companion dot required"""
		for position, dots in self._game.grid.items():
			if dots.get_dot() is not None and isinstance(dots.get_dot(), SwirlDot):
				yield (position, dots.get_dot())



def main():
	"""Sets-up the GUI for Dots & Co"""
	# Write your GUI instantiation code here
	root = tk.Tk()
	app = DotsApp(root)

	root.mainloop()


if __name__ == "__main__":
	main()
