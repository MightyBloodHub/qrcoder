import qrcode
from PIL import Image, ImageDraw
from collections import Counter
import tkinter as tk
from tkinter import filedialog, colorchooser
from tkinter import ttk

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

def get_gradient_color(colors, x, y, width, height):
    ratio = (x + y) / (width + height)
    r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
    g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
    b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
    return (r, g, b)

def create_qr_code(data, logo_path=None, filename="custom_qrcode.png", qr_color="black", bg_color="white", shape="circle", gradient=False, frame_width=0, frame_color="black"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    if logo_path:
        logo = Image.open(logo_path)
        gradient_colors = get_dominant_colors(logo)
        basewidth = 60
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)
    else:
        gradient_colors = [(255, 255, 255), (200, 200, 200)]  # Use light gradient colors

    qr_size = qr.get_matrix().__len__()
    img_size = (qr_size * 10, qr_size * 10)

    if gradient:
        background = create_gradient_background(img_size, gradient_colors[0], gradient_colors[1])
    else:
        background = Image.new('RGB', img_size, bg_color)

    qr_image = Image.new('RGBA', img_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(qr_image)
    matrix = qr.get_matrix()

    for y in range(qr_size):
        for x in range(qr_size):
            if matrix[y][x]:
                box = [(x * 10, y * 10), ((x + 1) * 10, (y + 1) * 10)]
                color = qr_color if not gradient else "black"  # Ensure QR code modules are black for high contrast
                if shape == "circle":
                    draw.ellipse(box, fill=color)
                else:
                    draw.rectangle(box, fill=color)

    combined = Image.alpha_composite(background.convert('RGBA'), qr_image)

    if logo_path:
        pos = ((combined.size[0] - logo.size[0]) // 2, (combined.size[1] - logo.size[1]) // 2)
        combined.paste(logo, pos, mask=logo)

    if frame_width > 0:
        img_with_frame = Image.new('RGB', (combined.size[0] + 2 * frame_width, combined.size[1] + 2 * frame_width), frame_color)
        img_with_frame.paste(combined, (frame_width, frame_width))
        combined = img_with_frame

    combined.save(filename)

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")

        self.url_label = tk.Label(root, text="URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        self.logo_label = tk.Label(root, text="Logo Path:")
        self.logo_label.grid(row=1, column=0, padx=10, pady=10)
        self.logo_path = tk.StringVar()
        self.logo_entry = tk.Entry(root, textvariable=self.logo_path, width=50)
        self.logo_entry.grid(row=1, column=1, padx=10, pady=10)
        self.logo_button = tk.Button(root, text="Browse", command=self.browse_logo)
        self.logo_button.grid(row=1, column=2, padx=10, pady=10)

        self.color_label = tk.Label(root, text="QR Code Color:")
        self.color_label.grid(row=2, column=0, padx=10, pady=10)
        self.qr_color = tk.StringVar(value="black")
        self.color_button = tk.Button(root, text="Choose Color", command=self.choose_color)
        self.color_button.grid(row=2, column=1, padx=10, pady=10)

        self.bg_color_label = tk.Label(root, text="Background Color:")
        self.bg_color_label.grid(row=3, column=0, padx=10, pady=10)
        self.bg_color = tk.StringVar(value="white")
        self.bg_color_button = tk.Button(root, text="Choose Background Color", command=self.choose_bg_color)
        self.bg_color_button.grid(row=3, column=1, padx=10, pady=10)

        self.shape_label = tk.Label(root, text="Shape:")
        self.shape_label.grid(row=4, column=0, padx=10, pady=10)
        self.shape = tk.StringVar(value="circle")
        self.shape_menu = ttk.Combobox(root, textvariable=self.shape, values=["circle", "square"])
        self.shape_menu.grid(row=4, column=1, padx=10, pady=10)

        self.gradient_label = tk.Label(root, text="Use Gradient Background:")
        self.gradient_label.grid(row=5, column=0, padx=10, pady=10)
        self.gradient = tk.BooleanVar(value=False)
        self.gradient_check = tk.Checkbutton(root, variable=self.gradient)
        self.gradient_check.grid(row=5, column=1, padx=10, pady=10)

        self.frame_width_label = tk.Label(root, text="Frame Width:")
        self.frame_width_label.grid(row=6, column=0, padx=10, pady=10)
        self.frame_width = tk.IntVar(value=10)
        self.frame_width_entry = tk.Entry(root, textvariable=self.frame_width, width=10)
        self.frame_width_entry.grid(row=6, column=1, padx=10, pady=10)

        self.frame_color_label = tk.Label(root, text="Frame Color:")
        self.frame_color_label.grid(row=7, column=0, padx=10, pady=10)
        self.frame_color = tk.StringVar(value="black")
        self.frame_color_button = tk.Button(root, text="Choose Frame Color", command=self.choose_frame_color)
        self.frame_color_button.grid(row=7, column=1, padx=10, pady=10)

        self.generate_button = tk.Button(root, text="Generate QR Code", command=self.generate_qr_code)
        self.generate_button.grid(row=8, column=0, columnspan=3, pady=20)

    def browse_logo(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("JPEG files", "*.jpeg"),
                ("GIF files", "*.gif"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.logo_path.set(filename)

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose QR Code Color")
        if color[1]:
            self.qr_color.set(color[1])

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.bg_color.set(color[1])

    def choose_frame_color(self):
        color = colorchooser.askcolor(title="Choose Frame Color")
        if color[1]:
            self.frame_color.set(color[1])

    def generate_qr_code(self):
        data = self.url_entry.get()
        logo_path = self.logo_path.get()
        qr_color = self.qr_color.get()
        bg_color = self.bg_color.get()
        shape = self.shape.get()
        gradient = self.gradient.get()
        frame_width = self.frame_width.get()
        frame_color = self.frame_color.get()
        create_qr_code(data, logo_path, qr_color=qr_color, bg_color=bg_color, shape=shape, gradient=gradient, frame_width=frame_width, frame_color=frame_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()
