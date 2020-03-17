function [Fmatrix,KNmatrix] = F_kn_generator(p,z)
%F_KN_GENERATOR generate the F functions and k parameters for the theoretical_light_curve_Pal
%starting only from p and z
% those calculation here a presented are referred to the paper analytic transit light-curve models Andr´as P´al
%doi:10.1111/j.1365-2966.2008.13723.x
% Author: Marco R. Inchingolo

a = (p-z)^2;
b = (p+z)^2;
t2 = p^2+z^2;
CI = 2/(9*pi*sqrt(1-a));
CIK = 1-5*z^2+p^2+a*b;
CG = 1/(9*pi*sqrt(p*z));
CGK = 3-6*(1-p^2)^2-2*p*z*(z^2+7*p^2-4+5*p*z);
pcap = sqrt(p*(1-p));
TI = 2/(3*pi)*acos(1-2*p)-4/(9*pi)*(3+2*p-8*p^2)*pcap;
k0 = acos((p^2+z^2-1)/(2*p*z));
k1 = acos((z^2+1-p^2)/(2*z));
G0 = 1/pi*(p^2*k0+k1-sqrt(z^2-1/4*(1+z^2-p^2)^2));
p1 = sqrt(1-p^2);
CIE = (z^2+7*p^2-4)*(1-a);
CIPI = -3*(p+z)/(p-z);
CGE = 4*p*z*(z^2+7*p^2-4);
CGPI = -3*(p+z)/(p-z);
G2 = (k1+p^2*(p^2+2*z^2)*k0-1/4*(1+5*p^2+z^2)*sqrt((1-a)*(b-1)))/(2*pi);
%matrix of table A2
         %F0          F1               FK                               FE                         FPI               F2   
Fmatrix = [p^2        2/3*(1-p1^3)     0                                 0                         0                 1/2*p^4;              %A
           1          2/3              0                                 0                         0                 1/2;                  %AG 
           p^2        2/3              CI*CIK                            CI*CIE                    CI*CIPI           1/2*p^2*(p^2+2*z^2);  %B    
           p^2        TI               0                                 0                         0                 1/2*p^2*(p^2+2*z^2);  %BT      
           G0         2/3              CG*CGK                            CG*CGE                    CG*CGPI           G2;                   %BG
           p^2        1/3              2/(9*pi)*(1-4*pi^2)               8/(9*pi)*(2*p^2-1)        0                 3/2*p^4;              %C      
           1/4        1/3-4/(9*pi)     0                                 0                         0                 3/32;                 %CT 
           G0         1/3              -1/(9*pi*p)*(1-4*p^2)*(3-8*p^2)   1/(9*pi)*16*p*(2*p^2-1)   0                 G2;                   %CG
           p^2        0                CI*CIK                            CI*CIE                    CI*CIPI           1/2*p^2*(p^2+2*z^2);  %D       
           p^2        TI               0                                 0                         0                 1/2*p^2*(p^2+2*z^2);  %E    
           G0         0                CG*CGK                            CG*CGE                    CG*CGPI           G2;                   %F
           0          0                0                                 0                         0                 0;                    %G
           ];
        %     k                     n
 KNmatrix = [ 0                     0;
              0                     0;        
              sqrt((4*p*z)/(1-a))   -(4*p*z)/a;                        
              0                     0;          
              sqrt((1-a)/(4*p*z))   (a-1)/a;                     
              2*p                   0;            
              0                     0;          
              1/(2*p)               0;                 
              sqrt((4*p*z)/(1-a))   -(4*p*z)/a;                            
              0                     0;           
              sqrt((1-a)/(4*p*z))   (a-1)/a;                        
              0                     0;
              ];
end

