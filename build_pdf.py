"""Builds linux-cert-prep-guide.pdf from the chapter Markdown files in this folder.

Understands the Markdown subset described in CHAPTER-SPEC.md: #/##/### headings,
paragraphs, - and 1. lists, **bold**, `code`, fenced code blocks and pipe tables.
Usage: python build_pdf.py
"""
import datetime
import glob
import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'webdev-bootcamp-revision-guide.pdf')
FONTS = 'C:/Windows/Fonts/'

# Segoe UI and Consolas cover the arrows, bullets and box characters the chapters use.
pdfmetrics.registerFont(TTFont('Body', FONTS + 'segoeui.ttf'))
pdfmetrics.registerFont(TTFont('Body-Bold', FONTS + 'segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('Mono', FONTS + 'consola.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body', boldItalic='Body-Bold')

ss = getSampleStyleSheet()
ACCENT = colors.HexColor('#1f4e79')
body = ParagraphStyle('body', parent=ss['BodyText'], fontName='Body', fontSize=9.5, leading=13.5, spaceAfter=4)
h1 = ParagraphStyle('h1', parent=body, fontName='Body-Bold', fontSize=20, leading=25, textColor=ACCENT, spaceAfter=10)
h2 = ParagraphStyle('h2', parent=body, fontName='Body-Bold', fontSize=13.5, leading=18, textColor=ACCENT, spaceBefore=10, spaceAfter=5)
h3 = ParagraphStyle('h3', parent=body, fontName='Body-Bold', fontSize=10.5, leading=14, spaceBefore=7, spaceAfter=3)
bullet = ParagraphStyle('bullet', parent=body, leftIndent=12, bulletIndent=2, spaceAfter=2)
cell = ParagraphStyle('cell', parent=body, fontSize=8.3, leading=10.5, spaceAfter=0)
cellh = ParagraphStyle('cellh', parent=cell, fontName='Body-Bold', textColor=colors.white)
code = ParagraphStyle('code', fontName='Mono', fontSize=7.8, leading=10, leftIndent=6, rightIndent=6,
                      backColor=colors.HexColor('#f3f5f8'), borderColor=colors.HexColor('#d5dbe3'),
                      borderWidth=0.5, borderPadding=5, spaceBefore=4, spaceAfter=8)
cover_t = ParagraphStyle('cover_t', parent=h1, fontSize=28, leading=34, alignment=TA_CENTER)
cover_s = ParagraphStyle('cover_s', parent=body, fontSize=12, leading=17, alignment=TA_CENTER)
toc_l1 = ParagraphStyle('toc1', parent=body, fontName='Body-Bold', fontSize=11, leading=16)
toc_l2 = ParagraphStyle('toc2', parent=body, fontSize=9, leading=12, leftIndent=14)


def inline(text):
    """Escape XML, then apply **bold** and `code`."""
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p) > 1:
            out.append('<font face="Mono" size="8.3">' + escape(p[1:-1]) + '</font>')
        else:
            e = escape(p)
            e = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', e)
            out.append(e)
    return ''.join(out)


def wrap_code(text, width=100):
    lines = []
    for line in text.split('\n'):
        while len(line) > width:
            lines.append(line[:width])
            line = '    ' + line[width:]
        lines.append(line)
    return '\n'.join(lines)


def make_table(rows):
    header, data = rows[0], rows[1:]
    ncols = len(header)
    data = [r + [''] * (ncols - len(r)) for r in data]
    t = [[Paragraph(inline(c), cellh) for c in header]] + [[Paragraph(inline(c), cell) for c in r[:ncols]] for r in data]
    avail = A4[0] - 36 * mm
    lens = [max(len(str(r[i])) for r in rows if i < len(r)) + 4 for i in range(ncols)]
    total = sum(lens)
    widths = [max(avail * l / total, 18 * mm) for l in lens]
    scale = avail / sum(widths)
    widths = [w * scale for w in widths]
    tbl = Table(t, colWidths=widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#c9d1dc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f6f8fb')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return tbl


class Heading(Paragraph):
    def __init__(self, text, style, level):
        super().__init__(text, style)
        self.toc_level = level


def parse(md):
    flow = []
    lines = md.split('\n')
    i = 0
    para = []

    def flush():
        if para:
            flow.append(Paragraph(inline(' '.join(para)), body))
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if s.startswith('```'):
            flush()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith('```'):
                buf.append(lines[j].rstrip())
                j += 1
            flow.append(Preformatted(wrap_code('\n'.join(buf)), code))
            i = j + 1
            continue
        if s.startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|?\s*:?-{2,}', lines[i + 1]):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip()
                if not re.match(r'^\|?\s*:?-{2,}', row):
                    rows.append([c.strip() for c in row.strip('|').split('|')])
                i += 1
            flow.append(make_table(rows))
            flow.append(Spacer(1, 6))
            continue
        m = re.match(r'^(#{1,3})\s+(.*)', s)
        if m:
            flush()
            level = len(m.group(1))
            text = inline(m.group(2))
            if level == 1:
                flow.append(PageBreak())
                flow.append(Heading(text, h1, 0))
            elif level == 2:
                flow.append(Heading(text, h2, 1))
            else:
                flow.append(Paragraph(text, h3))
            i += 1
            continue
        m = re.match(r'^[-*]\s+(\[[ xX]\]\s+)?(.*)', s)
        if m:
            flush()
            mark = '\u2610' if m.group(1) else '\u2022'
            flow.append(Paragraph(inline(m.group(2)), bullet, bulletText=mark))
            i += 1
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', s)
        if m:
            flush()
            flow.append(Paragraph(inline(m.group(2)), bullet, bulletText=m.group(1) + '.'))
            i += 1
            continue
        if not s:
            flush()
        else:
            para.append(s)
        i += 1
    flush()
    return flow


class Doc(SimpleDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Heading):
            self.notify('TOCEntry', (f.toc_level, f.getPlainText(), self.page))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Body', 8)
    canvas.setFillColor(colors.HexColor('#6b7785'))
    canvas.drawString(18 * mm, 10 * mm, 'Web Development Bootcamp Revision Guide')
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    canvas.restoreState()


def main():
    chapters = sorted(glob.glob(os.path.join(HERE, '0*.md')))
    story = [Spacer(1, 60 * mm),
             Paragraph('Web Development Bootcamp — Revision Guide', cover_t), Spacer(1, 6 * mm),
             Paragraph('HTML · CSS · JavaScript · Node · Express · Databases · React · Web3 / Internet Computer', cover_s),
             Spacer(1, 12 * mm),
             Paragraph('Prepared for Rizwan Khalid · ' + datetime.date.today().strftime('%B %Y'), cover_s),
             Spacer(1, 40 * mm),
             Paragraph('Study plans, hands-on labs, original practice questions and readiness checklists. '
                       'Prepared with AI assistance (Claude). Every exam and badge assessment is taken by you, '
                       'under each provider\'s rules. Exam facts were checked against official pages in '
                       'September 2026; confirm prices and dates before booking.', cover_s),
             PageBreak(), Paragraph('Contents', h1)]
    toc = TableOfContents()
    toc.levelStyles = [toc_l1, toc_l2]
    story.append(toc)
    intro = os.path.join(HERE, '00-overview.md')
    for path in ([intro] if os.path.exists(intro) else []) + [c for c in chapters if not c.endswith('00-overview.md')]:
        with open(path, encoding='utf-8') as f:
            story.extend(parse(f.read()))
    doc = Doc(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
              title='Web Development Bootcamp Revision Guide', author='Prepared for Rizwan Khalid (AI-assisted)')
    doc.multiBuild(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
