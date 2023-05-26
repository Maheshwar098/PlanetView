import matplotlib.pyplot as plt

num_colors = 11


# Get the "viridis" colormap
colormap = plt.cm.get_cmap('viridis')

# Generate a list of colors from the colormap
colors = [colormap(i / num_colors) for i in range(num_colors)]
print(colors)