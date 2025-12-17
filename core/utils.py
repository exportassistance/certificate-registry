import os
import fitz
import uuid
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def pdf_to_jpg(pdf_file_field):
    try:
        if pdf_file_field.closed:
            pdf_file_field.open()
        pdf_data = pdf_file_field.read()
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("jpg")
        return ContentFile(img_data, name=f"preview_manual_{uuid.uuid4().hex[:8]}.jpg")
    except Exception as e:
        print(f"PDF Convert Error: {e}")
        return None


def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split(' ')
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
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


def generate_certificates(certificate):
    ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets')
    company = certificate.seminar.company

    font_times = os.path.join(ASSETS_DIR, 'fonts', 'times.ttf')
    font_times_bold = os.path.join(ASSETS_DIR, 'fonts', 'timesbd.ttf')
    font_montserrat = os.path.join(ASSETS_DIR, 'fonts', 'Montserrat-Bold.ttf')
    font_roboto = os.path.join(ASSETS_DIR, 'fonts', 'Roboto.ttf')

    if company == 'CSE':
        tpl_clean = 'template_cse_clean.png'
        tpl_stamp = 'template_cse_stamp.png'

        style = {
            'font_main': font_times,
            'font_title': font_times_bold,
            'font_sec': font_times,
            'color_title': (180, 0, 0),
            'color_text': (0, 0, 0),

            'name': {
                'type': 'autofit',
                'align': 'center',
                'y_start': 465, 'y_end': 655,
                'max_width': 1600, 'max_size': 110, 'min_size': 50
            },
            'title': {
                'type': 'autofit',
                'align': 'center',
                'y_start': 820, 'y_end': 1185,
                'max_width': 2200, 'max_size': 90, 'min_size': 40
            },
            'program': {
                'type': 'autofit',
                'align': 'left',
                'y_start': 1370, 'y_end': 2685,
                'max_width': 2200, 'max_size': 60, 'min_size': 25
            },
            'number': {'type': 'simple', 'y': 2975, 'x': 120, 'size': 50},
            'date': {'type': 'simple', 'y': 3095, 'x': 60, 'size': 50},
        }
    else:
        tpl_clean = 'template_nika_clean.png'
        tpl_stamp = 'template_nika_stamp.png'

        style = {
            'font_main': font_montserrat,
            'font_title': font_montserrat,
            'font_sec': font_roboto,
            'color_title': (0, 64, 153),
            'color_text': (50, 50, 50),

            'name': {
                'type': 'autofit_one_line',
                'y_center': 480,
                'max_width': 1700,
                'max_size': 130,
                'min_size': 40
            },
            'title': {
                'type': 'autofit',
                'align': 'center',
                'y_start': 770, 'y_end': 1155,
                'max_width': 2300, 'max_size': 90, 'min_size': 40
            },
            'program': {
                'type': 'autofit',
                'align': 'left',
                'y_start': 1300, 'y_end': 2840,
                'max_width': 2300, 'max_size': 60, 'min_size': 25
            },
            'number': {'type': 'simple', 'y': 3030, 'x': 160, 'size': 50},
            'date': {'type': 'simple', 'y': 3097, 'x': 230, 'size': 50},
        }

    def process_image(template_name):
        path = os.path.join(ASSETS_DIR, 'templates', template_name)
        if not os.path.exists(path): return None

        image = Image.open(path).convert('RGB')
        draw = ImageDraw.Draw(image)
        img_w, img_h = image.size

        def draw_field(text, key, font_path, color):
            if not text: return
            cfg = style[key]

            # 1. ONE LINE
            if cfg['type'] == 'autofit_one_line':
                current_size = cfg['max_size']
                min_size = cfg['min_size']
                max_w = cfg['max_width']
                final_font = None
                while current_size >= min_size:
                    font = get_font(font_path, current_size)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    if (bbox[2] - bbox[0]) <= max_w:
                        final_font = font
                        break
                    current_size -= 2
                if not final_font: final_font = get_font(font_path, min_size)

                bbox = draw.textbbox((0, 0), text, font=final_font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                x = (img_w - text_w) / 2
                y = cfg['y_center'] - (text_h / 2)
                draw.text((x, y), text, font=final_font, fill=color)

            elif cfg['type'] == 'autofit':
                current_size = cfg['max_size']
                min_size = cfg['min_size']
                max_h = cfg['y_end'] - cfg['y_start']

                raw_paragraphs = str(text).replace('\r\n', '\n').split('\n')

                line_spacing = 13
                paragraph_spacing = 13

                final_font = None
                final_structure = []
                final_h = 0

                while current_size >= min_size:
                    font = get_font(font_path, current_size)
                    temp_structure = []
                    total_h = 0

                    for para in raw_paragraphs:
                        if not para.strip(): continue
                        lines = wrap_text(para, font, cfg['max_width'], draw)
                        temp_structure.append(lines)

                        for line in lines:
                            bbox = draw.textbbox((0, 0), line, font=font)
                            total_h += (bbox[3] - bbox[1]) + line_spacing

                        total_h += paragraph_spacing

                    if total_h > 0: total_h -= paragraph_spacing

                    if total_h <= max_h:
                        final_font = font
                        final_structure = temp_structure
                        final_h = total_h
                        break
                    current_size -= 2

                if not final_font:
                    final_font = get_font(font_path, min_size)
                    final_structure = []
                    final_h = 0
                    for para in raw_paragraphs:
                        if not para.strip(): continue
                        lines = wrap_text(para, final_font, cfg['max_width'], draw)
                        final_structure.append(lines)
                        for line in lines:
                            bbox = draw.textbbox((0, 0), line, final_font)
                            final_h += (bbox[3] - bbox[1]) + line_spacing
                        final_h += paragraph_spacing
                    if final_h > 0: final_h -= paragraph_spacing

                if key == 'program':
                    start_y = cfg['y_start']
                else:
                    start_y = cfg['y_start'] + (max_h - final_h) / 2

                max_line_w = 0
                for group in final_structure:
                    for line in group:
                        bbox = draw.textbbox((0, 0), line, font=final_font)
                        w = bbox[2] - bbox[0]
                        if w > max_line_w: max_line_w = w

                block_start_x = (img_w - max_line_w) / 2

                curr_y = start_y
                for group in final_structure:
                    for line in group:
                        bbox = draw.textbbox((0, 0), line, font=final_font)
                        line_w = bbox[2] - bbox[0]

                        if cfg['align'] == 'center':
                            draw_x = (img_w - line_w) / 2
                        else:
                            draw_x = block_start_x

                        draw.text((draw_x, curr_y), line, font=final_font, fill=color)
                        curr_y += (bbox[3] - bbox[1]) + line_spacing

                    curr_y += paragraph_spacing

            elif cfg['type'] == 'simple':
                font = get_font(font_path, cfg['size'])
                draw.text((cfg['x'], cfg['y']), str(text), font=font, fill=color)

        draw_field(certificate.full_name, 'name', style['font_main'], style['color_text'])
        draw_field(certificate.seminar.title, 'title', style['font_title'], style['color_title'])
        draw_field(certificate.seminar.program, 'program', style['font_sec'], style['color_text'])
        clean_num = certificate.certificate_number.replace('№', '').strip()
        draw_field(clean_num, 'number', style['font_sec'], style['color_text'])
        s_date = certificate.seminar.date_start.strftime('%d.%m.%Y')

        if certificate.seminar.date_end:
            s_date += f" - {certificate.seminar.date_end.strftime('%d.%m.%Y')}"
        draw_field(s_date, 'date', style['font_sec'], style['color_text'])

        return image

    try:
        unique_suffix = uuid.uuid4().hex[:8]

        img_clean = process_image(tpl_clean)
        if not img_clean: return None, None, None

        buf_print = BytesIO()
        img_clean.save(buf_print, format='PDF', resolution=300.0)
        file_print = ContentFile(buf_print.getvalue(), f"print_{certificate.certificate_number}_{unique_suffix}.pdf")

        img_stamp = process_image(tpl_stamp)
        if not img_stamp: return None, None, None

        buf_web = BytesIO()
        img_stamp.save(buf_web, format='PDF', resolution=300.0)
        file_web = ContentFile(buf_web.getvalue(), f"web_{certificate.certificate_number}_{unique_suffix}.pdf")

        base_width = 1000
        w_percent = (base_width / float(img_stamp.size[0]))
        h_size = int((float(img_stamp.size[1]) * float(w_percent)))
        img_preview = img_stamp.resize((base_width, h_size), Image.Resampling.LANCZOS)

        buf_jpg = BytesIO()
        img_preview.save(buf_jpg, format='JPEG', quality=85)
        file_preview = ContentFile(buf_jpg.getvalue(), f"preview_{certificate.certificate_number}_{unique_suffix}.jpg")

        return file_print, file_web, file_preview

    except Exception as e:
        print(f"Gen Error: {e}")
        return None, None, None
