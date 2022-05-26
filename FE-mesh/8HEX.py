# -*- coding: utf-8 -*-
"""
Created on Sat, 14 May 2022
@author: Cooman Long
"""
from typing import List, Tuple

Vectors = Tuple[tuple, tuple, tuple]
Scale = List[float]
KMesh = Tuple[int, int, int]
Nlo = List[float]


def lattice_vector_cal(lattice_param: List[float]):
    xlo, xhi, ylo, yhi, zlo, zhi, xy, xz, yz = lattice_param
    a0, b0, c0 = (xhi - xlo, 0, 0), (xy, yhi - ylo, 0), (xz, yz, zhi - zlo)
    return a0, b0, c0


def elements_vertex_index(k_: KMesh):
    k1, k2, k3 = k_
    nodes_number = (k1 + 1) * (k2 + 1) * (k3 + 1)
    plane_number = (k1 + 1) * (k2 + 1)
    elements_number = k1 * k2 * k3
    nodes_vertex = []
    for i in range(k3):
        tmp0 = i * plane_number
        for j in range(tmp0 + 1, plane_number - k1 - 1 + tmp0):
            if j % (k1 + 1):
                tmp1, tmp2 = j + k1, j + plane_number
                vertex = (j, j + 1, tmp1 + 2, tmp1 + 1, tmp2,
                          tmp2 + 1, tmp2 + k1 + 2, tmp2 + k1 + 1)
                nodes_vertex.append(vertex)
    return nodes_number, elements_number, nodes_vertex


def vector_cal(vectors: Vectors, scale: Scale):
    tmp_vect = []
    for (vector, i) in zip(vectors, scale):
        tmp_vect.append([j * i for j in vector])
    return [sum(i) if round(sum(i), 5) else int(sum(i)) for i in zip(*tmp_vect)]


def scale_cal(k_mesh: KMesh, node_index: int) -> Scale:
    scale1 = (node_index - 1) % ((k_mesh[0] + 1) * (k_mesh[1] + 1)) % (k_mesh[0] + 1) / k_mesh[0]
    scale2 = (node_index - 1) % ((k_mesh[0] + 1) * (k_mesh[1] + 1)) // (k_mesh[0] + 1) / k_mesh[1]
    scale3 = (node_index - 1) // ((k_mesh[0] + 1) * (k_mesh[1] + 1)) / k_mesh[2]
    scale = [scale1, scale2, scale3]
    return scale


def coord_modify(nlo: Nlo, nodes_coord):
    return [[node_coord[i] + nlo[i] for i in range(len(node_coord))] for node_coord in nodes_coord]


def nodes_coord_cal(vectors: Vectors, nodes_number: int, k_mesh: KMesh):
    nodes_coord = []
    for node_index in range(1, nodes_number + 1):
        scale = scale_cal(k_mesh, node_index)
        cartesian_coord = vector_cal(vectors, scale)
        nodes_coord.append(cartesian_coord)
    return nodes_coord


def write_mesh(nodes_coord, nodes_number, nodes_vertex):
    with open('data.mesh', 'w') as f:
        f.writelines(f'Coordinates {nodes_number}\n')
        for i in nodes_coord:
            f.writelines(f"  {i[0]:.6f}  {i[1]:.6f}  {i[2]:.6f}\n")
        f.writelines(f'\nElements {len(nodes_vertex)} HEX8\n')
        for i in nodes_vertex:
            f.writelines(f"{' '.join(str(j) for j in i)} \n")
        f.writelines('\n')


def main():
    lattice_param = [-15.81877983, 51.97599087, -27.3989303793, 31.3130632906, -49.978292, 57.118048, -33.89738535, 0.0, 0.0]
    k_mesh = (11, 11, 1)
    vectors = lattice_vector_cal(lattice_param)
    nodes_number, elements_number, nodes_vertex = elements_vertex_index(k_mesh)
    print("============================================================================================================"
          "============\n")
    if any(lattice_param[-3:]):
        print("\n#################First, we find it's a Non-orthogonal lattice################\n")
    else:
        print("\n#################First, we find it's an Orthogonal lattice################\n")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          "~~~~")
    print(f"\tCreated {nodes_number} nodes, {len(nodes_vertex)} unique nodes and {elements_number} elements!")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          "~~~~")
    print("\n\tNow, we are going to find coordinates of all nodes...\n")
    nodes_coord = nodes_coord_cal(vectors, nodes_number, k_mesh)
    nlo = [lattice_param[0], lattice_param[2], lattice_param[4]]
    nodes_coord = coord_modify(nlo, nodes_coord)
    print("\t\tCreated all nodes_coord successfully,\n\n\tNext, we are going to output the mesh... ")
    write_mesh(nodes_coord, nodes_number, nodes_vertex)
    print("\n\t\tWrite <data.mesh> to pwd, Finished!\n")
    print("============================================================================================================"
          "============\n")


if __name__ == "__main__":
    main()
