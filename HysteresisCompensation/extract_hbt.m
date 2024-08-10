function h_retrace = extract_hbt(image_address)
filename = image_address;
% cd(path_hysteresis);

% h_trace=readgwychannel(filename,0);
h_retrace=readgwychannel(filename,0);

% h_trace = h_trace.data;
h_retrace = h_retrace.data;

% h_trace = h_trace';
h_retrace = h_retrace';
% h_trace = fliplr(h_trace);

end

