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
            'size_small': 50,

            'name': {'y': 540, 'x': 'center', 'type': 'simple'},
            'number': {'y': 2980, 'x': 120, 'type': 'simple'},
            'date': {'y': 3100, 'x': 60, 'type': 'simple'},

            'title': {
                'type': 'autofit_v_center',
                'y_start': 860,
                'y_end': 1225,
                'max_width': 2200,
                'max_size': 120,
                'min_size': 40
            },
            'program': {
                'type': 'autofit_top',
                'y_start': 1330,
                'y_end': 2685,
                'max_width': 2200,
                'max_size': 60,
                'min_size': 25
            },
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
            'size_small': 50,

            'name': {'y': 390, 'x': 'center', 'type': 'simple'},
            'number': {'y': 2955, 'x': 120, 'type': 'simple'},
            'date': {'y': 3025, 'x': 200, 'type': 'simple'},

            'title': {
                'type': 'autofit_v_center',
                'y_start': 750,
                'y_end': 1135,
                'max_width': 2300,
                'max_size': 90,
                'min_size': 40
            },
            'program': {
                'type': 'autofit_top',
                'y_start': 1250,
                'y_end': 2840,
                'max_width': 2300,
                'max_size': 60,
                'min_size': 25
            },
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
            return None

        image = Image.open(path).convert('RGB')
        draw = ImageDraw.Draw(image)
        img_w, img_h = image.size

        def draw_field(text, key, font_path, size, color):
            if not text: return
            cfg = style[key]

            if cfg.get('type') == 'autofit_v_center' or cfg.get('type') == 'autofit_top':
                max_h = cfg['y_end'] - cfg['y_start']
                max_w = cfg['max_width']
                current_size = cfg['max_size']
                min_size = cfg['min_size']

                final_font = None
                final_lines = []
                final_total_h = 0

                while current_size >= min_size:
                    font = get_font(font_path, current_size)
                    lines = wrap_text_pixel(text, font, max_w, draw)

                    total_h = 0
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        total_h += (bbox[3] - bbox[1]) + 15
                    total_h -= 15

                    if total_h <= max_h:
                        final_font = font
                        final_lines = lines
                        final_total_h = total_h
                        break

                    current_size -= 2

                if final_font is None:
                    final_font = get_font(font_path, min_size)
                    final_lines = wrap_text_pixel(text, final_font, max_w, draw)
                    final_total_h = 0
                    for line in final_lines:
                        bbox = draw.textbbox((0, 0), line, final_font, fill=color)
                        final_total_h += (bbox[3] - bbox[1]) + 15
                    final_total_h -= 15

                start_y = cfg['y_start']
                if cfg.get('type') == 'autofit_v_center':
                    start_y = cfg['y_start'] + (max_h - final_total_h) / 2

                max_line_w = 0
                for line in final_lines:
                    bbox = draw.textbbox((0, 0), line, font=final_font)
                    w = bbox[2] - bbox[0]
                    if w > max_line_w: max_line_w = w

                block_start_x = (img_w - max_line_w) / 2

                curr_y = start_y
                for line in final_lines:
                    bbox = draw.textbbox((0, 0), line, font=final_font)
                    line_w = bbox[2] - bbox[0]
                    if cfg.get('type') == 'autofit_v_center':
                        draw_x = (img_w - line_w) / 2
                    else:
                        draw_x = block_start_x

                    draw.text((draw_x, curr_y), line, font=final_font, fill=color)
                    h = bbox[3] - bbox[1]
                    curr_y += h + 15
            elif cfg.get('x') == 'center':
                font = get_font(font_path, size)
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
                font = get_font(font_path, size)
                draw.text((cfg['x'], cfg['y']), str(text), font=font, fill=color)

        draw_field(certificate.full_name, 'name', style['font_main'], style['size_name'], style['color_text'])
        draw_field(certificate.seminar.title, 'title', style['font_main'], 0, style['color_title'])
        draw_field(certificate.seminar.program, 'program', style['font_sec'], 0, style['color_text'])

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