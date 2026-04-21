# PDF Form Filling Workflow

## Initial Assessment

Determine the PDF type first: `python scripts/check_fillable_fields <file.pdf>`

## For Fillable PDFs

1. Extract field information: `python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`
2. Convert to images for visual analysis: `python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
3. Create `field_values.json` matching extracted field IDs with values
4. Fill: `python scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>`

## For Non-Fillable PDFs

**Approach A (preferido):** `python scripts/extract_form_structure.py <input.pdf> form_structure.json` — coordenadas exactas desde la estructura interna del PDF.

**Approach B (fallback):** Convertir a imágenes y estimar coordenadas visualmente con crops de ImageMagick.

**Híbrido:** Combinar ambos. Convertir coordenadas de imagen a PDF:
```
pdf_x = image_x * (pdf_width / image_width)
```

## Validación

Siempre validar antes de llenar: `python scripts/check_bounding_boxes.py fields.json`

Llenar: `python scripts/fill_pdf_form_with_annotations.py <input.pdf> fields.json <output.pdf>`

Verificar resultado convirtiendo el output a imágenes.
