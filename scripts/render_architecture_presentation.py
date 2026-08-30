"""Render the presentation-focused LumenPrep architecture diagram as a PDF."""

from math import atan2, cos, sin
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "lumenprep-architecture-presentation-2.pdf"
PAGE = (1440, 900)


THEMES = {
    "ui": ("#EAF2FF", "#2563EB", "#172554"),
    "api": ("#EEF2FF", "#4F46E5", "#312E81"),
    "core": ("#ECFDF5", "#059669", "#064E3B"),
    "data": ("#FFF7ED", "#D97706", "#78350F"),
    "intel": ("#FAF5FF", "#9333EA", "#581C87"),
    "human": ("#FFF1F2", "#E11D48", "#881337"),
}


def color(value: str):
    return HexColor(value)


def group(c, x, y, width, height, title):
    c.setFillColor(color("#FFFEF2"))
    c.setStrokeColor(color("#CBD5E1"))
    c.setLineWidth(1.2)
    c.roundRect(x, y, width, height, 12, fill=1, stroke=1)
    c.setFillColor(color("#334155"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 16, y + height - 20, title)


def lines(c, values, x, y, width, font_size, fill):
    c.setFillColor(fill)
    c.setFont("Helvetica", font_size)
    leading = font_size * 1.32
    baseline = y - (len(values) - 1) * leading / 2
    for index, value in enumerate(values):
        text_width = c.stringWidth(value, "Helvetica", font_size)
        c.drawString(x + (width - text_width) / 2, baseline + (len(values) - 1 - index) * leading, value)


def node(c, x, y, width, height, title, details, theme, pill=False):
    fill, stroke, text = map(color, THEMES[theme])
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(2)
    radius = height / 2 if pill else 9
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)
    c.setFillColor(text)
    c.setFont("Helvetica-Bold", 14 if height < 60 else 15)
    title_width = c.stringWidth(title, "Helvetica-Bold", 14 if height < 60 else 15)
    title_y = y + height * (0.68 if details else 0.43)
    c.drawString(x + (width - title_width) / 2, title_y, title)
    if details:
        lines(c, details, x, y + height * 0.28, width, 11.5 if height < 70 else 12.5, text)


def arrow(c, points, label=None, dashed=False, label_offset=7):
    c.saveState()
    c.setStrokeColor(color("#475569"))
    c.setFillColor(color("#475569"))
    c.setLineWidth(1.6)
    if dashed:
        c.setDash(4, 4)
    for start, end in zip(points, points[1:]):
        c.line(start[0], start[1], end[0], end[1])
    c.restoreState()

    start, end = points[-2], points[-1]
    angle = atan2(end[1] - start[1], end[0] - start[0])
    head = 8
    left = (end[0] - head * cos(angle - 0.45), end[1] - head * sin(angle - 0.45))
    right = (end[0] - head * cos(angle + 0.45), end[1] - head * sin(angle + 0.45))
    c.setFillColor(color("#475569"))
    path = c.beginPath()
    path.moveTo(*end)
    path.lineTo(*left)
    path.lineTo(*right)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    if label:
        segment = points[-1]
        previous = points[-2]
        x = (segment[0] + previous[0]) / 2
        y = (segment[1] + previous[1]) / 2 + label_offset
        c.setFont("Helvetica", 9.5)
        text_width = c.stringWidth(label, "Helvetica", 9.5)
        c.setFillColor(white)
        c.roundRect(x - text_width / 2 - 4, y - 8, text_width + 8, 14, 3, fill=1, stroke=0)
        c.setFillColor(color("#475569"))
        c.drawCentredString(x, y - 4, label)


def render():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=PAGE, pageCompression=1)
    c.setTitle("Arquitetura de apresentação - LumenPrep")
    c.setAuthor("Nextwave")

    c.setFillColor(color("#0F172A"))
    c.setFont("Helvetica-Bold", 29)
    c.drawString(54, 856, "LumenPrep - arquitetura operacional")
    c.setFillColor(color("#475569"))
    c.setFont("Helvetica", 13)
    c.drawString(54, 833, "Fluxo determinístico, persistência operacional e limites explícitos para o contexto pós-incident")

    node(c, 610, 775, 220, 40, "Operador", [], "ui", pill=True)

    group(c, 54, 640, 1332, 104, "Experiência web - Next.js")
    node(c, 96, 663, 255, 48, "Entrada", ["transações e samples"], "ui")
    node(c, 552, 653, 336, 68, "Cliente API tipado", ["HTTP JSON"], "ui")
    node(c, 1088, 663, 255, 48, "Observação", ["logs, detalhe, incidentes e notificações"], "ui")

    group(c, 54, 505, 1332, 96, "Fronteira pública - FastAPI")
    node(c, 114, 526, 310, 48, "Transaction API", ["batch, catálogo e logs"], "api")
    node(c, 565, 526, 310, 48, "Operação", ["health, métricas e demo"], "api")
    node(c, 1016, 526, 310, 48, "Incident API", ["detalhe, review e sugestão"], "api")

    group(c, 54, 365, 1332, 110, "Núcleo determinístico - fonte da verdade operacional")
    core = [
        (76, "1. Aceitar lote", ["persistir PROCESSING"]),
        (293, "2. Worker durável", ["lease, retomada e progresso"]),
        (510, "3. Classificação", ["outcome e refusal codes"]),
        (727, "4. Ingestão", ["normalizar, validar e deduplicar"]),
        (944, "5. Detecção e RCA", ["baseline, métricas e anomalia"]),
        (1161, "6. Incident persistido", ["evidências, links e notificação"]),
    ]
    for x, title, detail in core:
        node(c, x, 389, 190, 56, title, detail, "core")

    group(c, 54, 218, 1332, 112, "Contexto pós-incidente - nunca altera fatos ou causa")
    node(c, 550, 270, 230, 42, "Explicação grounded", ["detalhe por transação"], "intel")
    node(c, 820, 270, 230, 42, "Agente opcional", ["hipótese HUMAN_ONLY"], "intel")
    node(c, 1090, 270, 230, 42, "Revisão humana", ["decisão idempotente"], "human")
    node(c, 820, 224, 230, 42, "Memória de precedentes", ["Neo4j opcional; fallback em memória"], "intel")

    group(c, 54, 48, 1332, 135, "DuckDB - estado operacional persistente")
    node(c, 82, 73, 280, 72, "Lotes e transações", ["status e outcomes"], "data")
    node(c, 408, 73, 280, 72, "Eventos raw e canônicos", ["tentativas e agregações"], "data")
    node(c, 734, 73, 280, 72, "Incidents, links", ["notificações e reviews"], "data")
    node(c, 1060, 73, 280, 72, "Sugestões e catálogo", ["de refusal codes"], "data")

    # Interface and public-boundary flows.
    arrow(c, [(720, 775), (720, 721)])
    arrow(c, [(351, 687), (552, 687)])
    arrow(c, [(888, 687), (1088, 687)])
    arrow(c, [(720, 653), (269, 574)], "batch, catálogo e logs")
    arrow(c, [(720, 653), (720, 574)], "health, métricas e demo")
    arrow(c, [(720, 653), (1171, 574)], "incidents, review e sugestão")

    # Core flow.
    for x in (266, 483, 700, 917, 1134):
        arrow(c, [(x, 417), (x + 27, 417)])
    arrow(c, [(269, 526), (269, 445)], "persiste antes do 202")
    arrow(c, [(720, 526), (720, 466), (822, 466), (822, 445)], "tráfego sintético", dashed=True, label_offset=-13)

    # Post-incident flow: facts remain in the core, and only human approval promotes a precedent.
    arrow(c, [(1256, 389), (1256, 345), (665, 345), (665, 312)], "fatos e evidências")
    arrow(c, [(1171, 526), (1171, 312)], "registra decisão")
    arrow(c, [(1090, 249), (1050, 249)], "somente APPROVED")

    # DuckDB is the single operational source of truth for the complete deterministic pipeline.
    arrow(c, [(475, 365), (475, 183)], "fatos e estado operacional")

    # Legend.
    c.setStrokeColor(color("#475569"))
    c.setLineWidth(1.5)
    c.line(74, 28, 102, 28)
    c.setFillColor(color("#475569"))
    c.setFont("Helvetica", 10)
    c.drawString(109, 24, "processamento ou persistência")
    c.setDash(4, 4)
    c.line(310, 28, 338, 28)
    c.setDash()
    c.drawString(345, 24, "consulta ou tráfego interno")
    c.setFillColor(color("#64748B"))
    c.drawRightString(1366, 24, "LumenPrep | arquitetura de apresentação")

    c.showPage()
    c.save()


if __name__ == "__main__":
    render()
