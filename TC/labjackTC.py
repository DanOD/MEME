import u6
import math
import numpy as np
# Coefficients

# -200 C to 0 C
# -5.891 mV to 0 mV
# 0.0E0
# 2.5173462E1
# -1.1662878E0
# -1.0833638E0
# -8.977354E-1
# -3.7342377E-1
# -8.6632643E-2
# -1.0450598E-2
# -5.1920577E-4
voltsToTemp1 = (0.0E0,
                2.5173462E1,
                -1.1662878E0,
                -1.0833638E0,
                -8.977354E-1,
                -3.7342377E-1,
                -8.6632643E-2,
                -1.0450598E-2,
                -5.1920577E-4)

# 0 C to 500 C
# 0 mV to 20.644 mV
# 0.0E0
# 2.508355E1
# 7.860106E-2
# -2.503131E-1
# 8.31527E-2
# -1.228034E-2
# 9.804036E-4
# -4.41303E-5
# 1.057734E-6
# -1.052755E-8
voltsToTemp2 = (0.0E0,
                2.508355E1,
                7.860106E-2,
                -2.503131E-1,
                8.31527E-2,
                -1.228034E-2,
                9.804036E-4,
                -4.41303E-5,
                1.057734E-6,
                -1.052755E-8)

# 500 C to 1372 C
# 20.644 mV to 54.886 mV
# -1.318058E2
# 4.830222E1
# -1.646031E0
# 5.464731E-2
# -9.650715E-4
# 8.802193E-6
# -3.11081E-8
voltsToTemp3 = (-1.318058E2,
                4.830222E1,
                -1.646031E0,
                5.464731E-2,
                -9.650715E-4,
                8.802193E-6,
                -3.11081E-8)


def voltsToTempConstants(mVolts):
    if mVolts < -5.891 or mVolts > 54.886:
        raise Exception("Invalid range")
    if mVolts < 0:
        return voltsToTemp1
    elif mVolts < 20.644:
        return voltsToTemp2
    else:
        return voltsToTemp3


# -270 C to 0 C
# 0E0
# 0.39450128E-1
# 0.236223736E-4
# -0.328589068E-6
# -0.499048288E-8
# -0.675090592E-10
# -0.574103274E-12
# -0.310888729E-14
# -0.104516094E-16
# -0.198892669E-19
# -0.163226975E-22
tempToVolts1 = (0.0E0,
                0.39450128E-1,
                0.236223736E-4,
                -0.328589068E-6,
                -0.499048288E-8,
                -0.675090592E-10,
                -0.574103274E-12,
                -0.310888729E-14,
                -0.104516094E-16,
                -0.198892669E-19,
                -0.163226975E-22)


# 0 C to 1372 C
# -0.176004137E-1
# 0.38921205E-1
# 0.1855877E-4
# -0.994575929E-7
# 0.318409457E-9
# -0.560728449E-12
# 0.560750591E-15
# -0.3202072E-18
# 0.971511472E-22
# -0.121047213E-25
#
# 0.1185976E0
# -0.1183432E-3
# 0.1269686E3
class ExtendedList(list):
    def __init__(self):
        list.__init__(self)
        self.extended = None


tempToVolts2 = ExtendedList()
tempToVolts2.append(-0.176004137E-1)
tempToVolts2.append(0.38921205E-1)
tempToVolts2.append(0.1855877E-4)
tempToVolts2.append(-0.994575929E-7)
tempToVolts2.append(0.318409457E-9)
tempToVolts2.append(-0.560728449E-12)
tempToVolts2.append(0.560750591E-15)
tempToVolts2.append(-0.3202072E-18)
tempToVolts2.append(0.971511472E-22)
tempToVolts2.append(-0.121047213E-25)
tempToVolts2.extended = (0.1185976E0, -0.1183432E-3, 0.1269686E3)


def tempToVoltsConstants(tempC):
    if tempC < -270 or tempC > 1372:
        raise Exception("Invalid range")
    if tempC < 0:
        return tempToVolts1
    else:
        return tempToVolts2


def evaluatePolynomial(coeffs, x):
    tot = 0
    y = 1
    for a in coeffs:
        tot += y * a
        y *= x
    return tot


def tempCToMVolts(tempC): ### converts temp input of C into mV
    coeffs = tempToVoltsConstants(tempC)
    if hasattr(coeffs, "extended"):
        a0, a1, a2 = coeffs.extended
        extendedCalc = a0 * math.exp(a1 * (tempC - a2) * (tempC - a2))
        return evaluatePolynomial(coeffs, tempC) + extendedCalc
    else:
        return evaluatePolynomial(coeffs, tempC)


def mVoltsToTempC(mVolts): ### converts TC input of mvolts into temp
    coeffs = voltsToTempConstants(mVolts)
    return evaluatePolynomial(coeffs, mVolts)

# d is labjack, pin is input pin #
def TCvalue(d,pin): ### pin is array of Nx1 where N is 14 or less (AINs used in labjack)

    CJ=d.getTemperature()+2.5-273.15 ### CJ is background temp for comparison to TC temp
    temperature = np.zeros(len(pin))
    mVbackground = tempCToMVolts(CJ)
    for i in range(0,len(pin)):
        mVlabjack = d.getAIN(pin[i], resolutionIndex = 8, gainIndex = 3)*1000 ### gets mV reading from labjack per pin
        temperature[i] = mVoltsToTempC(mVlabjack + mVbackground) ### add mV from labjack and background, convert to temp, fill in temperature array
    return temperature ### output array of array of  length len(pin)
