from __future__ import annotations

import numpy as np

from pymatgen.core.lattice import Lattice
from pymatgen.optimization.neighbors import find_points_in_spheres
from pymatgen.util.testing import MatSciTest


class TestNeighbors(MatSciTest):
    def setup_method(self):
        self.lattice = Lattice.cubic(10.0)
        self.cubic = self.lattice
        self.tetragonal = Lattice.tetragonal(10, 20)
        self.orthorhombic = Lattice.orthorhombic(10, 20, 30)
        self.monoclinic = Lattice.monoclinic(10, 20, 30, 66)
        self.hexagonal = Lattice.hexagonal(10, 20)
        self.rhombohedral = Lattice.rhombohedral(10, 77)

        family_names = [
            "cubic",
            "tetragonal",
            "orthorhombic",
            "monoclinic",
            "hexagonal",
            "rhombohedral",
        ]

        self.families = {}
        for name in family_names:
            self.families[name] = getattr(self, name)

    def test_points_in_spheres(self):
        points = [[0.0, 0.0, 0.0], [2.0, 2.0, 2.0]]
        lattice = Lattice.cubic(3)
        center_points = [[1.5, 1.5, 1.5]]
        nns = find_points_in_spheres(
            all_coords=np.array(points),
            center_coords=np.array(center_points),
            r=3,
            pbc=np.array([0, 0, 0], dtype=np.int64),
            lattice=np.array(lattice.matrix),
            tol=1e-8,
        )
        assert len(nns[0]) == 2  # two neighbors

        nns = find_points_in_spheres(
            all_coords=np.array(points),
            center_coords=np.array(center_points),
            r=3,
            pbc=np.array([1, 1, 1], dtype=np.int64),
            lattice=np.array(lattice.matrix),
        )
        assert len(nns[0]) == 12

        nns = find_points_in_spheres(
            all_coords=np.array(points),
            center_coords=np.array(center_points),
            r=3,
            pbc=np.array([True, False, False], dtype=np.int64),
            lattice=np.array(lattice.matrix),
        )
        assert len(nns[0]) == 4
