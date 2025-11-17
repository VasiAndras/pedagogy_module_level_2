#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

# ---------------------------------------------------------
# FONT – magyar ékezetekhez
# ---------------------------------------------------------
pdfmetrics.registerFont(TTFont("MagyarFont", "DejaVuSans.ttf"))
FONT = "MagyarFont"

PAGE_W, PAGE_H = A4


# ---------------------------------------------------------
# SORSZÁM
# ---------------------------------------------------------
def draw_page_footer(c):
    page_num = c.getPageNumber()
    text = f"Oldal {page_num}"
    c.setFont(FONT, 10)
    c.drawCentredString(PAGE_W / 2, 10 * mm, text)


# ---------------------------------------------------------
# SORTÖRDELÉS
# ---------------------------------------------------------
def wrap_text(text, max_width, c, font, size):
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""

    for w in words:
        test = (current + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w

    if current:
        lines.append(current)

    return lines


# ---------------------------------------------------------
# OLDALTÖRÉS
# ---------------------------------------------------------
def new_page_if_needed(c, y):
    if y < 25 * mm:
        draw_page_footer(c)
        c.showPage()
        c.setFont(FONT, 12)
        return PAGE_H - 30 * mm
    return y


# ---------------------------------------------------------
# PONTOZOTT SOR
# ---------------------------------------------------------
def draw_dotted_line(c, x, y, length=450, spacing=6):
    pos = x
    while pos < x + length:
        c.circle(pos, y, 0.6, stroke=1)
        pos += spacing


# ---------------------------------------------------------
# PDF GENERÁLÁSA egyetlen data.json alapján
# ---------------------------------------------------------
def generate_single_pdf(data_file, template):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    output_name = f"Generated/oralatogatasi_lap_{os.path.splitext(os.path.basename(data_file))[0]}.pdf"
    c = canvas.Canvas(output_name, pagesize=A4)
    c.setFont(FONT, 12)

    margin_left = 25 * mm
    max_width = 160 * mm
    y = PAGE_H - 30 * mm
    line_height = 16

    # -------- TITLE --------
    if "title" in template:
        c.setFont(FONT, 16)
        for line in wrap_text(template["title"], max_width, c, FONT, 16):
            c.drawCentredString(PAGE_W / 2, y, line)
            y -= 20
        c.setFont(FONT, 12)

    # -------- FIELDS --------
    for f in template.get("fields", []):
        field_id = f.get("id", None)
        label = f.get("label", "")
        lines = f.get("lines", 1)

        for line in wrap_text(label, max_width, c, FONT, 12):
            c.drawString(margin_left, y, line)
            y -= 14
            y = new_page_if_needed(c, y)

        value = data.get(field_id, "") if field_id else ""

        if value:
            for line in wrap_text(value, max_width, c, FONT, 12):
                c.drawString(margin_left, y, line)
                y -= 14
                y = new_page_if_needed(c, y)
        else:
            for _ in range(lines):
                draw_dotted_line(c, margin_left, y)
                y -= line_height
                y = new_page_if_needed(c, y)

        y -= 10
        y = new_page_if_needed(c, y)

    # -------- SECTIONS --------
    for section in template.get("sections", []):
        c.setFont(FONT, 14)
        for line in wrap_text(section["title"], max_width, c, FONT, 14):
            c.drawString(margin_left, y, line)
            y -= 20
            y = new_page_if_needed(c, y)
        c.setFont(FONT, 12)

        for q in section.get("questions", []):
            q_id = q.get("id", None)
            q_text = "• " + q.get("text", "")
            lines = q.get("lines", 1)

            for line in wrap_text(q_text, max_width, c, FONT, 12):
                c.drawString(margin_left, y, line)
                y -= 14
                y = new_page_if_needed(c, y)

            value = data.get(q_id, "") if q_id else ""

            if value:
                for line in wrap_text(value, max_width, c, FONT, 12):
                    c.drawString(margin_left, y, line)
                    y -= 14
                    y = new_page_if_needed(c, y)
            else:
                for _ in range(lines):
                    draw_dotted_line(c, margin_left, y)
                    y -= line_height
                    y = new_page_if_needed(c, y)

            y -= 8
            y = new_page_if_needed(c, y)

        y -= 10
        y = new_page_if_needed(c, y)

    draw_page_footer(c)
    c.save()

    print(f"✔ PDF elkészült: {output_name}")


# ---------------------------------------------------------
# MAIN – több data.json → több PDF
# ---------------------------------------------------------
if __name__ == "__main__":
    # Itt add meg a data fájlok listáját
    files = [
        "Database/data01.json",
        "Database/data02.json",
        "Database/data03.json",
        "Database/data04.json",
        "Database/data05.json",
        "Database/data06.json",
        "Database/data07.json",
        "Database/data08.json",
        "Database/data09.json",
        "Database/data10.json",
        "Database/data11.json",
        "Database/data12.json",
        "Database/data13.json",
        "Database/data14.json",
        "Database/data15.json",
    ]

    # template betöltése
    with open("orallatogatasi_template.json", "r", encoding="utf-8") as f:
        template = json.load(f)

    # mindegyikre generálunk egy külön PDF-et
    for f in files:
        if os.path.isfile(f):
            generate_single_pdf(f, template)
        else:
            print(f"⚠ Nem található: {f}")
