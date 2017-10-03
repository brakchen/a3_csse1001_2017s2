"""Factory classes for 

While quite concise, the purpose of these classes is to manage creation of instances (of dots, etc.). By having a
class managing this process, hooking into and extending this process becomes quite simple (through inheritance). This
allows for interesting things to be done, such as rigging a generator to ensure a game can be played a certain way.
"""

#
#                         /-------------\
#                        /               \
#                       /                 \
#                      /                   \
#                      |   XXXX     XXXX   |
#                      |   XXXX     XXXX   |
#                      |   XXX       XXX   |
#                      \         X         /
#                       --\     XXX     /--
#                        | |    XXX    | |
#                        | |           | |
#                        | I I I I I I I |
#                        |  I I I I I I  |
#                         \              /
#                           --         --
#                             \-------/
#                     XXX                    XXX
#                   XXXXX                  XXXXX
#                   XXXXXXXXX         XXXXXXXXXX
#                           XXXXX   XXXXX
#                             XXXXXXX
#                           XXXXX   XXXXX
#                   XXXXXXXXX         XXXXXXXXXX
#                   XXXXX                  XXXXX
#                     XXX                    XXX
#                           **************
#                           *  BEWARE!!  *
#                           **************
#                       All ye who enter here:
#                  Most of the code in this module
#                      is twisted beyond belief!
#                         Tread carefully
#                  If you think you understand it,
#                             You Don't,
#                           So Look Again
#


__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__version__ = "0.1.0"


class AbstractFactory:
    """Abstract factory"""

    def generate(self, position):
        """(AbstractTile) Abstract method to return a new dot

        Parameters:
            position (tuple<int, int>) The (row, column) position of the dot
        """
        raise NotImplementedError


class WeightedFactory(AbstractFactory):
    """Factory to generate instances based upon WeightedSelector value"""

    def __init__(self, selector, constructor):
        """Constructor

        Parameters:
            selector (WeightedSelector): The weighted selector to choose from
            constructor (WeightedSelector): A weighted selector to choose
                                            the constructor class from
        """
        self._selector = selector
        self._constructor = constructor

    def generate(self, position):
        """(AbstractTile) Generates a new dot"""
        constructor = self._constructor.choose()
        return constructor(self._selector.choose())
