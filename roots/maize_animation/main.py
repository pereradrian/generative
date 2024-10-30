from maize_animation import root_grow_animation

if __name__ == "__main__":
    fps = 15
    total_duration = 5*60
    growth_speed = 10 / total_duration / fps
    min_length_to_develop = total_duration
    root_grow_animation.save_maize_root_growth_animation(filename="maize_root_growth.mp4", growth_speed=growth_speed, growth_steps=fps*total_duration, fps=fps, min_length_to_develop=min_length_to_develop)
