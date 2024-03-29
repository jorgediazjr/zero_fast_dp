import time
import os
from logger import write

from image_names import image2template_directory, find_matching_images, \
    template_directory_number2image

from run_job import run_job

import sys

if sys.version_info < (3, 0):
    version = 2


def check_file_readable(filename):
    '''Check that the file filename exists and that it can be read. Returns
    only if everything is OK.'''

    if not os.path.exists(filename):
        if version == 2:
            try:
                raise RuntimeError, 'file %s not found' % filename
            except:
                pass
        else:
            raise RuntimeError('file {} not found'.format(filename))
    if not os.access(filename, os.R_OK):
        if version == 2:
            try:
                raise RuntimeError, 'file %s not readable' % filename
            except:
                pass
        else:
            raise RuntimeError('file {} not readable'.format(filename))

    return

def get_dectris_serial_no(record):
    if not 'S/N' in record:
        return '0'
    tokens = record.split()
    return tokens[tokens.index('S/N') + 1]

__hdf5_lib = ''
__eiger_lib = ''


def find_hdf5_lib():
    global __hdf5_lib
    global __eiger_lib
    if __eiger_lib:
        return __eiger_lib
    if __hdf5_lib:
        return __hdf5_lib
    for d in os.environ['PATH'].split(os.pathsep):
        if os.path.isfile(os.path.join(d, 'eiger2cbf-so-worker')):
            if os.path.isfile(os.path.join(d, 'eiger2cbf.so')):
                if version == 2:
                    try:
                        __eiger_lib ='LIB=%s\n' % os.path.join(d,'eiger2cbf.so')
                    except:
                        pass
                else:
                    __eiger_lib ='LIB={}\n'.format(os.path.join(d,'eiger2cbf.so'))
                return __eiger_lib
            elif  os.path.isfile(os.path.join(d, '..','lib','eiger2cbf.so')):
                if version == 2:
                    try:
                        __eiger_lib ='LIB=%s\n' % os.path.join(d,'..','lib','eiger2cbf.so')
                    except:
                        pass
                else:
                    __eiger_lib ='LIB={}\n'.format(os.path.join(d,'..','lib','eiger2cbf.so'))
                return __eiger_lib
    for d in os.environ['PATH'].split(os.pathsep):
        if os.path.isfile(os.path.join(d, 'xds_par')):
            if version == 2:
                try:
                    __hdf5_lib = 'LIB=%s\n' % os.path.join(d,'dectris-neggia.so')
                except:
                    pass
            else:
                __hdf5_lib = 'LIB={}\n'.format(os.path.join(d,'dectris-neggia.so'))
            return __hdf5_lib
    return ''

try:
    import bz2
except: # intentional
    bz2 = None

try:
    import gzip
except: # intentional
    gzip = None


def is_bz2(filename):
    if not '.bz2' in filename[-4:]:
        return False
    return 'BZh' in open(filename, 'rb').read(3)


def is_gzip(filename):
    if not '.gz' in filename[-3:]:
        return False
    magic = open(filename, 'rb').read(2)
    return ord(magic[0]) == 0x1f and ord(magic[1]) == 0x8b


def open_file(filename, mode='rb', url=False):
    if is_bz2(filename):
        if bz2 is None:
            if version == 2:
                try:
                    raise RuntimeError, 'bz2 file provided without bz2 module'
                except:
                    pass
            else:
                raise RuntimeError('bz2 file provided without bz2 module')

        fh_func = lambda: bz2.BZ2File(filename, mode)
    elif is_gzip(filename):
        if gzip is None:
            if version == 2:
                try:
                    raise RuntimeError, 'gz file provided without gzip module'
                except:
                    pass
            else:
                raise RuntimeError('gz file provided without gzip module')
        fh_func = lambda: gzip.GzipFile(filename, mode)
    else:
        fh_func = lambda: open(filename, mode)
    return fh_func()


def failover_hdf5(hdf5_file):
    from dxtbx.serialize import xds
    from dxtbx.datablock import DataBlockFactory
    import time
    t0 = time.time()
    db = DataBlockFactory.from_filenames([hdf5_file])[0]
    sweep = db.extract_sweeps()[0]
    t1 = time.time()
    if version == 2:
        try:
            write('Reading %s took %.2fs' % (hdf5_file, t1-t0))
        except:
            pass
    else:
        write('Reading {} took {:.2f}s'.format(hdf5_file, t1-t0))
    d = sweep.get_detector()
    s = sweep.get_scan()
    g = sweep.get_goniometer()
    b = sweep.get_beam()

    # returns slow, fast, convention here is reverse
    size = tuple(reversed(d[0].get_image_size()))

    size0k_to_class = {1:'eiger 1M',
                       2:'eiger 4M',
                       3:'eiger 9M',
                       4:'eiger 16M'}

    header = {}

    header['detector_class'] = size0k_to_class[int(size[0]/1000)]
    header['detector'] = size0k_to_class[int(size[0]/1000)].upper().replace(
        ' ', '_')
    header['size'] = size
    header['serial_number'] = 0
    header['extra_text'] = find_hdf5_lib()

    header['phi_start'] = s.get_angle_from_image_index(1.0, deg=True)
    header['phi_end'] = s.get_angle_from_image_index(2.0, deg=True)
    header['phi_width'] = header['phi_end'] - header['phi_start']
    header['oscillation'] = header['phi_start'], header['phi_width']
    header['exposure_time'] = s.get_exposure_times()[0]
    header['oscillation_axis'] = 'Omega_I_guess'
    header['distance'] = d[0].get_distance()
    header['wavelength'] = b.get_wavelength()
    header['pixel'] = d[0].get_pixel_size()
    header['saturation'] = d[0].get_trusted_range()[1]
    header['sensor'] = d[0].get_thickness()
    header['beam'] = d[0].get_beam_centre(b.get_s0())
    images = s.get_image_range()
    directory, template = os.path.split(hdf5_file)
    header['directory'] = directory
    header['template'] = template.replace('master', '??????')
    header['start'] = images[0]
    header['end'] = images[1]
    header['matching'] = range(images[0], images[1]+1)
    return header

def failover_cbf(cbf_file):
    '''CBF files from the latest update to the PILATUS detector cause a
    segmentation fault in diffdump. This is a workaround.'''

    header = {}

    header['two_theta'] = 0.0

    for record in open_file(cbf_file):
        if '_array_data.data' in record:
            break

        if 'EIGER 1M' in record.upper():
            header['detector_class'] = 'eiger 1M'
            header['detector'] = 'dectris'
            header['size'] = (1065, 1030)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'EIGER 4M' in record.upper():
            header['detector_class'] = 'eiger 4M'
            header['detector'] = 'dectris'
            header['size'] = (2176, 2070)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'EIGER 9M' in record.upper():
            header['detector_class'] = 'eiger 9M'
            header['detector'] = 'dectris'
            header['size'] = (3269, 3110)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'EIGER 16M' in record.upper():
            header['detector_class'] = 'eiger 16M'
            header['detector'] = 'dectris'
            header['size'] = (4371, 4150)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS 2M' in record:
            header['detector_class'] = 'pilatus 2M'
            header['detector'] = 'dectris'
            header['size'] = (1679, 1475)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS 6M' in record:
            header['detector_class'] = 'pilatus 6M'
            header['detector'] = 'dectris'
            header['size'] = (2527, 2463)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS3 6M' in record:
            header['detector_class'] = 'pilatus 6M'
            header['detector'] = 'dectris'
            header['size'] = (2527, 2463)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS 12M' in record:
            header['detector_class'] = 'pilatus 12M'
            header['detector'] = 'dectris'
            header['size'] = (5071, 2463)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'Detector: ADSC HF-4M' in record:
            header['detector_class'] = 'adsc 4M'
            header['detector'] = 'adsc-pad'
            header['size'] = (2290, 2100)
            header['serial_number'] = record.replace(',', '').split()[-1]
            continue
        
        if 'Start_angle' in record:
            header['phi_start'] = float(record.split()[-2])
            continue

        if 'Angle_increment' in record:
            header['phi_width'] = float(record.split()[-2])
            header['phi_end'] = header['phi_start'] + header['phi_width']
            header['oscillation'] = header['phi_start'], header['phi_width']
            continue

        if 'Exposure_period' in record:
            header['exposure_time'] = float(record.split()[-2])
            continue

        if 'Detector_distance' in record:
            header['distance'] = 1000 * float(record.split()[2])
            continue

        if 'Oscillation_axis' in record:
            header['oscillation_axis'] = record.split('axis')[-1].strip()

        if 'Wavelength' in record:
            header['wavelength'] = float(record.split()[-2])
            continue

        if 'Pixel_size' in record:
            header['pixel'] = 1000 * float(record.split()[2]), \
                              1000 * float(record.split()[5])
            continue

        if 'Count_cutoff' in record:
            header['saturation'] = int(record.split()[2])

        if 'Silicon sensor' in record:
            header['sensor'] = 1000 * float(record.split()[4])

        if 'Beam_xy' in record:
            beam_pixels = map(float, record.replace('(', '').replace(
                ')', '').replace(',', '').split()[2:4])

            # for CBF images need to swap these to put in XDS mosflm
            # coordinate frame...
            header['beam'] = beam_pixels[0] * header['pixel'][0], \
                             beam_pixels[1] * header['pixel'][1]

            continue

        # try to get the date etc. literally.

        try:
            datestring = record.split()[-1].split('.')[0]
            format = '%Y-%b-%dT%H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except:
            pass

        try:
            datestring = record.split()[-1].split('.')[0]
            format = '%Y-%m-%dT%H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except:
            pass

        try:
            datestring = record.replace('#', '').strip().split('.')[0]
            format = '%Y/%b/%d %H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except:
            pass

    # cope with vertical goniometer on I24 @ DLS from 2015/1/1
    # and possible alternative horizontal gonio if +FAST
    if header.get('serial_number', '0') == '60-0119' and \
            int(header['date'].split()[-1]) >= 2015:
        if '+FAST' in header.get('oscillation_axis', ''):
            header['goniometer_is_vertical'] = False
        else:
            header['goniometer_is_vertical'] = True

    else:
        header['goniometer_is_vertical'] = False

    return header

def read_image_metadata(image):
    '''Read the image header and send back the resulting metadata in a
    dictionary.'''

    assert(os.path.exists(image))

    if image.endswith('.h5'):
        assert 'master' in image
        return failover_hdf5(image)

    # FIXME also check that the file can also be read - assert is acceptable,
    # also use the first image in the wedge to get the frame metadata

    template, directory = image2template_directory(image)

    matching = find_matching_images(template, directory)
    image = template_directory_number2image(template, directory, min(matching))

    # work around (preempt) diffdump failure with the new 2M instrument
    # FIXME may also need to do this for the new 6M instrument which is
    # incoming...

    try:
        if '.cbf' in image:
            metadata = failover_cbf(image)

            assert(metadata['detector_class'] in \
                   ['pilatus 2M', 'pilatus 6M', 'pilatus 12M',
                    'eiger 1M', 'eiger 4M', 'eiger 9M', 'eiger 16M',
                    'adsc 4M'])

            if metadata['detector_class'] == 'pilatus 2M':
                metadata['detector'] = 'PILATUS_2M'
            elif metadata['detector_class'] == 'pilatus 12M':
                metadata['detector'] = 'PILATUS_12M'
            elif metadata['detector_class'] == 'eiger 1M':
                metadata['detector'] = 'EIGER_1M'
            elif metadata['detector_class'] == 'eiger 4M':
                metadata['detector'] = 'EIGER_4M'
            elif metadata['detector_class'] == 'eiger 9M':
                metadata['detector'] = 'EIGER_9M'
            elif metadata['detector_class'] == 'eiger 16M':
                metadata['detector'] = 'EIGER_16M'
            elif metadata['detector_class'] == 'adsc 4M':
                metadata['detector'] = 'ADSC_4M'
            else:
                metadata['detector'] = 'PILATUS_6M'

            # handle I24 @ DLS vertical goniometer from 2015/1/1
            if metadata['goniometer_is_vertical']:
                metadata['detector'] = '%sV' % metadata['detector']

            metadata['directory'] = directory
            metadata['template'] = template
            metadata['start'] = min(matching)
            metadata['end'] = max(matching)

            metadata['matching'] = matching

            return metadata

    except ValueError as e:
        pass

    # MAR CCD images record the beam centre in pixels...

    diffdump_output = run_job('diffdump', arguments = [image])

    metadata = {}

    for record in diffdump_output:
        if 'Wavelength' in record:
            wavelength = float(record.split()[-2])
            metadata['wavelength'] = wavelength

        elif 'Beam center' in record:
            x = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[3])
            y = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[4])
            metadata['beam'] = x, y

        elif 'Image Size' in record:
            x = int(record.replace('(', ' ').replace(
                'px', ' ').replace(',', ' ').split()[3])
            y = int(record.replace('(', ' ').replace(
                'px', ' ').replace(',', ' ').split()[4])
            metadata['size'] = x, y

        elif 'Pixel Size' in record:
            x = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[3])
            y = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[4])
            metadata['pixel'] = x, y

        elif 'Distance' in record:
            distance = float(record.split()[-2])
            metadata['distance'] = distance

        elif 'Exposure time' in record:
            metadata['exposure_time'] = float(record.split()[-2])

        elif 'Oscillation' in record:
            phi_start = float(record.split()[3])
            phi_end = float(record.split()[5])
            phi_width = phi_end - phi_start

            if phi_width > 360.0:
                phi_width -= 360.0

            metadata['phi_start'] = phi_start
            metadata['phi_width'] = phi_width
            metadata['phi_end'] = phi_end
            metadata['oscillation'] = phi_start, phi_width

        elif 'Manufacturer' in record or 'Image type' in record:
            detector = record.split()[-1]
            if detector == 'ADSC':
                metadata['detector'] = 'ADSC'
            elif detector == 'MAR':
                metadata['detector'] = 'MARCCD'
            elif detector == 'DECTRIS':
                metadata['detector'] = 'PILATUS_6M'
            elif detector == 'RIGAKU':
                metadata['detector'] = 'RIGAKU'
            else:
                if version == 2:
                    try:
                        raise RuntimeError, 'detector %s not yet supported' % \
                              detector
                    except:
                        pass
                else:
                    raise RuntimeError('detector {} not yet supported'.format(
                          detector))

    if (metadata['detector'] == 'PILATUS_6M') and \
       (metadata['size'] == (1679, 1475)):
        metadata['detector'] = 'PILATUS_2M'

    # now compute the filename template and what have you, and also
    # verify that the results stored make sense, particularly w.r.t.
    # the beam centre, which may be stored in pixels not mm.

    template, directory = image2template_directory(image)

    # MAR CCD images record the beam centre in pixels...

    if metadata['detector'] == 'MARCCD':
        metadata['beam'] = (metadata['beam'][0] * metadata['pixel'][0],
                            metadata['beam'][1] * metadata['pixel'][1])

    metadata['directory'] = directory
    metadata['template'] = template
    metadata['start'] = min(matching)
    metadata['end'] = max(matching)
    metadata['matching'] = matching

    return metadata

# FIXME add some unit tests in here...

if __name__ == '__main__':
    md = read_image_metadata(sys.argv[1])
    for name in sorted(md):
        if version == 2:
            try:
                print name, md[name]
            except:
                pass
        else:
            print(name, md[name])
