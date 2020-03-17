%% Light Curve Fitting of EPIC211089792 b - K2-29b
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
Mjupiter = 1.89813*10^27;%kg jupiter mass
G =  6.674*10^(-11);%m^3kg-1s^-2 gravitational constant
%% PARAMETERS
%data taken from EPIC211089792 B: AN ALIGNED AND INFLATED HOT JUPITER IN A YOUNG VISUAL BINARY
% JD/ Magnitude/ error
fileName = 'epic_12.txt';
%change those values according to the star that you are studying
P = 3.2588321; %days, orbital period epic
Rstar = 0.86*Rsun; %km +-0.01
%limb darkening coeffieints taken 
%from http://cdsarc.u-strasbg.fr/viz-bin/Cat?cat=J%2FA%2BA%2F529%2FA75&target=readme&
limbcoeff =  [0.2451 0.3552];%gamma1 gamma2,for the star considered
%the following are used for comparison of results
areal = 0.04217*au; %real semimajor axis for epic
inclReal = 86.656; %° real inclination
Mplanetreal = 0.73*Mjupiter; %kg +-0.04
RplanetReal = 1.19*Rjup;%km +-0.02
MstarReal = 0.94*Msun; %kg  table2 

%% File Importing 
file = fopen(fileName,'r');
X = fscanf(file,'%f',[3 Inf])';
format longg
jd = X(:,1);%giulian day
%the minus there is because the more the intensity the more the magnitude
%is low
Mag = -X(:,2);%magnitude
err = X(:,3);
[D,M,Y] = jd2dmy2(jd,false);
% plot(D,Mag)
%IMPROVEMENT--> calculate the error of the calculation using error bars? 
%errorbar(H,Mag,err);
%% Data optimization
%in this case is necessary to remove the outliers because there are a lot
%99.00 values of magnitude
TF = isoutlier(Mag,'movmedian',0.04,'SamplePoints',D);
%Movemedian:Returns true for elements more than three local scaled MAD from the local 
%median over a window length specified by window.
errout = err;
D(TF) = [];
Mag(TF) = [];
errout(TF) = [];
%divide my data into x subarrays of length n, and calculate the average
default = NaN;
%suddivision
%you can decide it based on the amount of data you have
n = 4;%number elements in subdivisions
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
title('spline fitted light curve')
xlabel('time [d]');
ylabel('Magnitude');
%% Linear fitting
%in this case 8 segments are not enough to describe the behaviour, because
%there is a peak in the first part that is otherwise considered like the
%begininng of the transit, the minimum numeber for which we have the knot
%in the right position is 13
Kn = 13;
%the numbers [15.31 15.37] are chosen so that the plot in the next section figure(2) is the wanted one 
%(no knots should be in the region inside the nominal magnitude at the
%beginning and end of the transit
slm = slmengine(D,Mag,'degree',1,'knots',Kn, 'interiorknots','free','plot','on','ConcaveUp',[15.31 15.37]);

%% Normalization ?
%for some reason the results are correct only if the magnitude is not
%normalized, but accordingly to https://www.astro.ex.ac.uk/people/alapini/Publications/PhD_chap1.pdf
%at pag 9, the flux should be normalized 

 averageMag = (slmeval(slm.knots(11),slm)+slmeval(13,slm))/2;
% Mnorm = Mag/abs(averageMag);%normalization 
% if averageMag<0
%     %if the average is negative, summing 2 to the normalized values (-1 is
%     %the reference) we obtain 1
%     Mnorm = Mnorm +2;
% end
Mnorm = Mag-averageMag+1;% in this wasy the flux is not normalized but simply translated, to put the average in 1 
slm1 = slmengine(D,Mnorm,'degree',1,'knots',Kn, 'interiorknots','free','plot','on','ConcaveUp',[15.31 15.37]);

%% Times
t1 =slm1.knots(3);
t2 = slm1.knots(5);
t3 = slm1.knots(9);
t4 = slm1.knots(10);
tmiddle = (t3+t2)/2;
tt = t4-t1;%the total duration,lenght of the transit [days]
tf = t3-t2; %the full duration [days]

%% Transit depth
[MinMag,MinTime] = slmpar(slm1,'minfun');
Depth = 1-MinMag;
DepthReal = (RplanetReal/Rstar)^2;
Rplanet = sqrt(Depth)*Rstar; %km

%impact parameter pag 120 the exoplanet handbook
b = sqrt(((1-sqrt(Depth))^2-(sin(tf*pi/P)^2)/(sin(tt*pi/P)^2)*(1+sqrt(Depth))^2)/(1-sin(tf*pi/P)^2/sin(tt*pi/P)^2));
%a, semimajor axis
a = Rstar*sqrt(((1+sqrt(Depth))^2-b^2*(1-sin(tt*pi/P)^2))/(sin(tt*pi/P)^2));%km
breal = cosd(inclReal)*areal/Rstar;
erra = abs((areal-a)/areal); %error semimajor axis
incl = rad2deg(acos(Rstar*b/a));
Psec = P*24*60*60; %the period must have the SI unit so that we can multiply it times G
rostar = 4*pi^2/(Psec^2*G)*(((1+sqrt(Depth))^2-b^2*(1-sin(tt*pi/P)^2))/(sin(tt*pi/P)^2))^(3/2);%kg/m^3
%another formula approximation of the last one
rostar2 = 32*Psec/G/pi*Depth^(3/4)*((tt*24*60*60)^2-(tf*24*60*60)^2)^(-3/2);%kg/m^3
MstarReal = rostar*4/3*pi*(Rstar*1000)^3; %kg
% errMstar = abs((Mrealstar-Mstar)/Mrealstar);
Mplanet = 4*pi^2*(a*1000)^3/Psec^2/G-MstarReal;

%% Theorethical Light Curves
tE = tmiddle-0.004;%d (-0.004 adjustment of the time of the transit) 
TIn = tE-0.1;%d
Tend = 0.1+tE;%d
Periodd = P;%period in days

figure(10)
[flux, time] = theoretical_light_curve_Pal(Rplanet,Rstar,limbcoeff,TIn,Tend,tE,Periodd,a,incl);
%the error is big because of the big error on the radius of the planet
plot(time,flux);
title('Obtained light curve')
hold on 
xlabel('time [d]');
ylabel('Magnitude');
plot(D,Mnorm)
hold off

figure(11)
[flux, time] = theoretical_light_curve_Pal(RplanetReal,Rstar,limbcoeff,TIn,Tend,tE,Periodd,areal,inclReal);
plot(time,flux);
title('Theoretical light curve')
xlabel('time [d]');
ylabel('Magnitude');
hold on 
plot(D,Mnorm)
hold off