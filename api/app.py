from flask import Flask, request, send_file
import qrcode
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import io

app = Flask(__name__)

def get_dominant_colors(image, num_colors=2):
    image = image.convert('RGB')
    pixels = list(image.getdata())
    count = Counter(pixels)
    return [color[0] for color in count.most_common(num_colors)]

def create_gradient_background(size, color1, color2):
    base = Image.new('RGB', size, color1)
    top = Image.new('RGB', size, color2)
    mask = Image.new('L', size)
    mask_data = []
    for y in range(size[1]):
        for x in range(size[0]):
            mask_data.append(int(255 * (y / size[1])))
    mask.putdata(mask_data)
    gradient = Image.composite(base, top, mask)
    return gradient

@app.route('/generate_qrcode', methods=['POST'])
def generate_qrcode():
    data = request.form['data']
    logo = request.files.get('logo')
    shape = request.form.get('shape', 'square')
    gradient = request.form.get('gradient', 'false').lower() == 'true'
    frame_width = int(request.form.get('frame_width', 0))
    frame_color = request.form.get('frame_color', 'black')
    custom_text = request.form.get('custom_text')
    text_color = request.form.get('text_color', 'black')
    text_font = request.form.get('text_font', 'Arial')
    text_size = int(request.form.get('text_size', 20))
    bold = request.form.get('bold', 'false').lower() == 'true'
    italic = request.form.get('italic', 'false').lower() == 'true'
    underline = request.form.get('underline', 'false').lower() == 'true'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    if logo:
        logo_image = Image.open(logo)
        gradient_colors = get_dominant_colors(logo_image)
        basewidth = 60
        wpercent = (basewidth / float(logo_image.size[0]))
        hsize = int((float(logo_image.size[1]) * float(wpercent)))
        logo_image = logo_image.resize((basewidth, hsize), Image.LANCZOS)
    else:
        gradient_colors = [(255, 255, 255), (200, 200, 200)]  # Use light gradient colors

    qr_size = qr.get_matrix().__len__()
    img_size = (qr_size * 10, qr_size * 10)

    if gradient:
        background = create_gradient_background(img_size, gradient_colors[0], gradient_colors[1])
    else:
        background = Image.new('RGB', img_size, 'white')

    qr_image = Image.new('RGBA', img_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(qr_image)
    matrix = qr.get_matrix()

    for y in range(qr_size):
        for x in range(qr_size):
            if matrix[y][x]:
                box = [(x * 10, y * 10), ((x + 1) * 10, (y + 1) * 10)]
                color = 'black'  # Ensure QR code modules are black for high contrast
                if shape == 'circle':
                    draw.ellipse(box, fill=color)
                else:
                    draw.rectangle(box, fill=color)

    combined = Image.alpha_composite(background.convert('RGBA'), qr_image)

    if logo:
        pos = ((combined.size[0] - logo_image.size[0]) // 2, (combined.size[1] - logo_image.size[1]) // 2)
        combined.paste(logo_image, pos, mask=logo_image)

    if custom_text:
        draw = ImageDraw.Draw(combined)
        font_style = ''
        if bold:
            font_style += 'Bold'
        if italic:
            font_style += 'Italic'
        
        # Fallback to a default font if the specified font is not found
        try:
            font_path = f"/Library/Fonts/{text_font} {font_style}.ttf" if font_style else f"/Library/Fonts/{text_font}.ttf"
            font = ImageFont.truetype(font_path, text_size)
        except IOError:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), custom_text, font=font)
        text_size_calculated = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
        text_position = ((combined.size[0] - text_size_calculated[0]) // 2, combined.size[1] - text_size_calculated[1] - 10)
        draw.text(text_position, custom_text, fill=text_color, font=font)

        if underline:
            underline_y = text_position[1] + text_size_calculated[1]
            draw.line([(text_position[0], underline_y), (text_position[0] + text_size_calculated[0], underline_y)], fill=text_color, width=2)

    if frame_width > 0:
        img_with_frame = Image.new('RGB', (combined.size[0] + 2 * frame_width, combined.size[1] + 2 * frame_width), frame_color)
        img_with_frame.paste(combined, (frame_width, frame_width))
        combined = img_with_frame

    output = io.BytesIO()
    combined.save(output, format='PNG')
    output.seek(0)

    return send_file(output, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

if __name__ == '__main__':
    app.run(debug=True)
