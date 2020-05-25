# Copyright 2020 de Claverie Chris
# Copyright 2020 Calka Magdalena
# Copyright 2020 Boitier William


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np

def Param(R_star, Period, time, k_ps, Y):
    """
    Input : Radius of the star, Period in seconds,
    timestamp in seconds, kept_peaks, magnitude
    """
    # Light curve data
    T_t = time[k_ps[5]] - time[k_ps[1]]
    T_f = time[k_ps[4]] - time[k_ps[2]]
    MinMag = Y[k_ps[3]]

    # Depth or Delta F
    Depth = 1 - abs(MinMag)

    # Impact parameter b
    sinT_t = np.sin(T_t * np.pi/Period)^2
    sinT_f = np.sin(T_f * np.pi/Period)^2

    return Depth, sinT_t, sinT_f

def Impact_parameter(sinT_t, sinT_f, Depth):
    """
    Input : sin^2(T_t*pi/Period), sin^2(T_f*pi/Period),
    Depth
    """
    A = (1 + np.sqrt(Depth))^2
    B = (1 - np.sqrt(Depth))^2

    b = np.sqrt((A - sinT_f*B/sinT_t) / (1 - sinT_f/sinT_t))
    return b

def Semimajor(R_star, sinT_t, Depth, b):
    """
    Input : Radius of the star, sin^2(T_t*pi/Period),
    Depth (or Delta Flux), impact parameter b
    """
    A = (1 + np.sqrt(Depth))^2

    a = R_star * np.sqrt((A^2 - (1-sinT_t)*b^2) / (sinT_t))
    return a

def Inclinaison(R_star, a, b):
    """
    Input : Radius of the star, semimajor axis a,
    impact parameter b
    """
    i = np.acos(R_star*b/a)
    return i

def Planet_radius(R_star, Depth):
    Rp = R_star*np.sqrt(Depth)
    return Rp

def Star_density(Depth, b, sinT_t, Period):
    G = 6.67430 * 10^-11
    A = (1 + np.sqrt(Depth))^2

    rho_star = (4*np.pi^2)/(G*Period^2) * ((A-(1-sinT_t)*b^2) / sinT_t)^(3/2)
    return rho_star

def Star_mass(R_star, rho_star):
    M_star = (4/3) * np.pi * rho_star * R_star^3
    return M_star

def Planet_mass(M_star, Period, a):
    M_planet = (4 * np.pi^2 * a^3)/(G * Period^2) - M_star
    return M_planet