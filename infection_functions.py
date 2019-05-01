from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import utils
import cv2
import numpy as np
import webcolors

# Functions:
def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]
def color_name(center_colours):
    colornames=[]
    for i in range(0,len(center_colours)):
        colornames.append(closest_colour((center_colours[i][0],center_colours[i][1],center_colours[i][2])))
    return colornames

def print_image(imagefile,image,center_colours,labels,k,output_dir):
    center_colours = np.uint8(center_colours)
    res = center_colours[labels.flatten()]
    res2 = res.reshape((image.shape))
    plt.imshow(res2)
    plt.title(imagefile.split('.')[0])
    plt.savefig('%s/standard_%s_%i_kmeans.jpg' % (output_dir,imagefile.split('.')[0],k))
    plt.clf()

## Getting the healthy and infected thresholds

def get_threshold_values(healthy,infected,k,output_dir):
    imagefiles = [healthy, infected] #,"mid.jpg"]
    plt.rcParams['figure.figsize'] = [14, 7]

    for imagefile in imagefiles:
        image = get_image(imagefile)
        Z = image.reshape((-1,3))
        # convert to np.float32
        Z = np.float32(Z)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = k #number of colours
        ret,labels,center_colours=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

        print_image(imagefile,image,center_colours,labels,K,output_dir)

        counts={}
        perc={}
        for i in range(0,K):
            counts[i]=list(labels.flatten()).count(i)
            perc[i]=round((list(labels.flatten()).count(i)/len(labels))*100,2)
        colorlabels=color_name(center_colours)
        # We get ordered colors by iterating through the keys
        ordered_colors = [center_colours[i]/255 for i in counts.keys()]

        # Get rid of the background and get the values for colour green (healthy) and khaki (infected)
        blackindex=colorlabels.index('black')
        green = [i for i, s in enumerate(colorlabels) if 'green' in s]
        khaki = [i for i, s in enumerate(colorlabels) if 'khaki' in s]

        if blackindex in counts:
            counts.pop(blackindex)
        if blackindex in perc:
            perc.pop(blackindex)
            ordered_colors.pop(blackindex)

        colorlabels.pop(blackindex)
        colornames=[]
        for colour in center_colours:
            colornames.append(closest_colour((colour[0],colour[1],colour[2])))
        colornames.pop(blackindex)
        list(center_colours).pop(blackindex)

        newpercs=[round((i/sum(perc.values()))*100,2) for i in perc.values()]



        if imagefile == imagefiles[0]:
            healthy_values=[center_colours[green[0]][0],center_colours[green[0]][1],center_colours[green[0]][2]]
            healthy_pie = [counts.values(),colorlabels,ordered_colors]
            #print("Healthy values: %s" %healthy_values)

        if imagefile == imagefiles[1]:
            inf_values=[center_colours[khaki[0]][0],center_colours[khaki[0]][1],center_colours[khaki[0]][2]]
            inf_pie = [counts.values(),colorlabels,ordered_colors]
            #print("Inf values: %s" % inf_values)

    plt.subplot(121)
    plt.pie(healthy_pie[0],labels=healthy_pie[1],colors=healthy_pie[2])
    plt.title(healthy.split(".")[0])
    plt.subplot(122)
    plt.pie(inf_pie[0],labels=inf_pie[1],colors=inf_pie[2])
    plt.title(infected.split(".")[0])
    plt.savefig('%s/standards_%i_pie.jpg' % (output_dir,K))
    plt.clf()
    return healthy_values, inf_values
