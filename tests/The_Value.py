import numpy as np

# Example 2D NumPy array
array = np.random.rand(100, 100)

# Get the center indices
rows, cols = array.shape
center_row = rows // 2
center_col = cols // 2

# Define half the grid size
half_size = 5  # 10x10 grid -> 5 cells on each side from center

# Select the 10x10 grid at the center
center_grid = array[
    center_row - half_size:center_row + half_size,
    center_col - half_size:center_col + half_size
]

# Calculate the average value
average_value = np.mean(center_grid)

print("Selected 10x10 grid:")
print(center_grid)

print("\nAverage value:", average_value)
