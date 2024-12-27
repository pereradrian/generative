from PIL import Image, ImageOps, ExifTags, ImageEnhance
import numpy as np
import os
import random

def correct_orientation(image):
    """Corrige la orientación de una imagen según sus datos EXIF."""
    try:
        exif = image._getexif()
        if exif is not None:
            orientation_tag = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            if orientation_tag is not None:
                orientation = exif.get(orientation_tag, None)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
    except Exception as e:
        print(f"Error al corregir la orientación: {e}")
    return image

def crop_to_square(image):
    """Recorta una imagen al tamaño cuadrado desde su centro."""
    width, height = image.size
    if width == height:
        return image  # Ya es cuadrada
    min_side = min(width, height)
    left = (width - min_side) // 2
    top = (height - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    return image.crop((left, top, right, bottom))

def resize_image(image, scale_factor):
    """Amplía la imagen base por un factor dado."""
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image.resize((new_width, new_height), Image.LANCZOS)

def apply_mask(tile, avg_color_target, factor):
    """
    Ajusta una baldosa para que se asemeje más a la región objetivo de la imagen base.
    
    Args:
        tile (Image): La baldosa que se va a ajustar.
        avg_color_target (float): El color promedio de la región objetivo.
        tile_avg_color (float): El color promedio de la baldosa.
    
    Returns:
        Image: La baldosa ajustada.
    """
    # Ajustar brillo
    tile_avg_color = calculate_avg_color(tile)
    new_avg_color = (1 - factor) * tile_avg_color + factor * avg_color_target
    brightness_factor = new_avg_color / tile_avg_color
    enhancer = ImageEnhance.Brightness(tile)
    adjusted_tile = enhancer.enhance(brightness_factor)

    # Si deseas ajustar colores, puedes expandir aquí
    # adjusted_tile = adjust_color(adjusted_tile, avg_color_target)

    return adjusted_tile


def resize_images(image_folder, tile_size, avg_color_target, factor):
    """Recorta y redimensiona todas las imágenes de una carpeta al tamaño especificado."""
    resized_images = []
    for file in os.listdir(image_folder):
        if file.endswith(('.jpg', '.png', '.jpeg')):
            img = Image.open(os.path.join(image_folder, file))
            img = correct_orientation(img)  # Recortar al tamaño cuadrado
            img = crop_to_square(img)  # Recortar al tamaño cuadrado
            img = img.resize(tile_size)  # Redimensionar al tamaño de baldosa
            img = img.convert("L")
            img = apply_mask(img, avg_color_target, factor)
            resized_images.append((img, np.array(img).mean(axis=(0, 1))))  # Imagen y su color promedio
    return resized_images

def calculate_avg_color(image):
    """Calcula el color promedio de una imagen."""
    image_array = np.array(image)
    return image_array.mean(axis=(0, 1))

def find_closest_tile(avg_color, tiles):
    """Encuentra la baldosa cuyo color promedio es más cercano al objetivo."""
    distances = [np.linalg.norm(avg_color - tile[1]) for tile in tiles]
    return tiles[np.argmin(distances)][0]

def weighted_random_choice(avg_color, tiles):
    """
    Selecciona una baldosa de manera aleatoria ponderada según la similitud de colores.
    
    Args:
        avg_color (float): El color promedio de la región objetivo.
        tiles (list of tuples): Lista de baldosas con su brillo promedio [(Image, avg_brightness), ...].
    
    Returns:
        Image: La baldosa seleccionada.
    """
    weights = []
    for _, tile_avg_color in tiles:
        # Calcular peso inverso de la diferencia de color promedio
        weight = 1 / (1 + abs(tile_avg_color - avg_color))
        weights.append(weight*weight*weight*weight)
    
    # Normalizar pesos
    total_weight = sum(weights)
    probabilities = [w / total_weight for w in weights]
    
    # Selección ponderada
    return random.choices(tiles, weights=probabilities, k=1)[0][0]

def adjust_base_image(image, num_tiles_height):
    """Ajusta la imagen base para que encaje con el número de baldosas especificado en el alto."""
    width, height = image.size
    
    # Tamaño de cada baldosa basado en el alto
    tile_size = height // num_tiles_height
    
    # Número de baldosas en el ancho
    num_tiles_width = width // tile_size
    
    # Nuevo ancho y alto ajustados
    new_width = num_tiles_width * tile_size
    new_height = num_tiles_height * tile_size
    
    # Recortar la imagen para ajustarse a las dimensiones exactas
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    return image.crop((left, top, right, bottom)), (num_tiles_width, num_tiles_height), tile_size

def create_collage(base_image, tiles, grid_size):
    """Crea un collage basado en una imagen y un conjunto de baldosas."""
    base_image = base_image.resize(grid_size)
    base_pixels = np.array(base_image)
    tile_width, tile_height = tiles[0][0].size
    collage = Image.new('RGB', (grid_size[0] * tile_width, grid_size[1] * tile_height))

    for i in range(grid_size[1]):  # Filas
        for j in range(grid_size[0]):  # Columnas
            avg_color = base_pixels[i, j]
            closest_tile = weighted_random_choice(avg_color, tiles)
            collage.paste(closest_tile, (j * tile_width, i * tile_height))

    return collage
