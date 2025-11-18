#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


# ---------------------------------------------------------
# FONT – Times New Roman + ékezetek
# ---------------------------------------------------------
pdfmetrics.registerFont(TTFont("TimesNewRoman", "C:/Windows/Fonts/TIMES.TTF"))
FONT = "TimesNewRoman"

PAGE_W, PAGE_H = A4


# ---------------------------------------------------------
# JUSTIFIED paragraph rajzolása
# ---------------------------------------------------------
def draw_justified(c, text, x, y, max_width):
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        'Justify',
        parent=styles['Normal'],
        fontName=FONT,
        fontSize=12,
        leading=20,
        alignment=TA_JUSTIFY
    )

    para = Paragraph(text, style)
    w, h = para.wrap(max_width, PAGE_H)

    if y - h < 25 * mm:
        draw_page_footer(c)
        c.showPage()
        c.setFont(FONT, 12)
        y = PAGE_H - 30 * mm

    para.drawOn(c, x, y - h)
    return y - h - 5


# ---------------------------------------------------------
# SORSZÁM – oldalszám a láblécben
# ---------------------------------------------------------
def draw_page_footer(c):
    page_num = c.getPageNumber()
    text = f"{page_num}"
    c.setFont(FONT, 10)
    c.drawCentredString(PAGE_W / 2, 10 * mm, text)


# ---------------------------------------------------------
# SORTÖRDELÉS – balra igazított szöveghez
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

    os.makedirs("Generated", exist_ok=True)
    out_name = f"Generated/oralatogatasi_lap_{os.path.splitext(os.path.basename(data_file))[0]}.pdf"

    c = canvas.Canvas(out_name, pagesize=A4)
    c.setFont(FONT, 12)

    margin_left = 25 * mm
    max_width = 160 * mm
    y = PAGE_H - 30 * mm
    line_height = 16

    # -------- TITLE --------
    if "title" in template:
        c.setFont(FONT, 16)
        for line in wrap_text(template["title"], max_width, c, FONT, 20):
            c.drawString(margin_left, y, line)
            y -= 20
        c.setFont(FONT, 12)

# -------- FIELDS TABLE --------
    table_data = []

    for f in template.get("fields", []):
        field_id = f.get("id", None)
        label = f.get("label", "")
        value = data.get(field_id, "") if field_id else ""

        # ha üres → pontozott vonal
        if not value.strip():
            value = "................................................"

        table_data.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle(
                name='LabelStyle',
                fontName=FONT,
                fontSize=12,
                leading=14
            )),
            Paragraph(value, ParagraphStyle(
                name='ValueStyle',
                fontName=FONT,
                fontSize=12,
                leading=14
            ))
        ])

    # táblázat készítése
    table = Table(table_data, colWidths=[60 * mm, 100 * mm])

        # táblázat stílus – teljes keretezés
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT, 12),

        # külső keret
        ("BOX", (0, 0), (-1, -1), 1.2, colors.black),

        # belső vonalak (rács)
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        # igazítás és paddings
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    # automatikus oldaltörés kezelés
    w, h = table.wrapOn(c, 0, 0)

    if y - h < 25 * mm:
        draw_page_footer(c)
        c.showPage()
        y = PAGE_H - 30 * mm
        c.setFont(FONT, 12)

    table.drawOn(c, margin_left, y - h)
    y -= h + 20

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

            # kérdés balra igazítva
            for line in wrap_text(q_text, max_width, c, FONT, 12):
                c.drawString(margin_left, y, line)
                y -= 14
                y = new_page_if_needed(c, y)

            # válasz justified
            value = data.get(q_id, "") if q_id else ""

            if value.strip():
                y = draw_justified(c, value, margin_left, y, max_width)
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

    print(f"✔ PDF elkészült: {out_name}")


# ---------------------------------------------------------
# MAIN – több data.json → több PDF
# ---------------------------------------------------------
if __name__ == "__main__":
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
        "Database/data15.json"
    ]

    with open("orallatogatasi_template.json", "r", encoding="utf-8") as f:
        template = json.load(f)

    for f in files:
        if os.path.isfile(f):
            generate_single_pdf(f, template)
        else:
            print(f"⚠ Nem található: {f}")
