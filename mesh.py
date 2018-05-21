# mesh.py

from includes.positional_list import *

class Mesh:
    """A mesh convertor from obj to vtk with
        a triangularization functionality."""

    def __init__(self):
        self._datapoints = []
        self._faces = PositionalList()
        self._boundaries = [[None, None], [None, None], [None, None]]
        self._polygon_counts = dict()
        self._polygon_names = {3: 'Triangle', 4: 'Quadrilateral',
            5: 'Pentagon', 6: 'Hexagon', 7: 'Heptagon', 8: 'Octagon'
            , 9: 'Nonagon', 10: 'Decagon', 11: 'Undecagon', 12: 'Dodecagon'
            , 13: 'Tridecagon', 14: 'Tetradecagon', 15: 'Pentadecagon'
            , 16: 'Hexadecagon', 17: 'Heptadecagon', 18: 'Octadecagon'
            , 19: 'Enneadecagon'}

    def _calc_boundaries(self, vertex):
        self._init_boundries(vertex)
        for i in range(0, 3):
            if float(vertex[i]) < self._get_min(i):
                self._set_min(i, float(vertex[i]))
            if float(vertex[i]) > self._get_max(i):
                self._set_max(i, float(vertex[i]))

    def _translate_polygons(self, ):
        output, cursor_positon = '', 0
        for polygon in self._polygon_counts:
            if not cursor_positon & 1 and cursor_positon > 0:
                output += '||\n'
            if 3 <= polygon < 20:
                output += '||{0:^18}:{1:^18}'.format\
                    (self._polygon_names[polygon] + 's'
                     ,self._polygon_counts[polygon])
            if polygon >= 20:
                output += '||{0:^18}:{1:^18}'.format\
                    (str(self._polygon_counts[polygon]) + '-gons'
                     ,self._polygon_counts[polygon])
            cursor_positon += 1
        if cursor_positon & 1:
            output += '{0:>42}'.format('||\n')
        else:
            output += '||\n'
        return output

    def _get_max(self, direction):
        return self._boundaries[direction][0]

    def _get_min(self, direction):
        return self._boundaries[direction][1]

    def _set_max(self, direction, magnitude):
        self._boundaries[direction][0] = magnitude

    def _set_min(self, direction, magnitude):
        self._boundaries[direction][1] = magnitude

    def _init_boundries(self, vertex):
        if self._get_max(0) is None:
            self._set_max(0, float(vertex[0]))
            self._set_max(1, float(vertex[1]))
            self._set_max(2, float(vertex[2]))
            self._set_min(0, float(vertex[0]))
            self._set_min(1, float(vertex[1]))
            self._set_min(2, float(vertex[2]))

    def _get_polygon_counts(self):
        return len(self._faces)

    def _get_dataset_size(self):
        return len(self._datapoints)

    # ------------------------------ public behaviors -------------------------

    def read(self, filename):
        """ Reads and stores an obj file to memory. """
        with open(filename, 'r') as mesh:
            for line in mesh:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                line = line.split()

                if line[0] == 'v':  # reads vectors
                    vertex = tuple(line[1:])
                    self._datapoints += vertex,
                    self._calc_boundaries(vertex)

                elif line[0] == 'f':  # reads faces
                    face = [int(vertex) - 1 for vertex in line[1:]] #index 1to0
                    self._polygon_counts[len(face)] =\
                        self._polygon_counts.setdefault(len(face), 0) + 1
                    self._faces.add_last(face)

    def triangularize(self):
        """ Converts all types of polygon faces to triangles. """
        position = self._faces.first()
        while position:
            face = position.element()

            if len(face) > 3:
                for j in range(1, len(face) - 1):
                    new_element = []
                    new_element += [face[0]]
                    new_element += face[j:j + 2]
                    self._faces.add_before(position, new_element)
                    self._polygon_counts.setdefault(3, 0)
                    self._polygon_counts[3] += 1
                self._polygon_counts[len(face)] -= 1

                position_holder = self._faces.after(position)
                self._faces.delete(position)
                position = position_holder
            else:
                position = self._faces.after(position)
        del_list = [polygon for polygon, counts in\
                    self._polygon_counts.items() if counts == 0]
        for polygon in del_list:
            del self._polygon_counts[polygon]

    def write_wtk(self, filename):
        """ Writes the mesh object to a vtk file. """
        with open(filename, 'w', newline='\n') as mesh:
            mesh.write('# vtk DataFile Version 3.0\n')
            mesh.write('converted from '+filename[:-3]+'obj\n')
            mesh.write('ASCII\nDATASET POLYDATA\n')
            mesh.write('POINTS {0} float\n'.format(self._get_dataset_size()))

            for vertex in self._datapoints:  # writes vertices
                mesh.write(' '.join(vertex) + '\n')
            mesh.write('\n')

            size = sum(polygon * counts for polygon,\
                            counts in self._polygon_counts.items())
            size += self._get_polygon_counts()
            mesh.write('POLYGONS {0} {1}\n'.format\
                           (self._get_polygon_counts(), size))

            for face in self._faces:
                mesh.write('{0} '.format(len(face)))
                mesh.write(' '.join\
                           (str(component) for component in face) + '\n')

    def __repr__(self):
        output = '{:^80}\n'.format('_' * 76)
        output += '||{0:^17}:{1:^17}'.format\
            ('Total Vertices', self._get_dataset_size())
        output += '|{0:^29}:{1:^10}||\n'.format\
            ('Total Polygon Faces', self._get_polygon_counts())
        output += '||{:<76}||\n'.format('-' * 76)

        output += '||{:^76}||\n'.format('Polygon Faces')
        output += '||{:<76}||\n'.format('-' * 76)
        output += self._translate_polygons()
        output += '||{:<76}||\n'.format('-' * 76)

        output += '||{:^76}||\n'.format('Boundaries')
        output += '||{:<76}||\n'.format('-' * 76)
        output += '||{0:^18}|{1:>13}: {2:<13}'.format\
            ('X', 'Minimum ', self._get_min(0))
        output += '|{0:>13}: {1:<13}||\n'.format('Maximum ', self._get_max(0))
        output += '||{0:^18}|{1:>13}: {2:<13}'.format\
            ('Y', 'Minimum ', self._get_min(1))
        output += '|{0:>13}: {1:<13}||\n'.format('Maximum ', self._get_max(1))
        output += '||{0:^18}|{1:>13}: {2:<13}'.format\
            ('Z', 'Minimum ', self._get_min(2))
        output += '|{0:>13}: {1:<13}||\n'.format('Maximum ', self._get_max(2))
        output += '||{:^76}||\n'.format('_' * 74)

        return output
