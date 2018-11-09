# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from aida.ldctools import ldc



class ImageMediaExtractor:

    def extract(self, dirs, destination):
        from json import dump
        import os
        for dir in dirs:
            ldc.unZipAll(dir, filters=['gif','jpg','png','pdf'], location=destination, unwrap_files=True, cleanup=True)
        images = [i for i in os.listdir(destination)  if os.path.splitext(i)[1].lower() in ['.png', '.jpg', '.gif']]
        with open('images.json','w') as fp:
           dump({'images':images},fp)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directories to search.')
    parser.add_argument('--dirs', nargs='+', help='directories to search')
    parser.add_argument('--destination', help='where to explode the files')
    args = parser.parse_args()
    ImageMediaExtractor().extract(args.dirs, args.destination)


if __name__ == '__main__':
    main()