from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pathlib import Path

def generate_pdf(schedule):
    path = "travel_map.pdf"

    # ✅ 한글 폰트 등록
    font_path = Path("fonts/NotoSansKR-Regular.ttf")
    pdfmetrics.registerFont(TTFont("NotoSansKR", str(font_path)))

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "NotoSansKR"
    styles["Title"].fontName = "NotoSansKR"
    styles["Heading2"].fontName = "NotoSansKR"

    doc = SimpleDocTemplate(path, pagesize=A4)
    story = []

    story.append(Paragraph("가족 일본여행 일정 요약", styles["Title"]))
    story.append(Spacer(1, 20))

    current_day = None
    for e in sorted(schedule, key=lambda x: x["day"]):
        if e["day"] != current_day:
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Day {e['day']}", styles["Heading2"]))
            current_day = e["day"]

        text = f"{e['title_ko']} ({e['title_ja']})<br/>{e.get('memo','')}"
        story.append(Paragraph(text, styles["Normal"]))

    doc.build(story)
    return path
