"""Page setup. SAGMB style by default; --cbc applies the Computational Biology and Chemistry
guide for authors: A4, 3 cm margins, double spacing, flush left (no full justification)."""
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

BLACK = RGBColor(0, 0, 0)
FONT = "Times New Roman"

def style_run(r, kill_bold):
    r.font.name = FONT
    r.font.color.rgb = BLACK
    rPr = r._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rPr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rf.set(qn(a), FONT)
    if kill_bold:
        r.bold = False

def walk(paragraphs, keep_bold=False, cbc=False, justify=False):
    """Justify running prose only. The title page and the reference list stay flush left,
    because justifying short metadata lines and long DOIs opens ugly word gaps."""
    seen_first_heading = False
    in_references = False
    for p in paragraphs:
        name = (p.style.name or "")
        heading = name.startswith("Heading") or name in ("Title", "Subtitle")
        if heading:
            if name.startswith("Heading"):
                seen_first_heading = True
            in_references = p.text.strip().lower().endswith("references")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if name == "Title" else WD_ALIGN_PARAGRAPH.LEFT
        elif (cbc and not justify) or not seen_first_heading or in_references:
            # CBC: "Avoid full justification, i.e., do not use a constant right-hand margin."
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for r in p.runs:
            style_run(r, kill_bold=(not heading) and not keep_bold)

def main(src, dst, keep_bold=False, cbc=False, justify=False):
    d = Document(src)
    st = d.styles["Normal"]
    st.font.name = FONT; st.font.size = Pt(12); st.font.color.rgb = BLACK
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    st.element.rPr.rFonts.set(qn('w:cs'), FONT)
    for s in d.styles:
        try:
            if s.font is not None:
                s.font.name = FONT
                if s.font.color is not None:
                    s.font.color.rgb = BLACK
        except Exception:
            pass

    if cbc:
        from docx.enum.text import WD_LINE_SPACING
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    walk(d.paragraphs, keep_bold, cbc, justify)
    if cbc:
        for p in d.paragraphs:
            p.paragraph_format.line_spacing = 2.0
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for r in p.runs:
                        style_run(r, kill_bold=False)
                        r.font.size = Pt(10)

    for sec in d.sections:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        m = Cm(3.0) if cbc else Cm(2.5)
        sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = m
        f = sec.footer; f.is_linked_to_previous = False
        p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
        p.text = ""; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(); style_run(r, kill_bold=True)
        fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE')
        inner = OxmlElement('w:r'); it = OxmlElement('w:t'); it.text = "1"
        inner.append(it); fld.append(inner)
        r._r.addnext(fld)

    if justify:
        # Automatic hyphenation keeps justified prose from opening river-sized word gaps.
        se = d.settings.element
        for tag in ("w:autoHyphenation",):
            if se.find(qn(tag)) is None:
                el = OxmlElement(tag); el.set(qn('w:val'), '1'); se.append(el)
        hz = OxmlElement('w:hyphenationZone'); hz.set(qn('w:val'), '360'); se.append(hz)

    d.save(dst)
    print("post-processed ->", dst)

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], "--keep-bold" in sys.argv, "--cbc" in sys.argv, "--justify" in sys.argv)
