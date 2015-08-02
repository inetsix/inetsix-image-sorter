inetsix-images-sorter
==================

# Description of the repository
Python script to sort massive list of JPEG files. Sort methodology is based on DATE of each image and create one directory per day. Directories can be created flat based (YYYY-MM-DD) or tree based (YYYY/MM/DD) by using a simple trigger in script parameters.

Script parses source directory recursively and catches all file with "JPG" or "jpg" extension and copy them to destination directory after creating correct directories. If an image with same filename is present, Image is not copied assuming they are equal.

Script handle some generic errors:
- Catch UTF-8 and non UTF-8 encoding: Usage of special characters in directory or filename is managed by script
- EXIF encoding method: some vendors encode 'DateTimeOriginal' field under its numerical identifier (36867)
- PIL cannot open some files due to their encoding. Exif Read is used as a backup Exif's reader

In any case, if no 'DateTimeOriginal' might be identified, then, image is moved to a generic directory named UNSORTED and created under destination directory.

## Setup Guide.

Following libraries must be installed before executing script:
- os
- io
- pprint
- re
- shutil
- PIL
- exifread
- fnmatch
- argparse
- logging
- sys

```
	pip install <module>
```

Most of them are built in Python. Others are available here:
- PIL: [Website](http://www.pythonware.com/products/pil/)
- EXIF Read: [Website](https://pypi.python.org/pypi/ExifRead)

## Usage:
* help :
```shell
	python inetsix-images-sorter.py -h
		usage: inetsix-images-sorter-v0.4.py [-h] [-s SOURCE] [-d DESTINATION]
                                     [-m MODE] [-l LOGFILE] [-v VERBOSE]

		Inetsix Image Sorter -- version 0.4

		optional arguments:
		  -h, --help            show this help message and exit
		  -s SOURCE, --source SOURCE
		                        Source Directory where photos are located
		  -d DESTINATION, --destination DESTINATION
		                        Destination Directory where photos are going to be
		                        sorted
		  -m MODE, --mode MODE  Mode for output: single(YYYY-MM-DD) / tree(YYYY/MM/DD)
		  -l LOGFILE, --logfile LOGFILE
		                        File uses to store log, default is activity.log
		  -v VERBOSE, --verbose VERBOSE
		                        Log Verbosity, default is set to info
```

* Use case with TREE structure:
```shell
	python inetsix-images-sorter.py -m tree -d ./test/
		2015-08-02 11:30:33,769 :: INFO :: <module> :: Script started
		2015-08-02 11:30:33,781 :: INFO :: <module> :: Start to sort images using tree mode
		2015-08-02 11:30:33,781 :: INFO :: <module> :: Source directory: ./src-img/
		2015-08-02 11:30:33,781 :: INFO :: <module> :: Destination directory: ./test/
		2015-08-02 11:30:33,978 :: INFO :: main :: Start to sort images
		2015-08-02 11:30:34,595 :: DEBUG :: get_field :: Search EXIF field: (DateTimeOriginal|DateTimeDigitized|36867) for image ./src-img/IMGP4091.JPG
		2015-08-02 11:30:34,724 :: DEBUG :: get_field :: EXIF (DateTimeOriginal|DateTimeDigitized|36867) found: 2012:04:18 17:31:52 (field 36867)
		2015-08-02 11:30:34,724 :: DEBUG :: main :: EXIF_FIELD is set to: 2012:04:18 17:31:52
		2015-08-02 11:30:34,725 :: DEBUG :: normalize_date :: Date to normalize: "2012:04:18 17:31:52"
		2015-08-02 11:30:34,725 :: DEBUG :: create_tree :: Destination directory is based on 2012-04-18/
		2015-08-02 11:30:34,725 :: DEBUG :: create_tree :: Directory is 2012
		2015-08-02 11:30:34,928 :: DEBUG :: create_tree :: Directory is 04
		2015-08-02 11:30:35,034 :: DEBUG :: create_tree :: Directory is 18/
		2015-08-02 11:30:35,036 :: INFO :: move_image :: Image IMGP4091.JPG exist, move to next image...
		2015-08-02 11:30:35,036 :: INFO :: move_image :: Move Image IMGP4091.JPG from ./src-img/ to ./test/2012/04/18/
```

* Use case with FLAT structure:
```shell
	python inetsix-images-sorter.py -d ./test/
		2015-08-02 11:33:56,310 :: INFO :: <module> :: Script started
		2015-08-02 11:33:56,312 :: INFO :: <module> :: Start to sort images using single mode
		2015-08-02 11:33:56,312 :: INFO :: <module> :: Source directory: ./src-img/
		2015-08-02 11:33:56,312 :: INFO :: <module> :: Destination directory: ./test/
		2015-08-02 11:33:56,604 :: INFO :: main :: Start to sort images
		2015-08-02 11:33:57,081 :: DEBUG :: get_field :: Search EXIF field: (DateTimeOriginal|DateTimeDigitized|36867) for image ./src-img/IMGP4091.JPG
		2015-08-02 11:33:57,297 :: DEBUG :: get_field :: EXIF (DateTimeOriginal|DateTimeDigitized|36867) found: 2012:04:18 17:31:52 (field 36867)
		2015-08-02 11:33:57,298 :: DEBUG :: main :: EXIF_FIELD is set to: 2012:04:18 17:31:52
		2015-08-02 11:33:57,298 :: DEBUG :: normalize_date :: Date to normalize: "2012:04:18 17:31:52"
		2015-08-02 11:33:57,689 :: INFO :: move_image :: Move Image IMGP4091.JPG from ./src-img/ to ./test/2012-04-18/
```

## Changelog
- v0.4:
	- Add VERBOSE switch
	- Add capability to define log file
	- Add comments to all functions.
- v0.3:
	- Workaround to cover issue when PIL is not able to open file: switch to exifread librairy
	- Add support for REGEXP to match EXIF Field: DateTimeOriginal|DateTimeDigitized|36867
	- Add support for numerical field in place of named field.
- v0.2: 
	- Add utf-8 support for both filenames and directories
	- Add support for special characters with unicode and decode
	- Add Logging capability
	- Add some Exception handler to secure script execution
	- Does not move image if target already exist (No overrride)