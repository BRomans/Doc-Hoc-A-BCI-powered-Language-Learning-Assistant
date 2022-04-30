import argparse
import logging

import mne
import numpy as np
import pyqtgraph as pg
from brainflow import BrainFlowModelParams, BrainFlowMetrics, BrainFlowClassifiers, MLModel
from matplotlib import pyplot as plt
from pyqtgraph.Qt import QtGui, QtCore

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations


class OctopusBCI:
    def __init__(self, board_shim, window_size=5, update_speed_ms=50):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = update_speed_ms
        self.window_size = window_size
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='OctopusBCI Plot', size=(1200, 800))

        self._init_timeseries()

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        timer2 = QtCore.QTimer()
        timer2.timeout.connect(self.update_classifier)
        timer2.start(self.window_size * 1000)

        QtGui.QApplication.instance().exec_()

        # timer = QtCore.QTimer()
        # timer.timeout.connect(self.update_classifier)
        # timer.start(self.window_size)
        # QtGui.QApplication.instance().exec_()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            p = self.win.addPlot(row=i, col=0)
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                p.setTitle('TimeSeries Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        # self.update_classifier()
        for count, channel in enumerate(self.exg_channels):
            # plot timeseries
            DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(data[channel], self.sampling_rate, 51.0, 100.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandpass(data[channel], self.sampling_rate, 51.0, 100.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 50.0, 4.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 60.0, 4.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            self.curves[count].setData(data[channel].tolist())

        self.app.processEvents()

    def update_classifier(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        eeg_channels = self.board_shim.get_eeg_channels(self.board_id)
        bands = DataFilter.get_avg_band_powers(data, eeg_channels, self.sampling_rate, True)
        feature_vector = np.concatenate((bands[0], bands[1]))
        print(feature_vector)
        self.calculate_focus(feature_vector)
        self.calculate_relaxation(feature_vector)

    def plot_psd(self):
        data = self.board_shim.get_board_data(self.num_points)
        eeg_channels = self.board_shim.get_eeg_channels(self.board_id)

        eeg_data = data[eeg_channels, :]
        eeg_data = eeg_data / 1000000  # BrainFlow returns uV, convert to V for MNE

        # Creating MNE objects from brainflow data arrays
        ch_types = ['eeg'] * len(eeg_channels)
        ch_names = self.board_shim.get_eeg_names(self.board_id)
        sfreq = self.board_shim.get_sampling_rate(self.board_id)
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        raw = mne.io.RawArray(eeg_data, info)
        freqs = (25.0, 50.0)
        raw_notch = raw.notch_filter(freqs=freqs)
        raw_bp = raw_notch.filter(l_freq=0.1, h_freq=30.0)

        # its time to plot something!
        raw_bp.plot_psd(average=True, fmax=50.0)

    def calculate_relaxation(self, feature_vector):
        relaxation_params = BrainFlowModelParams(BrainFlowMetrics.RELAXATION.value,
                                                 BrainFlowClassifiers.REGRESSION.value)
        relaxation = MLModel(relaxation_params)
        relaxation.prepare()
        prediction = relaxation.predict(feature_vector)
        print('Relaxation: %f' % prediction)
        relaxation.release()

        return prediction

    def calculate_focus(self, feature_vector):
        concentration_params = BrainFlowModelParams(BrainFlowMetrics.CONCENTRATION.value,
                                                    BrainFlowClassifiers.KNN.value)
        concentration = MLModel(concentration_params)
        concentration.prepare()
        prediction = concentration.predict(feature_vector)
        print('Concentration: %f' % prediction)
        concentration.release()

        return prediction


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file

    try:
        board_shim = BoardShim(args.board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)

        octo = OctopusBCI(board_shim, window_size=10, update_speed_ms=50)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        octo.plot_psd()
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == '__main__':
    main()
