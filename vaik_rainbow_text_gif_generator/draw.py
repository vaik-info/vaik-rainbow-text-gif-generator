import os
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import colorsys

def generate_rainbow_image(image_shape, band_width=90, angle=0, start_h_angle=0, poster_bit=1):
    canvas_image = np.zeros((max(image_shape), max(image_shape), 3), dtype=np.uint8)

    # create_band_image
    h_width = 180
    canvas_band_image = np.zeros((int(max(image_shape)*(h_width/band_width)), max(image_shape), 3), dtype=np.uint8)
    current_angle = start_h_angle % h_width
    for row in range(canvas_band_image.shape[0]):
        current_angle = (current_angle+1) % h_width
        poster_bit_angle = (current_angle // poster_bit) * poster_bit
        rgb = colorsys.hsv_to_rgb(poster_bit_angle/h_width, 1, 1)
        canvas_band_image[row, :] = (int(255*rgb[0]), int(255*rgb[1]), int(255*rgb[2]))
    canvas_image = np.asarray(Image.fromarray(canvas_band_image).resize((canvas_image.shape[1], canvas_image.shape[0])))

    # rotate and crop
    canvas_image = np.asarray(Image.fromarray(canvas_image).rotate(angle))
    start_y, start_x = int((canvas_image.shape[0] - image_shape[0]) / 2), int((canvas_image.shape[1] - image_shape[1]) / 2)
    canvas_image = canvas_image[start_y:start_y+image_shape[0], start_x: start_x+image_shape[1], :]
    return canvas_image

def draw_text(text, font_path, font_size):
    canvas_size = (len(text) * font_size, int(font_size * 1.2))
    pil_image = Image.new('RGB', canvas_size, (0, 0, 0))
    pil_draw = ImageDraw.Draw(pil_image)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = pil_draw.textsize(text, font=font)

    canvas_size = (text_width, text_height)
    pil_image = Image.new('RGB', canvas_size, (0, 0, 0))
    pil_draw = ImageDraw.Draw(pil_image)
    pil_draw.text(((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2), text, fill=(255, 255, 255),
                  font=font)
    return np.asarray(pil_image)

def draw_edge(text_image, iterations=1):
    filter_text_image = Image.fromarray(text_image)
    for _ in range(iterations):
        filter_text_image = filter_text_image.filter(ImageFilter.MaxFilter)

    edge_image = np.asarray(filter_text_image) - text_image

    return edge_image

def merge_text_rainbow_images(text_image, rainbow_image, edge_image, edge_color=(0, 0, 0)):
    canvas_image = np.zeros((text_image.shape[0], text_image.shape[1], 4), dtype=np.uint8)
    canvas_image[text_image[:, :, 0] > 0, -1] = 255
    canvas_image[text_image[:, :, 0] > 0, :-1] = rainbow_image[text_image[:, :, 0] > 0]
    canvas_image[edge_image[:, :, 0] > 0, -1] = 255
    canvas_image[edge_image[:, :, 0] > 0, :-1] = edge_color
    return canvas_image


def draw(text, font_path, font_size, output_git_path, angle=5, band_width=360, duration=20):
    text_image = draw_text(text, font_path, font_size)
    edge_image = draw_edge(text_image)
    gif_image_list = []
    for image_index in range(180):
        rainbow_image = generate_rainbow_image(text_image.shape, band_width, angle, image_index)
        merge_image = merge_text_rainbow_images(text_image, rainbow_image, edge_image)
        if image_index % 3 == 0:
            gif_image_list.append(Image.fromarray(merge_image))
    gif_image_list[0].save(output_git_path,
                   save_all=True, append_images=gif_image_list[1:], optimize=False, duration=duration, loop=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='draw rainbow text gif generator')
    parser.add_argument('--text', type=str, default='77.7%')
    parser.add_argument('--font_size', type=int, default=128)
    parser.add_argument('--font_path', type=str, default=os.path.join(os.path.dirname(__file__), 'fonts/ipag.ttf'))
    parser.add_argument('--output_git_path', type=str, default='./rainbow_text.gif')

    args = parser.parse_args()

    args.font_path = os.path.expanduser(args.font_path)
    args.output_git_path = os.path.expanduser(args.output_git_path)
    draw(args.text, args.font_path, args.font_size, args.output_git_path)
