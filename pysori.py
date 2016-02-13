import math
import wave
import pyaudio
import time
import struct
import random

globalIsPlaying = False

class Sound:
	channels = 1
	sampwidth = 1
	framerate = 44100
	data = ''
	
	def __init__(self, data, channels=1, sampwidth=1, framerate=44100):
		self.data = data
		self.channels = channels
		self.sampwidth = sampwidth
		self.framerate = framerate

	def __repr__(self):
		return "Sound Class "+str(self.framerate) + "Hz "+str(len(self.data))+"bytes channels"+str(self.channels)+" sampwidth"+str(self.sampwidth)

	def play(self):
		global globalIsPlaying
		if globalIsPlaying==False:
			format = pyaudio.PyAudio().get_format_from_width(self.sampwidth,True)
			stream = pyaudio.PyAudio().open(self.framerate,
									  self.channels,
									  format, False, True)
			stream.write(self.data)
			stream.stop_stream()
			stream.close()
		else:
			print "Sound is already playing."

	def playContinue(self):
		global globalSoundData, globalFrameCount, globalBytePerChannel, globalIsPlaying
		if globalIsPlaying==False:
			globalIsPlaying = True
			format = pyaudio.PyAudio().get_format_from_width(self.sampwidth,True)
			globalSoundData = str(self.data)
			globalFrameCount = 0
			globalBytePerChannel = self.channels*self.sampwidth
			self.stream = pyaudio.PyAudio().open(self.framerate,
									  self.channels,
									  format, False, True,
									  stream_callback = callback)
			self.stream.start_stream()
		else:
			print "Sound is already playing."

	def stop(self):
		global globalIsPlaying
		self.stream.stop_stream()
		self.stream.close()
		globalIsPlaying = False

	def save(self,filename):
		w = wave.open(filename,"w")
		w.setnchannels(self.channels)
		w.setsampwidth(self.sampwidth)
		w.setframerate(self.framerate)
		w.writeframes(self.data)
		w.close()
		print filename+" has been successfully saved."

	def processAll(self,func):
		newData = ''
		tempData = ''
		for i in xrange(len(self.data)):
			tempData += func(self.data[i])
			if i % (44100*self.channels*self.sampwidth) ==0 :
				newData += tempData
				tempData = ''
				print i,'/',len(self.data), i*100/len(self.data),'%'
		self.data = newData+tempData
		print "Process Completed"

class Instrum:
	name = 'Untitled'
	harmony = [1]

	def __init__(self, waveform):
		self.waveform = waveform
		self.env = Envelope()

	def __repr__(self):
		return 'Instrum '+self.name+':	'+self.waveform.__name__+'\n'+str(self.harmony)

	def tone(self,freq,sec):
		newData = ''
		modifSec = 0
		for i in xrange( int(44100*(sec+self.env.outro)) ):
			nowsec = float(i)/44100
			modifSec += self.env.shift(nowsec)/44100
			disp = 0
			for n in range(len(self.harmony)):
				disp += self.waveform(freq*(n+1),modifSec) * self.harmony[n]
			disp *= self.env.multiplier(nowsec,sec)
			newData += tobit( disp * 0.5)
		s = Sound( newData )
		return s

	def play(self):
		s1 = self.tone(262,0.7)
		s2 = self.tone(330,0.7)
		s3 = self.tone(392,0.7)
		s1.data += s2.data + s3.data
		s1.play()
		s1.save("tone.wav")

	def newHarmony(self):
		harmony = [1]
		while random.random()<0.8 and  len(harmony)<4:
			harmony.append( math.floor(random.random()*200-100)/100 )
		self.harmony = harmony
		print str(self.harmony)
		self.play()

class Envelope:
	def __init__(self):
		self.intro = 0.005
		self.relax = 0.5
		self.high = 0.1
		self.outro = 0.5
		self.pan = 0.1
		self.period = 0.1
		self.shift = constant

	def multiplier(self, nowsec, allsec):
		if nowsec<self.intro:
			return (nowsec / self.intro) * self.vibrate(nowsec)
		elif nowsec > allsec:
			return (self.high / self.outro * (allsec + self.outro - nowsec)) * self.vibrate(nowsec)
		elif nowsec<self.intro + self.relax:
			return (1 + (self.high-1)*(nowsec-self.intro)/self.relax )* self.vibrate(nowsec)
		else:
			return self.high* self.vibrate(nowsec)

	def vibrate(self,sec):
		return 1 + math.sin( sec / self.period * 6.2832 ) * self.pan









def readwav(filename):
	w = wave.open(filename,"r")
	params = w.getparams();
	data = w.readframes(params[3])
	w.close()

	res = Sound(data, params[0], params[1], params[2])
	print filename
	print "(nchannels, sampwidth, framerate, nframes, comptype, compname)"
	print params
	print str(len(data)) + ' bytes Sound Object returned.'
	return res

def callback(a,b,c,d):
	global globalSoundData, globalFrameCount, globalBytePerChannel, globalIsPlaying
	globalFrameCount += b*globalBytePerChannel
	if len(globalSoundData)<=globalFrameCount:
		globalIsPlaying = False
		print "Sound stopped.",len(globalSoundData) , globalFrameCount
		return (globalSoundData[globalFrameCount-b*globalBytePerChannel : ], pyaudio.paContinue)
	else:
		return (globalSoundData[globalFrameCount-b*globalBytePerChannel : globalFrameCount], pyaudio.paContinue)

def toint(bytes):
	return struct.unpack('B',bytes)[0]

def tofloat(bytes):
	return (float(struct.unpack('B',bytes)[0])-128)/128

def tobit(num):
	if num>=1:
		return chr(255)
	elif num<=-1:
		return chr(0)
	else:
		return chr(int( (num+1)*128 ))




# =================== Wave Form ======================

def sinwave(freq, nowsec, framerate=44100):
	return math.sin( nowsec * freq * 6.2832 )

def sawwave(freq, nowsec, framerate=44100):
	phase = (nowsec*freq)%1.0
	if phase < 0.25:
		return phase 
	elif phase < 0.75:
		return 1.0 - phase
	else:
		return -2.0 + phase

def sin3wave(freq, nowsec):
	return math.pow(math.sin( nowsec * freq * 6.2832 ),3)


def dubwave(freq, nowsec):
	phase = (nowsec*freq/4)%1.0
	if phase < 0.2 :
		return math.sin( phase*5*6.2832 )
	else:
		return 0

def dub3wave(freq, nowsec):
	phase = (nowsec*freq/4)%1.0
	if phase < 0.2 :
		return math.pow(math.sin( phase*5*6.2832 ),3)
	else:
		return 0

def tansin(freq, nowsec):
	return math.tan( math.sin( nowsec * freq * 3.14159 ) )

def logsin(freq, nowsec):
	return math.log10( 5.05 + 4.95 * math.sin(nowsec*freq*3.14159/2) )

def wsin(freq, nowsec):
	x = math.sin(nowsec*freq*3.14159)
	return x*(x-1)*(x+0.5)

def mixwave(freq, nowsec):
	phase = (nowsec*freq)%1.0
	if nowsec%0.06<0.03:
		return math.tan( math.sin( phase * 3.14159/4 ) )		
	else:
		return math.tan( math.sin( phase * 3.14159 ) )

# ================== Shift ======================

def constant(nowsec):
	return 1.0

def ascend(nowsec):
	if nowsec<0.1:
		return 0.9 + nowsec
	else:
		return 1.0