import os
import sys
import argparse
import utils
import cv2
import glob
import webcolors
import numpy as np
import matplotlib.pyplot as plt
from infection_functions import get_image,color_name,print_image, get_threshold_values, closest_colour

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k','--k', type=int, nargs='?', help='output directory for results (default=5)',default=5)
parser.add_argument('-o','--outputdir', type=str, help='output directory for results (default=results)',default="results")
parser.add_argument('-i','--inputdir', required= True, type=str, help='directory where the images to analyse are found')
parser.add_argument('-f','--format', type=str, help='format of the pictures (default=.tif)', default=".tif")
parser.add_argument('-p','--positivecontrol', required= True, type=str, help='Image file of an infected leaf')
parser.add_argument('-n','--negativecontrol', required= True, type=str, help='Image file of a healthy leaf')
args = parser.parse_args()
output_dir = args.outputdir
output_file = str(output_dir)+"/infection_percentages.csv"
input_dir = args.inputdir
format = args.format
healthy = args.negativecontrol
infected = args.positivecontrol
K = args.k

for file in [healthy,infected]:
    try:
        open(file, 'r')
    except FileNotFoundError:
        parser.error("File %s not found" % file)
if os.path.exists(input_dir) == False:
    parser.error("Directory %s not found" % input_dir)
if os.path.exists(output_dir) == False:
    os.mkdir(output_dir)

#sys.stdout = open('stdout.txt', 'w')
print('''
Output directory : %s
Input directory : %s
Images format : %s
Positive control (infected) image : %s
Negative control (healthy) image : %s
Number of clusters to find infection (k) : %i
Final output: %s
''' % (output_dir,input_dir,format,healthy,infected,K,output_file))

healthy_values,inf_values = get_threshold_values(healthy,infected,7,output_dir)
print("Healhy values: %s \nInfected values: %s" % (str(healthy_values),str(inf_values)))

#healthy_values=[75.95638, 85.271736, 46.02764]
#inf_values=[178.80173, 160.89029, 100.88039]

output = open(output_file, "a")

output.write("Image,K,%Infection")

for imagefile in glob.glob(str(input_dir)+"/*"+str(format)):
    image = get_image(imagefile)
    print("- File : %s " % imagefile)
    Z = image.reshape((-1,3))
    # convert to np.float32
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = K    #number of colours
    ret,labels,center_colours=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    # Now convert back into uint8, and make original image
    print_image(imagefile,image,center_colours,labels,K,output_dir)

    counts={}
    perc={}
    for i in range(0,K):
        counts[i]=list(labels.flatten()).count(i)
        perc[i]=round((list(labels.flatten()).count(i)/len(labels))*100,2)
    colorlabels=color_name(center_colours)

    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colours[i]/255 for i in counts.keys()]
    #plt.pie(counts.values(),labels=colorlabels,colors=ordered_colors)
    #plt.savefig('%s/%s_%i_pie_black.jpg' % (output_dir,imagefile.split('.')[0].split('/')[1],K))
    plt.clf()

    blackindex=colorlabels.index('black')
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

    plt.pie(counts.values(),labels=colorlabels,colors=ordered_colors)
    plt.title(os.path.splitext(os.path.basename(imagefile))[0])
    plt.savefig('%s/%s_%i_pie.jpg' % (output_dir,imagefile.split('.')[0].split('/')[1],K))
    plt.clf()

    ### GET COLOURS
    colors={}
    for i in range(0,len(center_colours)):
        rc=center_colours[i][0] ; gc=center_colours[i][1] ; bc=center_colours[i][2]
        rd=(healthy_values[0]-rc)**2
        gd=(healthy_values[1]-gc)**2
        bd=(healthy_values[2]-bc)**2
        healthy_rgb=rd + gd + bd
        rd_inf=(inf_values[0]-rc)**2
        gd_inf=(inf_values[1]-gc)**2
        bd_inf=(inf_values[2]-bc)**2
        inf_rgb=rd_inf + gd_inf + bd_inf
        colors[color_name(center_colours)[i]]=[healthy_rgb,inf_rgb]

    color_name(center_colours)
    ## WITH 5 CLUSTERS : 16.47 OF INFECTION
    percinf=0
    totalpercs=sum(newpercs)
    count=0
    if 'black' in colors:
        colors.pop('black')

    for color in colors.keys():
        if colors[color].index(min(colors[color])) == 0 :
            print("Healthy: %s" % color)
        else:
            print("Infected: %s" % color)
            percinf+=newpercs[count]
        count+=1

    print(percinf)
    output.write("\n%s,%i,%f" % (str(os.path.splitext(os.path.basename(imagefile))[0]),K,percinf))

output.close()
