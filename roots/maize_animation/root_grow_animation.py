import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from time import sleep

MAX_ROOTS = 1000
MIN_LENGHT_TO_DEVELOP = 200

def save_maize_root_growth_animation(filename="maize_root_growth.mp4", growth_speed=0.3, growth_steps=100, fps=15, min_length_to_develop=MIN_LENGHT_TO_DEVELOP):
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-20, 0.1)
    ax.set_aspect('equal')
    ax.axis("off")

    # Initialize root growth parameters
    roots = [np.array([0, 0])]
    angles = [1.5*np.pi]
    lines = [ax.plot([], [], color='k', lw=2)[0] for _ in range(MAX_ROOTS)]
    angle_variation_amplitude = np.pi / 2
    bifurcation_probability = 0.1

    # Complete branches

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        result_roots = []
        result_angles = []
        # Expand each line
        for branch_to_expand, angle_to_follow, line in zip(roots, angles, lines):
            # For each final node, expand
            # choose number of bifurcations
            angle_variation = np.random.uniform(-angle_variation_amplitude, angle_variation_amplitude)
            angle = angle_to_follow + angle_variation

            # Calculate new node
            dx = growth_speed * np.cos(angle)
            dy = growth_speed * np.sin(angle)

            # Append new segment to the root
            new_node = branch_to_expand[-1] + np.array([dx, dy])
            upper_bound = np.random.uniform(-growth_speed, 0.0)
            new_node[1] = min(new_node[1], upper_bound)
            # If branch for next iteration
            result_roots.append(np.vstack([branch_to_expand, new_node]))
            result_angles.append(angle_to_follow)
        
        # Test to bifurcate
        if len(roots[0])> min_length_to_develop:
            while np.random.uniform(0.0, 1.0) < bifurcation_probability and len(result_roots)<MAX_ROOTS:
                probabilities = np.square(np.asarray([root[-1,1] for root in roots]))
                probabilities = probabilities / probabilities.sum()
                index = np.random.choice(range(len(roots)), p=probabilities)
                branch_to_expand = roots[index]
                lenght = np.random.randint(1, len(branch_to_expand))
                branch_to_divide = branch_to_expand[:lenght]
                result_roots.append(branch_to_divide)
                result_angles.append(angle_to_follow + np.random.choice([-1, 1])*(np.pi/4 + np.random.uniform(-angle_variation_amplitude, angle_variation_amplitude)))

        roots.clear()
        angles.clear()
        for root, angle in zip(result_roots, result_angles):
            roots.append(root)
            angles.append(angle)
        print(f"Iteration {frame}/{growth_steps}, roots {len(roots)}", end="\r")
        for line, root in zip(lines, roots):
            x, y = root[:,0], root[:,1]
            line.set_data(x,y)
            line.set_linewidth(0.5)
        return lines

    ani = animation.FuncAnimation(fig, update, frames=growth_steps, init_func=init, blit=True, repeat=False)
    ani.save(filename, writer="ffmpeg", fps=fps)
    print(f"Animation saved as {filename}")
