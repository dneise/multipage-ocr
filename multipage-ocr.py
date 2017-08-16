#!/usr/bin/env python
"""Naval Fate.

Usage:
  multipage-ocr.py <input_file> <output_file> [options]

Options:
  --density N           dpi density to supply to ImageMagick convert [default: 300]
  --depth N             bit depth [default: 8]
  --imageformat FORMAT  image format (e.g., jpg, png, tif) [default: jpg]
  --psm N               tesseract layout analysis mode [default: 3]
  --quiet               tesseract quiet 0 or 1; defaults to 1
  --clean               delete intermediate files; defaults to 1
"""
from docopt import docopt
import sys
import os
import string
import random
from PyPDF2 import PdfFileReader


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    ''' generate random string'''
    return ''.join(random.choice(chars) for x in range(size))


def main(argv):

    input_file = None
    output_file = None
    density = 300
    depth = 8
    imageformat = "jpg"
    psm = 3
    quiet_flag = 1

    # command-line arguments
    try:
        # gnu_getopt allows interspersing of option and non-option arguments
        opts, args = getopt.gnu_getopt(argv, "hi:o:d:b:f:p:q:", ["help", "input=", "output=", "density=", "depth=", "imageformat=","psm=","quiet="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-d", "--density"):
            density = int(arg)
        elif opt in ("-b", "--depth"):
            depth = int(arg)
        elif opt in ("-f", "--imageformat"):
            imageformat = arg
        elif opt in ("-p", "--psm"):
            psm = int(arg)
        elif opt in ("-q", "--quiet"):
            quiet_flag = int(arg)

    # check if the file provided as argument exists
    if not os.path.exists(input_file):
        sys.exit('ERROR: Input file \'%s\' was not found!' % input_file)

    # check if input file is a PDF
    if not input_file.endswith(".pdf"):
        sys.exit('ERROR: Input file should be a PDF.')

    # extract dirname, base, ext
    dirname = os.path.dirname(input_file)
    base, ext = os.path.splitext(os.path.basename(input_file))

    # specify output file
    if None == output_file:
        if "" == dirname:
            output_file = base + "_ocr.txt"
        else:
            output_file = dirname + "/" + base + "_ocr.txt"

    # get number of pages
    num_pages = PdfFileReader(file(input_file)).getNumPages()
    print("Number of pages: %d" % num_pages)

    # make random directory
    created_dir_flag = False
    iteration = 0
    itermax = 10
    while not created_dir_flag and iteration < itermax:
        tmp_dir = '/tmp/' + "ocr_" + id_generator()
        if not os.path.exists(tmp_dir):
            try:
                os.makedirs(tmp_dir)
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(tmp_dir):
                    pass
                else: raise
            created_dir_flag = True
        iteration += 1
        print(tmp_dir)

    if not created_dir_flag:
        sys.exit('ERROR: Unable to create random temporary directory.')

    # iterate through pages
    for i in xrange(0,num_pages):

        # convert PDF to image format
        cmd = ("convert -density %d -depth %d " % (density,depth)) + ("%s[%d] -background white %s/%d.%s" % (input_file,i,tmp_dir,i,imageformat))
        print("Convert PDF to image: " + cmd)
        os.system(cmd)

        # execute OCR
        cmd = "tesseract -psm %d %s/%d.%s %s/%d" % (psm,tmp_dir,i,imageformat,tmp_dir,i)
        if 1 == quiet_flag:
            cmd = cmd + " quiet"
        print("OCR on image: " + cmd)
        os.system(cmd)

    # concatenate results and delete them
    text_files = " ".join([tmp_dir+"/"+str(x)+".txt" for x in xrange(0,num_pages)])
    cmd = "cat %s > %s" % (text_files, output_file)
    print("Concatenate OCR outputs: " + cmd)
    os.system(cmd)

    # cleanup
    cmd = 'rm -r %s' % tmp_dir
    print("Cleanup temporary files: " + cmd)
    os.system(cmd)
