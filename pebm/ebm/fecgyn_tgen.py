import numpy as np
import scipy

#matlab function by Joachim Bahar, translated to python by Sheina Gendelman

def fecgyn_tgen(ecg, qrs, fs):
    #consts
    n_samples = len(ecg)
    PI = np.pi
    start_cycle = 1
    n_bins = 250
    Th = 0.9
    MIN_TRESH = 0.6
    nc_relev_mode =0
    MIN_nc = 30
    n_modes = 1
    PACE = 0.1
    n_rel = 10
    MIN_TLEN = 0.35
    template= {}

    ## calc phase
    phase = np.zeros([n_samples])
    m = np.diff(qrs)
    L = qrs[0]
    if m is None:
        phase[0:(n_samples-1)] = np.linspace(-2*PI, 2*PI, n_samples)
    else:
        phase[0:L] = np.linspace(2*PI-L*2*PI/m[0], 2*PI, L)
        for i in range(0,len(qrs)-1):
            phase[qrs[i]-1:qrs[i+1]] = np.linspace(0, 2*PI, m[i]+1)
        L = n_samples - qrs[-1]
        phase[qrs[-1]-1:] = np.linspace(0, L*2*PI/m[-1], L+1)
    phase = np.mod(phase, 2*PI)
    phase[phase > PI] = phase[phase > PI]-2*PI
    ####

    phase_change_points = np.asarray(np.where((phase[1:] < 0) & (phase[:-1] > 0))).squeeze()
    n_cycles = len(phase_change_points)
    cycle_index = np.arange(phase_change_points[start_cycle]+1, phase_change_points[start_cycle+1]+1)
    cycle_f = scipy.interpolate.splrep(phase[cycle_index], ecg[cycle_index])
    cycle = np.expand_dims(scipy.interpolate.splev(np.linspace(-PI, PI, n_bins), cycle_f), 1)
    Mode = {'cycles': {1: cycle},
            'mean_cycle': {1: cycle},
            'std_cycle': {1: np.zeros([1,n_bins])},
            'nc': {1: 1},
            'cycle_len': {1: len(cycle_index)}}


    while (nc_relev_mode < MIN_nc) & (Th> MIN_TRESH):

        for i in range(start_cycle+1, n_cycles-2):

            cycle_index = np.arange(phase_change_points[i] + 1, phase_change_points[i + 1] + 1)
            cycle_f = scipy.interpolate.splrep(phase[cycle_index], ecg[cycle_index])
            cycle = np.expand_dims(scipy.interpolate.splev(np.linspace(-PI, PI, n_bins), cycle_f), 1)
            match = 0
            ind_mode = 1

            while (not match) & (ind_mode <= n_modes):
                coeff = np.corrcoef(cycle.squeeze(), Mode['mean_cycle'][ind_mode].squeeze())
                coeff_m = np.amax(coeff.flatten())##why??
                match = coeff_m > Th
                ind_mode = ind_mode +1
            if not match:
                n_modes = n_modes +1
                Mode['cycles'][n_modes] = cycle
                Mode['mean_cycle'][n_modes] = cycle
                Mode['std_cycle'][n_modes] = np.zeros([1, n_bins])
                Mode['nc'][n_modes] = 1
                Mode['cycle_len'][n_modes] = len(cycle_index)
            else:
                Mode['cycles'][ind_mode - 1] = np.concatenate((Mode['cycles'][ind_mode - 1], cycle), axis=1)
                Mode['mean_cycle'][ind_mode - 1] = np.mean(Mode['cycles'][ind_mode - 1], axis =1)
                Mode['std_cycle'][ind_mode - 1] = np.std(Mode['cycles'][ind_mode - 1], axis =1)
                Mode['nc'][ind_mode - 1] = Mode['nc'][ind_mode - 1] + 1
                Mode['cycle_len'][ind_mode - 1] = np.hstack((Mode['cycle_len'][ind_mode - 1], len(cycle_index)))

        rel_mode_ind = []
        for i in Mode['nc']:
            if (Mode['nc'][i] > n_rel) & (np.mean(Mode['cycle_len'][i]) >= MIN_TLEN*fs):
                rel_mode_ind.append(i)
        if not len(rel_mode_ind):
            template['avg'] = None
            template['std'] = None
        else:
            max_ind = max(Mode['nc'], key=Mode['nc'].get)
            des1 = int(np.round(n_bins/6))
            template['avg'] = np.roll(Mode['mean_cycle'][max_ind], -des1)
            template['std'] = np.roll(Mode['std_cycle'][max_ind], -des1)
            mean_cycle_len = sum(Mode['cycle_len'][max_ind])/len(Mode['cycle_len'][max_ind])
            template['avg'] = scipy.signal.resample(template['avg'], int(np.round(mean_cycle_len)))
            template['std'] = scipy.signal.resample(template['std'], int(np.round(mean_cycle_len)))
        Th = Th - PACE
    return template
