# project2.py

from mesh import *

import sys
import os.path

if __name__ == '__main__':
    try:
        imgfilepath = sys.argv[1]
        imgbasename = os.path.basename(imgfilepath)
        imgtype = imgbasename[-3:]

        if imgtype == 'obj':
            mesh = Mesh()
        else:
            raise ValueError('Unknown file extension.')

        # use -c to have a clear result
        if '-c' in sys.argv:
            os.system('cls' if os.name == 'nt' else 'clear')
        print('Reading ' + imgbasename + ' ...')
        mesh.read(imgfilepath)
        print('Reading has been finished.')
        print(mesh)
        print('Triangularizing ...')
        mesh.triangularize()
        print('Triangularization has been finished.')
        print(mesh)
        print('Converting and writing with VTK format ...')
        mesh.write_wtk(imgbasename[:-4]+'.vtk')
        print(imgbasename[:-4]+'.vtk has has been saved.')

    except Exception as e:
        print('Exception raised:')
        print(e)
