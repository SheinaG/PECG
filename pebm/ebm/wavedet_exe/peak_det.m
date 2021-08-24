function output = peak_det(file1, file2,fs)
ecg = readtable(file1);
peaks = readtable(file2);
ecg = ecg{:,:};
peaks = peaks{:,:};
fs=str2double(fs);

heasig = struct("nsig",1,"freq",fs,"nsamp",length(ecg));
[output,~,~] = wavedet_3D(ecg, peaks, heasig, []);
save("output.mat", "output");
end
