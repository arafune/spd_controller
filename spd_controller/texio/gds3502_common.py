
from numpy as np
from numpy.typing import NDArray


class GDS3502common:
    def __init__(self):
        self.header: dict[str, float|str] = {}
        self.memory: NDArray[np.float_]
        self.TERM = "\n"

        def 
