import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from time import sleep

MAX_ROOTS = 1000
MIN_LENGHT_TO_DEVELOP = 200

def validate_dim(array, shape):
    array_shape = array.shape
    condition = len(array.shape) == len(shape) and all(a == b for a, b, in zip(array.shape, shape))
    if not condition:
        input_dim = ", ".join(str(a) for a in array_shape)
        expected_dim = ", ".join(str(a) for a in shape)
        message = f"input {input_dim} != Expected {expected_dim}"
    assert condition, message
    return condition

def expand_update_branch(branch, angles, angle_variation_amplitude, growth_speed, drift_proportion):
    """
    branch :float[N, 3, n_trees]
    angles :float[N, 2, n_trees]
    """
    n_trees = branch.shape[2]
    node_to_expand = branch[[-1]]
    angle_to_expand = angles[[-1]]
    assert validate_dim(node_to_expand, [1, 3, n_trees]), angle_to_expand.shape
    assert validate_dim(angle_to_expand, [1, 2, n_trees]), angle_to_expand.shape
    # Compute new orientations
    angle = angle_to_expand + angle_variation_amplitude * np.random.uniform(-1, 1, size=angle_to_expand.shape)
    angle_x = angle[:,0]
    angle_z = angle[:,1]
    assert validate_dim(angle, [1, 2, n_trees])
    assert validate_dim(angle_x, [1, n_trees])
    assert validate_dim(angle_z, [1, n_trees])

    # Calculate new node
    dx = growth_speed * np.cos(angle_x) * np.cos(angle_z)
    dy = growth_speed * np.maximum(-1, np.sin(angle_x) * np.cos(angle_z) - drift_proportion)
    dz = growth_speed * np.cos(angle_x) * np.sin(angle_z)
    assert validate_dim(dx, [1, n_trees])
    assert validate_dim(dy, [1, n_trees])
    assert validate_dim(dz, [1, n_trees])
    branch_segment = np.stack((dx, dy, dz), axis=1)
    assert validate_dim(branch_segment, [1, 3, n_trees])

    # Append new segment to the root
    new_node = node_to_expand + branch_segment
    assert validate_dim(new_node, [1, 3, n_trees])
    upper_bound = np.random.uniform(-growth_speed, 0.0)
    indices_to_update = (new_node[:,1,:] >= upper_bound).ravel()
    assert validate_dim(indices_to_update, [n_trees])
    new_node[:,1,indices_to_update] = upper_bound
    updated_branch = np.vstack([branch, new_node])
    assert validate_dim(updated_branch, [len(branch)+1, 3, n_trees])
    return updated_branch, angle

def save_maize_root_growth_animation(filename="maize_root_growth.mp4", growth_speed=0.3, growth_steps=100, fps=15,
                                     min_length_to_develop=MIN_LENGHT_TO_DEVELOP, 
                                     branch_probability='y', angular_velocity=0.0,
                                     n_trees = 1, weight_time_delta=0.001):
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    fig.patch.set_facecolor('black')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-20, 0.1)
    ax.set_aspect('equal')
    ax.axis("off")

    # Initialize root growth parameters
    branches = [np.zeros(shape=(1, 3, n_trees))]
    angles = [np.stack([[1.5*np.pi, 0.0] for _ in range(n_trees)]).reshape(1, 2, n_trees)]
    weight = np.random.uniform(0.0, 1.0, n_trees)
    weight /= weight.sum()
    weights = [weight]
    

    bifurcation_probability = 0.07
    max_roots = int((growth_steps - min_length_to_develop)*bifurcation_probability)
    max_alpha = 1.0
    min_alpha = 0.01
    # make alphas decay faster
    aplha_weights = np.arange(max_roots)[::-1]
    max_weight = np.max(aplha_weights)
    min_weight = np.min(aplha_weights)
    alphas = (aplha_weights - min_weight) / (max_weight - min_weight) * (max_alpha - min_alpha) + min_alpha
    lines = [ax.plot([], [], color='white', lw=2, alpha=alphas[i])[0] for i in range(max_roots)]
    angle_variation_amplitude = np.pi / 16
    angle_variation_branch = angle_variation_amplitude
    drift_proportion = 0.1

    # Complete branches

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        result_roots = []
        result_angles = []
        # Expand each present branch
        for branch, angle in zip(branches, angles):
            assert validate_dim(branch, [len(branch), 3, n_trees])
            # For each final node, expand
            updated_branch, updated_orientation = expand_update_branch(branch, angle, angle_variation_amplitude, growth_speed, drift_proportion)
            assert validate_dim(updated_branch, [len(branch)+1, 3, n_trees])
            assert validate_dim(updated_orientation, [1, 2, n_trees])
            # If branch for next iteration
            result_roots.append(updated_branch)
            result_angles.append(updated_orientation)
        
        # Test to bifurcate
        if len(branches[0])> min_length_to_develop:
            while np.random.uniform(0.0, 1.0) < bifurcation_probability and len(result_roots)<max_roots:
                probabilities = np.square(np.asarray([np.sum(-branch[-1,1]) for branch in branches]))
                probabilities = probabilities / probabilities.sum()
                    
                index = np.random.choice(range(len(branches)), p=probabilities)
                branch_to_expand = branches[index]
                angle_to_expand = angles[index]
                index_node = np.random.randint(len(branch_to_expand)//2, len(branch_to_expand))

                result_roots.append(branch_to_expand[index_node].reshape(1, 3, n_trees))
                random_offset = np.random.choice([-1, 1], size=(1, 2, n_trees))
                noise = 0.5*np.random.normal(0.0, 1.0, size=(1, 2, n_trees))
                new_angle = angle_to_expand + angle_variation_branch*(random_offset+noise)
                assert validate_dim(new_angle, [1, 2, n_trees])
                
                result_angles.append(new_angle)
        
        # Rotate roots
        angle_rotation = float(angular_velocity) * float(frame)
        rotation_matrix = np.array([
            [np.cos(angle_rotation), 0, -np.sin(angle_rotation)],
            [0, 1, 0],
            [np.sin(angle_rotation), 0, np.cos(angle_rotation)],
        ])

        branches.clear()
        angles.clear()
        for branch, angle in zip(result_roots, result_angles):
            branches.append(branch)
            angles.append(angle)

        print(f"Iteration {frame}/{growth_steps}, roots {len(branches)}", end="\r")

        for line, branch in zip(lines, branches):
            assert validate_dim(branch, [len(branch), 3, n_trees])
            # Branch of shape n_nodes, n_trees, n_dim
            n_nodes = branch.shape[0]
            weight_change = weight_time_delta*np.random.uniform(-1.0, 1.0, n_trees)
            new_weights = weights[-1] + weight_change
            new_weights /= new_weights.sum()
            weights.append(new_weights)
            collapsed_branch = branch @ new_weights
            assert validate_dim(collapsed_branch, [len(collapsed_branch), 3])

            result_root = collapsed_branch @ rotation_matrix
            x, y = result_root[:,0], result_root[:,1]
            line.set_data(x,y)
            line.set_linewidth(1.0)
        return lines

    ani = animation.FuncAnimation(fig, update, frames=growth_steps, init_func=init, blit=True, repeat=False)
    ani.save(filename, writer="ffmpeg", fps=fps)
    print(f"Animation saved as {filename}")
