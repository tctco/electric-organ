function [amplitude] = find_maxima(frequency_index, interval, spectra_info)
amplitude = spectra_info(frequency_index);
for i = frequency_index - interval : frequency_index + interval
        if spectra_info(i) > amplitude
            amplitude = spectra_info(i);
        end
end
end

