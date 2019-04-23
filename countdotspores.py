#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 11:54:44 2018

@author: buenov
"""

import os
import sys
from skimage import io
from scipy import ndimage
import matplotlib.pyplot as plt
from skimage import measure

os.chdir('/Users/buenov/Documents/PhD/Spores/counts')


image_title=sys.argv[1] 
im = io.imread('%s'%image_title, as_grey=True)
labels = measure.label(im)
print(labels.max())
plt.imshow(im, cmap='gray')
title=image_title.split('.')[0]
plt.title('Number of spores: %s' %labels.max())
plt.savefig('results/%s_%s.png'%(title,labels.max()))
plt.show()

