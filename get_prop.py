'''
image-18308534-1606302696329.pgm
tag = 19mm
brightness = 5.46875 percent
gain = 9.8272 dB
sharpness = 1024
gamma = 9.8272
shutter = 10.0009 ms
'''
def get_prop(fn):
	import re
	prop = {}
	with open(fn, 'r') as f:
		lines = [x.strip().strip() for x in f.readlines()]
	fn_basename = lines[0]
	prop['fn'] = fn_basename
	#print(fn_basename)

	patterns = {}
	patterns['timestamp'] = re.compile('.*-(\d+)\.pgm$')
	patterns['camid'] = re.compile('.*-(\d+)-\d+\.pgm$')
	patterns['tag'] = re.compile('tag = (.*)$')
	patterns['brightness'] = re.compile('brightness = ((.|-|\d)+) percent$')
	patterns['gain'] = re.compile('gain = ((.|-|\d)+) dB$')
	patterns['sharpness'] = re.compile('sharpness = (\d+)$')
	patterns['gamma'] = re.compile('gain = ((.|-|\d)+)$')
	patterns['shutter'] = re.compile('shutter = ((.|-|\d)+) ms$')
	patterns['temperature'] = re.compile('temperature = ((.|-|\d)+)K.*$')
	for line in lines:
		for key in patterns:
			matches = patterns[key].match(line)
			if matches is not None:
				prop[key] = matches.group(1)
		
	
	return prop

if __name__ == "__main__":
	prop = get_prop('image-18308534-1606302696329_prop.txt')
	print(prop)
	