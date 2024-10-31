import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from time import sleep

MAX_ROOTS = 1000
MIN_LENGHT_TO_DEVELOP = 200

def save_maize_root_growth_animation(filename="maize_root_growth.mp4", growth_speed=0.3, growth_steps=100, fps=15,
                                     min_length_to_develop=MIN_LENGHT_TO_DEVELOP, 
                                     branch_probability='y', angular_velocity=0.0):
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    fig.patch.set_facecolor('black')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-20, 0.1)
    ax.set_aspect('equal')
    ax.axis("off")

    # Initialize root growth parameters
    roots = [np.array([0, 0, 0])]
    angles = [(1.5*np.pi, 1.5*np.pi)]
    bifurcation_probability = 0.07
    max_roots = int((growth_steps - min_length_to_develop)*bifurcation_probability)
    max_alpha = 1.0
    min_alpha = 0.01
    # make alphas decay faster
    weights = np.arange(max_roots)[::-1]
    max_weight = np.max(weights)
    min_weight = np.min(weights)
    alphas = (weights - min_weight) / (max_weight - min_weight) * (max_alpha - min_alpha) + min_alpha
    lines = [ax.plot([], [], color='white', lw=2, alpha=alphas[i])[0] for i in range(max_roots)]
    angle_variation_amplitude = np.pi / 2
    drift_proportion = 0.1

    # Complete branches

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        result_roots = []
        result_angles = []
        # Expand each line
        for index in range(len(roots)):
            branch_to_expand = roots[index]
            angle_x_to_follow, angle_z_to_follow = angles[index]
            line = lines[index]
            # For each final node, expand
            # choose number of bifurcations
            angle_variation_x = angle_variation_amplitude * np.random.uniform(-1, 1)
            angle_variation_z = angle_variation_amplitude * np.random.uniform(-1, 1)
            angle_x = angle_x_to_follow + angle_variation_x
            angle_z = angle_z_to_follow + angle_variation_z

            # Calculate new node
            dx = growth_speed * np.cos(angle_x) * np.cos(angle_z)
            dy = growth_speed * max(-1, np.sin(angle_x) * np.cos(angle_z) - drift_proportion)
            dz = growth_speed * np.cos(angle_x) * np.sin(angle_z)

            # Append new segment to the root
            new_node = branch_to_expand[-1] + np.array([dx, dy, dz])
            upper_bound = np.random.uniform(-growth_speed, 0.0)
            if upper_bound <= new_node[1]:
                new_node[1] = upper_bound
            # If branch for next iteration
            result_roots.append(np.vstack([branch_to_expand, new_node]))
            result_angles.append((angle_x_to_follow, angle_z_to_follow))
        
        # Test to bifurcate
        if len(roots[0])> min_length_to_develop:
            while np.random.uniform(0.0, 1.0) < bifurcation_probability and len(result_roots)<max_roots:
                if branch_probability == "uniform":
                    probabilities = np.ones(len(roots))
                elif branch_probability == "y":
                    probabilities = np.square(np.asarray([root[-1,1] for root in roots]))
                elif branch_probability == "L2":
                    probabilities = np.square(np.asarray([root[-1,1]*root[-1,1] + root[-1,0]*root[-1,0] for root in roots]))
                elif branch_probability == "length":
                    probabilities = np.asarray([len(root) for root in roots])

                probabilities = probabilities / probabilities.sum()
                    
                index = np.random.choice(range(len(roots)), p=probabilities)
                branch_to_expand = roots[index]
                index_node = np.random.randint(len(branch_to_expand)//2, len(branch_to_expand))
                result_roots.append(branch_to_expand[index_node].reshape(-1, 3))
                random_offset_x = angle_variation_amplitude*np.random.choice([-1, 1])
                random_noise_x = angle_variation_amplitude/2*np.random.normal(0.0, 1.0)
                random_offset_z = angle_variation_amplitude*np.random.choice([-1, 1])
                random_noise_z = angle_variation_amplitude/2*np.random.normal(0.0, 1.0)
                angle_x = angle_x_to_follow + random_offset_x + random_noise_x
                angle_z = angle_z_to_follow + random_offset_z + random_noise_z
                result_angles.append((angle_x, angle_z))
        # Rotate roots
        angle_rotation = float(angular_velocity) * float(frame)
        rotation_matrix = np.array([
            [np.cos(angle_rotation), 0, -np.sin(angle_rotation)],
            [0, 1, 0],
            [np.sin(angle_rotation), 0, np.cos(angle_rotation)],
        ])
        roots.clear()
        angles.clear()
        for root, angle in zip(result_roots, result_angles):
            roots.append(root)
            angles.append(angle)

        print(f"Iteration {frame}/{growth_steps}, roots {len(roots)}", end="\r")
        for line, root in zip(lines, roots):
            result_root = root @ rotation_matrix
            x, y = result_root[:,0], result_root[:,1]
            line.set_data(x,y)
            line.set_linewidth(1.0)
        return lines

    ani = animation.FuncAnimation(fig, update, frames=growth_steps, init_func=init, blit=True, repeat=False)
    ani.save(filename, writer="ffmpeg", fps=fps)
    print(f"Animation saved as {filename}")
