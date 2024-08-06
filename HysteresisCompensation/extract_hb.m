function h_retrace = extract_hb(image_address)
filename = image_address;
h_trace=readgwychannel(filename,0);
channel_label = 'Height [Fwd]';
channel_number = 0;
while ~strcmp(channel_label,'Height [Bwd]')
    channel_number = channel_number + 1;
    h_retrace = readgwychannel(filename,channel_number);
    channel_label = cell2mat(h_retrace.title);
end
h_trace = h_trace.data;
h_retrace = h_retrace.data;
h_trace = h_trace;
h_retrace = fliplr(h_retrace);
end

