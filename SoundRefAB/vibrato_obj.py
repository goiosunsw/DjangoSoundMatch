import numpy as np
from scipy.interpolate import interp1d

def Centroid(hamp):
    '''Calculate the centroid of a harmonic sequence'''
    allamp = 0.0
    allfsum = 0.0
    for hno0, amp in enumerate(hamp):
        hno = hno0+1
        allamp += amp
        allfsum += hno*amp
    
    return allfsum/allamp

def RMSampl(hamp):
    '''Calculate the RMS amplitude of a harmonic sequence'''
    ampsq = 0.0
    for hno0, amp in enumerate(hamp):
        hno = hno0+1
        ampsq += amp*amp
    
    return np.sqrt(ampsq)

def SlopeToHmult(slope, nharm):
    '''Calculate a harmonic sequence for a constant dB slope'''
    
    base = np.exp(slope)
    hamp = []
    for i in xrange(nharm):
        hn = i
        hamp.append(base**(hn-(nharm-1)/2.0))
        #hamp.append(np.sqrt(((hn/float(nharm-1)-.5 )*2.*(-slope)+1.)/nharm)) 
    ha = np.array(hamp)
    return ha /np.sqrt(sum(ha*ha))


class SlopeHarmonicScaler(object):
    '''Object for quick calculation of a harmonic for 
    a desired spectral centroid
    * for val=0, centroid is on 1st harmonic
    * for val=1, centroid is on last harmonic
    * Centroid variation is produced by a change in spectral slope
    * Spectrum is a linear slope in dB'''
    def __init__(self, nharm=2, npoints=100, slopelim=4):
        self.nharm = nharm
        
        slopes = np.linspace(-slopelim,slopelim,npoints)
        cent = np.zeros(len(slopes)+2)
        hamps = np.zeros((len(slopes)+2,nharm))
        
        
        
        for (ii,slope) in enumerate(slopes):
            hamp = SlopeToHmult(slope,nharm)
            cent[ii+1]=(Centroid(hamp))
            hamps[ii+1,...] = hamp
        
        hamps[0,0]=1.
        hamps[-1,-1]=1.
        
        cent[0] = 1.
        cent[-1] = nharm
        
        self.fharm=[]
        
        for ii in xrange(nharm):
            ff = interp1d(cent, hamps[...,ii], kind='cubic')
            self.fharm.append(ff)
        
        self.vmin = np.min(cent)
        self.vmax = np.max(cent)
        
    def __call__(self, val):
        hh = []
        cent = val*(self.nharm-1.)+1.
        for ii in xrange(self.nharm):
            hh.append(self.fharm[ii](cent))
        return np.array(hh)

class VibratoProfile(object):
    '''A vibrato time-profile'''
    def __init__(self, t_vals=[0.0,1.0], a_vals=[1.0,1.0], vibfreq=5.0):
        ti=np.array(t_vals)
        ai=np.array(a_vals)
        # max of vibrato profile is 1
        ai = ai/np.max(ai)

        t_max = max(ti)
        tout = np.arange(0,t_max,1./vibfreq/16.0)
        aout = np.interp(tout,ti,ai)

        i_st = min(np.argmin(ai>0.0),1)-1
        t_st = t_vals[i_st]

        self.t = tout
        self.vibprof = aout*np.sin(2*np.pi*vibfreq*(tout-t_st))
    
    def __call__(self,t):
        return np.interp(t,self.t,self.vibprof)
        
    def getDuration(self):
        return max(self.t)

class Vibrato(object):
    '''Generate a sound from vibrato profile'''
    def __init__(self, harm0=[1.], vmin=0.0, vmax=1.0, type='amplitude', sr=44100, f0=500.):
        self.sr=sr
        self.f0=f0
        self.h0 = np.array(harm0)
        self.nharm = len(harm0)
        if type == 'amplitude':
            self.hs = lambda x: np.outer(np.ones(self.nharm)/float(self.nharm),x)
        if type == 'slope':
            self.hs = SlopeHarmonicScaler(self.nharm)
        
        self.setProfile()
        self.setEnvelope()
        


    def setProfile(self, t_prof=[0.0,1.0], v_prof=[1.0,1.0]):
        self.prof = VibratoProfile(t_prof,v_prof)
        
    def setEnvelope(self,t_att=0.0, t_rel=0.0):
        self.at_sam = int(round(t_att*self.sr));
        self.rel_sam = int(round(t_rel*self.sr));
        
        
    def calculate_wav(self,vmin,vmax):
        # Build signal
        t = np.arange(0,self.prof.getDuration(),1/float(self.sr));
        sig = np.zeros_like(t);
        
        vibsig = self.prof(t)*(vmax-vmin)/2. + (vmax+vmin)/2.
        
        hamp = self.hs(vibsig)
        for i in range(1,self.nharm+1):
            # vector of frequency per sample
            #fharm = i*self.f0 * (1 + f0vib*vibsig);
            fharm = i*self.f0 *np.ones_like(vibsig)
            # phase vector
            fcumsum = np.cumsum(2*np.pi*fharm)/self.sr;
            phi = np.concatenate(([0],fcumsum[0:-1]));

            # amplitude vector
            aharm = hamp[i-1];
            hsig = self.h0[i-1] * aharm * np.sin(phi);

            sig = sig+hsig;

        ## Build overal envelope
        env_a = np.ones_like(vibsig);
        
        if self.at_sam>0:
            env_a[0:self.at_sam]    = np.linspace(0,1,self.at_sam);
        if self.rel_sam>0:
            env_a[-self.rel_sam:] = np.linspace(1,0,self.rel_sam);

        sig=sig*env_a;

        # scale signal to audio range
        #sig = .9 * sig / max(abs(sig));

        #display(Audio(data=sig, rate=sr))
        return sig
        
         