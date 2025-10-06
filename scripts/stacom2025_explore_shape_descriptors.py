import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def explore_shape_descriptors():
    descriptor_folder = "C:/data/ImageCAS-STACOM2025-02-10-2025/descriptors/"
    output_csv = f"{descriptor_folder}combined_shape_descriptors.csv"

    print(f"Reading combined shape descriptors from {output_csv}")
    data = np.genfromtxt(output_csv, delimiter=',', names=True, dtype=None, encoding='utf-8')
    fieldnames = data.dtype.names
    print(f"Field names: {fieldnames}")
    print(f"Number of entries: {len(data)}")

    # Remove the filename field for PCA
    data_matrix = np.array([list(row)[1:] for row in data], dtype=float)

    # Standardize the data by removing the mean and scaling to unit variance
    # mostly to handle the volume variation which is much larger than the other descriptors
    mn = np.mean(data_matrix, axis=0)
    data_matrix = data_matrix - mn
    std = np.std(data_matrix, axis=0)
    data_matrix = data_matrix / std

    # Perform PCA
    pca = PCA()
    components = pca.fit_transform(data_matrix)
    plt.plot(pca.explained_variance_ratio_ * 100)
    plt.xlabel('Principal component')
    plt.ylabel('Percent explained variance')
    plt.show()

    pc_1 = components[:, 0]
    pc_2 = components[:, 1]
    pc_3 = components[:, 2]
    pc_4 = components[:, 3]

    plt.plot(pc_1, pc_2, '.')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.show()

    plt.plot(pc_1, pc_3, '.')
    plt.xlabel('PC1')
    plt.ylabel('PC3')
    plt.show()

    plt.plot(pc_1, pc_4, '.')
    plt.xlabel('PC1')
    plt.ylabel('PC3')
    plt.show()


if __name__ == '__main__':
    explore_shape_descriptors()
