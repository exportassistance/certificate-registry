import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile


def generate_certificates(certificate):
    ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets')
    company = certificate.seminar.company

    font_times = os.path.join(ASSETS_DIR, 'fonts', 'times.ttf')
    font_montserrat = os.path.join(ASSETS_DIR, 'fonts', 'Montserrat-Bold.ttf')
    font_roboto = os.path.join(ASSETS_DIR, 'fonts', 'Roboto.ttf')

    def get_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    if company == 'CSE':
        tpl_clean = 'template_cse_clean.png'
        tpl_stamp = 'template_cse_stamp.png'

        style = {
            'color_title': (180, 0, 0),
            'color_text': (0, 0, 0),
            'font_main': font_times,
            'font_sec': font_times,

            'size_name': 110,
            'size_title': 120,
            'size_prog': 60,
            'size_small': 50,
            'name': {'y': 540, 'x': 'center'},
            'title': {'y': 920, 'x': 'center'},
            'program': {'y': 1380, 'x': 'adaptive', 'max_width': 2200},
            'number': {'y': 2980, 'x': 120},
            'date': {'y': 3100, 'x': 60},
        }

    else:
        tpl_clean = 'template_nika_clean.png'
        tpl_stamp = 'template_nika_stamp.png'

        style = {
            'color_title': (0, 64, 153),
            'color_text': (50, 50, 50),
            'font_main': font_montserrat,
            'font_sec': font_roboto,
            'size_name': 125,
            'size_title': 90,
            'size_prog': 50,
            'size_small': 50,
            'name': {'y': 390, 'x': 'center'},
            'title': {'y': 780, 'x': 'center'},
            'program': {'y': 1300, 'x': 'adaptive', 'max_width': 2300},
            'number': {'y': 2955, 'x': 120},
            'date': {'y': 3025, 'x': 200},
        }

    def wrap_text_pixel(text, font, max_width, draw):
        lines = []
        paragraphs = str(text).replace('\r\n', '\n').split('\n')

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]

                if width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            if current_line:
                lines.append(' '.join(current_line))
        return lines

    def process_image(template_name):
        path = os.path.join(ASSETS_DIR, 'templates', template_name)
        if not os.path.exists(path):
            print(f"Template not found: {path}")
            return None

        image = Image.open(path).convert('RGB')
        draw = ImageDraw.Draw(image)
        img_w, img_h = image.size

        def draw_field(text, key, font_path, size, color):
            if not text: return
            cfg = style[key]
            font = get_font(font_path, size)

            if cfg.get('x') == 'adaptive':
                lines = wrap_text_pixel(text, font, cfg['max_width'], draw)

                max_line_w = 0
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    if (bbox[2] - bbox[0]) > max_line_w:
                        max_line_w = (bbox[2] - bbox[0])

                start_x = (img_w - max_line_w) / 2

                current_y = cfg['y']
                for line in lines:
                    draw.text((start_x, current_y), line, font=font, fill=color)
                    bbox = draw.textbbox((0, 0), line, font=font)
                    h = bbox[3] - bbox[1]
                    current_y += h + 15

            elif cfg.get('x') == 'center':
                lines = wrap_text_pixel(text, font, img_w - 200, draw)
                current_y = cfg['y']
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    x = (img_w - w) / 2
                    draw.text((x, current_y), line, font=font, fill=color)
                    current_y += h + 15

            else:
                draw.text((cfg['x'], cfg['y']), str(text), font=font, fill=color)

        draw_field(certificate.full_name, 'name', style['font_main'], style['size_name'], style['color_text'])
        draw_field(certificate.seminar.title, 'title', style['font_main'], style['size_title'], style['color_title'])
        draw_field(certificate.seminar.program, 'program', style['font_sec'], style['size_prog'], style['color_text'])

        clean_num = certificate.certificate_number.replace('№', '').strip()
        draw_field(clean_num, 'number', style['font_sec'], style['size_small'], style['color_text'])

        s_date = certificate.seminar.date_start.strftime('%d.%m.%Y')
        if certificate.seminar.date_end:
            s_date += f" - {certificate.seminar.date_end.strftime('%d.%m.%Y')}"
        draw_field(s_date, 'date', style['font_sec'], style['size_small'], style['color_text'])

        return image

    try:
        img_clean = process_image(tpl_clean)
        if not img_clean: return None, None, None

        buf_print = BytesIO()
        img_clean.save(buf_print, format='PDF', resolution=300.0)
        file_print = ContentFile(buf_print.getvalue(), f"print_{certificate.certificate_number}.pdf")

        img_stamp = process_image(tpl_stamp)
        if not img_stamp: return None, None, None

        buf_web = BytesIO()
        img_stamp.save(buf_web, format='PDF', resolution=300.0)
        file_web = ContentFile(buf_web.getvalue(), f"web_{certificate.certificate_number}.pdf")

        base_width = 1000
        w_percent = (base_width / float(img_stamp.size[0]))
        h_size = int((float(img_stamp.size[1]) * float(w_percent)))
        img_preview = img_stamp.resize((base_width, h_size), Image.Resampling.LANCZOS)

        buf_jpg = BytesIO()
        img_preview.save(buf_jpg, format='JPEG', quality=85)
        file_preview = ContentFile(buf_jpg.getvalue(), f"preview_{certificate.certificate_number}.jpg")

        return file_print, file_web, file_preview

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None