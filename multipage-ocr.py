#!/usr/bin/env python
"""Naval Fate.

Usage:
  multipage-ocr.py <input_path> <output_path> [options]

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
import os.path
import string
import random
from PyPDF2 import PdfFileReader


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    ''' generate random string'''
    return ''.join(random.choice(chars) for x in range(size))


def main(arguments):
    '''arguments example:
    {'--clean': False,
     '--density': '300',
     '--depth': '8',
     '--imageformat': 'jpg',
     '--psm': '3',
     '--quiet': False,
     '<input_path>': 'in',
     '<output_path>': 'out'}

    '''
    arguments['<input_path>'] = os.path.realpath(arguments['<input_path>'])
    arguments['<output_path>'] = os.path.realpath(arguments['<output_path>'])
    arguments['--density'] = int(arguments['--density'])
    arguments['--depth'] = int(arguments['--depth'])
    arguments['--psm'] = int(arguments['--psm'])
    assert os.path.exists(arguments['<input_path>'])
    assert arguments['<input_path>'].endswith(".pdf")

    input_file = PdfFileReader(open(arguments['<input_path>']))
    num_pages = input_file.getNumPages()

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
