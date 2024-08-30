# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: dump_data_process.py
@time: 2021/8/26 19:35
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np


def read_data_from_file(data_path):
    with open(data_path, "r") as DATA:
        content = DATA.readlines()
    return content


class DumpData:
    def __init__(self, dump_data_list, fsample_mhz):
        self.data_content = dump_data_list
        self.freq_sample_hz = fsample_mhz * 1e6
        self.time_sample = 1.0/self.freq_sample_hz
        self.data_i, self.data_q = self.__data_process__()

    def __data_process__(self):
        # process data dump from ADC
        data_ix = []
        data_qx = []
        data_i = []
        data_q = []
        for line in self.data_content:
            if line.startswith("0003-") or line.startswith("0004-"):
                [data1, data2, data3, data4] = line.split()[1:5]
                data_ix.extend([int(data1[5:8], 16), int(data2[5:8], 16), int(data3[5:8], 16), int(data4[5:8], 16)])
                data_qx.extend([int(data1[0:4], 16), int(data2[0:4], 16), int(data3[0:4], 16), int(data4[0:4], 16)])
        for i in range(len(data_ix)):
            data_i.append((data_ix[i] - 2048.0) / 2048.0)
            data_q.append((data_qx[i] - 2048.0) / 2048.0)
        return data_i, data_q

    def fft_iq(self):
        # fft(data_i + j*data_q)
        data_iq = []
        for i in range(len(self.data_i)):
            data_iq.append(complex(self.data_i[i], self.data_q[i]))
        return np.fft.fftshift(np.fft.fft(data_iq))

    def spectrum_iq(self):
        # caculate spectrum
        # fft freq label
        self.fft_freq = np.fft.fftshift(np.fft.fftfreq(len(self.data_i), self.time_sample))
        # fft mag and phase
        self.fft_result = self.fft_iq()
        self.fft_mag_db = 20.0 * np.log10(np.abs(self.fft_result))
        self.fft_phase = np.angle(self.fft_result, deg=True)

    def plot_time_wave(self):
        # plot time wave
        time_x = [i*self.time_sample for i in range(len(self.data_i))]
        plt.plot(time_x, self.data_i)
        plt.plot(time_x, self.data_q)
        plt.show()

    def plot_spectrum_wave(self):
        self.spectrum_iq()
        # plot mag and phase
        plt.plot(self.fft_freq, self.fft_mag_db)
        # plt.plot(fft_freq, fft_phase)
        plt.show()

    def fft_peak_search(self):
        self.spectrum_iq()
        x_index = np.where(self.fft_mag_db == np.max(self.fft_mag_db))
        return [self.fft_freq[x_index], self.fft_mag_db[x_index], self.fft_phase[x_index]]


if __name__ == "__main__":
    data_path = r"F:/FTP_AIC/Share/huangpeng/aic8801t/20210826/matlab/session_1n.log"
    ADC_DATA = DumpData(read_data_from_file(data_path), 193)
    aaa = ADC_DATA.fft_peak_search()
    print(aaa)
    # ADC_DATA.plot_time_wave()
    # plot_iqwave(data_i, data_q, 193)
