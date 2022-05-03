import argparse
import time
import numpy as np

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

from src import FocusRelaxProcessingEngine


if __name__ == "__main__":
    FocusRelaxProcessingEngine.main()