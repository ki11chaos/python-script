import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def update_lines(num, walks, lines):
    for line, walk in zip(lines, walks):
        # NOTE: there is no .set_data() for 3 dim data...
        # But when I looked up source code, and it gave a 3D set_data,,, anyway, it worked.
        # line.set_data(walk[:num, :2].T)
        # line.set_3d_properties(walk[:num, 2])
        line.set_data_3d(walk[:num, :].T)
    return lines


with open('data.mesh', 'r') as f:
    info = f.readlines()
    coord = np.array(list(list(map(lambda x: float(x), i.split())) for i in info[1:289]))
    vertex = np.array(list(list(map(lambda x: int(x) - 1, i.split())) for i in info[291:412]))


# Attaching 3D axis to the figure
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

# Get walk
walks = [coord[i] for i in vertex]
num_steps = 9

# Create lines initially without data
lines = [ax.plot([], [], [])[0] for _ in walks]

# Setting the axes properties
ax.set(xlim3d=(-50, 50), xlabel='X')
ax.set(ylim3d=(-40, 50), ylabel='Y')
ax.set(zlim3d=(-70, 70), zlabel='Z')

# Creating the Animation object
ani = animation.FuncAnimation(
    fig, update_lines, num_steps, fargs=(walks, lines), interval=1000)

plt.show()

