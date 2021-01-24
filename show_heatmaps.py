import os
import sys

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import cv2

img_dir = 'images/'
fns = sorted([x for x in os.listdir(img_dir) if x.endswith('.pgm')])


for fn in fns:
	img_fn = img_dir + fn
	output_fig_fn = img_dir + 'heatmap_' + os.path.splitext(fn)[0] + '.png'

	img = cv2.imread(img_fn, cv2.IMREAD_GRAYSCALE)
	norm = mpl.colors.Normalize(vmin=20, vmax=40)

	fig = plt.figure(figsize=(16,12))
	ax = fig.add_subplot(111)

	ax.imshow(img, norm=norm, cmap='rainbow', interpolation='nearest')
	#ax.imshow(img, cmap='rainbow', interpolation='nearest')
	fig.colorbar(mappable=mpl.cm.ScalarMappable(norm=norm, cmap='rainbow'), ax=ax)
	ax.set_title(fn)
	plt.tight_layout()
	fig.savefig(output_fig_fn, dpi=80)
	print('saving to ', output_fig_fn)
	#plt.show()