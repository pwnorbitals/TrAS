function [F,t] =  theoretical_light_curve_mandel(Rplanet,Rstar,limbcoeff,TIn,Tend,tE,Periodd,aplanet,incld)
%%this program has been built following the instructions in 
%ANALYTIC LIGHT CURVES FOR PLANETARY TRANSIT SEARCHES-MANDEL&AGOL 2002
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
%coefficients of sun ->wikipedia https://en.wikipedia.org/wiki/Limb_darkening
%by putting 0 you remove the effect of limb darkening
gam1 = limbcoeff(1);
gam2 = limbcoeff(2);
c2 = gam1+2*gam2;
c4 = -gam2;
c0 = 1-c2-c4;
OMEG = c0/4+c2/6+c4/8;
t = TIn:0.001:Tend;%time days
w = 2*pi/Periodd;%orbital angular speed
bplanet = aplanet/Rstar*cosd(incld);%impact parameter 
z1 = sqrt((aplanet./Rstar).^2.*sin(w.*(t-tE)).^2+bplanet.^2.*cos(w.*(t-tE)).^2);%z(t)
%z1 = sqrt((w*aplanet./Rstar).^2.*(t-tE).^2+bplanet.^2);%approximation of the upper one
F = zeros(1,length(z1));

for i = 1:length(z1)
 z = z1(i);
 a = (z-p)^2;
 b = (z+p)^2;
 k = sqrt((1-a)/(4*z*p));
 q = p^2-z^2;
 k0 = acos((p^2+z^2-1)/(2*p*z));
 k1 = acos((1-p^2+z^2)/(2*z));
 eta2 = p^2/2*(p^2+2*z^2);
 eta1 = 1/(2*pi)*(k1+2*eta2*k0-1/4*(1+5*p^2+z^2)*sqrt((1-a)*(b-1)));
 %the elliptic integrals calculations are contained in the if, to reduce
 %the time of the calculations
 %different cases
 if p>=0&&z>=(1+p) %1 
    %G 
    lambd = 0;
    etad = 0;
 elseif p>=0&&z>(1/2+abs(p-1/2))&&z<(1+p)%2
    %F    
    %the variable to put inside the ellipke and ellipticPi is not simply k as
    %it was supposed to be but k^2 according to https://math.stackexchange.com/questions/627956/how-to-compute-elliptic-integrals-in-matlab
    % section "more about" in https://fr.mathworks.com/help/matlab/ref/ellipke.html
    [K1,E1] = ellipke(k^2);
    PI1 = ellipticPi((a-1)/a,k^2);
    lamb1 = 1/(9*pi*sqrt(p*z))*(((1-b)*(2*b+a-3)-3*q*(b-2))*K1+4*p*z*(z^2+7*p^2-4)*E1-3*q/a*PI1);
    lambd = lamb1;
    etad = eta1;
 elseif p>0&&p<1/2&&z>p&&z<(1-p)%3
    %D    
    [K2,E2] = ellipke((1/k)^2);
    PI2 = ellipticPi((a-b)/a,(1/k)^2);
    lamb2 = 2/(9*pi*sqrt(1-a))*((1-5*z^2+p^2+q^2)*K2+(1-a)*(z^2+7*p^2-4)*E2-3*q/a*PI2);
    lambd = lamb2;
    etad = eta2;
 elseif z==(1-p)&&p>0&&p<1/2%4
    %E   
    lamb5 = 2/(3*pi)*acos(1-2*p)-4/(9*pi)*(3+2*p-8*p^2)*sqrt(p*(1-p))-2/3*((p-0.5)>0);%added sqrt(p*(1-p))-2/3*((p-0.5)>0)
    lambd = lamb5;
    etad = eta2;
 elseif z==p&&p>0&&p<1/2%5
    %C   
    [K4,E4] = ellipke((2*p)^2);%changed 2k
    lamb4 = 1/3+2/(9*pi)*(4*(2*p^2-1)*E4+(1-4*p^2)*K4);
    lambd = lamb4;
    etad = eta2;
 elseif z==p&&p==1/2%6
    %Ct    
    disp(z)
    lambd = 1/3-4/(9*pi);
    etad = 3/32;
 elseif z==p&&p>1/2%7
    %Cg    
    [K3,E3] = ellipke((1/(2*k))^2);%changed 1/2k
    lamb3 = 1/3+16*p/(9*pi)*(2*p^2-1)*E3-(1-4*p^2)*(3-8*p^2)/(9*pi*p)*K3;
    lambd = lamb3;
    etad = eta1;
 elseif p>1/2&&z>=abs(1-p)&&z<p%8
    %Bg   
    [K1,E1] = ellipke(k^2);
    PI1 = ellipticPi((a-1)/a,k^2);
    lamb1 = 1/(9*pi*sqrt(p*z))*(((1-b)*(2*b+a-3)-3*q*(b-2))*K1+4*p*z*(z^2+7*p^2-4)*E1-3*q/a*PI1);
    lambd = lamb1;
    etad = eta1;   
 elseif p>0&&p<1&&z>0&&z<(1/2-abs(p-1/2))%9
    %B    
    [K2,E2] = ellipke((1/k)^2);
    PI2 = ellipticPi((a-b)/a,(1/k)^2);
    lamb2 = 2/(9*pi*sqrt(1-a))*((1-5*z^2+p^2+q^2)*K2+(1-a)*(z^2+7*p^2-4)*E2-3*q/a*PI2);
    lambd = lamb2;
    etad = eta2;  
 elseif z==0&&p>0&&p<1%10
    %A
    lamb6 = -2/3*(1-p^2)^(3/2);
    lambd = lamb6;
    etad = eta2;   
 elseif p>1&&z>=0&&z<=(p-1)%11
    %Ag 
    lambd = 0;
    etad = 1/2;   
 end  
    
if (1+p)<z
    lambE = 0;
elseif abs(1-p)<z&&z<=(1+p)
    lambE = 1/pi*(p^2*k0+k1-sqrt((4*z^2-(1+z^2-p^2)^2)/4));    
elseif z<=(1-p)
    lambE = p^2;   
elseif z<=(p-1)
    lambE = 1;
end

 F(i) = 1-1/(4*OMEG)*((1-c2)*lambE+c2*(lambd+2/3*(p>z))-c4*etad);
end

