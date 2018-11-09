# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
from aida.ldctools import ldc
from logging import INFO, ERROR
from cv2 import imwrite, imdecode, IMREAD_COLOR
from io import BytesIO
import numpy as np
import pikepdf
from aida.ldctools.ldc import log

def __decode(img_stream):
    file_bytes = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    return imdecode(file_bytes, IMREAD_COLOR)

def decodeImage(page,prefix):
    xObject = page.images
    count = 0
    for name, img in xObject.items():
        count += 1
        if img['/Filter'] in ['/DCTDecode','/JPXDecode','/FlatDecode']:
            try:
                pdfimage = pikepdf.PdfImage(img)
                input = imdecode(np.asarray(bytearray(img.get_raw_stream_buffer())), IMREAD_COLOR)
                suffixes = {'/JPXDecode':'jp2','/DCTDecode':'jpg','/FlatDecode':'png'}
                suffixes[img['/Filter']]
                imwrite(prefix + '_%03d.%s' % (count,suffixes[img['/Filter']]),input)
            except Exception as ex:
                log(ERROR,'Cannot extract %s:%s due to %s' % (prefix,name, str(ex)))

class ImageMediaExtractor:

    def __init__(self, pages_dir='representative_pages'):
        self.pages_dir = pages_dir

    def _page_extract_cb(self, filename):
        # open allows you to read the file
        destination = os.path.join(os.path.split(filename)[0], self.pages_dir)
        if not os.path.exists(destination):
            os.mkdir(destination)
        prefix = os.path.splitext(os.path.basename(filename))[0]
        try:
            pdfobject = pikepdf.open(filename)
            num_pages = len(pdfobject.pages)

            count = 0
            text = ""
            while count < num_pages:
                pageObj = pdfobject.pages[count]
                count += 1
                decodeImage(pageObj, os.path.join(destination,prefix + '_%03d' % count))
                #text += pageObj.extractText()
        except Exception as ex:
            log(ERROR, 'Cannot extract %s due to %s' % (filename,  str(ex)))

    def extract(self, dirs, destination):
        for dir in dirs:
            ldc.unZipAll(dir, filters=['pdf'], location=destination, unwrap_files=True,
                         cleanup=True,cb=self._page_extract_cb)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directories to search.')
    parser.add_argument('--dirs', nargs='+', help='directories to search')
    parser.add_argument('--destination', help='where to explode the files')
    args = parser.parse_args()
    ImageMediaExtractor().extract(args.dirs, args.destination)


if __name__ == '__main__':
    main()