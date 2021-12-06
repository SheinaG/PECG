import numpy as np


def compute_amp(ecg, features_dict):
    amp = np.ones(len(features_dict[0])) * -1
    if len(features_dict) == 1:
        amp[features_dict[0] != -1] = ecg[features_dict[0][features_dict[0] != -1]]

    else:
        begin_amp = np.ones(len(features_dict[0])) * -1
        end_amp = np.ones(len(features_dict[0])) * -1
        begin_amp[features_dict[0] != -1] = ecg[features_dict[0][features_dict[0] != -1]]
        end_amp[features_dict[1] != -1] = ecg[features_dict[1][features_dict[1] != -1]]
        amp = np.abs(end_amp - begin_amp)
        amp[(begin_amp == -1) | (end_amp == -1)] = -1

    return amp


def compute_area(ecg, freq, features_dict, factor=1000):
    begin_fiducial = features_dict[0]
    end_fiducial = features_dict[1]
    area = np.ones(len(features_dict[0])) * -1
    r_index = (begin_fiducial != -1) & (end_fiducial != -1)
    area = area[r_index]
    bfi = begin_fiducial[r_index].astype(int)
    efi = end_fiducial[r_index].astype(int)
    for i in range(0, len(bfi) - 1):
        area[i] = np.sum(np.abs(ecg[bfi[i]: efi[i]]))

    units = (factor / freq)
    area = area * units
    return area


def extract_waves_characteristics(ecg, freq, features_dict):

    amplitude_points = dict(Pwave=[features_dict['P'], features_dict['Poff']],
                            Twave=[features_dict['T'], features_dict['Toff']],
                            Rwave=[features_dict['qrs']],
                            STamp=[features_dict['QRSoff'], features_dict['Ton']])
    area_points = dict(Parea=[features_dict['Pon'], features_dict['Poff']],
                       Tarea=[features_dict['Ton'], features_dict['Toff']],
                       QRSarea=[features_dict['QRSon'], features_dict['QRSoff']])
    amplitude = {}
    for key in amplitude_points:
        amplitude[key] = compute_amp(ecg, amplitude_points[key])
    area = {}
    for key in area_points:
        area[key] = compute_area(ecg, freq, area_points[key], factor=1000)
    J_offset = int(0.04 * freq)
    J_ecg = ecg[features_dict['QRSoff'] + J_offset]
    J_point = dict(Jpoint=J_ecg)
    Waves = {}
    Waves.update(amplitude)
    Waves.update(area)
    Waves.update(J_point)

    return Waves
