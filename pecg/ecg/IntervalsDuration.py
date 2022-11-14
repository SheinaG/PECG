import numpy as np


def compute_int(freq, features_dict, factor=1000):
    if len(features_dict[0][~np.isnan(features_dict[0])]) == 0 or 0 == len(
        features_dict[1][~np.isnan(features_dict[1])]
    ):
        return np.nan
    begin_fiducial = features_dict[0]
    end_fiducial = features_dict[1]

    units = factor / freq
    intv = (end_fiducial - begin_fiducial) * units
    intv = intv[~np.isnan(intv)]
    return intv


def compute_QTc(QT, RR, factor=1000):
    if len(RR[~np.isnan(RR)]) == 0 or len(QT[~np.isnan(QT)]) == 0:
        QTc_dict = dict(
            QTc_b=np.asarray(np.nan),
            QTc_frid=np.asarray(np.nan),
            QTc_fra=np.asarray(np.nan),
            QTc_hod=np.asarray(np.nan),
        )
        return QTc_dict

    HR = np.median(RR[~np.isnan(RR)])
    HRf = HR / factor
    n = len(QT)
    QTc_b, QTc_frid, QTc_fra, QTc_hod = (
        [np.nan] * n,
        [np.nan] * n,
        [np.nan] * n,
        [np.nan] * n,
    )
    for i, QTi in enumerate(QT):
        if (HR == np.nan) | (QTi == np.nan):
            continue
        else:
            QTc_b[i] = QTi / np.sqrt(HRf)  # ms
            QTc_frid[i] = QTi / HRf ** (1 / float(3))  # ms
            QTc_fra[i] = QTi + (0.154 * (1 - HRf) * factor)  # ms
            QTc_hod[i] = QTi + (0.00175 * (60 / HRf - 60) * factor)  # ms
    QTc_b = np.asarray([QTc_b], dtype=np.float64).squeeze()
    QTc_frid = np.asarray([QTc_frid], dtype=np.float64).squeeze()
    QTc_fra = np.asarray([QTc_fra], dtype=np.float64).squeeze()
    QTc_hod = np.asarray([QTc_hod], dtype=np.float64).squeeze()

    QTc_dict = dict(
        QTc_b=QTc_b[~np.isnan(QTc_b)],
        QTc_frid=QTc_frid[~np.isnan(QTc_frid)],
        QTc_fra=QTc_fra[~np.isnan(QTc_fra)],
        QTc_hod=QTc_hod[~np.isnan(QTc_hod)],
    )
    return QTc_dict


def extract_intervals_duration(fs, features_dict, factor=1000):

    intervals_points = dict(
        Pwave_int=[features_dict["Pon"], features_dict["Poff"]],
        PR_int=[features_dict["Pon"], features_dict["QRSon"]],
        PR_seg=[features_dict["Poff"], features_dict["QRSon"]],
        PR_int2=[features_dict["P"], features_dict["qrs"]],
        QRS_int=[features_dict["QRSon"], features_dict["QRSoff"]],
        QT_int=[features_dict["QRSon"], features_dict["Toff"]],
        Twave_int=[features_dict["Ton"], features_dict["Toff"]],
        TP_seg=[features_dict["Toff"][:-1], features_dict["Pon"][1:]],
        RR_int=[features_dict["qrs"][:-1], features_dict["qrs"][1:]],
        R_dep=[features_dict["QRSon"], features_dict["qrs"]],
    )
    intervals = {}
    for key in intervals_points:
        intervals[key] = np.asarray(
            compute_int(fs, intervals_points[key], factor=factor)
        )
    QTc_dict = compute_QTc(intervals["QT_int"], intervals["RR_int"], factor=factor)
    intervals.update(QTc_dict)
    return intervals
