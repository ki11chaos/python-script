import os.path
from xml.dom import minidom
import collections
import re
import shutil
import sys


def clean_data(data):
    """clean the part not the number, '.' or '-'"""
    pattern = re.compile('[0-9.-]+')
    if isinstance(data, str):
        return list(map(lambda x: float(x), pattern.findall(data)))
    else:
        return [list(map(lambda x: float(x), pattern.findall(i))) for i in data]


def read_pre_input():
    with open('pre-input', 'r', encoding='utf-8') as f:
        info = [re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]+', '', line) for line in f.readlines()]
    pattern = re.compile(r'([\w\s]+)=([\w\s/_.-]+)')
    pattern2 = re.compile(r'([\w\s]+)=([\w\s/|.-]+)')
    attributes = collections.defaultdict(list)
    for i in info:
        if '|' in i and '#' not in i:
            group1, *group2 = pattern2.match(i).groups()
            attributes[group1.strip()] = group2[0].strip()
        elif pattern.match(i) is not None:  # that means '#' or '!' in <pre-input> file represent annotation
            group1, *group2 = pattern.match(i).groups()
            attributes[group1.strip()] = group2[0].strip()
    return attributes


def read_k_path():
    with open('k-path', 'r', encoding='utf-8') as f:
        info = [re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]+', '', line) for line in f.readlines()]
    pattern = re.compile(r'([\w\s]+)=([\d\s.+-]+)')
    k_path = []
    for i in info:
        if pattern.match(i) is not None:
            group1, group2 = pattern.match(i).groups()
            k_path.append([group1.strip(), group2.strip()])
    return k_path


def read_input_xml(node_name):
    """
    input.xml for xs (TDDFT, rt-TDDFT),
    The reason why operate 'r' and 'w' <input.xml> first: Remove Newlines, Spaces, Tabs in *.xml
    which useful when write xml in some formats again.
    """
    dom = minidom.parse('input.xml')  # To make sure the initial *.xml format is standardized
    with open('input.xml', 'w', encoding='utf-8') as f:
        dom.writexml(f, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    with open('input.xml', 'r', encoding='utf-8') as f:
        info = [re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]+', '', line) for line in f.readlines()]
        tmp = [i.strip() for i in info]
    with open('input.xml', 'w', encoding='utf-8') as f:
        f.writelines(tmp)
    dom = minidom.parse('input.xml')
    if node_name == 'input':
        node = dom.getElementsByTagName('input')[0]
        return dom, node


class InputXml:
    def __init__(self):
        self.dom = minidom.Document()
        self.root_node = None
        self.sub_node = None  # The 'default_setting' method may need it when sub-node occur in one mode.
        self.num = 0  # Control how to use 'add_attributes' method when laser occur.
        self.filter_rule = r'[-\w.]+'
        self.attributes = read_pre_input()  # a dict

    def default_setting(self, node, mode):
        """
        The default settings fall into two categories:
        No.1 When the <pre-input> is not containing the key, ignoring it, otherwise, writing it.
        No.2 When the the key is not in the <pre-input>, giving a default value,
        The reason why we do No.1 is that some of parameters are not necessarily specified, but when they occur in
        <pre-input> file, adding them to attributes.
        :param node: can be any node exist in InputXml.
        :param mode: 1, 2, 3, 4, 5 modes.
        :return:node
        """
        if mode in ['1', '6']:  # ground state mode default setting
            if self.attributes['rgkmax']:
                node.setAttribute('rgkmax', self.attributes['rgkmax'])
            if self.attributes['do']:
                node.setAttribute('do', self.attributes['do'])
            if self.attributes['nempty']:
                node.setAttribute('nempty', self.attributes['nempty'])
            if not self.attributes['epsengy']:
                node.setAttribute('epsengy', '1.0d-6')
            if not self.attributes['outputlevel']:
                node.setAttribute('outputlevel', 'normal')
            if self.sub_node:
                if not self.attributes['excoeff']:
                    self.sub_node.setAttribute('excoeff', '0.25')
                if not self.attributes['xctype']:
                    node.setAttribute('xctype', 'HYB_PBE0')
                if self.attributes['omega']:
                    self.sub_node.setAttribute('omega', self.attributes['omega'])
            return node
        elif mode in ['2', '3']:  # dos mode default setting
            return node
        elif mode == '4':  # rt-TDDFT
            if not self.attributes['xstype']:
                node.setAttribute('xstype', 'RT-TDDFT')
            if self.attributes['rgkmax']:
                node.setAttribute('rgkmax', self.attributes['rgkmax'])  # eg, ignoring
            if not self.attributes['nosym']:
                node.setAttribute('nosym', 'true')  # eg, giving a default value
            if not self.attributes['reducek']:
                node.setAttribute('reducek', 'false')
            if self.sub_node:
                if not self.attributes['propagator']:
                    self.sub_node.setAttribute('propagator', 'AETRS')
                if not self.attributes['printTimingGeneral']:
                    self.sub_node.setAttribute('printTimingGeneral', 'true')
                if not self.attributes['printAfterIterations']:
                    self.sub_node.setAttribute('printAfterIterations', '10')
                if self.attributes['calculateNExcitedElectrons']:
                    self.sub_node.setAttribute('calculateNExcitedElectrons',
                                               self.attributes['calculateNExcitedElectrons'])
        elif mode == '5':  # TDDFT
            if self.sub_node:
                if self.num == 0:
                    if not self.attributes['fxctype']:
                        self.sub_node.setAttribute('fxctype', 'RPA')
                    if self.attributes['intraband']:
                        self.sub_node.setAttribute('intraband', self.attributes['intraband'])
                    self.num += 1
                elif self.num == 1:
                    if not self.attributes['points']:
                        self.sub_node.setAttribute('points', '1000')
            else:
                if not self.attributes['xstype']:
                    node.setAttribute('xstype', 'TDDFT')
                if self.attributes['rgkmax']:
                    node.setAttribute('rgkmax', self.attributes['rgkmax'])
                if not self.attributes['tevout']:
                    node.setAttribute('tevout', 'true')
        self.sub_node = None

    def add_attributes(self, node, attributes_):
        for attribute in attributes_:  # Whether the key is exists in <pre-input>, write it.
            if self.num != 0 and self.attributes['laser']:
                try:
                    node.setAttribute(attribute, self.split_laser_param(attribute)[self.num - 1])
                except IndexError:
                    print('------------------------------------------------------------------------------------------')
                    print('ERROR!!\nPlease check your <input.xml> file, the parameter "{}" may lost.'.format(attribute))
            else:
                node.setAttribute(attribute, self.attributes[attribute])

    @staticmethod
    def add_k_path(node, k_point):
        node.setAttribute('coord', k_point[-1])
        node.setAttribute('label', k_point[0])

    def creat_root(self):
        self.root_node = self.dom.createElement('input')
        self.dom.appendChild(self.root_node)

    def creat_title(self):
        title_node = self.dom.createElement('title')  # creating child node for root_node
        self.root_node.appendChild(title_node)  # add title_node to root_node as a child node
        title_text_node = self.dom.createTextNode(self.attributes['title'])  # creating text node for title_node
        title_node.appendChild(title_text_node)  # add text for father node

    def ground_state(self, mode):
        ground_node = self.dom.createElement('groundstate')
        self.root_node.appendChild(ground_node)
        self.add_attributes(ground_node, ['ngridk', 'outputlevel', 'xctype', 'epsengy'])
        if mode == '6':
            hybrid_node = self.dom.createElement('Hybrid')
            ground_node.appendChild(hybrid_node)
            self.add_attributes(hybrid_node, ['excoeff'])
            self.sub_node = hybrid_node
        self.default_setting(ground_node, mode)
        return ground_node

    def add_atoms(self, species_node, coords):
        for coord in coords:
            atom_node = self.dom.createElement('atom')
            species_node.appendChild(atom_node)
            atom_node.setAttribute('coord', '   '.join(map(lambda x: str(x), coord)))

    def structure(self):
        poscar_info = POSCARInfo()
        elements, number = poscar_info.elements_from_poscar()
        lattice_constant, lattice_vectors = poscar_info.lattice_from_poscar()
        coords = poscar_info.coordinates_from_poscar()
        # creat structure node for input
        structure_node = self.dom.createElement('structure')
        self.root_node.appendChild(structure_node)
        structure_node.setAttribute('speciespath', self.attributes['speciespath'])
        # creat child node crystal of father node structure
        crystal_node = self.dom.createElement('crystal')
        structure_node.appendChild(crystal_node)
        crystal_node.setAttribute('scale', str(lattice_constant))
        for i, vector in enumerate(lattice_vectors):  # creat lattice vector node
            basevect_node = self.dom.createElement('basevect')
            crystal_node.appendChild(basevect_node)
            basevect_text_node = self.dom.createTextNode('   '.join(map(lambda x: str(x), vector)))
            basevect_node.appendChild(basevect_text_node)
        # creat child node species of father node structure
        rmt = self.split_laser_param('rmt')  # type format in pre-input: "rmt = 2.1 4.05 None" = "rmt = 2.1 4.05"
        for i, species in enumerate(elements):                         # "rmt = None 2.1 None" = "rmt = None 2.1"
            species_node = self.dom.createElement('species')
            structure_node.appendChild(species_node)
            species_node.setAttribute('speciesfile', '{}.xml'.format(species))
            if i < len(rmt) and (rmt[i] != 'None'):
                species_node.setAttribute('rmt', '{}'.format(rmt[i]))
            #  add atoms child node of species node
            self.add_atoms(species_node, coords[sum(number[:i]):sum(number[:i + 1])])

    def coord_relax(self):
        relax_node = self.dom.createElement('relax')
        self.root_node.appendChild(relax_node)
        method = self.attributes['method']
        if method:
            self.add_attributes(relax_node, ['method'])
            if method == 'bfgs':
                self.add_attributes(relax_node, ['taubfgs'])
            elif method in ['newton', 'harmonic']:
                self.add_attributes(relax_node, ['taunewton'])
            else:
                print('ERROR!!!\nYou may type a wrong method "{}" for ion coordinates relax!'.format(method))
                print('==============================================================================================')
                sys.exit(1)
        else:
            self.add_attributes(relax_node, ['taubfgs'])

    def properties_get(self, mode):
        if mode in ['2', '3']:
            pass
        else:
            self.dom, self.root_node = read_input_xml('input')
        properties_node = self.dom.createElement('properties')
        self.root_node.appendChild(properties_node)
        if mode == '2':  # creat dos root and it's child node
            dos_node = self.dom.createElement('dos')
            properties_node.appendChild(dos_node)
            self.add_attributes(dos_node, ['nsmdos', 'ngrdos', 'nwdos', 'winddos'])
            self.default_setting(dos_node, mode)
            return dos_node
        if mode == '3':  # creat band structure node and it's child node
            band_structure_node = self.dom.createElement('bandstructure')
            properties_node.appendChild(band_structure_node)
            # creat plot1d node for band_structure node as child node
            plot_1d_node = self.dom.createElement('plot1d')
            band_structure_node.appendChild(plot_1d_node)
            # creat k-points path node
            path_node = self.dom.createElement('path')
            plot_1d_node.appendChild(path_node)
            path_node.setAttribute('steps', self.attributes['steps'])
            # creat k-point node
            k_path = read_k_path()  # a list contain k-points names and coordinates
            for i in k_path:
                point_node = self.dom.createElement('point')
                path_node.appendChild(point_node)
                self.add_k_path(point_node, i)
        if mode == '8':
            ground_node = self.dom.getElementsByTagName('groundstate')[0]
            self.add_attributes(ground_node, ['do'])
            self.root_node.appendChild(properties_node)
            moment_matrix_node = self.dom.createElement('momentummatrix')
            properties_node.appendChild(moment_matrix_node)
            shg_node = self.dom.createElement('shg')
            properties_node.appendChild(shg_node)
            self.add_attributes(shg_node, ['wmax', 'wgrid', 'swidth', 'etol', 'tevout'])
            chi_component_node = self.dom.createElement('chicomp')
            shg_node.appendChild(chi_component_node)
            chi_text_node = self.dom.createTextNode(self.attributes['chicomp'])
            chi_component_node.appendChild(chi_text_node)

    def laser(self, laser_node, laser):
        if laser == 'trapCos':
            trap_cos_node = self.dom.createElement('trapCos')
            laser_node.appendChild(trap_cos_node)
            self.add_attributes(trap_cos_node, ['amplitude', 'omega', 'phase', 't0', 'riseTime', 'width', 'direction'])
        elif laser == 'kick':
            kick_node = self.dom.createElement('kick')
            laser_node.appendChild(kick_node)
            self.add_attributes(kick_node, ['amplitude', 't0', 'width', 'direction'])
        elif laser == 'sinSq':
            sin_sq_node = self.dom.createElement('sinSq')
            laser_node.appendChild(sin_sq_node)
            self.add_attributes(sin_sq_node, ['amplitude', 'omega', 'phase', 't0', 'pulseLength', 'direction'])

    def split_laser_param(self, param):
        """
        The default filter rules are given, but when multiple calls happened,
        it should be clearly given by yourself.
        :param param, key of self.attributes
        """
        pattern = re.compile(self.filter_rule)
        return pattern.findall(str(self.attributes[param]))

    def excited_states(self, mode):
        self.dom, self.root_node = read_input_xml('input')
        ground_node = self.dom.getElementsByTagName('groundstate')[0]
        self.add_attributes(ground_node, ['do'])
        xs_node = self.dom.createElement('xs')
        self.root_node.appendChild(xs_node)
        self.add_attributes(xs_node, ['xstype', 'ngridk', 'vkloff', 'nempty'])
        if mode == '4':  # rt-TDDFT
            self.add_attributes(xs_node, ['nosym', 'reducek'])
            rt_tddft_node = self.dom.createElement('realTimeTDDFT')
            xs_node.appendChild(rt_tddft_node)
            self.add_attributes(rt_tddft_node, ['propagator', 'timeStep', 'endTime', 'printAfterIterations'])
            self.sub_node = rt_tddft_node
            self.default_setting(xs_node, mode)

            laser_node = self.dom.createElement('laser')
            rt_tddft_node.appendChild(laser_node)
            for self.num, laser in enumerate(self.split_laser_param('laser'), 1):
                self.laser(laser_node, laser)
            self.num = 0
        if mode == '5':  # TDDFT
            self.add_attributes(xs_node, ['gqmax', 'broad', 'tevout'])
            self.default_setting(xs_node, mode)

            tddft_node = self.dom.createElement('tddft')
            xs_node.appendChild(tddft_node)
            self.add_attributes(tddft_node, ['fxctype'])
            self.sub_node = tddft_node
            self.default_setting(xs_node, mode)

            energy_window_node = self.dom.createElement('energywindow')
            xs_node.appendChild(energy_window_node)
            self.add_attributes(energy_window_node, ['intv', 'points'])
            self.sub_node = energy_window_node
            self.default_setting(xs_node, mode)

            qpointset_node = self.dom.createElement('qpointset')
            xs_node.appendChild(qpointset_node)
            self.num = 0
            self.filter_rule = r'[\s\d.-]+'
            for point in self.split_laser_param('qpoint'):
                qpoint_node = self.dom.createElement('qpoint')
                qpointset_node.appendChild(qpoint_node)
                qpoint_text_node = self.dom.createTextNode(point.strip())
                qpoint_node.appendChild(qpoint_text_node)


class POSCARInfo:
    def __init__(self):
        self.number = None

    def elements_from_poscar(self):
        """read atoms name and number from POSCAR"""
        with open(r'POSCAR', 'r') as f:
            name_number = f.readlines()[5:7]
        self.number = [int(i) for i in re.split(r'\s+', name_number[1].strip())]
        elements = re.split(r'\s+', name_number[0].strip())
        return elements, self.number

    def coordinates_from_poscar(self):
        """Read from the 'POSCAR'"""
        with open(r'POSCAR', 'r') as f:
            return clean_data(f.readlines()[8:8 + sum(self.number)])

    @staticmethod
    def lattice_from_poscar():
        """:return lattice_constant and lattice_vector"""
        with open(r'POSCAR', 'r') as f:
            lattice_constant, *lattice_vectors = clean_data(f.readlines()[1:5])
        return lattice_constant[0] / 0.529177, lattice_vectors


def ground_state_mode(mode):
    input_xml = InputXml()
    input_xml.creat_root()
    input_xml.creat_title()
    input_xml.structure()
    input_xml.ground_state(mode)
    return input_xml


def relax_mode():
    input_xml = ground_state_mode('1')
    input_xml.coord_relax()
    return input_xml


def dos_band_mode(mode):
    input_xml = ground_state_mode('1')
    input_xml.properties_get(mode)
    return input_xml


def shg_mode(mode):
    input_xml = InputXml()
    input_xml.properties_get(mode)
    return input_xml


def xs_mode(mode):
    input_xml = InputXml()
    input_xml.excited_states(mode)
    return input_xml


def write_xml(input_xml, newl='\n', indent='\t', addindent='\t'):
    with open('input.xml', 'w', encoding='utf-8') as f:
        input_xml.dom.writexml(f, indent=indent, addindent=addindent, newl=newl, encoding='utf-8')
    print('--------------------------------------------------------------------------------------------------')
    print("Finished to creat <input.xml> for you, now, please check it again by yourself!\nGood Luck!!")
    print('========================================================================================================'
          '==========')


def pre_file_generate(mode):
    """generate file like, <pre-input>, <k-path>..."""
    if not os.path.exists('pre-input'):
        with open('pre-input', 'w', encoding='utf-8') as f:
            if mode in ['1', '2', '3', '6', '7']:
                f.writelines('#Ground State param\ntitle =\nspeciespath = /public/home/lyw/software/exciting/species/'
                             '\nngridk =\nxctype =\n#rmt =\n#outputlevel =\n#do =\nrgkmax =\n#nempty =\n#epsengy '
                             '= 1.d-7\n\n#DOS param\n#nsmdos = 2\n#ngrdos = 300\n#nwdos = 1000\n#winddos = -0.3 0.3\n\n'
                             '#Band structure param\n#steps = 100\n\n#Hybrid calculation param\n#excoeff = 0.25\n#omega'
                             ' = 0.11\n\n#Ion Coordinates Relax param\n#method = bfgs or newton or harmonic\n'
                             '#taubfgs = 0.5\n#taunewton = 0.2\n')
            elif mode == '4':
                f.writelines('do = skip\n#nosym = false\n#reducek = true\n#xstype = RT-TDDFT\nnempty =\nendTime =\n'
                             'timeStep =\n#laser = kick sinSq trapCos\n#amplitude = 0.01d0 1.d0 1.0d0\n'
                             '#t0 = 1.d0 0.5d0 0.25d0\n#width = 0.1d0 None 30.d0\n#direction = z y x\n'
                             '#omega = None 1.0d0 1.0d0\n#phase = None 0.d0 0.d0\n#vkloff =\n#pulseLength = '
                             'None 5.d0 None\n#riseTime = None None 5.d0\nngridk =\n#rgkmax =\n\n#screenshots = '
                             'true\n#niter = 100\n#printAbsProjCoeffs = true\n')
            elif mode == '5':
                f.writelines('do = skip\nngridk =\nnempty =\ngqmax =\nbroad =\n#tevout =\nintv =\npoints =\n#vkloff =\n'
                             '#fxctype =\nqpoint = | 0.0 0.0 0.0 |\n')
            elif mode == '8':
                f.writelines('wmax = 0.3\nwgrid = 400\nswidth = 0.008\netol = 1.d-4\ntevout = true\nchicomp = 1 2 3\n'
                             'do = skip\n')
    if (not os.path.exists('k-path')) and (mode in '3'):
        with open('k-path', 'w', encoding='utf-8') as f:
            if mode == '3':
                f.writelines('M = 0.0 0.5 0.0\nGamma = 0.0 0.0 0.0\nK = -0.333 0.667 0.0\n')


def main():
    """
    First obtain a instance of InputXml, then, creat root, title, structure, ground_state... in order, in case of some
    parameters, which must be gotten from 'pre-input' file, are not exist before use method of InputXml,
    finally, you can get 'input.xml' in your pwd.
    :return: InputXml
    """
    print('''
===================================================================================================================
Tips: No.1  1 and 2 mode need <pre-input> and <POSCAR> files, while 3 needs <k-path> file in addition!
      No.2  4 an 5 mode need <input.xml> file based on the ground state you just calculated!
      In addition, the code would copy <input.xml> to <copy_input.xml> each time you executing 4 and 5 mode. 
-------------------------------------------------------------------------------------------------------------
<pre-input> format,           <k-path> format,          And if you wanna creat laser with 'Combining field',
title  = Diamond              Gamma = 1.0 0.0 0.0            The format in <pre-input> file,
ngridk = 8 8 8                K = 0.625 0.375 0.0            laser     = kick sinSq trapCos
qpoint = |0.0 0.0 0.0|        X = 0.5 0.5 0.0                amplitude = 0.01d0 1.d0 1.0d0
xstype = TDDFT                L = 0.5 0.0 0.0                phase     = None 0.d0 0.d0
     ...                           ...                                 ...
-------------------------------------------------------------------------------------------------------------
    Please choose a mode you want to calculate from below:
        0. generate template of <pre-input>, <k-path> or ...;
        1. generate ground state <input.xml>;
        2. generate dos <input.xml>;
        3. generate band structure <input.xml>;
        4. generate rt-TDDFT based on the ground state <input.xml>;
        5. generate TDDFT based on the ground state <input.xml>;
        6. generate HSE calculation <input.xml>;
        7. generate Ion Coordinates Relax <input.xml>;
        8. generate SHG (Second Harmonic Generation) <input.xml>;
        ''')
    mode = input('    type the number of a mode: ')
    if mode == '0':
        print('''
    Please choose a number:
        1. <pre-input> for ground state <input.xml>;
        2. <pre-input> for dos <input.xml>;
        3. <pre-input> and <k-path> for band structure <input.xml>;
        4. <pre-input> for rt-TDDFT <input.xml>;
        5. <pre-input> for TDDFT <input.xml>;
        6. <pre-input> for HSE calculation;
        7. <pre-input> for Ion Coordinates Relax;
        8. <pre-input> for SHG (Second Harmonic Generation);
        ''')
        pre_file_generate(input('    type the number above: '))
        print("\nThe file(s) is(are) successfully generated, now, you should go and edit it!!!")
        print("=======================================================================================================")
        sys.exit(0)
    try:
        if mode in ['1', '6']:
            input_xml = ground_state_mode(mode)
            write_xml(input_xml)
        elif mode in ['2', '3']:
            input_xml = dos_band_mode(mode)
            write_xml(input_xml)
        elif mode in ['4', '5']:
            shutil.copyfile('input.xml', 'copy_input.xml')
            input_xml = xs_mode(mode)
            write_xml(input_xml)
        elif mode == '7':
            input_xml = relax_mode()
            write_xml(input_xml)
        elif mode == '8':
            input_xml = shg_mode(mode)
            write_xml(input_xml)
        else:
            print('You might input a wrong number, end of code execution.')
    except FileNotFoundError:
        print("======================================================================================================="
              "============")
        print("ERROR!!!\nThe 1 and 2 mode work only if both <pre-input> and <POSCAR> files are exist, \n"
              "    while 3 needs <k-path> file in addition! \nThe 4 and 5 mode need <input.xml> of ground state"
              " and <pre-input> of TDDFT/rt-TDDFT!\nCheck it again!")
        print("======================================================================================================="
              "============")
        sys.exit(1)


if __name__ == '__main__':
    main()
