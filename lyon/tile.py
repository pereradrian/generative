#
# This is a final version 
# 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
from copy import deepcopy
import os

# Constants
X = 1
Y = 0

R = 0
G = 1
B = 2
ALPHA = -1

BLACK = [0,0,0]

CMYK_TO_RGB_MATRIX = [
     ([255, 0, 0] , [122, 122, 0]),
     ([0, 255, 0] , [0, 122, 122]),
     ([0, 0, 255] , [122, 0, 122]),
]
# 122 / 2 = 61
MY_OWN_TO_RGB_MATRIX = [
     ([255, 0, 0] , [61, 183, 0]),
     ([0, 255, 0] , [0, 61, 183]),
     ([0, 0, 255] , [183, 0, 61]),
]


# Functions
def read_transparent_png(filename):
    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    alpha_channel = image_4channel[:,:,3]
    rgb_channels = image_4channel[:,:,:3]

    # White Background Image
    white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255

    # Alpha factor
    alpha_factor = alpha_channel[:,:,np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor,alpha_factor,alpha_factor), axis=2)

    # Transparent Image Rendered on White Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    white = white_background_image.astype(np.float32) * (1 - alpha_factor)
    final_image = base + white
    return base.astype(np.uint8)

def test_tile_function_mass(tile, img):
    return tile.sum()<=img.sum()

def test_tile_function_mask(tile, img):
    return np.linalg.norm(tile - img) < np.linalg.norm(tile)

def posterize(img, n):
    indices = np.arange(0,256)   # List of all colors 
    divider = np.linspace(0,255,n+1)[1] # we get a divider
    quantiz = np.int0(np.linspace(0,255,n)) # we get quantization colors
    color_levels = np.clip(np.int0(indices/divider),0,n-1) # color levels 0,1,2..
    palette = quantiz[color_levels] # Creating the palette
    im2 = palette[img]  # Applying palette on image
    return cv2.convertScaleAbs(im2) # Converting image back to uint8

def add_padding(src, padding):
    return cv2.copyMakeBorder(src, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=BLACK)

def apply_color_transform(img, color_map):
    result = deepcopy(img)
    for key, value in color_map:
        r_mask = (img[:,:,R] == key[R]) 
        g_mask = (img[:,:,G] == key[G]) 
        b_mask = (img[:,:,B] == key[B]) 
        result[r_mask & g_mask & b_mask] = np.asarray(value)
    return result

def tile_selection_function_random(source, tiles, dim, test, axis):
    tile =  tiles[np.random.choice(range(len(tiles)))]
    tile = cv2.resize(tile, dim)
    tile = posterize(tile, 2)
     
    # Check if tile is active
    if test(tile[:,:,axis],source):
        factor = 254
    else:   
        factor = 0
    
    return tile, factor

def tile_selection_function_max_vero(source, tiles, dim, test, axis):
    ## Dimensions must be permuted!
    tiles_use = [cv2.resize(tile, dim[::-1]) for tile in tiles]
    arg_min = np.argmin([np.linalg.norm(source - tile[:,:,axis]) for tile in tiles_use])
    tile =  tiles_use[arg_min]

    # Check if tile is active
    if test(tile[:,:,axis],source):
        factor = 254
    else:   
        factor = 0

    return tile, factor


def tile_image(img, number_of_patches, tiles, offset_tile_factor=0.0,
               tile_selection_function=tile_selection_function_random,
               test_tile_function=test_tile_function_mass):
    print(img.shape)
    # Copy to result
    result = np.zeros_like(img)

    # TODO: add padding to make image square=
    # TODO: here we ave a problem to solve, the tile size must be choosed as current implementation only works with square images!
    # Compute tile dimensions
    image_size = min(img.shape[X], img.shape[Y])
    tile_size = int(image_size / number_of_patches)
    dim = tile_size, tile_size

    for axis in [R,G,B]:
        # Compute a random offset for layer
        if 1 <= offset_tile_factor*tile_size:
            random_x_offset = np.random.randint(0,offset_tile_factor*tile_size)
        else:
            random_x_offset = 0
        if 1 <= offset_tile_factor*tile_size:
            random_y_offset = np.random.randint(0,offset_tile_factor*tile_size)
        else:
            random_y_offset = 0

        #For each patch
        offset_y = 0
        while offset_y + tile_size <= img.shape[Y]:
            l_y = offset_y
            r_y = offset_y + tile_size
            offset_x = 0
            while offset_x + tile_size <= img.shape[X]:
                # Get tile positions
                l_x = offset_x
                r_x = offset_x + tile_size
                # Get patch of image to tile
                source = img[l_y:r_y,l_x:r_x,axis]
                # Get tile and factor
                tile, factor = tile_selection_function(source, tiles, dim, test_tile_function, axis)
                # print(f"Factor: {factor}")
                # Fix patch size and apply
                indices =  (slice(l_y+random_y_offset, r_y+random_y_offset),
                            slice(l_x+random_x_offset, r_x+random_x_offset),
                            axis)
                
                assert (result[l_y+random_y_offset:r_y+random_y_offset,l_x+random_x_offset:r_x+random_x_offset,axis]-result[indices]).sum() == 0
                dst_patch = result[indices]
                patch_size = dst_patch.shape
                #Scale to patch size
                input_patch = factor*tile[:,:,axis]
                # Resize (Wathc out for the ::-1)
                input_patch = cv2.resize(input_patch, patch_size[::-1])
                result[indices] = input_patch
                offset_x += tile_size
            offset_y += tile_size

    # Apply filter, if any intensity -> max intensity
    result[1<result] = 255

    return result

def load_tiles(folder, tile_padding):
    # Load tiles
    tiles = [read_transparent_png(folder + file_name) for file_name in os.listdir(folder)]

    # Apply padding to tiles
    if 0< tile_padding:
        tiles = [add_padding(tile, tile_padding) for tile in tiles]

    return tiles

def load_image(path_to_image): 
    # Load input image
    img=cv2.imread(path_to_image, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Source image not found '{path_to_image}'")
    else:
        return img