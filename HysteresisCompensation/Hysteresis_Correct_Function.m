function [x , x_c , f_x , g_x ,left_index, right_index]= Hysteresis_Correct_Function(h_trace,h_retrace,cut_image,l_points)
% funny: remember when the trace and retrace mapping was not scaled down to 0 to 1 and I got strange curves + I was scared af!
% it uses other m files, including: image_resize.m 
%% read and crop the file (based on cut_image)
% creat correlation and cut
correlation_height = (h_trace'*h_retrace)./(repmat(diag(h_trace'*h_trace),1,size(h_trace,2))+repmat(diag(h_retrace'*h_retrace)',size(h_retrace,2),1));
% - element (i,j) is the correlation between h_trace(:,i) and h_retrace(:,j)
% find cut points : 
%[m,left_index]=max(correlation_height(:,1));
%[m,right_index]=max(correlation_height(end,:));
% cut matrices
%if cut_image==0
left_index = 1;
right_index = length(correlation_height(:,1));
%end
h_trace=h_trace(:,left_index:end);
h_retrace=h_retrace(:,1:right_index);
%% match the sizes and increase the points
h_trace=image_resize(h_trace,l_points,2);
h_retrace=image_resize(h_retrace,l_points,2);
% find the mapping from trace to retrace and from retrace to trace
%correlation_height_tr=corr(h_trace,h_trace)+corr(h_retrace,h_retrace)-2*corr(h_trace,h_retrace);
correlation_height_tr = (h_trace'*h_retrace)./(repmat(diag(h_trace'*h_trace),1,l_points)+repmat(diag(h_retrace'*h_retrace)',l_points,1));
[m,Index]=max(correlation_height_tr');
mapping_tr=Index/length(Index); % trace to retrace
[m,Index]=max(correlation_height_tr);
mapping_rt=Index/length(Index); % retrace to trace
%% find the function of mapping
CostFunction=@(x) error_function(x,mapping_rt,length(mapping_rt)-1);
% options=optimoptions('ga','FunctionTolerance',0.000000000001);
nVar=10;      
x_final=ga(CostFunction,nVar);
%% construct grpahs from coefficients
N=length(mapping_tr)-1;
x_c=(0:1:N)'/N; % x coordinate
x=1+abs(x_final);
if size(x,2)==1
    x=x';
end
f_x=(x_c.^x)*ones(length(x),1)/length(x); % it is Nx1
% f_inv_y=interp1(f_x,x_c,x_c,'spline');
g_x=1-((1-x_c).^x)*ones(length(x),1)/length(x); % it is Nx1
% g_inv_y=interp1(g_x,x_c,x_c,'spline');
%% other functions
    function image_resized=image_resize(image_original,n_points,dimension)
        % image_original : matrix containing the image
        % n_points : number of points to be interpolated on the row or column
        % dimension=1 : increase points on the rows
        % dimension=2 : increase points on the columns
        if dimension==2
            % run it without for loop:
            image_resized=interp1(0:1:size(image_original,2)-1,image_original',(0:1:n_points-1)/(n_points-1)*(size(image_original,2)-1),'spline')';
            % run with for loop:
            %     for i=1:size(image_original,1) % go along the rows
            %         image_resized(i,:)=interp1(0:1:size(image_original,2)-1,image_original(i,:),(0:1:n_points-1)/(n_points-1)*(size(image_original,2)-1),'spline');
            %     end
        end
        if dimension==1
            % run it without for loop:
            image_resized=interp1(0:1:size(image_original,1)-1,image_original,(0:1:n_points-1)/(n_points-1)*(size(image_original,1)-1),'spline');
            % run with for loop:
            %     for j=1:size(image_original,2)
            %     image_resized(:,j)=(interp1(0:1:size(image_original,1)-1,image_original(:,j)',(0:1:n_points-1)/(n_points-1)*(size(image_original,1)-1),'spline'))';
            %     end
        end
    end

    function error=error_function(x_e,x_in_e,N_e)
        x_e=1+abs(x_e);
        x_c_e=(0:1:N_e)'/N_e; % x coordinate
        if size(x_in_e,1)==1
            x_in_e=x_in_e';
        end
        if size(x_e,2)==1
            x_e=x_e';
        end
        f_x_e=(x_c_e.^x_e)*ones(length(x_e),1)/length(x_e); % it is Nx1
        f_inv_y_e=interp1(f_x_e,x_c_e,x_c_e,'spline');
        g_x_e=1-((1-f_inv_y_e).^x_e)*ones(length(x_e),1)/length(x_e); % it is Nx1
        error=sqrt((g_x_e-x_in_e)'*(g_x_e-x_in_e))/length(x_in_e);
    end
end