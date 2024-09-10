#!/usr/bin/env python

import pygame
import sys
import math
import random
import os
import numpy as np
import mandelbruh

from mandelbruh.shader import Shader
from mandelbruh.camera import Camera

from ctypes import *
from OpenGL.GL import *
from pygame.locals import *

from mandelbruh import fractals

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Epsilon (resolution)
EPS = 1e-12

# Dimensions
X = 0
Y = 1
Z = 2
N_DIMENSIONS = 3

# Size of the window and rendering
win_size = (1280, 720)

# Maximum frames per second
MAX_FPS = 30

# Forces an 'up' orientation when True, free-camera when False
gimbal_lock = True

# Mouse look speed
look_speed = 0.003

# Use this avoids collisions with the fractal
auto_velocity = True
auto_multiplier = 2.0

# Maximum velocity of the camera
max_velocity = 2.0

# Acceleration rate when moving
ACCELERATION_RATE = 2.0

# Velocity decay factor when keys are released
FRICTION = 0.95

clicking = False
mouse_pos = None

START_POSITION = [0, 0, 12.0]

screen_center = (win_size[0]/2, win_size[1]/2)
velocity = np.zeros((N_DIMENSIONS,), dtype=np.float32)
look_x = 0.0
look_y = 0.0

# Free mouse option
lock_mouse = True

# Holde key flag
keep_moving = False

PLAY_BACK_FRAME_INTERPOLATION_RATE = 0.99


# ----------------------------------------------
#    When building your own fractals, you can
# substitute numbers with string placeholders
# which can be tuned real-time with key bindings.
#
# In this example program:
#    '0'   +Insert  -Delete
#    '1'   +Home    -End
#    '2'   +PageUp  -PageDown
#    '3'   +NumPad7 -NumPad4
#    '4'   +NumPad8 -NumPad5
#    '5'   +NumPad9 -NumPad6
#
# Hold down left-shift to decrease rate 10x
# Hold down right-shift to increase rate 10x
#
# Set initial values of '0' through '6' below
# ----------------------------------------------
key_vars = [1.5, 1.5, 2.0, 1.0, 1.0, 1.0]


# ----------------------------------------------
#             Helper Utilities
# ----------------------------------------------
def interp_data(x, f=2.0):
    new_dim = int(x.shape[0]*f)
    output = np.empty((new_dim,) + x.shape[1:], dtype=np.float32)
    for i in range(new_dim):
        a, b1 = math.modf(float(i) / f)
        b2 = min(b1 + 1, x.shape[0] - 1)
        output[i] = x[int(b1)]*(1-a) + x[int(b2)]*a
    return output


def make_rot(angle, axis_ix):
    s = math.sin(angle)
    c = math.cos(angle)
    if axis_ix == 0:
        return np.array([[1,  0,  0],
                         [0,  c, -s],
                         [0,  s,  c]], dtype=np.float32)
    elif axis_ix == 1:
        return np.array([[c,  0,  s],
                         [0,  1,  0],
                         [-s,  0,  c]], dtype=np.float32)
    elif axis_ix == 2:
        return np.array([[c, -s,  0],
                         [s,  c,  0],
                         [0,  0,  1]], dtype=np.float32)

def reorthogonalize(mat):
    u, _, v = np.linalg.svd(mat)
    return np.dot(u, v)

# move the cursor back , only if the window is focused
def center_mouse():
    if pygame.key.get_focused():
        pygame.mouse.set_pos(screen_center)

def check_displacement_key(key):
    return key == pygame.K_w or key == pygame.K_a or key == pygame.K_s or key == pygame.K_d or key == pygame.K_z or key == pygame.K_x

def process_acceleration(all_keys, speed_accel=ACCELERATION_RATE, max_fps=MAX_FPS):
    """
    Processes keys pressed, computing acceleration 
    """
    acceleration = np.zeros((N_DIMENSIONS,), dtype=np.float32)
    if all_keys[pygame.K_a]:
        acceleration[X] -= speed_accel / max_fps
    if all_keys[pygame.K_d]:
        acceleration[X] += speed_accel / max_fps
    if all_keys[pygame.K_z]:
        acceleration[Y] -= speed_accel / max_fps
    if all_keys[pygame.K_x]:
        acceleration[Y] += speed_accel / max_fps
    if all_keys[pygame.K_w]:
        acceleration[Z] -= speed_accel / max_fps
    if all_keys[pygame.K_s]:
        acceleration[Z] += speed_accel / max_fps

    return acceleration
# --------------------------------------------------
# Help utilities
# --------------------------------------------------


def print_keys():
    help_str = """
	Move: WASDZX
	Run: Space
	Start/stop recording: r
	Play recorded: p
	Screenshot: s
	"""
    print(help_str)

# --------------------------------------------------
#                  Video Recording
#
#    When you're ready to record a video, press 'r'
# to start recording, and then move around.  The
# camera's path and live '0' through '5' parameters
# are recorded to a file.  Press 'r' when finished.
#
#    Now you can exit the program and turn up the
# camera parameters for better rendering.  For
# example; window size, anti-aliasing, motion blur,
# and depth of field are great options.
#
#    When you're ready to playback and render, press
# 'p' and the recorded movements are played back.
# Images are saved to a './playback' folder.  You
# can import the image sequence to editing software
# to convert it to a video.
#
#    You can press 's' anytime for a screenshot.
# ---------------------------------------------------


FRACTALS = [
    fractals.infinite_spheres,
    fractals.butterweed_hills,
    fractals.mandelbox,
    fractals.mausoleum,
    fractals.menger,
    fractals.tree_planet,
    fractals.sierpinski_tetrahedron,
    fractals.snow_stadium,
]


def fractal_options_menu(fractals):
    print("Select one of the fractals below")
    for i_fractal, fractal in enumerate(fractals):
        print("{} - {}".format(i_fractal + 1, fractal.__name__))
    try:
        i_fractal = int(input("Select a number option\n"))
        assert 0 < i_fractal < len(fractals) + 1
        return fractals[i_fractal - 1]
    except ValueError:
        print("Error!")
        return fractal_options_menu(fractals)


def update_control_keys(key_vars, all_keys):
    if all_keys[pygame.K_INSERT]:
        key_vars[0] += rate
    if all_keys[pygame.K_DELETE]:
        key_vars[0] -= rate
    if all_keys[pygame.K_HOME]:
        key_vars[1] += rate
    if all_keys[pygame.K_END]:
        key_vars[1] -= rate
    if all_keys[pygame.K_PAGEUP]:
        key_vars[2] += rate
    if all_keys[pygame.K_PAGEDOWN]:
        key_vars[2] -= rate
    if all_keys[pygame.K_KP7]:
        key_vars[3] += rate
    if all_keys[pygame.K_KP4]:
        key_vars[3] -= rate
    if all_keys[pygame.K_KP8]:
        key_vars[4] += rate
    if all_keys[pygame.K_KP5]:
        key_vars[4] -= rate
    if all_keys[pygame.K_KP9]:
        key_vars[5] += rate
    if all_keys[pygame.K_KP6]:
        key_vars[5] -= rate


if __name__ == '__main__':

    # Display helper
    print_keys()

    # Allow selecting a fractal
    fractal = fractal_options_menu(FRACTALS)

    pygame.init()
    #window = pygame.display.set_mode(win_size, OPENGL | DOUBLEBUF)
    #window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # This is the best looking
    window = pygame.display.set_mode(
        (0, 0), pygame.FULLSCREEN | HWSURFACE | DOUBLEBUF | RESIZABLE)
    pygame.mouse.set_visible(False)
    center_mouse()

    # ======================================================
    #             Change camera settings here
    # See mandelbruh/camera.py for all camera options
    # ======================================================
    camera = Camera()
    camera['ANTIALIASING_SAMPLES'] = 1
    camera['AMBIENT_OCCLUSION_STRENGTH'] = 0.01
    # ======================================================

    obj_render = fractal()
    shader = Shader(obj_render)
    program = shader.compile(camera)
    print("Shader compiled")

    matID = glGetUniformLocation(program, "iMat")
    prevMatID = glGetUniformLocation(program, "iPrevMat")
    resID = glGetUniformLocation(program, "iResolution")
    ipdID = glGetUniformLocation(program, "iIPD")

    glUseProgram(program)
    glUniform2fv(resID, 1, win_size)
    glUniform1f(ipdID, 0.04)

    fullscreen_quad = np.array(
        [-1.0, -1.0, 0.0, 1.0, -1.0, 0.0, -1.0, 1.0, 0.0, 1.0, 1.0, 0.0], dtype=np.float32)
    glVertexAttribPointer(0, N_DIMENSIONS, GL_FLOAT,
                          GL_FALSE, 0, fullscreen_quad)
    glEnableVertexAttribArray(0)

    # TODO comment
    mat = np.identity(N_DIMENSIONS+1, np.float32)
    mat[N_DIMENSIONS, :N_DIMENSIONS] = np.array(START_POSITION)
    prevMat = np.copy(mat)
    for i in range(len(key_vars)):
        shader.set(str(i), key_vars[i])

    recording = None
    rec_vars = None
    playback = None
    playback_vars = None
    playback_ix = -1
    frame_num = 0

    def start_playback():
        global playback
        global playback_vars
        global playback_ix
        global prevMat
        if not os.path.exists('playback'):
            os.makedirs('playback')
        playback = np.load('recording.npy')
        playback_vars = np.load('rec_vars.npy')
        playback = interp_data(playback, 2)
        playback_vars = interp_data(playback_vars, 2)
        playback_ix = 0
        prevMat = playback[0]

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                print("Keydown detected", frame_num, event.key)
                if event.key == pygame.K_r:
                    if recording is None:
                        print("Recording...")
                        recording = []
                        rec_vars = []
                    else:
                        np.save('recording.npy', np.array(
                            recording, dtype=np.float32))
                        np.save('rec_vars.npy', np.array(
                            rec_vars, dtype=np.float32))
                        recording = None
                        rec_vars = None
                        print("Finished Recording.")
                elif event.key == pygame.K_p:
                    start_playback()
                elif event.key == pygame.K_c:
                    pygame.image.save(window, 'screenshot.png')
                elif event.key == pygame.K_ESCAPE:
                    sys.exit(0)
                elif event.key == pygame.K_INSERT:
                    lock_mouse = not lock_mouse
                    pygame.mouse.set_visible(not lock_mouse)
                elif check_displacement_key(event.key):
                    keep_moving = True
            elif event.type == pygame.KEYUP:
                print("Keyup detected", frame_num, event.key)
                if check_displacement_key(event.key):
                    keep_moving = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                print("Mouse motion detected", frame_num, mouse_pos)

        mat[N_DIMENSIONS, :N_DIMENSIONS] += velocity * clock.get_time() / 1000

        # Update distance to object
        if auto_velocity:
            de = np.log(obj_render.DE(mat[N_DIMENSIONS]) + 1) * auto_multiplier
            if not np.isfinite(de):
                de = 0.0
        else:
            de = 1e20

        all_keys = pygame.key.get_pressed()

        rate = 0.01
        if all_keys[pygame.K_LSHIFT]:
            rate *= 0.1
        elif all_keys[pygame.K_RSHIFT]:
            rate *= 10.0

        update_control_keys(key_vars, all_keys)

        # If not playing a recorded trip
        if playback is None:
            # If the mouse is locked to be used as camera
            if lock_mouse:
                prev_mouse_pos = mouse_pos
                mouse_pos = pygame.mouse.get_pos()
                dx, dy = 0, 0
                if prev_mouse_pos is not None:
                    center_mouse()
                    time_rate = clock.get_time() / 1000.0 * MAX_FPS
                    dx = (mouse_pos[0] - screen_center[0]) * time_rate
                    dy = (mouse_pos[1] - screen_center[1]) * time_rate
                    print("Computing dx, dy", frame_num, dx, dy, mouse_pos)
                else:
                    print("Prev mouse position is none", frame_num, dx, dy, mouse_pos)

            # If we recceive input from keyboard
            if pygame.key.get_focused():
                if gimbal_lock:
                    look_x += dx * look_speed
                    look_y += dy * look_speed
                    look_y = min(max(look_y, -math.pi/2), math.pi/2)

                    rx = make_rot(look_x, 1)
                    ry = make_rot(look_y, 0)

                    mat[:N_DIMENSIONS, :N_DIMENSIONS] = np.dot(ry, rx)
                else:
                    rx = make_rot(dx * look_speed, 1)
                    ry = make_rot(dy * look_speed, 0)

                    mat[:N_DIMENSIONS, :N_DIMENSIONS] = np.dot(ry, np.dot(rx, mat[:N_DIMENSIONS, :N_DIMENSIONS]))
                    mat[:N_DIMENSIONS, :N_DIMENSIONS] = reorthogonalize(mat[:N_DIMENSIONS, :N_DIMENSIONS])
                    print("Applying dx, dy", frame_num, dx, dy)

            acceleration = process_acceleration(all_keys)
            print("Processed acceleration", frame_num, velocity)

            if (acceleration != 0.0).sum() == 0.0:
                velocity *= FRICTION
            else:
                velocity += np.dot(mat[:N_DIMENSIONS,:N_DIMENSIONS].T, acceleration)
                vel_ratio = min(max_velocity, de) / \
                    (np.linalg.norm(velocity) + EPS)
                if vel_ratio < 1.0:
                    velocity *= vel_ratio
                print("Applied velocity", frame_num, velocity)

            if all_keys[pygame.K_SPACE]:
                velocity *= 10.0

            if recording is not None:
                recording.append(np.copy(mat))
                rec_vars.append(np.array(key_vars, dtype=np.float32))
        else:
            if playback_ix >= 0:
                ix_str = "{:04d}".format(playback_ix)
                pygame.image.save(window, 'playback/frame' + ix_str + '.png')
            if playback_ix >= playback.shape[0]:
                playback = None
                break
            else:
                # Move smoothly between frames
                mat = prevMat * PLAY_BACK_FRAME_INTERPOLATION_RATE + \
                    playback[playback_ix] * \
                    (1.0 - PLAY_BACK_FRAME_INTERPOLATION_RATE)
                mat[:N_DIMENSIONS, :N_DIMENSIONS] = reorthogonalize(
                    mat[:N_DIMENSIONS, :N_DIMENSIONS])
                key_vars = playback_vars[playback_ix].tolist()
                playback_ix += 1

        for i in range(N_DIMENSIONS):
            shader.set(str(i), key_vars[i])

        shader.set('v', np.array(key_vars[N_DIMENSIONS:2*N_DIMENSIONS]))
        shader.set('pos', mat[N_DIMENSIONS, :N_DIMENSIONS])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniformMatrix4fv(matID, 1, False, mat)
        glUniformMatrix4fv(prevMatID, 1, False, prevMat)
        prevMat = np.copy(mat)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        pygame.display.flip()
        clock.tick(MAX_FPS)
        frame_num += 1
        # Avoid printing
        # print(clock.get_fps())
