import shapefile
import dbf
import numpy as np
from math import pi, cos, sin, atan2

shp_reader = shapefile.Reader('data/merged_footprints_edgeidx.shp')
db = dbf.Table('data/merged_footprints_edgeidx.dbf')

shapes = shp_reader.shapes()

# open dbf file in write mode
with db:
    # iterate shape
    for idx, shape in enumerate(shapes):
        # get properties for current shape
        properties = db[idx]

        # initialize variables
        fid = properties['fid']
        daf = properties['daf']
        gebid = properties['gebid']
        dachneig = properties['dachneig']
        dachorient = properties['dachorient']
        
        # initialize some meta data
        points = shape.points
        length = len(points)
        edge = -1
        if dachorient == -1.0:
            dachorient = None

        print('process shape:', \
            'fid=', fid, \
            'rooftype=', daf, \
            'dachorient=', dachorient, \
            'clockwise=', shapefile.signed_area(points) > 0, \
            'vertex_count=', length)

        # if the roof orientation and inclination are given, search for edge index
        if dachneig and dachorient:
            idx = 0
            i = length - 1

            # process first edge index
            print('processing edge=', idx)
            x2 = points[0][0]
            x1 = points[1][0]
            y2 = points[0][1] * -1
            y1 = points[1][1] * -1
            dx = x2 - x1;
            dy = y2 - y1;

            # calculate the orientation of current edge
            dachorient_calc = atan2(dy, dx);

            # radians to degree
            dachorient_calc = dachorient_calc * 180 / pi + 180
            edge = idx

            print('edge (', \
                'id=', idx, \
                ', x1=', x1, \
                ', x2=', x2, \
                ', y1=', y1,
                ', y2=', y2, \
                ') orientation=' , dachorient_calc)

            # calculate differenz of roof orientation
            dachorient_diff = abs(dachorient - dachorient_calc)
            
            # start from beind and process until the second edge is reached
            while i > 1:
                idx = idx + 1
                print('processing edge=', idx)
                x1 = points[i][0]
                x2 = points[i-1][0]
                y1 = points[i][1] * -1
                y2 = points[i-1][1] * -1
                dx = x2 - x1;
                dy = y2 - y1;
                
                # calculate the orientation of current edge
                dachorient_calc = atan2(dy, dx);

                # radians to degree. Add 180 degrees: 90 degree for math to geodatic,
                # 90 degree for getting the angle of the normal
                dachorient_calc = dachorient_calc * 180 / pi + 180

                dachorient_diff_temp = abs(dachorient - dachorient_calc)

                # check if the current orientation differenz is lower then the stored
                if dachorient_diff_temp < dachorient_diff:
                    print('found better edge idx.', \
                        'new_edge=', idx, \
                        'old_edge=', edge, \
                        'new_dachorient_diff=', dachorient_diff_temp, \
                        'old_dachorient_diff', dachorient_diff)
                    # update stored orienation differenz
                    dachorient_diff = dachorient_diff_temp
                    # update edge idx
                    edge = idx

                print('edge (', \
                    'id=', idx, \
                    'x1=', x1, \
                    'x2=', x2, \
                    'y1=', y1,
                    'y2=', y2, \
                    ') orientation=' , dachorient_calc)

                i = i - 1
        # write the found edge index to the shapes dbf file.
        dbf.write(properties, edgeidx=edge)

        print('edge index for feature ', fid, ' is: ', edge)
