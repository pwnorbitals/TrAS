function [f,t] =  theoretical_light_curve_Pal(Rplanet,Rstar,limbcoeff,TIn,Tend,tE,Periodh,a,incld) 
%%this program has been built following the instructions in Properties of
%analytic transit light-curve models Andr´as P´al
%doi:10.1111/j.1365-2966.2008.13723.x
% Author: Marco R. Inchingolo

%input example 
% Rplanet = 121536.4;%km
% Rstar = 1217475;%km
% tE = 10;%time of the eclipse [days]
% Period =  2.14363592;%orbital period days
% a = 5152150.666908;%semimajor axis km
% limbcoeff = [0.47 0.23]
% incl = 80.09; %inclination of the orbit degree

%initialization
p = Rplanet/Rstar;
%coefficient of sun ->wikipedia https://en.wikipedia.org/wiki/Limb_darkening
%by putting 0 you remove the effect of limb darkening
gam1 = limbcoeff(1);
gam2 = limbcoeff(2);
t = TIn:0.001:Tend;%time days
w = 2*pi/Periodh;%orbital angular speed
b = a/Rstar*cosd(incld);%impact parameter 
z1 = sqrt((a./Rstar).^2.*sin(w.*(t-tE)).^2+b.^2.*cos(w.*(t-tE)).^2);%z(t)
Df = zeros(1,length(z1));

for i = 1:length(z1)
 z = z1(i);
[Fmatrix,KNmatrix] = F_kn_generator(p,z);
%F = zeros(1,6);%F0,F1,FK,FE,FPI,F2 in the same order of the table A2
%kn = zeros(1,2);%k,n
%different cases
if z==0&&p<1
    %A
    F = Fmatrix(1,:);
    kn = KNmatrix(1,:);
elseif z<=(p-1)
    %Ag 
    F = Fmatrix(2,:);
    kn = KNmatrix(2,:);
elseif z<p&&z<(1-p)
    %B    
    F = Fmatrix(3,:);
    kn = KNmatrix(3,:);
elseif z<p&&z==(1-p)
    %Bt
    F = Fmatrix(4,:);
    kn = KNmatrix(4,:);
elseif z<p
    %Bg   
    F = Fmatrix(5,:);
    kn = KNmatrix(5,:);
elseif z==p&&z<(1-p)
    %C    
    F = Fmatrix(6,:);
    kn = KNmatrix(6,:);
elseif z==p&&p==1/2
    %Ct    
    F = Fmatrix(7,:);
    kn = KNmatrix(7,:);
elseif z==p
    %Cg    
    F = Fmatrix(8,:);
    kn = KNmatrix(8,:);
elseif z<(1-p)
    %D    
    F = Fmatrix(9,:);
    kn = KNmatrix(9,:);
elseif z==(1-p)
    %E    
    F = Fmatrix(10,:);
    kn = KNmatrix(10,:);
elseif z<(1+p)
    %F    
    F = Fmatrix(11,:);
    kn = KNmatrix(11,:);
else 
    %G 
    F = Fmatrix(12,:);
    kn = KNmatrix(12,:);
end
%the variable to put inside the ellipke and ellipticPi is not simply k as
%it was supposed to be but k^2 according to https://math.stackexchange.com/questions/627956/how-to-compute-elliptic-integrals-in-matlab
% section "more about" in https://fr.mathworks.com/help/matlab/ref/ellipke.html
[K,E] = ellipke(kn(1)^2);
PI = ellipticPi(kn(2),kn(1)^2);
W = 6-2*gam1-gam2;
W0 = (6-6*gam1-12*gam2)/W; 
W1 = (6*gam1+12*gam2)/W;
W2 = 6*gam2/W;
%F0,F1,FK,FE,FPI,F2
%Df = W0*F0 + W2*F2+W1(F1 + FK*K + FE*E + FPI*PI]
Df(i) = W0*F(1)+W2*F(6)+W1*(F(2)+F(3)*K+F(4)*E+F(5)*PI);
end
f = 1-Df;


