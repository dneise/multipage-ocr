#!/usr/bin/env python
"""Naval Fate.

Usage:
  multipage-ocr.py <input_path> <output_path> [options]

Options:
  --density N           dpi density to supply to ImageMagick convert [default: 300]
  --depth N             bit depth [default: 8]
  --imageformat FORMAT  image format (e.g., jpg, png, tif) [default: jpg]
  --psm N               tesseract layout analysis mode [default: 3]
"""
from docopt import docopt
import os
import os.path
import tempfile
from PyPDF2 import PdfFileReader
from tqdm import trange
from glob import glob
from io import StringIO


def main(arguments):
    arguments['<input_path>'] = os.path.realpath(arguments['<input_path>'])
    arguments['<output_path>'] = os.path.realpath(arguments['<output_path>'])
    arguments['--density'] = int(arguments['--density'])
    arguments['--depth'] = int(arguments['--depth'])
    arguments['--psm'] = int(arguments['--psm'])
    assert os.path.exists(arguments['<input_path>'])
    assert arguments['<input_path>'].endswith(".pdf")

    num_pages = PdfFileReader(open(arguments['<input_path>'], 'rb')).getNumPages()

    #  with tempfile.TemporaryDirectory(suffix='', prefix='tmp', dir='.') as tmp_dir:
    tmp_dir = tempfile.mkdtemp(suffix='', prefix='multipage_ocr_temp_', dir='.')

    for i in trange(num_pages):
        tmp_file_path = os.path.join(tmp_dir, '{page:010d}.{imageformat}'.format(
            page=i,
            imageformat=arguments['--imageformat']))

        cmd = '''convert \
        -density {density}\
        -depth {depth}\
        {input_path}[{page}]\
        -background white\
        {tmp_file_path}'''.format(
            density=arguments['--density'],
            depth=arguments['--depth'],
            input_path=arguments['<input_path>'],
            page=i,
            tmp_file_path=tmp_file_path
            )
        os.system(cmd)

        text_file_path = os.path.join(tmp_dir, '{page:010d}'.format(page=i))

        cmd = '''tesseract \
        -psm {psm} \
        {tmp_file_path} \
        {text_file_path} \
        > /dev/null 2>&1
        '''.format(
            psm=arguments['--psm'],
            tmp_file_path=tmp_file_path,
            text_file_path=text_file_path)
        os.system(cmd)

    with open(arguments['<output_path>'], 'wt') as outfile:
        for path in sorted(glob(os.path.join(tmp_dir, '*.text'))):
            outfile.write(open(path).read())

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)
    main(arguments)
