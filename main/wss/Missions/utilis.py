def constrain(MA, MB):
    MA = int(MA)
    MB = int(MB)
    if MA > 15: MA = 15
    if MB > 20: MB = 20

    if MA < -15: MA = -15
    if MB < -20: MB = -20

    return MA, MB

def u_colcultor(e, EOLD, x = 1):
    from wss.consumers import KD, KP
    Up = KP * e * x
    Ud = x * KD * (e - EOLD) 
    EOLD = e
    U = Up + Ud

    return U