import os
import sys

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import cv2
from get_prop import get_prop

import gc

img_dir = 'images/'
prop_fns = sorted([x for x in os.listdir(img_dir) if x.endswith('_prop.txt')])


for prop_fn in prop_fns:
	prop = get_prop(img_dir + prop_fn)
	# print(prop)
	fn = prop['fn']
	img_fn = img_dir + fn
	output_fig_fn = img_dir + 'heatmap_' + os.path.splitext(fn)[0] + '.png'

	img = cv2.imread(img_fn, cv2.IMREAD_GRAYSCALE)
	norm = mpl.colors.Normalize(vmin=20, vmax=40)

	fig = plt.figure(figsize=(16,12))
	ax = fig.add_subplot(111)

	ax.imshow(img, norm=norm, cmap='rainbow', interpolation='nearest')
	# ax.imshow(img, cmap='rainbow', interpolation='nearest')
	fig.colorbar(mappable=mpl.cm.ScalarMappable(norm=norm, cmap='rainbow'), ax=ax)

	tmp_title = '%s, tag:%s, temp:%sK' % (fn, prop['tag'], prop['temperature'])

	ax.set_title(tmp_title)
	plt.tight_layout()
	fig.savefig(output_fig_fn, dpi=80)
	print('saving to', output_fig_fn)
	fig.clf()
	plt.close()

	gc.collect()
	# plt.show()