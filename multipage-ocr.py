#!/usr/bin/env python
"""Naval Fate.

Usage:
  multipage-ocr.py <input_path> <output_path> [options]

Options:
  --density N           dpi density for ImageMagick convert [default: 300]
  --depth N             bit depth for ImageMagick convert [default: 8]
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


def main(args):
    args['<input_path>'] = os.path.realpath(args['<input_path>'])
    args['<output_path>'] = os.path.realpath(args['<output_path>'])
    args['--density'] = int(args['--density'])
    args['--depth'] = int(args['--depth'])
    args['--psm'] = int(args['--psm'])
    assert os.path.exists(args['<input_path>'])
    assert args['<input_path>'].endswith(".pdf")

    num_pages = PdfFileReader(open(args['<input_path>'], 'rb')).getNumPages()
    tmp_dir = tempfile.mkdtemp(
        prefix='multipage_ocr_temp_',
        dir='.'
    )

    for i in trange(num_pages):
        tmp_file_path = os.path.join(
            tmp_dir,
            '{page:010d}.{imageformat}'.format(
                page=i,
                imageformat=args['--imageformat']
            )
        )

        cmd = '''convert \
        -density {density}\
        -depth {depth}\
        {input_path}[{page}]\
        -background white\
        {tmp_file_path}'''.format(
            density=args['--density'],
            depth=args['--depth'],
            input_path=args['<input_path>'],
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
            psm=args['--psm'],
            tmp_file_path=tmp_file_path,
            text_file_path=text_file_path)
        os.system(cmd)

    with open(args['<output_path>'], 'wt') as outfile:
        for path in sorted(glob(os.path.join(tmp_dir, '*.text'))):
            outfile.write(open(path).read())

if __name__ == '__main__':
    args = docopt(__doc__, version='Naval Fate 2.0')
    print(args)
    main(args)
