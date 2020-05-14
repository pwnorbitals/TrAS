import numpy as np

def Header(head):
    Y = list()
    for i in head:
        if(i.find('-')!=-1):
            Y.append(i)
    return Y

def Find_tftt(T, kp, Y):
    mean = sum(Y)/len(Y)
    Up_1 = 0
    Down_1 = 0
    Up_2 = 0
    Down_2 = 0

    for i in range(len(Y)):
        if (Y[i] < mean and Down_1 == 0):
            Down_1 = T[kp[i]]
        elif (Y[i] < mean and Down_1 != 0):
            Down_2 = T[kp[i]]
        else:
            if (Down_1 == 0):
                Up_1 = T[kp[i]]
            elif(Down_2 != 0 and Up_2 == 0):
                Up_2 = T[kp[i]]
    
    T_t = Up_2 - Up_1
    if Down_2 == 0:
        T_f = 0
    else:
        T_f = Down_2 - Down_1
    return T_t, T_f


def Param(R_star, Period, time, k_ps, Y):
    """
    Input : Radius of the star, Period in seconds,
    timestamp in seconds, kept_peaks, magnitude
    """
    # Light curve data
    T_t, T_f = Find_tftt(time, k_ps, Y)
    Depth = abs(max(Y) - min(Y))
    print("\t",T_t)
    print("\t",T_f)
    # Impact parameter b
    sinT_t = np.float_power( np.sin(T_t * np.pi/Period), 2) 
    sinT_f = np.float_power( np.sin(T_f * np.pi/Period), 2)

    return Depth, sinT_t, sinT_f, T_t, T_f

def Impact_parameter(sinT_t, sinT_f, Depth):
    """
    Input : sin^2(T_t*pi/Period), sin^2(T_f*pi/Period),
    Depth
    """
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    B = np.float_power((1 - np.sqrt(Depth)), 2)
    b = np.sqrt(abs(B - sinT_f*A/sinT_t) / (1 - sinT_f/sinT_t))
    return b

def Semimajor(R_star, sinT_t, Depth, b):
    """
    Input : Radius of the star, sin^2(T_t*pi/Period),
    Depth (or Delta Flux), impact parameter b
    """
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    a = R_star * np.sqrt(abs(A - (1-sinT_t)*np.float_power(b, 2)) / (sinT_t))
    return a

def Inclinaison(R_star, a, b):
    """
    Input : Radius of the star, semi-major axis a,
    impact parameter b
    """
    i = np.arccos(R_star*b/a)
    return i*180/np.pi

def Planet_radius(R_star, Depth):
    Rp = R_star*np.sqrt(Depth)
    return Rp

def Star_density(Depth, b, sinT_t, Period):
    G = 6.67430 * np.float_power(10, -17)
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    x1 = (4* np.float_power(np.pi, 2) )/(G* np.float_power(Period, 2))
    x2 = (A-np.float_power(b, 2)*(1-sinT_t)) / sinT_t

    rho_star = x1 * np.float_power(x2, 3/2)
    return rho_star

def Star_mass(R_star, rho_star):
    M_star = (4/3) * np.pi * rho_star * np.float_power(R_star, 3)
    return M_star

def Planet_mass(M_star, Period, a):
    G = 6.67430 * np.float_power(10, -17)
    M_planet = abs((4 * np.float_power(np.pi, 2) * np.float_power(a, 3))/(G * np.float_power(Period, 2)) - M_star)
    return M_planet