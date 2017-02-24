import numpy as np
import sys
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

def dBAampl(hamp,f0):
    '''Calculate the dBA level of a harmonic sequence'''
    ampsq = 0.0
    fseq = f0*(np.arange(len(hamp))+1)
    fs2 = fseq**2
    a2 = 12200.**2
    b2 = 20.6**2
    c2 = 107.7**2
    d2 = 737.9**2
    
    corr = 1.259*(a2 * fseq**4) / ((fs2 + b2 ) * np.sqrt((fs2+c2)*(fs2+d2)) * (fs2+a2))
    hacorr = hamp*corr
    hasq = np.array(hacorr)**2
    
    return np.sqrt(sum(hasq))

def SlopeToHmult(slope, nharm, mode='RMS', f0=1000., calfile=None):
    '''Calculate a harmonic sequence for a constant dB slope'''
    
    base = np.exp(slope)
    hamp = []
    for i in xrange(nharm):
        hn = i
        hamp.append(base**(hn-(nharm-1)/2.0))
        #hamp.append(np.sqrt(((hn/float(nharm-1)-.5 )*2.*(-slope)+1.)/nharm)) 
    ha = np.array(hamp)
    if mode=='RMS':     
        return ha /np.sqrt(sum(ha*ha))
    if mode=='dBA':     
        return ha /dBAampl(ha,f0)
   

class SlopeHarmonicScaler(object):
    '''Object for quick calculation of a harmonic for 
    a desired spectral centroid
    * for val=0, centroid is on 1st harmonic
    * for val=1, centroid is on last harmonic
    * Centroid variation is produced by a change in spectral slope
    * Spectrum is a linear slope in dB'''
    def __init__(self, nharm=2, npoints=100, slopelim=4, f0=1000., 
                 mode='RMS', harmfile=None):
        self.nharm = nharm
        
        slopes = np.linspace(-slopelim,slopelim,npoints)
        cent = np.zeros(len(slopes)+2)
        hamps = np.zeros((len(slopes)+2,nharm))
        
        
        
        for (ii,slope) in enumerate(slopes):
            hamp = SlopeToHmult(slope,nharm,f0=f0,mode=mode)
            cent[ii+1]=(Centroid(hamp))
            hamps[ii+1,...] = hamp
        
        hamps[0,0]=1.
        hamps[-1,-1]=1.
        
        if mode=='dBA':
            hamps[0,:] = hamps[0,:]/dBAampl(hamps[0,:],f0)
            hamps[-1,:] = hamps[-1,:]/dBAampl(hamps[-1,:],f0)
                
        cent[0] = 1.
        cent[-1] = nharm
        
        self.cent = cent
        self.hamp = hamps
        if harmfile:
            self.loadNumpy(harmfile)
            

        self.generateInterpolators()
        

        
        self.vmin = np.min(cent)
        self.vmax = np.max(cent)
        
    def __call__(self, val):
        '''
        Return harmonic amplitudes for a given spectral centroid
        '''
        hh = []
        cent = val*(self.nharm-1.)+1.
        for ii in xrange(self.nharm):
            hh.append(self.fharm[ii](cent))
        return np.array(hh)
    
    def saveNumpy(self,filename):
        '''
        Save a table of harmonic amplitudes to file
        '''
        np.savez(filename, cent=self.cent,hamp=self.hamp)
        
    def loadNumpy(self,filename):
        '''
        Load a table of harmonic amplitudes from file
        '''
        dd = np.load(filename)
        self.cent = dd['cent']
        self.hamp = dd['hamp']
        self.nharm = self.hamp.shape[1]
        self.generateInterpolators()
        
    def generateInterpolators(self):
        '''
        Generates the interpolator function from a table 
        of harmonic amplitudes
        '''
        self.fharm=[]
        
        for ii in xrange(self.nharm):
            l = self.hamp[0,ii]
            r = self.hamp[-1,ii]
            ff = interp1d(self.cent, self.hamp[...,ii], 
                          kind='cubic', 
                          bounds_error=False,fill_value=(l,r))
            self.fharm.append(ff)
        
        
    def outputJSArray(self, npoints=100, vlims=[0.,1.]):
        '''
        Outputs an interpolated array of harmonic amplitudes
        for each value of spectral centroid (0-1)
        '''

        sys.stdout.write("scvals = [ \n")

        for ii in xrange(npoints+1):
            vrange = max(vlims) - min(vlims)
            cent = min(vlims) + ii * vrange / float(npoints)
            hamp = self(cent)
            sys.stdout.write('[')
            for hh in hamp:
                sys.stdout.write('%f,'%hh)
                
            sys.stdout.write('], // %f\n'% cent)
            
        sys.stdout.write('];\n')
        

class VibratoProfile(object):
    '''A vibrato time-profile'''
    def __init__(self, t_vals=[0.0,1.0], a_vals=[1.0,1.0], vibfreq=5.0):
        self.ti=np.array(t_vals)
        self.ai=np.array(a_vals)
        self.vibfreq = vibfreq
        
        # max of vibrato profile is 1
        amax = np.max(self.ai)
        if amax>0.:
            self.ai = self.ai/amax
        self.recalc_profile()
        
        
    def recalc_profile(self):

        t_max = max(self.ti)
        tout = np.arange(0,t_max,1./self.vibfreq/16.0)
        aout = np.interp(tout,self.ti,self.ai)
        self.t = tout
        
        amax = np.max(self.ai)
        if amax>0.:
            i_st = min(np.argmin(self.ai>0.0),1)-1
            t_st = self.ti[i_st]

            self.vibprof = aout*np.sin(2*np.pi*self.vibfreq*(tout-t_st))
        else:
            self.vibprof = np.zeros_like(tout)
        
    
    def __call__(self,t):
        return np.interp(t,self.t,self.vibprof)
        
    def getDuration(self):
        return max(self.t)
        
    def setVibratoFreq(self, vibfreq):
        self.vibfreq=vibfreq
        self.recalc_profile()

class Vibrato(object):
    '''Generate a sound from vibrato profile'''
    def __init__(self, harm0=[1.],  sr=44100, f0=500., 
                 vibfreq=5.0,norm_mode='RMS',
                 harmfile = None):
        self.sr=sr
        self.f0=f0
        self.h0 = np.array(harm0)
        if harmfile:
            self.hs = SlopeHarmonicScaler(harmfile=harmfile, f0=self.f0)
            self.nharm = self.hs.nharm
        else:
            
            self.nharm = len(harm0)
            self.hs = SlopeHarmonicScaler(self.nharm, f0=self.f0, mode=norm_mode)
        self.vibfreq=vibfreq
        
        self.setProfile()
        self.setEnvelope()
        


    def setProfile(self, t_prof=[0.0,1.0], v_prof=[1.0,1.0]):
        self.prof = VibratoProfile(t_prof,v_prof,vibfreq=self.vibfreq)

    def setVibratoFreq(self, vibfreq=5.0):
        self.prof.setVibFreq(vibfreq)
        
    def setEnvelope(self,t_att=0.0, t_rel=0.0):
        self.at_sam = int(round(t_att*self.sr));
        self.rel_sam = int(round(t_rel*self.sr));
        
        
    def calculateWav(self,brightness=[0.5,0.5], amplitude=0.0, frequency = 0.0):
        # Build signal
        bmin = min(brightness)
        bmax = max(brightness)
        
        t = np.arange(0,self.prof.getDuration(),1/float(self.sr));
        sig = np.zeros_like(t);
        
        
        vibsig = self.prof(t)
        bsig = vibsig * (bmax-bmin)/2. + (bmax+bmin)/2.
        
        hamp = self.hs(bsig)
        for i in range(1,self.nharm+1):
            # vector of frequency per sample
            fharm = i*self.f0 * (1 + frequency*vibsig);
            #fharm = i*self.f0 *np.ones_like(vibsig)
            # phase vector
            fcumsum = np.cumsum(2*np.pi*fharm)/self.sr;
            phi = np.concatenate(([0],fcumsum[0:-1]));

            # amplitude vector
            aharm = hamp[i-1];
            a0 = self.h0[i-1] * (1. + amplitude * vibsig) 
            
            hsig = a0 * aharm * np.sin(phi);

            sig = sig+hsig;

        ## Build overal envelope
        env_a = np.ones_like(vibsig);
        
        if self.at_sam>0:
            env_a[0:self.at_sam]    = np.linspace(0,1,self.at_sam);
        if self.rel_sam>0:
            env_a[-self.rel_sam:] = np.linspace(1,0,self.rel_sam);

        sig=sig*env_a;

        self.sig = sig
        return sig
        
    def saveWav(self,filename,sampwidth = 2):
        import wave
        import struct
        
        wav_file = wave.open(filename, "w")

        nchannels = 2
        amp = 2**(8*sampwidth)

        framerate = int(self.sr)
        nframes = len(self.sig)

        comptype = "NONE"
        compname = "not compressed"

        wav_file.setparams((nchannels, sampwidth, framerate, nframes,
            comptype, compname))

        # numpy convert float to int
        xstereo = np.reshape(np.tile(self.sig,[2,1]).T*amp/2,2*len(self.sig)).astype('int16').tostring()

        wav_file.writeframes(xstereo)

        wav_file.close()
        
        
def SlopeVibratoWAV(filename='out.wav',
        slope=0,
        nharm = 7,
        f0tonic=500.0,
        amp=0.1,
        hdepth = 6.0,
        vib_slope=1.0,
        sr=44100):
    '''Generate a sequence of similar vibrato notes:fluctuating in amplitude or slope
    '''
    #sr=44100
    base = np.exp(slope)
    
    print vib_slope
    fact = 20./np.log(10)
    if vib_slope>0.0:
        hvib = [(float(hn)-(nharm-2.0)/2.0)*hdepth for hn in xrange(nharm-1)]
    else:
        hvib = [hdepth for hn in xrange(nharm-1)]
    print hvib
    #hvib = [fact*np.log10((hn-(nharm+1.0)/2.0)*slope) for hn in xrange(nharm-1)]
    
    hamp = np.array([(1.)**xx/xx**slope for xx in xrange(1,nharm)])
    #hamp = np.concatenate(([0],hamp))
    #hamp = np.zeros(nharm)
    #f0tonic = 500.
    #amp=0.05
    #amp=0.1
    #hamp = amp*np.ones(nharm)
    #hamp[0]=0.0


    #hvib = np.zeros(len(hamp))
    # if vib_slope > 0.0:
    #     for nn in range(nharm-1):
    #         hvib[nn] = hdepth * (nharm/2. - float(nn))
    # else:
    #for nn in range(nharm-1):
    #    hvib[nn] = hdepth
    
    
    
    sig = HarmonicVibrato(ampseq=hamp,hvib=hvib,f0vib=0.00,f0=f0tonic,
                        vib_prof_t=[0.0,0.3,0.7,1.5,1.6],vib_prof_a=[0.0,0.0,0.5,1.0,0.0],vibfreq=6.0,
                        a0=amp,sr=sr,t_att=.05)
    
    write_wav(filename,sig,sr=sr)
    #wavwrite(filename,rate=sr,data=np.tile(sig,[1,2]))

    #return sig, sr
    #display(Audio(data=sig,rate=sr,autoplay=True))


