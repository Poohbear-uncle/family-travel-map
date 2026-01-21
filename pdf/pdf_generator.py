from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

pdfmetrics.registerFont(TTFont("Korean", "fonts/NotoSansKR-Regular.ttf"))

def generate_pdf(itinerary, map_image_path, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    style = ParagraphStyle("k", fontName="Korean", fontSize=12, leading=16)
    title = ParagraphStyle("t", fontName="Korean", fontSize=22, leading=26)

    elements = []
    elements.append(Paragraph("가족 여행 일정", title))

    if map_image_path and os.path.exists(map_image_path):
        elements.append(Image(map_image_path, width=16*cm, height=10*cm))
    else:
        elements.append(Paragraph("📌 지도 이미지는 네트워크 문제로 생략되었습니다.", style))

    for i, item in enumerate(itinerary,1):
        elements.append(
            Paragraph(
                f"<b>{i}. {item['name_ko']}</b> ({item.get('name_ja','')})<br/>"
                f"🕒 {item.get('start','')} ~ {item.get('end','')}<br/>"
                f"{item.get('note','')}",
                style
            )
        )

    doc.build(elements)
