function [ D,M,Y] = jd2dmy2(jd,giulian)%giulian or gregorian calendar
%transform a julian date in a normal date of the kind D,M,Y,H 
a = jd+32044;
%for giulian calendat
b = 0;
c = jd+32082;
if ~giulian%change in gregorian case
    b = floor((4*a+3)/146097);
    c = a-floor(146097*b/4);
end
d = floor((4*c+3)/1461);
e = c-floor(1461*d/4);
m = floor((5*e+2)/153);
D = e-floor((153*m+2)/5)+1;
M = m+3-12*floor(m/10);
Y = 100*b+d-4800+floor(m/10);
%in case also the hour is needed
% H = (jd-floor(jd))*240+12;
% H = (jd-floor(jd))*24+12;
% if ~isempty(H(H>24))
%     D(H>24)=floor(D(H>24))+1;
%     H(H>24)=H(H>24)-24;
% end

%to obtain minutes (H-floor(H))*60
end

