# 1️⃣ import
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

# 2️⃣ 한글 폰트 등록 (맨 위!)
pdfmetrics.registerFont(
    TTFont("Korean", "fonts/NotoSansKR-Regular.ttf")
)

# 3️⃣ generate_pdf 함수
def generate_pdf(itinerary, map_image_path, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)

    style = ParagraphStyle(
        "Korean",
        fontName="Korean",
        fontSize=11,
        leading=15
    )

    elements = []
    elements.append(Paragraph("가족 여행 일정", style))

    # 📍 지도 이미지 (있을 때만)
    if map_image_path and os.path.exists(map_image_path):
        elements.append(Image(map_image_path, width=16*cm, height=10*cm))
    else:
        elements.append(
            Paragraph(
                "📌 지도 이미지는 네트워크 환경으로 인해 포함되지 않았습니다.",
                style
            )
        )

    # 일정 목록
    for i, item in enumerate(itinerary, 1):
        elements.append(
            Paragraph(f"{i}. {item['name_ko']}<br/>{item.get('note','')}", style)
        )

    # 4️⃣ 반드시 맨 마지막
    doc.build(elements)
