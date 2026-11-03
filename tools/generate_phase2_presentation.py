from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Phase2_Serverless_Computer_Vision_Pipeline.pptx"

NAVY = RGBColor(20, 39, 70)
BLUE = RGBColor(46, 116, 181)
LIGHT_BLUE = RGBColor(221, 235, 247)
GRAY = RGBColor(90, 90, 90)
WHITE = RGBColor(255, 255, 255)


def add_footer(slide, number):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(7.05), Inches(12.3), Inches(0.25))
    tf = box.text_frame
    tf.text = f"Serverless Computer Vision Pipeline | Phase 2 | {number}"
    tf.paragraphs[0].font.size = Pt(9)
    tf.paragraphs[0].font.color.rgb = GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.RIGHT


def add_title(slide, title, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(0.25), Inches(12.2), Inches(0.65))
    tf = box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(28)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = NAVY
    if subtitle:
        sub = slide.shapes.add_textbox(Inches(0.6), Inches(0.9), Inches(12), Inches(0.35))
        stf = sub.text_frame
        stf.text = subtitle
        stf.paragraphs[0].font.size = Pt(13)
        stf.paragraphs[0].font.color.rgb = GRAY


def add_bullets(slide, bullets, left=0.8, top=1.4, width=11.5, height=5.2, size=21):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    for index, item in enumerate(bullets):
        paragraph = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        paragraph.text = item
        paragraph.level = 0
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = RGBColor(30, 30, 30)
        paragraph.space_after = Pt(10)
    return box


def add_code(slide, text, left=0.8, top=1.5, width=11.4, height=4.8):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(35, 38, 42)
    shape.line.color.rgb = BLUE
    tf = shape.text_frame
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.15)
    tf.text = text
    tf.paragraphs[0].font.name = "Consolas"
    tf.paragraphs[0].font.size = Pt(15)
    tf.paragraphs[0].font.color.rgb = WHITE


def add_architecture(slide):
    labels = [
        ("Client", 0.7, 2.5),
        ("S3\nprivat", 3.0, 2.5),
        ("Lambda\nPython 3.12", 5.5, 2.5),
        ("Pillow\nBildanalyse", 8.3, 1.6),
        ("DynamoDB", 8.3, 3.4),
        ("SQS DLQ", 10.7, 2.5),
    ]
    for label, left, top in labels:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left),
            Inches(top),
            Inches(1.8),
            Inches(0.9),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_BLUE
        shape.line.color.rgb = BLUE
        tf = shape.text_frame
        tf.text = label
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    arrows = [
        (2.5, 2.95, 3.0, 2.95),
        (4.8, 2.95, 5.5, 2.95),
        (7.3, 2.75, 8.3, 2.05),
        (7.3, 3.15, 8.3, 3.85),
        (7.3, 2.95, 10.7, 2.95),
    ]
    for x1, y1, x2, y2 in arrows:
        line = slide.shapes.add_connector(
            1, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
        )
        line.line.color.rgb = BLUE
        line.line.width = Pt(2)


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY
    title = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.8), Inches(1.4))
    title.text_frame.text = "Serverless Computer Vision Pipeline"
    title.text_frame.paragraphs[0].font.size = Pt(36)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = WHITE
    sub = slide.shapes.add_textbox(Inches(0.85), Inches(3.3), Inches(11.5), Inches(1.3))
    sub.text_frame.text = "Phase 2 – Erarbeitungs- und Reflexionsphase\nIU Cloud Programming | Aufgabe 2"
    sub.text_frame.paragraphs[0].font.size = Pt(24)
    sub.text_frame.paragraphs[0].font.color.rgb = LIGHT_BLUE
    sub.text_frame.paragraphs[1].font.size = Pt(18)
    sub.text_frame.paragraphs[1].font.color.rgb = WHITE

    slide = prs.slides.add_slide(blank)
    add_title(slide, "Gliederung")
    add_bullets(slide, [
        "1. Ausgangslage, Zielsetzung und Anforderungen",
        "2. Architektur und Auswahl der Cloud-Dienste",
        "3. Terraform- und Lambda-Umsetzung",
        "4. Sicherheits-, Kosten- und Betriebsmaßnahmen",
        "5. Deployment, Test und Reflexion",
    ])
    add_footer(slide, 2)

    slides = [
        ("1. Ausgangslage und realistisches Szenario", [
            "Fiktiver Onlinehändler für gebrauchte Elektronik",
            "Ca. 100 Bild-Uploads pro Monat durch Mitarbeitende",
            "Automatische technische Qualitätsprüfung von Produktbildern",
            "Kleines IT-Team ohne dauerhaft laufende Server",
            "Testbudget: höchstens 1 EUR pro Monat",
        ]),
        ("2. Anforderungen und Entscheidungskriterien", [
            "Kosten: Pay-per-use, keine EC2- oder NAT-Gateway-Ressourcen",
            "Sicherheit: private Datenhaltung, Verschlüsselung, Least Privilege",
            "Automatisierung: Upload startet Analyse ohne manuellen Eingriff",
            "Skalierbarkeit: verwaltete, ereignisgesteuerte Dienste",
            "Reproduzierbarkeit: vollständige Infrastruktur als Terraform-Code",
        ]),
        ("3. Architektur und Datenfluss", None),
        ("4. Auswahl der AWS-Dienste", [
            "Amazon S3: privater, verschlüsselter Objektspeicher",
            "AWS Lambda: Python 3.12, ereignisgesteuerte Verarbeitung",
            "Pillow in Lambda: Format, Größe, Helligkeit, Kontrast und Schärfe",
            "Amazon DynamoDB: strukturierte Metadaten mit On-Demand-Billing",
            "Amazon SQS: Dead-Letter-Queue für fehlgeschlagene Aufrufe",
        ]),
        ("5. Terraform als IaC-Methode", [
            "Deklarativer Soll-Zustand statt manueller Einzelkonfiguration",
            "Reproduzierbare Ressourcen in mehreren Umgebungen",
            "Reviewbarer Plan vor jeder Änderung",
            "Variablen für Region, Profile und Ressourcennamen",
            "Provider-Lockfile für reproduzierbare Versionen",
        ]),
        ("6. Zentrale Terraform-Konfiguration", None),
        ("7. Lambda-Verarbeitungslogik", None),
        ("8. Sicherheitsmaßnahmen", [
            "S3 Public Access Block vollständig aktiviert",
            "S3 und DynamoDB mit serverseitiger Verschlüsselung",
            "Lambda erhält nur erforderliche Aktionen",
            "Keine Schlüssel oder Passwörter im Repository",
            "CloudWatch-Logs mit begrenzter Aufbewahrung",
        ]),
        ("9. Kostenkontrolle und Free-Tier-Risiken", [
            "Kein dauerhaft laufender Server; Lambda skaliert bei Bedarf",
            "128 MB Speicher, 30 Sekunden Timeout und Parallelität 1",
            "S3-Testbilder werden nach sieben Tagen gelöscht",
            "SQS-DLQ hält Nachrichten nur 24 Stunden",
            "Free Tier ist eine Budgetannahme, keine Kosten-Garantie",
        ]),
        ("10. Deployment-Prozess", None),
        ("11. Funktionstest und Nachweise", [
            "[Screenshot ergänzen] Terraform-Plan mit erwarteten Ressourcen",
            "[Screenshot ergänzen] erfolgreicher Terraform-Apply",
            "[Screenshot ergänzen] Upload eines kleinen Testbildes in S3",
            "[Screenshot ergänzen] CloudWatch-Lauf und DynamoDB-Ergebnis",
            "[Screenshot ergänzen] Ressourcen vor terraform destroy",
        ]),
        ("12. Alternativen und Grenzen", [
            "Rekognition oder Textract wären spätere Erweiterungen für Objekte und OCR",
            "EC2 gäbe mehr Kontrolle, erzeugte aber Leerlaufkosten und Wartung",
            "Die lokale Pillow-Analyse vermeidet externe Vision-APIs und Vendor Lock-in",
            "Produktivbetrieb benötigt zusätzlich Monitoring, zentrale States und KMS",
        ]),
        ("13. Reflexion und Lessons Learned", [
            "Die ereignisgesteuerte Architektur passt besser als ein Dauerbetrieb",
            "Anforderungen wurden durch Szenario, Budget und Kostenabschätzung konkretisiert",
            "IaC macht die Infrastruktur prüfbar und reproduzierbar",
            "Kostenkontrolle benötigt technische Limits und manuelle Kontrollen",
            "Die reale Bereitstellung und die Screenshots sind Teil des Nachweises",
        ]),
    ]

    slide_number = 3
    for title, bullets in slides:
        slide = prs.slides.add_slide(blank)
        add_title(slide, title)
        if title == "3. Architektur und Datenfluss":
            add_architecture(slide)
            add_bullets(slide, [
                "S3 ObjectCreated → Lambda + Pillow → DynamoDB",
                "Fehlerhafte asynchrone Aufrufe werden an SQS-DLQ weitergeleitet",
            ], top=5.2, height=1.0, size=15)
        elif title == "6. Zentrale Terraform-Konfiguration":
            add_code(slide, """resource "aws_lambda_function" "vision_processor" {
  runtime     = "python3.12"
  timeout     = 30
  memory_size = 128
  reserved_concurrent_executions = 1
}""")
        elif title == "7. Lambda-Verarbeitungslogik":
            add_code(slide, """key = unquote_plus(record["s3"]["object"]["key"])
image = s3.get_object(Bucket=bucket, Key=key)
metrics = analyze_image(image["Body"].read())
table.put_item(Item={
    "image_id": key,
    "quality": metrics["quality"],
    "sharpness": metrics["sharpness"],
})""")
        elif title == "10. Deployment-Prozess":
            add_code(slide, """terraform init
terraform fmt -check
terraform validate
terraform plan -out phase2.tfplan
terraform apply phase2.tfplan

# nach Test und Dokumentation:
terraform destroy""")
        else:
            add_bullets(slide, bullets)
        add_footer(slide, slide_number)
        slide_number += 1

    slide = prs.slides.add_slide(blank)
    add_title(slide, "Quellen und Repository")
    add_bullets(slide, [
        "AWS Lambda, S3, DynamoDB, SQS und IAM sowie Pillow – offizielle Dokumentationen",
        "Terraform AWS Provider – Registry und Ressourcendokumentation",
        "IU: Aufgabenstellung Cloud Programming (DLBSEPCP01_D)",
        "Repository: https://github.com/matthiasworz-wq/serverless-computer-vision-pipelin",
    ], size=18)
    add_footer(slide, slide_number)

    prs.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
