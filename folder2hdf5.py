import os
import h5py
import numpy as np

def parse_obj(file_path):
    """Parse a .obj file and return vertices and faces as numpy arrays."""
    vertices = []
    faces = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                # Vertex definition
                parts = line.strip().split()
                vertex = list(map(float, parts[1:4]))
                vertices.append(vertex)
            elif line.startswith('f '):
                # Face definition
                parts = line.strip().split()
                face = []
                for part in parts[1:]:
                    # Faces can be defined in various formats; we extract vertex indices
                    idx = part.split('/')[0]
                    face.append(int(idx) - 1)  # OBJ indices are 1-based
                faces.append(face)
    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    return vertices, faces

def create_hdf5_dataset(input_dir, output_file):
    """Traverse the dataset directory, parse .obj files, and store data in HDF5 format."""
    with h5py.File(output_file, 'w') as hdf5_file:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.obj'):
                    obj_path = os.path.join(root, file)
                    rel_path = os.path.relpath(obj_path, input_dir)
                    # Create group hierarchy in HDF5 file
                    hdf5_group = hdf5_file
                    path_parts = rel_path.split(os.sep)
                    for part in path_parts[:-1]:  # All parts except the file name
                        if part not in hdf5_group:
                            hdf5_group = hdf5_group.create_group(part)
                        else:
                            hdf5_group = hdf5_group[part]
                    mesh_name = os.path.splitext(path_parts[-1])[0]  # File name without extension
                    if mesh_name not in hdf5_group:
                        mesh_group = hdf5_group.create_group(mesh_name)
                    else:
                        mesh_group = hdf5_group[mesh_name]
                    # Parse the .obj file
                    vertices, faces = parse_obj(obj_path)
                    # Store vertices and faces as datasets
                    # Enable chunking and compression for performance
                    mesh_group.create_dataset('vertices', data=vertices, dtype=np.float32,
                                              chunks=True, compression="gzip")
                    mesh_group.create_dataset('faces', data=faces, dtype=np.int32,
                                              chunks=True, compression="gzip")
                    print(f"Stored {rel_path} in HDF5 file.")
    print(f"Finished creating HDF5 dataset at {output_file}")

if __name__ == '__main__':
    create_hdf5_dataset('./breaking_bad', './breaking_bad.hdf5')