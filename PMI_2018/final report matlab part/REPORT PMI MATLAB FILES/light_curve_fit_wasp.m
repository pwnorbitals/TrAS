%% Light Curve Fitting
% This file is meant to elaborate data obtained by Muniwin to fit a light curve 
% and get results data. 
% Author: Marco R. Inchingolo

clc; clear all; close all;
%% CONSTANTS 
Rsun = 695700;%km sun radius
Rjup = 7.1492*10^4;%km jupiter radius
au = 149597870.700;%km astronomical unit
Msun = 1.98855*10^30;%kg sun mass
Mearth = 5.9722*10^24;%kg earth mass
G =  6.674*10^(-11);%m^3kg-1s^-2 gravitational constant
%% PARAMETERS
% name of the file, this must be in the matlab search path, and should be
% obtained by muniwin, ensure that it has the followinf format:
% JD Magnitude error
fileName = 'WASP-48b.txt';
%change those values according to the star that you are studying
P = 2.14363592; %days, orbital period for wasp 48b
Rstar = 1.75*Rsun; %km +-0.09
limbcoeff = [0.4 0.4];%gamma1 gamma2,for the star considered
%the following are used for comparison of results
areal = 0.03444*au; %real semimajor axis for wasp 48b
inclReal = 80.09; %° real inclination
Mplanetreal = 311*Mearth; %kg 311+-29 for wasp48b
Mrealstar = 1.19*Msun; %kg
RplanetReal = 1.7*Rjup;%km+-0.1

%% File Importing 
file = fopen(fileName,'r');
X = fscanf(file,'%f',[3 Inf])';
format longg
jd = X(:,1);%giulian day
Mag = -X(:,2);%magnitude
err = X(:,3);
[D,M,Y] = jd2dmy2(jd,false);
plot(D,Mag)
%IMPROVEMENT--> calculate the error of the calculation using error bars? 
%errorbar(H,Mag,err);
%% Data optimization
%divide my data into x subarrays of length n, and calculate the average
default = NaN;
%suddivision
%you can decide it based on the amount of data you have
n = 10;%number of elements in subdivisions
MagMat = vec2mat(Mag,n,default)';
DMat = vec2mat(D,n,default)';
% IMPROVEMENT--> last column cannot be used for the medium
Mmedium = mean(MagMat);
Dmedium = mean(DMat);
%remove the last column with NaN values
Mmedium(:,end) = [];
Dmedium(:,end) = [];
f = fit(Dmedium',Mmedium','smoothingspline');
figure(1)
plot(f,Dmedium,Mmedium,'o');
TF = isoutlier(Mag,'movmedian',0.01,'SamplePoints',D);
%Movemedian:Returns true for elements more than three local scaled MAD from the local 
%median over a window length specified by window.
Dout = D;
Mout = Mag;
errout = err;
Dout(TF) = [];
Mout(TF) = [];
errout(TF) = [];
figure(2)
hold on 
plot(D,Mag,D(TF),Mag(TF),'x');
plot(f,Dmedium,Mmedium,'o');%here the outlier are not removed
hold off
%% Linear fitting
Kn = 8;%to obtain 7 segment we need 8 knots
slmengine(D,Mag,'degree',1,'knots',Kn, 'interiorknots','free','plot','on','ConcaveUp',[26.42 26.52]);
slm1 = slmengine(Dout,Mout,'degree',1,'knots',Kn, 'interiorknots','free','plot','off');
dist = 0.01;
slm = slmengine(Dout,Mout,'degree',1,'knots',Kn, 'interiorknots','free','plot','on','ConcaveUp',[slm1.knots(2)+dist slm1.knots(end-1)-dist]);
t1 = slm.knots(2);
t2 = slm.knots(3);
t3 = slm.knots(end-2);
t4 = slm.knots(end-1);
tmiddle = (t3+t2)/2;
tt = t4-t1;%the total duration,lenght of the transit [days]
tf = t3-t2; %the full duration [days]
%% Transit depth
averageMag = (slmeval(slm.knots(end),slm)+slmeval(slm.knots(end-1),slm))/2;
Mnorm = Mout/abs(averageMag);%normalization
if averageMag<0
    %if the average is negative, summing 2 to the normalized values (-1 is
    %the reference) we obtain 1, see light_curve_fit_epic.m for example
    Mnorm = Mnorm +2;
end
slm2 = slmengine(Dout,Mout,'degree',1,'knots',Kn, 'interiorknots','free','plot','on','ConcaveUp',[slm1.knots(2)+dist slm1.knots(end-1)-dist]);
[MinMag,MinTime] = slmpar(slm2,'minfun');
Depth = 1-MinMag;
Rplanet = sqrt(Depth)*Rstar; %km
%impact parameter pag 120 the exoplanet handbook
b = sqrt(((1-sqrt(Depth))^2-(sin(tf*pi/P)^2)/(sin(tt*pi/P)^2)*(1+sqrt(Depth))^2)/(1-sin(tf*pi/P)^2/sin(tt*pi/P)^2));
%a, semimajor axis
a = Rstar*sqrt(((1+sqrt(Depth))^2-b^2*(1-sin(tt*pi/P)^2))/(sin(tt*pi/P)^2));%km
erra = abs((areal-a)/areal); %error semimajor axis
incl = rad2deg(acos(Rstar*b/a));
Psec = P*24*60*60; %the period must have the SI unit so that we can multiply it times G
rostar = 4*pi^2/(Psec^2*G)*(((1+sqrt(Depth))^2-b^2*(1-sin(tt*pi/P)^2))/(sin(tt*pi/P)^2))^(3/2);%kg/m^3
%another formula approximation of the last one
rostar2 = 32*Psec/G/pi*Depth^(3/4)*((tt*24*60*60)^2-(tf*24*60*60)^2)^(-3/2);%kg/m^3
Mstar = rostar*4/3*pi*(Rstar*1000)^3; %kg
errMstar = abs((Mrealstar-Mstar)/Mrealstar);
Mplanet = 4*pi^2*(a*1000)^3/Psec^2/G-Mstar;

%% Theorethical Light Curves
tE = tmiddle;%d
TIn = tE-0.1;%d
Tend = 0.1+tE;%d
Periodd = P;%period in days
figure(10)
[flux, time] = theoretical_light_curve_Pal(RplanetReal,Rstar,limbcoeff,TIn,Tend,tE,Periodd,areal,inclReal);
plot(time,flux);
hold on 
title('theoretical light curve')
xlabel('time [d]');
ylabel('normalized flux');
plot(Dout,Mnorm)
hold off
