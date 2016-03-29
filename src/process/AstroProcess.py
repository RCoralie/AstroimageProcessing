#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import numpy as np
from math import sqrt

# INFO : 
# http://astro.dialou.fr/techniques/astrophotographie/capture-des-images-de-calibration/
# http://www.astrosurf.com/d_bergeron/astronomie/Bibliotheque/Traitement%20image/Pretraitement%20des%20images/traitement%20image.htm#Images%20DARK


# GENERAL METHODE ------------------------------------------------------------------------------------------------------------#



# MEDIAN : the median combination allow to eliminates pixels deviants. It is the one that we shall usually use to combine Flat field (remove completely any tracks of artéfacts)
# so this combination eliminates space rays, tracks of satellites, travel of asteroids, etc. 
# but we obtain a MASTERDARK with a S/N of the order of 25 % a 30 %

def median(ndarray_list):
	""" Create a median array from all array, i.e calcul the median for each pixel.
		> More the number of ndarray is, more the median will be precise !
		> All ndarray must have same dimensions !
	"""
	if len(ndarray_list) == 1:
    	# Shouldn't happen ...
		return ndarray_list
   	else:
    	# Initialise the median array at dimensions of frame
		t = np.copy(ndarray_list[0])
        # Fills the median array
       	h,l,r = t.shape
       	lenght = len(ndarray_list)
       	for i in range(0,h-1):
			for j in range(0,l-1):
				for k in range(0,r-1):
					liste = np.zeros((lenght))
					for frame in range(0,lenght-1):
						liste[frame] = ndarray_list[frame][i][j][k]
       	           	t[i][j][k] = np.median(liste)
			print "Median : " + str(i) + "/" + str(h-2)
        return t


# SIGMA-CLIP (SIGMA REJECT) : Better than the median. It is the one that we shall usually use to combine the LIGHT images, DARK, FLAT FIELD and DARK FOR FLAT FIELD.
# 1) From the set of corresponding pixel values from each source image, compute the mean (average) and standard deviation of these values.
# 2) Compute a new mean, omitting pixels from the above set that fall further away than threshold standard deviations from the mean. Use this new mean as the output value for this pixel location.
# 3) Repeat steps 1-2 for every pixel in the final image.

def sigmaReject(ndarray_list):
	""" Create a sigma reject array from all array, i.e calcul the sigma reject for each pixel.
		> More the number of ndarray is, more the sigma reject will be precise !
		> All ndarray must have same dimensions !
	"""
	if len(ndarray_list) == 1:
    	# Shouldn't happen ...
		return ndarray_list
	else:
    	# Initialise the sigmaReject array at dimensions of frame
		t = np.copy(ndarray_list[0])
        # Fills the sigmaReject array
		h,l,r = ndarray_list[0].shape
		lenght = len(ndarray_list)
		for i in range(0,h-1):
			for j in range(0,l-1):
				for k in range(0,r-1):
					# from the set of corresponding pixel values from each source image, compute the average
					liste = []
					for frame in range(0,lenght-1):
						liste.append(ndarray_list[frame][i][j][k])
                   	mean = np.mean(liste)
                   	# Find standard deviation of these values
                   	variance = 0
                   	for frame in range(0,lenght-1):
                   		variance = variance + (ndarray_list[frame][i][j][k]-mean)**2
                   	variance = variance/lenght
                   	ecart_type = sqrt(variance)
                   	# Compute a new mean, omitting pixels from the above set that fall further away than threshold standard deviations from the mean.
                   	sigmaClip = np.zeros((lenght))
                   	for frame in range(0,lenght-1):
                   		if (ndarray_list[frame][i][j][k] <= ecart_type):
                   			sigmaClip[frame] = ndarray_list[frame][i][j][k]
                   	mean = np.mean(sigmaClip)
                   	t[i][j][k] = mean
			print "SigmaReject : " + str(i) + "/" + str(h-2)
        return t



# AVERAGE : only for BIAS !

def average(ndarray_list):
	""" Create a average array from all array, i.e calcul the average for each pixel.
		> More the number of ndarray is, more the average will be precise !
		> All ndarray must have same dimensions !
	"""
	if len(ndarray_list) == 1:
    	# Shouldn't happen ...
		return ndarray_list
	else:
    	# Initialise the median array at dimensions of frame
		t = np.copy(ndarray_list[0])
        # Fills the median array
		h,l,r = t.shape
		lenght = len(ndarray_list)
		for i in range(0,h-1):
			for j in range(0,l-1):
				for k in range(0,r-1):
					liste = np.zeros((lenght))
					for frame in range(0,lenght-1):
						liste[frame] = ndarray_list[frame][i][j][k]
                   	t[i][j][k] = np.average(liste)
			print "Average : " + str(i) + "/" + str(h-2)
        return t



# The normalization consists in putting pixels in the same intensity before being combined

# By dividing the flat-field pixel value by the mean of all the pixels in the flat-field image, we arrive at the normalized pixel value. 
# A pixel that has a value equal to the mean will be normalized to 1, while a pixel that has a value less than the mean will be normalized to less than 1, and pixels with values above the mean will be normalized to more than 1. 
# Any image-processing program that performs calibration takes care of this normalization automatically, but it’s important to understand the process, as we’ll see when we talk about how to get good flats.

def normalize(ndarray_list):
    """ Normalize each ndarray and scale all
    """   
    t = list(ndarray_list)
    liste = []
    lenght = len(t)
    # 1) Normalize each flat field, i.e. divide it by its mean entry value
    for i in range(lenght):
        mean = np.mean(t[i]) # Find the mean of the ndarray
        liste.append(mean)
        t[i] = np.divide(t[i], mean) # Divide ndarray by its mean, normalizing it
    	print "Normalize 1/2 with mean " + mean + " : " + str(i) + "/" + str(lenght)
    # 2) Scale all of the fields’ means so that their individual averages are equal to one another
    meanofmean = sum(liste) / len(liste)  # Find the mean of the total set of ndarray_list
    for i in range(lenght):
        t[i] = np.multiply(t[i], np.divide(meanofmean, np.mean(t[i]))) # Divide
        print "Normalize 2/2 with " + np.divide(meanofmean, np.mean(t[i])) + " : "+ str(i) + "/" + str(lenght)
    return t



# MASTER DARK ---------------------------------------------------------------------------------------------------------------#

# Dark fields capture the noise inherent to the CCD array, which we would like to eliminate so the sensor doesn’t contaminate the light we’re collecting from the night sky

def processMasterDark(ndarray_list) :
	""" The MASTERDARK image will serve to remove the thermal noise and random noise on our LIGHT image
		> without MASTERBIAS
	"""
	# 1) Create a sigma reject array from all of them, entry-by-entry.
	return sigmaReject(ndarray_list)


def processMasterDarkWithBias(ndarray_list, ndarray_masterBias) :
	""" The MASTERDARK image will serve to remove the thermal noise and random noise on our LIGHT image
		> with MASTERBIAS
	"""
	# 1) Subtract the master bias frame
	darks = list(ndarray_list)
	lenght = len(darks)
	h,l,r = darks[0].shape
	for i in range(lenght):
		darks[i] = np.subtract(darks[i], ndarray_masterBias)
	# 2) Create a sigma reject array from all of them, entry-by-entry.
	return sigmaReject(darks)


def processMasterDarkFlat(ndarray_list, ndarray_masterBias) :
	""" The MASTER DARK FLAT image will serve to calcul the MASTER FLAT FIELD WITH BIAS
	"""
	# 1) Subtract the master bias frame
	darkflats = list(ndarray_list)
	lenght = len(darkflats)
	h,l,r = darkflats[0].shape
	for i in range(lenght):
		darkflats[i] = np.subtract(darkflats[i], ndarray_masterBias)
	# 2) Create a sigma reject array from all of them, entry-by-entry.
	return sigmaReject(darkflats)


# MASTER FLAT ---------------------------------------------------------------------------------------------------------------#

# Flats are images portraying the sensitivity of individual pixels in the frame, which is illuminated uniformly

def processMasterFlat(ndarray_list, ndarray_masterDark) :
	""" The MASTERFLAT image will serve to remove all track of dusts, gradient, vignetting on our LIGHT image
		> Without MASTERBIAS
	"""
	# 1) Subtract the master dark frame
	flats = list(ndarray_list)
	lenght = len(flats)
	h,l,r = flats[0].shape
	for i in range(lenght):
		flats[i] = np.subtract(flats[i], ndarray_masterDark)
	# 2) Normalize all frame
	# 3) Create a median array from all of them, entry-by-entry.
	return median(normalize(flats))


def processMasterFlatWithBias(ndarray_list, ndarray_masterDarkFlat, ndarray_masterBias) :
	""" The MASTERFLAT image will serve to remove all track of dusts, gradient, vignetting on our LIGHT image
		> With MASTERBIAS & MasterDarkFlat
	"""
	# 1) Subtract the MasterBias and the MasterDarkFlat
	flats = list(ndarray_list)
	lenght = len(flats)
	h,l,r = flats[0].shape
	for i in range(lenght):
		flats[i] = np.subtract(flats[i], ndarray_masterBias)
		flats[i] = np.subtract(flats[i], ndarray_masterDarkFlat)
	# 2) Normalize all frame
	flats = normalize(flats)
	# 3) Create a median array from all of them, entry-by-entry.
	return median(flats)


# MASTER BIAS ---------------------------------------------------------------------------------------------------------------#

# If you take your series of images DARK with same parameters (the same exposure time, same binning, same temperature) as the LIGHT images and for your images of FLAT FIELD, you will not need to set of images of BIAS.
# CAREFUL : OVERALL BY AVERAGE only !
def processMasterBias(ndarray_list) :
	""" The MASTERBIAS image will serve to remove the initial exposure level of pixels in our LIGHT
		> If you take your series of images DARK with same parameters (the same exposure time, same binning, same temperature) as the LIGHT images and for your images of FLAT FIELD, you will not need to set of images of BIAS.
	"""
	# 1) Create an average array from all of them, entry-by-entry.
	return average(ndarray_list)


# LIGHT ----------------------------------------------------------------------------------------------------------------------#

# We will use master flat and dark field to clean up each light frame, which contains data about the night sky : (Light-Dark)/Flat

def calibration(ndarray_list, ndarray_masterDark, ndarray_masterFlat):
	""" The final result will be a perfectly corrected LIGHT image
		> without BIAS
	"""
	lights_list = list(ndarray_list)
	length = len(lights_list)
	# Use masterflat and masterdark to clean up each light frame
	for i in range(lenght):
		lights_list[i] = np.true_divide(np.subtract(lights_list[i], ndarray_masterDark), ndarray_masterFlat)
	# Normalize each light frame
	return normalize(lights_list)


def calibrationWithBias(ndarray_list, ndarray_masterDark, ndarray_masterFlat, ndarray_masterBias):
	""" The final result will be a perfectly corrected LIGHT image
		> with BIAS
	"""
	lights_list = list(ndarray_list)
	length = len(lights_list)
	# Use masterflat, masterdark and masterbias to clean up each light frame
	for i in range(lenght):
		lights_list[i] = np.subtract(lights_list[i], ndarray_masterBias)
		lights_list[i] = np.true_divide(np.subtract(lights_list[i], ndarray_masterDark), ndarray_masterFlat)
	# Normalize each light frame
	return normalize(lights_list)


def registration(ndarray_list):
	""" To overlap LIGHT image (after the calibration) """
	pass



#---------- TESTS -------------#

if __name__ == '__main__':
	import imageio
	from ImageRaw import ImageRaw

 # MasterDark :
	path = '../../Pictures_test/darks/'
	dark1 = ImageRaw(path + 'D_0003_IC405_ISO800_300s__13C.CR2').getndarray()
	dark3 = ImageRaw(path + 'D_0015_IC405_ISO800_300s__13C.CR2').getndarray()
	dark4 = ImageRaw(path + 'D_0014_IC405_ISO800_300s__13C.CR2').getndarray()
	dark5 = ImageRaw(path + 'D_0013_IC405_ISO800_300s__13C.CR2').getndarray()
	dark7 = ImageRaw(path + 'D_0012_IC405_ISO800_300s__13C.CR2').getndarray()
	dark8 = ImageRaw(path + 'D_0011_IC405_ISO800_300s__13C.CR2').getndarray()
	dark9 = ImageRaw(path + 'D_0010_IC405_ISO800_300s__13C.CR2').getndarray()
	dark11 = ImageRaw(path + 'D_0003_IC405_ISO800_300s__13C.CR2').getndarray()
	result_dark = processMasterDark([dark1,dark3,dark4,dark5,dark7,dark8,dark9,dark11])
	imageio.imsave('../../Pictures_test/testMasterDark.tiff', result_dark)
	del dark1
	del dark3
	del dark4
	del dark5
	del dark7
	del dark8
	del dark9
	del dark11

# MasterFlat :
#	from PIL import Image
#	from skimage import data
#	dark = data.imread('../../Pictures_test/testMasterDark.tiff')
	path = '../../Pictures_test/flats/'
	flat1 = ImageRaw(path + 'IMG_3059.CR2').getndarray()
	flat2 = ImageRaw(path + 'IMG_3059.CR2').getndarray()
	flat3 = ImageRaw(path + 'IMG_3060.CR2').getndarray()
	flat4 = ImageRaw(path + 'IMG_3061.CR2').getndarray()
	flat5 = ImageRaw(path + 'IMG_3062.CR2').getndarray()
	flat6 = ImageRaw(path + 'IMG_3063.CR2').getndarray()
	flat7 = ImageRaw(path + 'IMG_3064.CR2').getndarray()
	flat8 = ImageRaw(path + 'IMG_3065.CR2').getndarray()
	flat9 = ImageRaw(path + 'IMG_3066.CR2').getndarray()
	flat10 = ImageRaw(path + 'IMG_3067.CR2').getndarray()
	flat11 = ImageRaw(path + 'IMG_3068.CR2').getndarray()
	result_flat = processMasterFlat([flat1,flat2,flat3,flat4,flat5,flat6,flat7,flat8,flat9,flat10,flat11],result_dark)
	imageio.imsave('../../Pictures_test/testMasterFlat.jpg', result_flat)
	del flat1
	del flat2
	del flat3
	del flat4
	del flat5
	del flat6
	del flat7
	del flat8
	del flat9
	del flat10
	del flat11

#------------------------------#


