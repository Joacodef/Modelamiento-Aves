from abc import ABC, abstractmethod

import numpy as np

from engine import Entity

class fObjeto(Entity, ABC):

    @property
    @abstractmethod
    def v(self):
        pass

    @property
    @abstractmethod
    def a(self):
        pass

    @property
    @abstractmethod
    def pos(self):
        pass

    def distance_to(self, other):
        return np.linalg.norm(self.pos - other.pos)