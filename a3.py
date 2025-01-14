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
except ImportError:
	HAS_PIL = False

from view import GridView, ObjectivesView
from game import DotGame, ObjectiveManager
from dot import BasicDot
from util import create_animation, ImageManager

# Fill these in with your details
__author__ = "Zian Wang (s4457600)"
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
COMPANIONSMANAGER = {
	"useless.gif": "images/companions/useless.gif",
	"penguin.gif": "images/companions/penguin.gif",
	"penguin.png": "images/companions/penguin.png",
	"penguin_large.png": "images/companions/penguin_large.png",
}

# Define your classes here

class InfoPanel(tk.Frame):
	def __init__(self, master):
		self._imgContainer = {}
		self.dotsSerialize = []
		info_frame = tk.Frame(master)
		_turns_frame = tk.Frame(info_frame)


		companions_frame = tk.Frame(info_frame)

		self.dots_frame = tk.Frame(info_frame)

		self._turns_label = tk.Label(_turns_frame,
									 text="jkhjjkhkjhs", font=(None, 30))

		# Set center image and score next to image
		self.image_register("useless.gif")
		self._useless_image = tk.Label(companions_frame, text="",
									   font=(None, 40),
									   image=self.get_image("useless.gif"),
									   compound="right")


		# Packing all the frames
		info_frame.pack()
		_turns_frame.pack(side=tk.LEFT, ipadx=50)
		companions_frame.pack(side=tk.LEFT, expand=True)
		self.dots_frame.pack(side=tk.LEFT, expand=True)
		self._turns_label.pack(anchor=tk.W, expand=False)
		self._useless_image.pack(side=tk.RIGHT)




	def set_turns(self, turn):
		self._turns_label.config(text="{}".format(turn))


	def get_image(self, imageId):
		return self._imgContainer.get(imageId, "Sorry Please register image first")

	def set_image(self,imageId):
		self._useless_image.config(image=imageId)
	def set_status(self, image_id, count, obj):


		self._status_label = tk.Label(self.dots_frame,
									  image=image_id,
									  text=count, compound="top")
		self._status_label.pack(side=tk.RIGHT)

		self.dotsSerialize.append([obj.get_kind(),
								   obj.get_name(),
								   count,
								   self._status_label])

	def set_score(self, score):
		self._useless_image.config(text="{}".format(score))

	def set_docts_step(self, obj):

		for num in range(len(self.dotsSerialize)):
			if obj[num][1] is not self.dotsSerialize[num][2]:
				self.dotsSerialize[num][3].config(text=obj[num][1])
				self.dotsSerialize[num][2] = obj[num][1]

	# functionality
	def image_register(self, imageId=None, load_all=False):
		if imageId is None and not load_all:
			raise KeyError("Sorry image id is important")
		else:
			if load_all:
				for id, path in COMPANIONSMANAGER:
					self._imgContainer[id] = tk.PhotoImage(file=COMPANIONSMANAGER[path])
			else:
				self._imgContainer[imageId] = tk.PhotoImage(file=COMPANIONSMANAGER[imageId])

class IntervalBar(tk.Canvas):


	def __init__(self, master,displacement,numBar,x=(0,0)):
		self.count=0
		self.numBar=numBar
		X1,X2=x
		Y1=10
		Y2=30
		self.canvas_coordinate = [
			(X1 + displacement * num, Y1, X2 + displacement * (num + 1), Y2)
			for num in range(0,numBar)
		]


		self._canvas = tk.Canvas(master, bg="white",
										width=500, height=30)
		self._canvas.pack(side=tk.TOP)

		self.draw_rectangle()


	def draw_rectangle(self):
		for data in self.canvas_coordinate:
			x,y,h,l=data
			self._canvas.create_rectangle(x,y,h,l)


	def fill_rectangle_blue(self, data):
		x, y, h, l = data
		self._canvas.create_rectangle(x,y,h,l, fill='blue')

	def fill_rectangle_blank(self,data):
		for data in data:
			x, y, h, l = data
			self._canvas.create_rectangle(x, y, h, l, fill='white')

	def config_progress(self):
		if self.count<self.numBar:
			self.fill_rectangle_blue(list(self.canvas_coordinate[self.count]))
			self.count += 1
		else:
			self.count=0
			self.fill_rectangle_blank(self.canvas_coordinate)













# You may edit as much of DotsApp as you wish
class DotsApp:
	"""Top level GUI class for simple Dots & Co game"""

	def __init__(self, master):
		"""Constructor

		Parameters:
			master (tk.Tk|tk.Frame): The parent widget
		"""

		# ------------------------
		self._info_panel = InfoPanel(master)
		self._interval_bar = IntervalBar(master, 60, 6, (80, 80))
		# --------------------------
		self._master = master

		self._playing = True

		self._image_manager = ImageManager('images/dots/', loader=load_image)

		# Game
		counts = [10, 15, 25, 25]
		random.shuffle(counts)
		# randomly pair counts with each kind of dot
		objectives = zip([BasicDot(1), BasicDot(2), BasicDot(4), BasicDot(3)], counts)

		self._objectives = ObjectiveManager(objectives)
		# --------------------------------
		self._objectivesView = ObjectivesView(master,
											  image_manager=self._image_manager)
		for data in self._objectives.get_status():
			self._info_panel.set_status(self._objectivesView.load_image(data[0], (20, 20)),
										data[1],
										data[0])
		# --------------------------------
		# Game
		dead_cells = {(2, 2), (2, 3), (2, 4),
					  (3, 2), (3, 3), (3, 4),
					  (4, 2), (4, 3), (4, 4),
					  (0, 7), (1, 7), (6, 7), (7, 7)}
		self._game = DotGame({BasicDot: 1}, objectives=self._objectives, kinds=(1, 2, 3, 4), size=(8, 8),
							 dead_cells=dead_cells)

		# The following code may be useful when you are implementing task 2:
		# for i in range(0, 4):
		#     for j in range(0, 2):
		#         position = i, j
		#         self._game.grid[position].set_dot(BasicDot(3))
		# self._game.grid[(7, 3)].set_dot(BasicDot(1))

		# Grid View
		self._grid_view = GridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
		self._grid_view.pack()
		self._grid_view.draw(self._game.grid)
		self.draw_grid_borders()

		# Events
		self.bind_events()

		# Set initial score again to trigger view update automatically
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
		print(step_name)
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

		# Useful for when implementing a companion
		# if self._game.companion.is_fully_charged():
		#     self._game.companion.reset()
		#     steps = self._game.companion.activate(self._game)
		#     self._refresh_status()
		#
		#     return self.animate(steps)
		self._interval_bar.config_progress()

		# Need to check whether the game is over
		raise NotImplementedError()  # no mercy for stooges

	def _refresh_status(self):
		"""Handles change in score"""

		# Normally, this should raise the following error:
		# raise NotImplementedError()
		# But so that the game can work prior to this method being implemented,
		# we'll just print some information
		# Sometimes I believe Python ignores all my comments :(
		score = self._game.get_score()
		self._info_panel.set_score(score)
		self._info_panel.set_docts_step(self._objectives.get_status())
		self._info_panel.set_turns(self._game.get_moves())
		print("Score is now {}.".format(score))


def main():
	"""Sets-up the GUI for Dots & Co"""
	# Write your GUI instantiation code here
	root = tk.Tk()
	app = DotsApp(root)

	root.mainloop()


if __name__ == "__main__":
	main()
