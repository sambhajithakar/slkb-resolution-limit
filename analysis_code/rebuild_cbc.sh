set -e
python3 fill.py ../delivery/PROJECT1_BRCARAG_FINAL_MANUSCRIPT_FOR_RESEARCHER_APPROVAL/B_REPRODUCIBILITY/pilot_report_REAL.json CBC_raw.md
python3 numbers_cbc.py CBC_raw.md PROJECT1_BRCARAG_CBC.md
rm -f cbc_raw.docx PROJECT1_BRCARAG_CBC.docx PROJECT1_BRCARAG_CBC.pdf
pandoc PROJECT1_BRCARAG_CBC.md -o cbc_raw.docx --standalone --reference-doc=../docxref/reference_academic.docx
python3 postprocess.py cbc_raw.docx PROJECT1_BRCARAG_CBC.docx --cbc
soffice --headless --convert-to pdf --outdir . PROJECT1_BRCARAG_CBC.docx >/dev/null 2>&1
pdfinfo PROJECT1_BRCARAG_CBC.pdf | grep -E '^Pages'
