import numpy as np


def GenVibratoProfile(f=5.0,t=[0.0,2.0],a=[.1,.1]):
    '''Generates an oscillant profile with frequency "f",
    and amplitude envelope given by "a" at times "t"
    '''

    ti=np.array(t)
    ai=np.array(a)

    t_max = max(ti)
    tout = np.arange(0,t_max,1./f/16.0)
    aout = np.interp(tout,ti,ai)

    i_st = min(np.argmin(ai>0.0),1)-1
    t_st = t[i_st]

    vibprof = aout*np.sin(2*np.pi*f*(tout-t_st))

    return tout,vibprof

def HarmonicVibrato(f0=220.0,
                    ampseq=lambda x: 1/x,
                    hvib=[0,.1,.1], f0vib=.05,
                    sr=44100,
                    t_att=0.05, t_rel=0.02,
                    dur=1.0,
                    vib_prof_t=[0.0,1.0], vib_prof_a = [1.0,1.0],
                    vibfreq = 5.0,a0=.5):

    '''Generates a complex sound with frequency modulation and
    synchronous modulation of harmonic amplitudes.
    Signal parameters:
    * sr: sample rate
    Carrrier parameters:
    * f0: Fundamental frequency
    * ampseq: vector with harmonic amplitudes, or function.
      If vector, number of harmonics is finite (len(ampseq))
      If a function, there are as many harmonics as possible
                     in the nyquist range
    * a0: Overal scaling of amplitude
    Vibrato profile parameters:
    * vibfreq: frequecy of the vibrato oscillation (constant)
    * vib_prof_t, vib_prof_a: Envelope of the vibrato depth
    Frequency vibrato:
    * f0vib: overall scaling of frequency vibrato (as fraction of f0)
    Timbre vibrato:
    * hvib: harmonic vibrato depth in dB
    Global enveloppe:
    * t_att: "fade in" duration
    * t_rel: "fade-out"
    '''


    nharm = int(sr/f0)

    if hasattr(ampseq, '__call__'):
        amp=[0]
        amp.extend([ampseq(float(i)) for i in range(1,nharm)])
    else:
        amp = np.zeros(max(len(ampseq),len(hvib))+1)
        amp[1:len(ampseq)+1] = ampseq
        nharm = min(nharm,len(amp))


    # Build signal
    t = np.arange(0,max(vib_prof_t),1/float(sr));
    sig = np.zeros_like(t);

    # vibrato signal
    tvib,vsig = GenVibratoProfile(t=vib_prof_t,a=vib_prof_a,f=vibfreq);
    vibsig = np.interp(t,tvib,vsig)

    # remove linear offset
    vibsig = vibsig - np.linspace(vibsig[1],vibsig[-1],len(vibsig));


    # attack / release size in samples
    at_sam = int(round(t_att*sr));
    rel_sam = int(round(t_rel*sr));
    vibrat = np.zeros(nharm)
    vibrat[1:len(hvib)+1] = hvib
    for i in range(1,nharm):
        # vector of frequency per sample
        fharm = i*f0 * (1 + f0vib*vibsig);
        # phase vector
        fcumsum = np.cumsum(2*np.pi*fharm)/sr;
        phi = np.concatenate(([0],fcumsum[0:-1]));

        # amplitude vector
        aharm = amp[i] * 10**(vibrat[i]*vibsig/20);
        hsig = a0 * aharm * np.sin(phi);

        sig = sig+hsig;

    ## Build overal envelope
    env_a = np.ones_like(vibsig);

    env_a[0:at_sam]    = np.linspace(0,1,at_sam);
    env_a[-rel_sam:] = np.linspace(1,0,rel_sam);

    sig=sig*env_a;

    # scale signal to audio range
    #sig = .9 * sig / max(abs(sig));

    #display(Audio(data=sig, rate=sr))
    return sig

def VibratoWAV(filename='out.wav',
        slope=0,
        nharm = 7,
        f0tonic=500.0,
        amp=0.1,
        hdepth = 6.0,
        phrel=1.0,
        hvib1 = 4,
        hvib2 = 5,
        sr=44100):
    '''Generate a sequence of similar notes based on parameters given as a
    dictionary in parseq.
    interval controls the silence between 2 samples
    '''
    #sr=44100

    #hamp = np.array([(1.)**xx/xx**slope for xx in xrange(0,nharm-1)])
    base = np.exp(slope)
    hamp = [(hn-(nharm+1.0)/2.0) for hn in xrange(nharm-1)]
    #hamp = np.zeros(nharm)
    #f0tonic = 500.
    #amp=0.05
    #amp=0.1


    nhvib = [hvib1,hvib2*np.sign(phrel)]
    hvib = np.zeros(len(hamp))
    for nn in nhvib:
        hvib[abs(nn)] = np.sign(nn) * hdepth

    sig = HarmonicVibrato(ampseq=hamp,hvib=hvib,f0vib=0.00,f0=f0tonic,
                        vib_prof_t=[0.0,0.3,0.7,1.5,1.6],vib_prof_a=[0.0,0.0,0.5,1.0,0.0],vibfreq=6.0,
                        a0=amp,sr=sr,t_att=.05)

    write_wav(filename,sig,sr=sr)
    #wavwrite(filename,rate=sr,data=np.tile(sig,[1,2]))

    #return sig, sr
    #display(Audio(data=sig,rate=sr,autoplay=True))

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


def write_wav(filename , x, sr=44100, sampwidth=2):
    import wave
    import struct


    wav_file = wave.open(filename, "w")

    nchannels = 2
    amp = 2**(8*sampwidth)

    framerate = int(sr)
    nframes = len(x)

    comptype = "NONE"
    compname = "not compressed"

    wav_file.setparams((nchannels, sampwidth, framerate, nframes,
        comptype, compname))

    # numpy convert float to int
    xstereo = np.reshape(np.tile(x,[2,1]).T*amp/2,2*len(x)).astype('int16').tostring()

    wav_file.writeframes(xstereo)

    wav_file.close()
