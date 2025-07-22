import numpy as np

class BandpassIsobaricBox:
    def __init__(self, params):
        # params: diccionario con todos los parámetros necesarios
        self.p = params

    def simulate(self, freq):
        # Extrae parámetros
        p = self.p
        ρ0 = p['rho0']
        c0 = p['c0']
        BL = p['BL']
        Re = p['Re']
        Red = p['Red']
        Qes = p['Qes']
        Qms = p['Qms']
        fs = p['fs']
        Lvc = p['Lvc']
        S = p['S']
        Vab = p['Vab']
        fp = p['fp']
        dd = p['dd']
        dp = p['dp']

        # Derivados
        Mms = Qes*(BL**2)/(2*np.pi*fs*Re)
        Cms = 1/(Mms*(2*np.pi*fs)**2)
        Rms = 2*np.pi*fs*Mms/Qms
        Cab = Vab/(ρ0*c0**2)
        M_ap = 1/(Cab*(2*np.pi*fp)**2)
        ad = dd/2
        ap = dp/2
        A = np.pi*(ap**2)
        k = 2*np.pi*fp/c0

        # Impedancias de radiación y ducto
        Rarf = c0*ρ0/(np.pi*(ad)**2)
        Marf = 8*ρ0/(3*ad*(np.pi)**2)
        Rarp = c0*ρ0/(np.pi*(ad)**2)
        Marp = p['B']*ρ0/(np.pi*ad)
        Rapp = 0.479*ρ0*c0/ap**2
        Mapp = 0.270*ρ0/ap

        # Cambios por isobárico doble
        Re = Re/2
        Lvc = Lvc/2
        Mmd = 2*p['Mmd']
        Cms = Cms/2
        Rms = 2*Rms
        S = 2*S
        Marf = Marf/2

        # Valores acústicos
        Carp = Marp*(S**2)/(BL**2)
        Rarp = (BL**2)/(Rarp*(S**2))
        Lbox = (BL**2)*Cab/S**2
        Rbox = 1200
        Cp = Marp*(S**2)/(BL**2)
        Rp = (BL**2)/(Rapp*(S**2))
        Rap = 50
        Map = M_ap*(S**2)/(BL**2)
        Ca = Marf*(S**2)/(BL**2)
        Ra = (BL**2)/(Rarf*(S**2))
        Csps = Mmd/(BL**2)
        Lsps = Cms*(BL**2)
        Reps = 56.7

        # Simulación
        f = np.arange(1, len(freq)+1)
        SPL = []
        SPLΦ = []
        Zt = []
        ZtΦ = []
        DEZ = []
        LWA = []
        datos = []
        lineal = []

        for i in f:
            freqi = freq[i-1]
            w = 2*np.pi*freqi

            Z10 = Rarp + 1/(1j*w*Carp)
            ZLbox = 1j*w*Lbox
            ZRbox = Rbox
            Z20 = 1/(1/Z10 + 1/ZRbox + 1/ZLbox)
            ZMap = 1/(1j*w*Map)
            ZRap = Rap
            ZB1 = Rp + 1/(1j*w*Cp)
            Znext = 1/(1/ZMap + 1/ZRap + 1/ZB1)
            Z30 = Znext + Z20
            ZB2 = Ra + 1/(1j*w*Ca)
            ZReps = Reps
            ZLsps = 1j*w*Lsps
            ZCsps = 1/(1j*w*Csps)
            Zmiddle = 1/(1/ZCsps + 1/ZLsps + 1/ZReps + 1/ZB2)
            Z40 = 1/(1/Zmiddle + 1/Z30)
            ZLvc = 1j*w*Lvc
            Zinput = 1/(1/ZLvc + 1/Red) + Re
            Z50 = Zinput + Z40

            R39 = np.abs(Z50)
            R40 = np.angle(Z50, deg=True)
            R33 = np.abs(Z20)
            R37 = np.abs(Z40)
            R35 = np.abs(Z30)

            Zt.append(R39)
            ZtΦ.append(R40)

            Gspl = R33*R37/(R35*R39)
            SPLi = 20*np.log10(ρ0*w*(dd**2)*Gspl*p['V0']/(16*(10**-5)*BL))
            SPL.append(SPLi)
            lineali = (ρ0*(dd**2)*Gspl*p['V0']/(16*(10**-5)*BL))
            lineal.append(lineali)

            datos.append(R40)
            Gain = R37/R39
            DEZi = np.sqrt(2)*Gain*p['V0']/(w*BL)
            DEZi = DEZi*1000
            DEZ.append(DEZi)
            LWAi = 10*np.log10((Ra*(Gspl*p['V0']/(R33))**2)/(6.31*(10**-12)))
            LWA.append(LWAi)

        # Group delay
        groupdelay = []
        for i in range(1, len(datos)-1):
            groupdelayi = -1000*((datos[i] - datos[i-1])/(freq[i] - freq[i-1]) + (datos[i+1]-datos[i])/(freq[i+1] - freq[i]))/(2*360)
            groupdelay.append(groupdelayi)
        groupdelay = [groupdelay[0]] + groupdelay + [groupdelay[-1]]

        return {
            "freq": freq,
            "Zt": np.array(Zt),
            "ZtΦ": np.array(ZtΦ),
            "SPL": np.array(SPL),
            "DEZ": np.array(DEZ),
            "groupdelay": np.array(groupdelay),
            "LWA": np.array(LWA),
        }