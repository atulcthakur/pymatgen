from __future__ import annotations

from pymatgen.analysis.chemenv.coordination_environments.coordination_geometries import AllCoordinationGeometries
from pymatgen.analysis.chemenv.coordination_environments.coordination_geometry_finder import LocalGeometryFinder

all_cg = AllCoordinationGeometries()

lgf = LocalGeometryFinder()

mp_symbol = "DD:20"
coordination = 20
indices = [8, 12, 11, 0, 14, 10, 13, 6, 18, 1, 9, 17, 3, 19, 5, 7, 15, 2, 16, 4]
cg = all_cg.get_geometry_from_mp_symbol(mp_symbol=mp_symbol)
lgf.allcg = AllCoordinationGeometries(only_symbols=[mp_symbol])
lgf.setup_test_perfect_environment(
    mp_symbol,
    randomness=False,
    indices=indices,
    random_translation="NONE",
    random_rotation="NONE",
    random_scale="NONE",
)
se = lgf.compute_structure_environments(
    only_indices=[0],
    maximum_distance_factor=1.01 * cg.distfactor_max,
    min_cn=cg.coordination_number,
    max_cn=cg.coordination_number,
    only_symbols=[mp_symbol],
)

print(se.ce_list[0][20][0])
