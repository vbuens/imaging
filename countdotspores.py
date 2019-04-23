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

#Get the image file as an argument
image_title=sys.argv[1] 
im = io.imread('%s'%image_title, as_grey=True)
# Get the number of spores
labels = measure.label(im)
print(labels.max())
plt.imshow(im, cmap='gray')
#Use the name of the image as title for the output
title=image_title.split('.')[0]
plt.title('Number of spores: %s' %labels.max())
plt.savefig('results/%s_%s.png'%(title,labels.max()))
plt.show()

