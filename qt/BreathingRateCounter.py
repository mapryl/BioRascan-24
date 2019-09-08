from scipy import signal
from numpy.fft import rfft, rfftfreq, fft
import numpy as np
from scipy.signal import butter, find_peaks

"""" Объявляем константы """
fsB = 50  # частота дисретизации БРЛ
lowFreqHearthGlobal = 0.7
highFreqHearthGlobal = 2.5
lowFreqBreathGlobal = 0.01
highFreqBreathGlobal = 0.4


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs  # приведение к удобному формату ввода частоты среза
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def fourier_analysis(signal1, signal2, fs, freq_low, freq_high):
    sum_signal = []
    for i in range(0, min(len(signal1), len(signal2))):  # собираем общий сигнал из двух квадратур
        sum_signal.append(complex(signal1[i], signal2[i]))

    fsignal = fft(sum_signal)  # используем преобразование Фурье
    fsignal = np.abs(fsignal)  # только положительную часть спектра
    time_step = 1 / fs
    freqs = np.fft.fftfreq(len(sum_signal), time_step)  # находим частоты составляющих спектра
    freqs = np.abs(freqs)
    freq_low = min(freqs, key=lambda x: abs(x - freq_low))  # находим в массиве частот ближайшие
    freq_high = min(freqs, key=lambda x: abs(x - freq_high))  # к частотам среза
    freq_low_ind = np.where(freqs == freq_low)[0][0]
    freq_high_ind = np.where(freqs == freq_high)[0][0]
    fsignal_max = max(fsignal[freq_low_ind:freq_high_ind])  # находим максимальную составляющую частоты
    freq_max_ind = np.where(fsignal == fsignal_max)
    freq_max = freqs[freq_max_ind]
    return freq_max[0]


def breath_filter(signal1, signal2):
    order = 2
    global lowFreqBreathGlobal
    global highFreqBreathGlobal

    freq_sum = fourier_analysis(signal1, signal2, fsB, lowFreqBreathGlobal, highFreqBreathGlobal)
    low_freq_breath = freq_sum - 0.1
    high_freq_breath = freq_sum + 0.1
    if (freq_sum - 0.1) <= 0:
        low_freq_breath = 0.01

    B_br, A_br = butter_bandpass(low_freq_breath, high_freq_breath, fsB, order=order)

    signalfilt_r1_1 = signal.filtfilt(B_br, A_br, signal1)
    signalfilt_r1_2 = signal.filtfilt(B_br, A_br, signal2)
    return signalfilt_r1_1, signalfilt_r1_2


def signal_without_breath(sig1, sig2):
    sig_res = []
    for i in range(0, min(len(sig1), len(sig2))):
        sig_res = np.append(sig_res, sig1[i] - sig2[i])
    return sig_res


def heart_filter(signal_r1_1, signal_r1_2):
    """фильтрация по широкой полосе"""
    order = 2
    global lowFreqHearthGlobal
    global highFreqHearthGlobal

    B_hb_w, A_hb_w = butter_bandpass(lowFreqHearthGlobal, highFreqHearthGlobal, fsB, order=order)
    signalfilt_hb_r1_1_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r1_1)
    signalfilt_hb_r1_2_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r1_2)

    freq_sum = fourier_analysis(signal_r1_1, signal_r1_2, fsB, lowFreqHearthGlobal, highFreqHearthGlobal)

    low_freq_hearth = freq_sum - 0.3
    if low_freq_hearth < 0:
        low_freq_hearth = 0.7
    high_freq_heath = freq_sum + 0.4

    B_hb, A_hb = butter_bandpass(low_freq_hearth, high_freq_heath, fsB, order=order)
    signalfilt_hb_r1_1 = signal.filtfilt(B_hb, A_hb, signal_r1_1)
    signalfilt_hb_r1_2 = signal.filtfilt(B_hb, A_hb, signal_r1_2)

    return signalfilt_hb_r1_1, signalfilt_hb_r1_2, signalfilt_hb_r1_1_w, signalfilt_hb_r1_2_w


def breath_rate_counter(signal_r1_1, signal_r1_2, time, lowFreqHearth, highFreqHearth, lowFreqBreath, highFreqBreath):
    """
    Предварительная обработка данных
    """
    global lowFreqHearthGlobal
    global highFreqHearthGlobal
    global lowFreqBreathGlobal
    global highFreqBreathGlobal
    lowFreqHearthGlobal = lowFreqHearth
    highFreqHearthGlobal = highFreqHearth
    lowFreqBreathGlobal = lowFreqBreath
    highFreqBreathGlobal = highFreqBreath

    signal_r1_1 = signal.detrend(signal_r1_1)  # удаляем тренд средней линии
    signal_r1_2 = signal.detrend(signal_r1_2)
    signalfilt_br_r1_1, signalfilt_br_r1_2 = breath_filter(signal_r1_1, signal_r1_2)

    signalfilt_hb_r1_1 = signal_without_breath(signal_r1_1, signalfilt_br_r1_1)
    signalfilt_hb_r1_2 = signal_without_breath(signal_r1_2, signalfilt_br_r1_2)

    signalfilt_hb_r1_1, signalfilt_hb_r1_2, \
    signalfilt_hb_r1_1_w, signalfilt_hb_r1_2_w = heart_filter(signalfilt_hb_r1_1, signalfilt_hb_r1_2)

    '''Поиск пиков'''
    # peaks_hb_r1_1_w = find_peaks(signalfilt_hb_r1_1_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r1_2_w = find_peaks(signalfilt_hb_r1_2_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r2_1_w = find_peaks(signalfilt_hb_r2_1_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r2_2_w = find_peaks(signalfilt_hb_r2_2_w, distance=fsB / highcut_hb)[0]

    peaks_hb_r1_1 = find_peaks(signalfilt_hb_r1_1, distance=fsB / highFreqHearthGlobal)[0]
    peaks_hb_r1_2 = find_peaks(signalfilt_hb_r1_2, distance=fsB / highFreqHearthGlobal)[0]

    peaks_br_r1_1 = find_peaks(signalfilt_br_r1_1, distance=fsB / highFreqBreathGlobal)[0]
    peaks_br_r1_2 = find_peaks(signalfilt_br_r1_2, distance=fsB / highFreqBreathGlobal)[0]

    total_breath_rate = (len(peaks_br_r1_1) + len(peaks_br_r1_2)) / 2
    total_breath_rate = total_breath_rate / time * 60

    total_heart_rate = (len(peaks_hb_r1_1) + len(peaks_hb_r1_2)) / 2
    total_heart_rate = total_heart_rate / time * 60

    return total_heart_rate, total_breath_rate, \
           signalfilt_hb_r1_1, signalfilt_hb_r1_2, peaks_hb_r1_1,  peaks_hb_r1_2, \
           signalfilt_br_r1_1, signalfilt_br_r1_2, peaks_br_r1_1, peaks_br_r1_2

