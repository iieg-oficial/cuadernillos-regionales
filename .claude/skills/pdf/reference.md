# PDF Processing Advanced Reference

## pypdfium2 (Apache/BSD License)

Alternativa a PyMuPDF. Ideal para renderizar páginas a imagen.

### Render PDF to Images
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    bitmap = page.render(scale=2.0)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.png", "PNG")
```

### Extract Text
```python
pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {i+1}: {len(text)} chars")
```

## pdfplumber Advanced Features

### Extract Text with Coordinates
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    chars = page.chars
    for char in chars[:10]:
        print(f"'{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # Extract text within a bounding box
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

### Advanced Table Extraction
```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15,
    }
    tables = page.extract_tables(table_settings)

    # Debug visual
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

## CLI Avanzado

### poppler-utils

```bash
# Texto con coordenadas (útil para datos estructurados)
pdftotext -bbox-layout document.pdf output.xml

# Convertir a imágenes
pdftoppm -png -r 300 document.pdf output_prefix

# Extraer imágenes embebidas
pdfimages -all document.pdf images/img
pdfimages -list document.pdf
```

### qpdf Advanced

```bash
# Split en grupos de páginas
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# Merge páginas específicas de múltiples PDFs
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 -- combined.pdf

# Optimizar para web
qpdf --linearize input.pdf optimized.pdf

# Reparar PDF dañado
qpdf --check corrupted.pdf
qpdf --fix-qdf damaged.pdf repaired.pdf

# Cifrado con permisos específicos
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf
```

## Batch Processing
```python
import glob
from pypdf import PdfReader, PdfWriter
from pathlib import Path

def batch_extract_text(input_dir):
    for pdf_file in Path(input_dir).glob("*.pdf"):
        try:
            reader = PdfReader(pdf_file)
            text = "".join(page.extract_text() for page in reader.pages)
            pdf_file.with_suffix(".txt").write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Error en {pdf_file}: {e}")
```

## Troubleshooting

### PDFs cifrados
```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

### PDFs corruptos
```bash
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### Texto no extraíble (scans)
```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    return "".join(pytesseract.image_to_string(img) for img in images)
```

## Performance Tips

- Para PDFs grandes: procesar páginas individualmente con pypdfium2
- Para texto plano: `pdftotext -bbox-layout` es el más rápido
- Para tablas: pdfplumber con `extract_tables()`
- Para extraer imágenes: `pdfimages` es mucho más rápido que renderizar páginas
- pdf-lib mantiene mejor la estructura de formularios que la mayoría de alternativas

## Licencias

| Librería | Licencia |
|---|---|
| pypdf | BSD |
| pdfplumber | MIT |
| pypdfium2 | Apache/BSD |
| reportlab | BSD |
| poppler-utils | GPL-2 |
| qpdf | Apache |
