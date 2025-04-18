from __future__ import annotations

import math
import re
from xml.etree import ElementTree as ET

from numpy.testing import assert_allclose

from pymatgen.core import Lattice, Structure
from pymatgen.io.exciting import ExcitingInput
from pymatgen.util.testing import TEST_FILES_DIR, MatSciTest

__author__ = "Christian Vorwerk"
__copyright__ = "Copyright 2016"
__version__ = "0.1"
__maintainer__ = "Christian Vorwerk"
__email__ = "vorwerk@physik.hu-berlin.de"
__date__ = "Dec 01, 2016"


TEST_DIR = f"{TEST_FILES_DIR}/io/exciting"


class TestExcitingInput(MatSciTest):
    def test_fromfile(self):
        # Test for the import of a structure directly from an exciting
        # input file
        filepath = f"{TEST_DIR}/input_exciting1.xml"
        exc_input = ExcitingInput.from_file(filepath)
        lattice = [[0.0, 2.81, 2.81], [2.81, 0.0, 2.81], [2.81, 2.81, 0.0]]
        atoms = ["Na", "Cl"]
        frac_coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
        assert_allclose(lattice, exc_input.structure.lattice.matrix.tolist())
        assert atoms == [site.specie.symbol for site in exc_input.structure]
        assert frac_coords == [site.frac_coords.tolist() for site in exc_input.structure]

    def test_write_string(self):
        # Test for the string export of structure into the exciting input xml schema
        input_string = (
            '<input xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:noNamespaceSchemaLocation="http://xml.exciting-code.org/excitinginput'
            '.xsd">\n  <title>Na4 Cl4</title>\n  <structure speciespath="./">\n    '
            '<crystal scale="1.8897543768634038">\n      <basevect>      5.62000000'
            "       0.00000000       0.00000000</basevect>\n      <basevect>      "
            "0.00000000       5.62000000       0.00000000</basevect>\n      "
            "<basevect>      0.00000000       0.00000000       5.62000000</basevect>"
            '\n    </crystal>\n    <species speciesfile="Na.xml">\n      <atom coord='
            '"      0.00000000       0.00000000       0.00000000" />\n      <atom coor'
            'd="      0.50000000       0.50000000       0.00000000" />\n      <atom co'
            'ord="      0.50000000       0.00000000       0.50000000" />\n      <atom '
            'coord="      0.00000000       0.50000000       0.50000000" />\n    </spec'
            'ies>\n    <species speciesfile="Cl.xml">\n      <atom coord="      0.5000'
            '0000       0.00000000       0.00000000" />\n      <atom coord="      0.00'
            '000000       0.50000000       0.00000000" />\n      <atom coord="      0.'
            '00000000       0.00000000       0.50000000" />\n      <atom coord="      '
            '0.50000000       0.50000000       0.50000000" />\n    </species>\n  </str'
            "ucture>\n</input>\n"
        )
        lattice = Lattice.cubic("5.62")
        structure = Structure(
            lattice,
            ["Na", "Na", "Na", "Na", "Cl", "Cl", "Cl", "Cl"],
            [
                [0, 0, 0],
                [0.5, 0.5, 0.0],
                [0.5, 0.0, 0.5],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.0],
                [0.0, 0.5, 0.0],
                [0.0, 0.0, 0.5],
                [0.5, 0.5, 0.5],
            ],
        )
        exc_in = ExcitingInput(structure)
        for l1, l2 in zip(
            input_string.split("\n"),
            exc_in.write_string("unchanged").split("\n"),
            strict=True,
        ):
            if not l1.strip().startswith("<crystal scale"):
                assert l1.strip() == l2.strip()

    def test_writebandstr(self):
        filepath = f"{TEST_FILES_DIR}/cif/CsI3Pb.cif"
        structure = Structure.from_file(filepath)
        exc_in = ExcitingInput(structure)
        string = exc_in.write_string("primitive", bandstr=True)
        band_str = string.split("<properties>")[1].split("</properties>")[0]

        coord = []
        label = []
        coord_ref = [
            [0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.0, 0.5, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.5],
            [0.5, 0.0, 0.5],
            [0.5, 0.5, 0.5],
            [0.0, 0.5, 0.5],
            [0.0, 0.0, 0.5],
            [0.0, 0.5, 0.0],
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
            [0.5, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.5, 0.5, 0.5],
        ]
        label_ref = [
            "GAMMA",
            "X",
            "S",
            "Y",
            "GAMMA",
            "Z",
            "U",
            "R",
            "T",
            "Z",
            "Y",
            "T",
            "U",
            "X",
            "S",
            "R",
        ]
        root = ET.fromstring(band_str)
        for plot1d in root.iter("plot1d"):
            for point in plot1d.iter("point"):
                coord.append([float(i) for i in point.get("coord").split()])
                label.append(point.get("label"))
        assert label == label_ref
        assert coord == coord_ref

    def test_param_dict(self):
        coords = [[0.0, 0.0, 0.0], [0.75, 0.5, 0.75]]
        lattice = Lattice.from_parameters(a=3.84, b=3.84, c=3.84, alpha=120, beta=90, gamma=60)
        struct = Structure(lattice, ["Si", "Si"], coords)
        param_dict = {
            "grst": {
                "do": "fromscratch",
                "ngridk": "8 8 8",
                "xctype": "GGA_PBE_SOL",
                "gmaxvr": "14.0",
            },
            "xs": {
                "xstype": "BSE",
                "ngridk": "4 4 4",
                "ngridq": "4 4 4",
                "nempty": "30",  # codespell:ignore: nempty
                "gqmax": "3.0",
                "broad": "0.07",
                "tevout": "true",
                "energywindow": {"intv": "0.0 1.0", "points": "1200"},
                "screening": {"screentype": "full", "nempty": "100"},  # codespell:ignore: nempty
                "BSE": {"bsetype": "singlet", "nstlbse": "1 5 1 4"},
            },
        }

        test_input = ExcitingInput(struct)
        test_str = test_input.write_string("unchanged", **param_dict)

        # read reference file
        filepath = f"{TEST_DIR}/input_exciting2.xml"
        tree = ET.parse(filepath)
        root = tree.getroot()
        ref_str = ET.tostring(root, encoding="unicode")

        ref_list = ref_str.strip().split()
        test_list = test_str.strip().split()

        # "scale" is float, direct compare might give surprising results
        ref_scale = float(re.search(r'scale="([-+]?\d*\.\d+|\d+)"', ref_list.pop(7))[1])
        test_scale = float(re.search(r'scale="([-+]?\d*\.\d+|\d+)"', test_list.pop(7))[1])

        assert ref_list == test_list
        assert math.isclose(ref_scale, test_scale)
