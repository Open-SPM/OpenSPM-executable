function x = hysteresis_detect(height_forward,height_backward,line_limit)

h_trace=height_forward(line_limit+1:end,:);
h_retrace=height_backward(line_limit+1:end,:);
h_retrace = fliplr(h_retrace);

cut_image=0;
l_points = 1000;
[x , x_c , f_x , g_x ,left_index, right_index]= Hysteresis_Correct_Function(h_trace,h_retrace,cut_image,l_points);

trace_curve = f_x;
retrace_curve = g_x;
normal_curve = x_c; 



end

