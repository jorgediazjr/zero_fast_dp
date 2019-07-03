import os
import sys

if sys.version_info < (3, 0):
    version = 2


class _writer:
    '''A specialist class to write to the screen and fast_dp.log.'''

    def __init__(self):
        self._fout = None
        self._afout = None
        self._filename = 'fast_dp.log'
        self._afilename = None
        self._afilepath = None
        self._afileprefix = None
        return

    def set_filename(self, filename):
        self._filename = filename

    def set_afilename(self, afilename):
        self._afilename = afilename

    def set_afilepath(self, afilepath):
        self._afilepath = afilepath

    def get_afilepath(self):
        return self._afilepath

    def set_afileprefix(self, afileprefix):
        self._afileprefix = afileprefix

    def get_afileprefix(self):
        return self._afileprefix

    def __del__(self):
        if self._fout:
            self._fout.close()
        self._fout = None
        if self._afout:
            self._afout.close()
        self._afout = None
        self._afilename = None
        self._afileprefix = None
        return

    def __call__(self, record):
        self.write(record)

    def write(self, record):
        if not self._fout:
            self._fout = open(self._filename, 'w')
        if version == 2: 
            try:
                self._fout.write('%s\n' % record)
            except:
                pass
        else:
            self._fout.write('{}\n'.format(record))

        if version == 2:
            try:
                print record
            except:
                pass
        else:
            print(record)

        if self._afilename:
            try:
                if not self._afout:
                    self._afout = open(self._afilename, 'w')
                if version == 2: 
                    try:
                        self._afout.write('%s\n' % record)
                    except:
                        pass
                else:
                    self._afout.write('{}\n'.format(record))
            except:
                if version == 2:
                    try:
                        print self._afilename+' not available for writing'
                        self._afilename = None
                    except:
                        pass
                else:
                    print(self._afilename+' not available for writing')
                    self._afilename = None
        return

write = _writer()

def set_filename(filename):
    write.set_filename(filename)

def set_afilename(afilename):
    write.set_afilename(afilename)

def set_afilepath(afilepath):
    write.set_afilepath(afilepath)

def get_afilepath():
    return write.get_afilepath()

def set_afileprefix(afileprefix):
    write.set_afileprefix(afileprefix)

def get_afileprefix():
    return write.get_afileprefix()
