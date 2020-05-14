from numpy import float_power as fpow
from numpy import arccos as acos
from numpy import sqrt, pi, cos, sin

from sympy.functions.special.elliptic_integrals import elliptic_k, elliptic_e, elliptic_pi

def F_kn_generator(p,z):
    
    a = fpow((p-z),2)
    b = fpow((p+z),2)
    
    # Special formula (not calculated in specific cases)
    if a>=1:
        CI = 0
    else:
        CI = 2 / (9*pi*sqrt(1-a))
    if a==0:
        CIPI = 0
    else:
        CIPI = -3*(p+z)/(p-z)
    if z==0:
        CG = 0
        k0 = 0
        k1 = 0
    else:
        CG = 1 / (9*pi*sqrt(p*z))
        k0 = acos((fpow(p,2)+fpow(z,2)-1)/(2*p*z))
        k1 = acos((fpow(z,2)+1-fpow(p,2))/(2*z))
    if(a<1 or b>1): #(a+b-a*b-1)<0
        G2 = 0
    else:
        G2 = (k1 + fpow(p,2)*(fpow(p,2)+2*fpow(z,2))*k0 - (1/4)*(1+5*fpow(p,2)+fpow(z,2))*sqrt(a+b-a*b-1))/(2*pi)
    if(fpow(z,2) -(1/4)* fpow((1+fpow(z,2)-fpow(p,2)), 2))<0:
        G0 = 0
    else:
        G0 = (fpow(p,2)*k0 + k1 - sqrt(fpow(z,2) -(1/4)* fpow((1+fpow(z,2)-fpow(p,2)), 2)) )/pi

    t2 = fpow(p,2) + fpow(z,2)
    p_hat = sqrt(p*(1-p))
    p_prim = sqrt(1-fpow(p,2))
    CIK = 1 - 5*fpow(z,2)+ fpow(p,2)+ a*b
    CIE = (fpow(z,2) +7*fpow(p,2)-4)*(1-a)
    CGK = 3 - 6*fpow((1-fpow(p,2)),2)-2*p*z*(fpow(z,2)+7*fpow(p,2)-4+5*p*z)
    CGE = 4*z*p*(fpow(z,2) +7*fpow(p,2)-4)
    CGPI = CIPI
    TI = 2/(3*pi) * acos(1-2*p) - (4/(9*pi))*(3+2*p-8*fpow(p,2))*p_hat

    k_vector = [0,0, sqrt(4*p*z/(1-a)), 0, sqrt((1-a)/(4*p*z)), 2*p, 0, 1/(2*p), sqrt(4*p*z/(1-a)), 0, sqrt((1-a)/(4*p*z)),0]
    
    n_vector = [0,0, -4*p*z/a, 0, (a-1)/a, 0, 0, 0, -4*p*z/a, 0, (a-1)/a, 0]
    
    F_matrix = [[fpow(p,2), (2/3)*(1 - fpow(p_prim,3)), 0, 0, 0, (1/2)*fpow(p,4)],
            [1, 2/3, 0, 0, 0, 1/2],
            [fpow(p,2), 2/3, CI*CIK, CI*CIE, CI*CIPI, (1/2)*fpow(p,2)*(fpow(p,2)+2*fpow(z,2))],
            [fpow(p,2), TI, 0, 0, 0, (1/2)*fpow(p,2)*(fpow(p,2)+2*fpow(z,2))],
            [G0, 2/3, CG*CGK, CG*CGE, CG*CGPI, G2],
            [fpow(p,2), 1/3, (2/(pi*9))*(1-4*fpow(p,2)), (8/(9*pi))*(2*fpow(p,2)-1), 0, (3/2)*fpow(p,4)],
            [1/4, (1/3 - (4/(9*pi))), 0, 0, 0, 3/32],
            [G0, 1/3, -(1/(9*pi*p))*(1-4*fpow(p,2))*(3-8*fpow(p,2)), (1/(9*pi))*16*p*(2*fpow(p,2)-1), 0, G2],
            [fpow(p,2), 0, CI*CIK, CI*CIE, CI*CIPI, (1/2)*fpow(p,2)*(fpow(p,2)+2*fpow(z,2))],
            [fpow(p,2), TI, 0, 0, 0, (1/2)*fpow(p,2)*(fpow(p,2)+2*fpow(z,2))],
            [G0, 0, CG*CGK, CG*CGE, CG*CGPI, G2],
            [0, 0, 0, 0, 0, 0]]
    
    return F_matrix, n_vector, k_vector

def W_limbcoefficient(lico):
    W = 6 - 2*lico[0] - lico[1]

    W0 = (6-6*lico[0]-12*lico[1])/W
    W1 = (6*lico[0]+12*lico[1])/W
    W2 = 6*lico[1] / W

    return [W0,W1,W2]

def Cases_z_p(z, p):
    if(z==0 and p<1):
        #A
        return 0
    elif(z<=(p-1)):
        #Ag
        return 1
    elif(z<p and z<(1-p)):
        #B
        return 2
    elif(z<p and z==(1-p)):
        #Bt
        return 3
    elif(z<p):
        #Bg
        return 4
    elif(z==p and z<(1-p)):
        #C
        return 5
    elif(z==p and p==1/2):
        #Ct
        return 6
    elif(z==p):
        #Cg
        return 7
    elif(z<(1-p)):
        #D
        return 8
    elif(z==(1-p)):
        #E
        return 9
    elif(z<(1+p)):
        #F
        return 10
    else:
        #G
        return 11


def Theoretical_LC(Depth, Rstar, time, Te, Period, a, b, incli, limbcoef=[0,0]):
    """ Period, time and Te must have the same unit
    Hours or days are the best option has we take a step of 0.001"""
    p = sqrt(Depth)
    w = 2*pi/Period
    W_vec = W_limbcoefficient(limbcoef)

    f = list()
    for t in time:
        
        z = sqrt(fpow(a/Rstar,2) * fpow(sin(w*(t-Te)),2) + fpow(b,2)*fpow(cos(w*(t-Te)),2))
        
        F, n, k = F_kn_generator(p, z)
        
        i = Cases_z_p(z, p)
        
        K = elliptic_k(k[i])
        
        E = elliptic_e(k[i])
        
        PI = elliptic_pi(n[i],k[i])
        
        Df = W_vec[0]*F[i][0] + W_vec[2]*F[i][5] + W_vec[1]*(F[i][1] + F[i][2]*K + F[i][3]*E + F[i][4]*PI)
        
        f.append(1-Df)
    return f


