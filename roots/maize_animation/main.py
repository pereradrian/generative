from maize_animation import root_grow_animation
import numpy as np

if __name__ == "__main__":
    fps = 15
    total_duration = 5*60
    growth_speed = 40.0 / total_duration / fps
    min_length_to_develop = total_duration
    frames = fps*total_duration
    rps = 2.0 / 60.0
    angular_velocity = 2*np.pi * rps / fps
    root_grow_animation.save_maize_root_growth_animation(filename="maize_root_growth_rotation.mp4",
                                                         growth_speed=growth_speed,
                                                         growth_steps=frames,
                                                         fps=fps,
                                                         min_length_to_develop=min_length_to_develop,
                                                         angular_velocity=angular_velocity)

#mysql-connector-java-8.0.29.jar