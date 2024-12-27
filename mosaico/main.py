import argparse
from PIL import Image
import mosaic

def main():
    parser = argparse.ArgumentParser(description="Generates a mosaic of a target image with the images in the tiles folder.")
    parser.add_argument('target', help='Target image.')
    parser.add_argument('tile_folder', help='Tile folder')
    parser.add_argument('output_image', help='Output image')
    args = parser.parse_args()

    # Configuración
    base_image_path = args.target
    tiles_folder = args.tile_folder
    output_collage_path = args.output_image

    # Configuración
    num_tiles_height = 100  # Número de baldosas deseado en el alto
    grid_size = (num_tiles_height, num_tiles_height)

    # Aumentar el límite permitido
    Image.MAX_IMAGE_PIXELS = None

    # Ajustar la imagen base
    scale_factor = 10
    base_image = Image.open(base_image_path)# Ampliar la imagen base
    base_image = base_image.convert("L")
    base_image = mosaic.resize_image(base_image, scale_factor)
    base_image, (num_tiles_width, num_tiles_height), tile_size = mosaic.adjust_base_image(base_image, num_tiles_height)
    avg_color_target = mosaic.calculate_avg_color(base_image)

    tile_size = (tile_size, tile_size)
    # Proceso
    tiles = mosaic.resize_images(tiles_folder, tile_size, avg_color_target, 0.5)
    collage = mosaic.create_collage(base_image, tiles, grid_size)
    collage.save(output_collage_path)
    print(f"Collage guardado en {output_collage_path}")


if __name__ == "__main__":
    main()