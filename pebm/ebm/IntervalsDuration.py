import numpy as np


def compute_int(freq, features_dict, factor=1000):
    begin_fiducial = features_dict[0]
    end_fiducial = features_dict[1]
    # int = np.zeros(1,len(begin_fiducial))
    units = (factor / freq)
    int = (end_fiducial - begin_fiducial) * units
    int[(begin_fiducial == -1) | (end_fiducial == -1)] = -1
    return int


def compute_QTc(QT, RR, factor=1000):
    HR = np.median(RR)
    HRf = HR / factor
    n = len(QT)
    QTc_b, QTc_frid, QTc_fra, QTc_hod = [None] * n, [None] * n, [None] * n, [None] * n
    for i, QTi in enumerate(QT):
        if ((HR == -1) | (QTi == -1)):
            QTc_b[i], QTc_frid[i], QTc_fra[i], QTc_hod[i] = [-1, -1, -1, -1]
        else:
            QTc_b[i] = QTi / np.sqrt(HRf)  # ms
            QTc_frid[i] = QTi / HRf ** (1 / float(3))  # ms
            QTc_fra[i] = QTi + (0.154 * (1 - HRf) * factor)  # ms
            QTc_hod[i] = QTi + (0.00175 * (60 / HRf - 60) * factor)  # ms
    QTc_dict = dict(QTc_b=np.asarray([QTc_b], dtype=np.float64).squeeze(),
                    QTc_frid=np.asarray([QTc_frid], dtype=np.float64).squeeze(),
                    QTc_fra=np.asarray([QTc_fra], dtype=np.float64).squeeze(),
                    QTc_hod=np.asarray([QTc_hod], dtype=np.float64).squeeze())
    return QTc_dict


def extract_intervals_duration(fs, features_dict, factor=1000):
    # feat_df = pd.DataFrame()
    intervals_points = dict(Pwave_int=[features_dict['Pon'], features_dict['Poff']],
                            PR_int=[features_dict['Pon'], features_dict['QRSon']],
                            PR_seg=[features_dict['Poff'], features_dict['QRSon']],
                            PR_int2=[features_dict['P'], features_dict['qrs']],
                            QRS_int=[features_dict['QRSon'], features_dict['QRSoff']],
                            QT_int=[features_dict['QRSon'], features_dict['Toff']],
                            Twave_int=[features_dict['Ton'], features_dict['Toff']],
                            TP_seg=[features_dict['Toff'][:-1], features_dict['Pon'][1:]],
                            RR_int=[features_dict['qrs'][:-1], features_dict['qrs'][1:]])
    intervals = {}
    for key in intervals_points:
        intervals[key] = compute_int(fs, intervals_points[key], factor=1000)
    QTc_dict = compute_QTc(intervals['QT_int'], intervals['RR_int'], factor=1000)
    intervals.update(QTc_dict)
    return intervals
