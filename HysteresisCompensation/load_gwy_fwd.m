function h_trace = load_gwy_fwd(Forward_Address)

h_trace=readgwychannel(Forward_Address,0);
%h_retrace=readgwychannel(Backward_Address,0);

h_trace = h_trace.data;
%h_retrace = h_retrace.data;

h_trace = h_trace';
%h_retrace = h_retrace';
h_trace = fliplr(h_trace);

end

