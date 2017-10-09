"""Dot classes for Dots & Co game mode"""

# To understand recursion, see the bottom of this file

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__version__ = "1.0.0rc3"


class AbstractDot:
    """Abstract representation of a dot"""
    DOT_NAME = "abstract"

    def __init__(self, kind):
        """Constructor

        Parameters:
             kind (*): The dot's kind
        """
        self._kind = kind

    def get_kind(self):
        """(*) Returns the kind of this dot"""
        return self._kind

    def set_kind(self, kind):
        """Sets the kind of the dot, unless the kind cannot be changed

        Parameters:
            kind (*): The kind to set the dot to
        """
        if self._kind is not None:
            self._kind = kind

    def get_view_id(self):
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        """Returns the name of this dot"""
        return cls.DOT_NAME

    # Note:
    #   The activated & activated neighbours parameters should really be an
    #   ordered set, to retain order *and* efficient lookup (position in set
    #   vs. position in list), but for simplicity, a list has been used
    def activate(self, position, game, activated):
        """
        Activates this dot

        Parameters:
            position (tuple<int, int>): The current position of the dot
            game (AbstractGame): The game currently being played
            activated (list<tuple<int, int>>): A list of all neighbouring dots that were activated
        """
        raise NotImplementedError

    def adjacent_activated(self, position, game, activated, activated_neighbours):
        """
        Called when an adjacent dot(s) is activated

        Parameters:
            position (tuple<int, int>): The current position of the dot
            game (AbstractGame): The game currently being played
            activated (list<tuple<int, int>>): A list of all neighbouring dots that were activated
            activated_neighbours (list<tuple<int, int>>): A list of all neighbouring dots that were activated
             
        Return:
            list<tuple<int, int>>: Returns a list of positions for all dots to be removed
                                   Can return None
        """
        raise NotImplementedError

    def __eq__(self, other):
        """(bool) Returns True iff other is the same kind as this dot
        
        Parameters:
            other (AbstractDot): The dot to compare this dot with
        """
        return self.get_name() == other.get_name() and self._kind == other.get_kind()

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self._kind)

    def __str__(self):
        return self.__repr__()


class BasicDot(AbstractDot):
    """A basic dot"""

    DOT_NAME = "basic"

    def activate(self, position, game, activated):
        pass

    def adjacent_activated(self, position, game, activated, activated_neighbours):
        pass

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), self.get_kind())

# To understand recursion, see the top of this file
