from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

import os

def generate_pdf(itinerary, map_image_path, output_path):
    pdfmetrics.registerFont(
        TTFont("Nanum", "fonts/NanumGothic.ttf")
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Nanum"
    styles["Title"].fontName = "Nanum"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elements = []

    # 1️⃣ 지도 페이지
    elements.append(
        Paragraph("🗺️ 가족 여행 전체 지도", styles["Title"])
    )
    elements.append(Spacer(1, 12))

    if map_image_path and os.path.exists(map_image_path):
        elements.append(Image(map_image_path, width=16*cm, height=10*cm))

    if map_image_path and os.path.exists(map_image_path):
        elements.append(
            Image(map_image_path, width=16*cm, height=10*cm)
        )
    else:
        elements.append(
            Paragraph("지도 이미지 없음", styles["Normal"])
        )

    elements.append(PageBreak())

    # 2️⃣ 일정 페이지
    elements.append(
        Paragraph("📋 여행 일정 요약", styles["Title"])
    )
    elements.append(Spacer(1, 12))

    for item in itinerary:
        text = f"""
        <b>📍 {item['name_ko']}</b>
        {f" ({item['name_ja']})" if item.get('name_ja') else ""}<br/>
        🕒 {item.get('start','')} ~ {item.get('end','')}<br/>
        {item.get('note','')}
        """
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)

