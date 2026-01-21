from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

def generate_pdf(itinerary, map_image_path, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(
        "가족 자유여행 일정",
        ParagraphStyle(
            "title",
            fontSize=20,
            spaceAfter=20
        )
    )
    elements.append(title)

    # ---- 지도 영역 ----
    if map_image_path and os.path.exists(map_image_path):
        elements.append(Image(map_image_path, width=16*cm, height=10*cm))
    else:
        elements.append(
            Paragraph(
                "📌 지도 이미지 안내<br/>"
                "네트워크 환경 문제로 지도 이미지를 불러오지 못했습니다.<br/>"
                "아래 일정 정보는 정상적으로 확인 및 인쇄하실 수 있습니다.",
                styles["Normal"]
            )
        )

    elements.append(PageBreak())

    # ---- 일정 상세 ----
    for idx, item in enumerate(itinerary, start=1):
        text = f"""
        <b>{idx}. {item['name_ko']}</b>
        {f"({item['name_ja']})" if item.get("name_ja") else ""}<br/>
        🕒 {item.get('start','')} ~ {item.get('end','')}<br/>
        {item.get('note','')}
        """
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 0.7*cm))

    doc.build(elements)
