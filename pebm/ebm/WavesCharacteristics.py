import numpy as np
from scipy import interpolate


def compute_amp(ecg, features_dict):
    if len(features_dict[0][~np.isnan(features_dict[0])]) == 0:
        return np.nan
    amp = np.ones(len(features_dict[0])) * np.nan

    if len(features_dict) == 1:
        amp[~np.isnan(features_dict[0])] = ecg[
            features_dict[0][~np.isnan(features_dict[0])]
        ]

    else:
        if (
            len(features_dict[0][~np.isnan(features_dict[0])]) == 0
            or len(features_dict[1][~np.isnan(features_dict[1])]) == 0
        ):
            return np.nan
        begin_amp = np.ones(len(features_dict[0])) * np.nan
        end_amp = np.ones(len(features_dict[0])) * np.nan
        begin_amp[~np.isnan(features_dict[0])] = ecg[
            features_dict[0][~(np.isnan(features_dict[0]))].astype(int)
        ]
        end_amp[~np.isnan(features_dict[1])] = ecg[
            features_dict[1][~(np.isnan(features_dict[1]))].astype(int)
        ]
        amp = np.abs(end_amp - begin_amp)
        amp = amp[~np.isnan(amp)]
    return amp


def compute_area(ecg, freq, features_dict, factor=1000):
    if (
        len(features_dict[0][~np.isnan(features_dict[0])]) == 0
        or len(features_dict[1][~np.isnan(features_dict[1])]) == 0
    ):
        return np.nan
    begin_fiducial = features_dict[0]
    end_fiducial = features_dict[1]
    area = np.ones(len(begin_fiducial)) * -1
    r_index = (~np.isnan(begin_fiducial)) & (~np.isnan(end_fiducial))
    area = area[r_index]
    bfi = begin_fiducial[r_index].astype(int)
    efi = end_fiducial[r_index].astype(int)

    # compute rectangular
    for i in range(0, len(bfi)):
        f = interpolate.interp1d([bfi[i], efi[i]], [ecg[bfi[i]], ecg[efi[i]]])
        rect_base = f(range(bfi[i], efi[i] + 1))
        area[i] = 0
        for j in range(len(rect_base)):
            area[i] += np.abs(ecg[bfi[i] + j] - rect_base[j])

    units = factor / freq
    area = area * units
    return area


def extract_waves_characteristics(ecg, freq, features_dict):

    amplitude_points = dict(
        Pwave=[features_dict["P"], features_dict["Poff"]],
        Twave=[features_dict["T"], features_dict["Toff"]],
        Rwave=[features_dict["qrs"]],
        STamp=[features_dict["QRSoff"], features_dict["Ton"]],
    )
    area_points = dict(
        Parea=[features_dict["Pon"], features_dict["Poff"]],
        Tarea=[features_dict["Ton"], features_dict["Toff"]],
        QRSarea=[features_dict["QRSon"], features_dict["QRSoff"]],
    )
    amplitude = {}
    for key in amplitude_points:
        amplitude[key] = np.asarray(compute_amp(ecg, amplitude_points[key]))
    area = {}
    for key in area_points:
        area[key] = np.asarray(compute_area(ecg, freq, area_points[key], factor=1000))

    # J point
    J_offset = int(0.04 * freq)
    J_feature = features_dict["QRSoff"] + J_offset
    J_feature = J_feature[J_feature < len(ecg)]

    if len(J_feature[~np.isnan(J_feature)]) == 0:
        J_ecg = np.asarray(np.nan)
    else:
        J_ecg = np.asarray(ecg[J_feature[~np.isnan(J_feature)].astype(int)])

    J_point = dict(Jpoint=J_ecg)
    Waves = {}
    Waves.update(amplitude)
    Waves.update(area)
    Waves.update(J_point)

    return Waves
