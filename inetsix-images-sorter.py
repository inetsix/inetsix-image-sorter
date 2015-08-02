'''
Title:
    inetsix-image-sort
Description:
    Script to sort images based on EXIFs information.
Author:
    titom73
Date:
    August 2 2015
Version:
    0.3
Changelog:
	v0.3:
		- Workaround to cover issue when PIL is not able to open file: switch to exifread librairy
		- Add support for REGEXP to match EXIF Field: DateTimeOriginal|DateTimeDigitized|36867
		- Add support for numerical field in place of named field.
	v0.2: 
		- Add utf-8 support for both filenames and directories
		- Add support for special characters with unicode and decode
		- Add Logging capability
		- Add some Exception handler to secure script execution
		- Does not move image if target already exist (No overrride)
'''

import os
import io
import pprint
import re
import shutil
import PIL
import exifread
import fnmatch
import argparse
import logging
import sys

from PIL import Image
from PIL.ExifTags import TAGS
from optparse import OptionParser
from logging.handlers import RotatingFileHandler

# ----------------------------------------------------------------- #
# GENERIC PARAMs Section											#
# ----------------------------------------------------------------- #

### Default values
src_dir = "./src-img/"
dst_dir = "./sorted/"

### Init Logger and Formatter
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(funcName)s :: %(message)s')
### Display log with DEBUG level and higher
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)
### Write log with INFO level and higher
file_handler = logging.FileHandler('activity.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ----------------------------------------------------------------- #
# LOG LEVEL															#
# ----------------------------------------------------------------- #
# DEBUG: information uses to understand script's actions
# INFO: generic information to log
# WARNING: Action for special cases (no EXIF information, ...)
# ERROR: Use cases not managed: issue identify with no workaround
# CRITICAL: Script is aborted


# ----------------------------------------------------------------- #
# Function Section 													#
# ----------------------------------------------------------------- #

### Get Exif Field value
### exif: PIL.ExifTags
### field: Name of Exif searched for
def get_field (exif , field,image) :
	#logger.debug(type(exif))
	logger.debug('Search EXIF field: %s for image %s', field, image )
	if isinstance(exif, dict):
		my_regex = r".*" + field + r".*"
		for tag in exif.keys():
		    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
		        #logger.debug("Key: %s, value %s", tag, exif[tag])
		        if( re.match(my_regex, str(tag), re.M|re.I) ):
		        #if( tag == field ):
		        	logger.debug('EXIF %s found: %s (field %s)', field, exif[tag],str(tag))
		        	return exif[tag]
	else:
		logger.debug('EXIF is not an instance')
	logger.warning('No EXIF found in %s',image)
	return False

### List all Exif Fields and values
### exif: array of values
def list_exif(exif):
	if isinstance(exif, dict):
		for tag in exif.keys():
		    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
		        logger.debug("Key: %s, value %s", tag, exif[tag])
	else:
		logger.debug('EXIF is not an instance')

### Create Directory:
### dirIn is name of new directory.
### It will be created under dst_dir
def create_single_dir( dirIn, base):
	if os.path.isdir(os.path.join(base, dirIn) ) is not True:
		os.makedirs(os.path.join(base, dirIn) )

def create_tree(date, base):
	directories = date.split("-")
	logger.debug('Destination directory is based on %s', date)
	do_it = False
	for directory in directories:
		#logger.debug('Directory is %s', directory)
		if os.path.isdir( os.path.join(base, directory) ) is not True:
			logger.debug('Directory %s does not exist, create it !', directory)
			os.makedirs( os.path.join(base, directory) )
			do_it = True
		base = os.path.join(base, directory)
	if do_it is True:
		logger.info('Create directory %s', base)

### Def to move image to directory based on simgle structure
def move_image( image, src_dir, dst_dir ):
	try:
		target_image = os.path.join( dst_dir.encode('utf-8'), image.encode('utf-8'))
		src_image = os.path.join( src_dir.encode('utf-8') , image.encode('utf-8'))
	except:
		logger.critical("Unexpected error: %s", sys.exc_info()[0])
	if os.path.exists( target_image ):
		logger.info('Image %s exist, move to next image...', image.encode('utf-8') )
		exit
	# Copy image from source directory to destination
	try:
		logger.info('Move Image %s from %s to %s',image.encode('utf-8') , src_dir.encode('utf-8'), dst_dir.encode('utf-8'))
		shutil.copy(src_image, target_image)
	except IOError,e :
		logger.warning('Can\'t copy %s from %s to the destination dir %s', image.encode('utf-8') , src_dir.encode('utf-8'), dst_dir.encode('utf-8'))
		logger.error('IOError:%s' , format(e))

### Def to create structure at the first step.
def init_script():
	if os.path.isdir(options.destination) is not True:
		logger.debug('Create Directory: %s',options.destination)
		os.makedirs(options.destination)
	if os.path.isdir(options.destination+"UNSORTED/") is not True:
		logger.debug('Create Directory: %s',options.destination+"/UNSORTED/")
		os.makedirs(options.destination+"UNSORTED/")

### Delete hours, minutes and second from Exif value
### Replace all : to - to be able to create directories per date
def normalize_date(dateIn):
	logger.debug('Date to normalize: \"%s\"', str(dateIn) )
	dateIn = re.sub(r"(\s+\d{2}:\d{2}:\d{2})", "/", str(dateIn) )
	dateOut = re.sub(r":", "-", dateIn)
	return dateOut

def main( options ):
	init_script()
	logger.info('Start to sort images')
	for root, dirnames, filenames in os.walk(options.source.encode('utf8')):
		for image in fnmatch.filter(filenames, '*.[Jj][Pp][Gg]'):
			# Open Image file
			try:
				img = PIL.Image.open( os.path.join( unicode(root.decode('utf-8')) , unicode(image.decode('utf-8')) ) )
				# Extract EXIF datas. Will be used later
				exif_data = img._getexif()
			except EnvironmentError, e:
				logger.critical('%s cannot be opened using PIL from directory %s', unicode(image.decode('utf-8')), unicode(root.decode('utf-8')) )
				logger.error('IOError:%s' , format(e))
				logger.info('Try to use EXIFREAD to extract data')
				f = open( os.path.join( unicode(root.decode('utf-8')) , unicode(image.decode('utf-8')) ), 'rb' )
				exif_data = exifread.process_file(f)
			# Extract EXIF field for date based on DateTimeOriginal field
			# Hack to identify EXIF Code used by pentax to store DateTimeOriginal field
#			# http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html
			exif_field = get_field( exif_data , '(DateTimeOriginal|DateTimeDigitized|36867)', os.path.join( root.decode('utf-8'), image.decode('utf-8') ) )
			logger.debug('EXIF_FIELD is set to: %s', exif_field)
			# If Image has no EXIF information, we go to next image
			if exif_field == False:
				logger.warning('No EXIF found in %s, move it to UNSORTED directory and go to next image', os.path.join(root, image))
				move_image(unicode(image.decode('utf-8')), unicode(root.decode('utf-8')), str(options.destination+"/UNSORTED/").encode('utf-8'))
				continue
			# Else we can work on it
			# Create Date format with only YYYY-MM-DD and delete all other entries such as hours and minutes
			date = normalize_date( exif_field )
			# Create a single directory named YYYY-MM-DD
			if options.mode == "single":
				# Create directory structure
				create_single_dir(date,options.destination)
				# Copy file based on previous source and destination path
				move_image(image, root, options.destination+date)
			# Tree mode based on directory strutucte like this: YYY / MM / DD
			elif options.mode == "tree":
				# Create directory structure
				create_tree(date,options.destination)
				# Convert DATE format to directory format
				date_as_dir = re.sub(r"-", "/", date)
				# Copy image to destination dir
				move_image(image.decode('utf-8') , root.decode('utf-8') , options.destination.decode('utf-8')+date_as_dir.decode('utf-8'))
			# Default is single mode
			else:
				create_single_dir(date)

# ----------------------------------------------------------------- #
# MAIN Section 														#
# ----------------------------------------------------------------- #

if __name__ == "__main__":
	"""
	Script Launcher
	"""
	logger.info("Script started")
	# Manage cmdLine parameters.
	parser = argparse.ArgumentParser(description="Inetsix Image Sorter -- version 0.1")
	parser.add_argument('-s','--source' ,help='Source Directory where photos are located',default=src_dir)
	parser.add_argument('-d','--destination' ,help='Destination Directory where photos are going to be sorted',default=dst_dir)
	parser.add_argument('-m','--mode' ,help='Mode for output: single(YYYY-MM-DD) / tree(YYYY/MM/DD)',default="single")

	# Manage All options and construct array
	options = parser.parse_args()
	logger.info('Start to sort images using %s mode', options.mode)
	logger.info('Source directory: %s',options.source)
	logger.info('Destination directory: %s',options.destination)
	# Launch script engine
	main(options)