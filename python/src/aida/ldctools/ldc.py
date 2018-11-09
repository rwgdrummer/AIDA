# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
from zipfile import ZipFile
from subprocess import Popen, PIPE
from aida.ldctools.textloader import log
from logging import INFO, ERROR

class Scanner:

    def __init__(self,filename,fp):
        self.fp = fp
        self.filename = filename
        self.b = None
        self.pos = 0
        self.data = {}

    def _fillBuffer(self,size=1024):
        self.b = self.fp.read(size)

    def _extendBuffer(self,size=1024):
        self.b = self.b + self.fp.read(size)

    def _readNext(self):
        start = self.pos
        while self.b[self.pos] != 10:
            self.pos += 1
        last = self.pos
        self.pos+=1
        return self.b[start:last]

    def _readHead(self):
        return self._readNext()[:4].decode() == 'LDCc'

    def _readSize(self):
        return int(self._readNext().decode().strip())

    def _readSep(self):
        self._readNext()[:3].decode() == '---'

    def _readProperties(self):
        while True:
            next = self._readNext().decode()
            if next.strip() == 'endLDCc':
                break
            parts = next.split(':')
            self.data[parts[0].strip()] = parts[1].strip()

    def readHeader(self):
        self._fillBuffer()
        if self._readHead():
            size = self._readSize()
            if size-1024 > 0:
                self._extendBuffer(size-1024)
            self._readSep()
            self._readProperties()
            return True
        return False

    def md5(self, filename):
        try:
            p = Popen(['md5',filename],stdout=PIPE)
            stdout, stderr = p.communicate()
            if p.returncode == 0:
                return stdout.strip()[-32:].decode()
        except:
            try:
                from hashlib import md5
                hash_md5 = md5()
                with open(filename, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            except:
                return ''
        return ''

    def writeContents(self,dir='.'):
        newname = os.path.join(dir,os.path.splitext(os.path.basename(self.filename))[0])
        with open(newname,'wb') as op:
            b = self.fp.read()
            if b is not None:
                op.write(b)
        return newname

def mkdirs(path):
    current = '.'
    for entry in path.split(os.path.sep):
        if not os.path.exists(os.path.join(current,entry)):
            os.mkdir(os.path.join(current, entry))
        current = os.path.join(current, entry)

def unwrap(path, location=None, check_md5=True):
    """
    :param path:
    :param location:
    :param check_md5:
    :return: None if error
    """
    if location is None:
        location =  os.path.split(os.path.abspath(path))[0]
    newname = os.path.join(location, os.path.splitext(os.path.basename(path))[0])
    if os.path.exists(newname):
        return newname
    if not os.path.exists(location):
        mkdirs(location)
    with open(path,'rb') as fp:
        scanner = Scanner(path,fp)
        if scanner.readHeader():
            newname = scanner.writeContents(location)
            if check_md5:
                md5 = scanner.md5(newname)
                if scanner.data['data_md5'] != md5:
                    log(ERROR,'corrupt {}'.format(path))
                    os.remove(newname)
                    return None
    return newname

def unZip(dir, item, destination):
    with ZipFile(os.path.join(dir, item), 'r') as inzip:
        for info in inzip.infolist():
            if info.filename[-1] == '/':
                continue
            if info.filename.endswith('ldcc'):
                info.filename = os.path.basename(info.filename)
                log(INFO,'extracting: ' + str(info.filename))
                inzip.extract(info, destination)
                yield os.path.join(destination,info.filename)

def unZipAll(dir='.', filters=[''], location='.', cleanup=False, unwrap_files=False, cb=None):
    """

    :param dir: where the zipfile(s) are
    :param filter: string to search for to filter results
    :param location: where the media goes
    :param cleanup: what files to remove after
    :return:
    """
    for root, dirs, files in os.walk(dir):
        for name in files:
            if any([filter in name for filter in filters]) and name.endswith('zip'):
                files = unZip(root,name, location)
                for file in files:
                    if file.endswith('ldcc') and unwrap_files:
                        newname = unwrap(file, location=location)
                        if cb is not None:
                            cb(newname)
                        try:
                            if newname is not None and cleanup:
                                os.remove(file)
                        except OSError:
                            pass
                if cleanup:
                    try:
                        os.remove(root)
                    except OSError:
                        pass



#unZip(dir='/Volumes/TOSHIBA EXT/AIDA Corpora/LDC2018E52_AIDA_Scenario_1_Seedling_Corpus_Part_2/data/jpg/jpg')
#unZip(dir='/Volumes/TOSHIBA EXT/AIDA Corpora/LDC2018E01_AIDA_Seedling_Corpus_V1/data/mp4/mp4')