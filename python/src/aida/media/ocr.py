# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

import pytesseract
import os
from cv2 import imread
from aida.ldctools.textloader import log
from logging import INFO
import re

class OCR:

    def __init__(self,languages=['eng']):
        self.languages = languages
        log(INFO, 'configured OCR with languages %s' % ', '.join(languages))

    def extract_text(self, image):
        return {language:pytesseract.image_to_string(image, lang=language,config='-psm 3') for language in self.languages}


    def extract(self, dirs, destination):
        with open (os.path.join(destination,'ocr.txt'),'w', encoding='utf-8') as fp:
            for dir in dirs:
                for root, walked_dirs, files in os.walk(dir):
                    for name in files:
                        path = os.path.join(root, name)
                        if os.path.splitext(name)[1] in ['.png','.jpg']:
                            try:
                                print ('Inspect %s' % name)
                                text_by_language = self.extract_text(imread(path))
                                relative_path = os.path.abspath(path)[len(dir):]
                                if relative_path[0] in ['/','\\']:
                                    relative_path = relative_path[1:]
                                if text_by_language is not None and len(text_by_language) > 0:
                                    lines = ['\t'.join([relative_path, language, re.sub("\n|\r|\t", " ", text),'\n']) \
                                                            for language, text in text_by_language.items() \
                                                            if text is not None and len(text) > 0]
                                    fp.writelines(lines)
                                    fp.flush()
                            except Exception as e:
                                print ('fail ' + str(e))

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directories to search.')
    parser.add_argument('--dirs', nargs='+', help='directories to search')
    parser.add_argument('--destination', help='where to explode the files')
    parser.add_argument('--languages', nargs='+', help='where to explode the files')
    args = parser.parse_args()
    OCR(languages=args.languages if args.languages is not None else ['eng']).extract(args.dirs, args.destination)


if __name__ == '__main__':
    main()