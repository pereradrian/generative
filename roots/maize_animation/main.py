from maize_animation import root_grow_animation
import numpy as np

if __name__ == "__main__":
    fps = 30
    total_duration = 2*60
    growth_speed = 40.0 / total_duration / fps
    min_length_to_develop = 1#total_duration
    frames = fps*total_duration
    rps = 2.0 / 60.0
    angular_velocity = 2*np.pi * rps / fps
    np.random.seed(0)
    root_grow_animation.save_maize_root_growth_animation(filename="maize_root_growth_rotation.mp4",
                                                         growth_speed=growth_speed,
                                                         growth_steps=frames,
                                                         fps=fps,
                                                         min_length_to_develop=min_length_to_develop,
                                                         angular_velocity=angular_velocity,
                                                         n_trees=10)

#mysql-connector-java-8.0.29.jar