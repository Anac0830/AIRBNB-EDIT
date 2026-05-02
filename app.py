from flask import Flask, request, send_file, render_template, jsonify
import fitz  # PyMuPDF
import io
import os
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_pdf():
    """Scan PDF and return all money values found"""
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    pdf_file = request.files['pdf']
    pdf_bytes = pdf_file.read()

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        money_values = []
        all_text_samples = []

        import re
        money_pattern = re.compile(r'\$[\d,]+\.?\d*')

        for page_num, page in enumerate(doc):
            text = page.get_text()
            found = money_pattern.findall(text)
            for val in found:
                if val not in money_values:
                    money_values.append(val)

            # Also grab first 300 chars of text for preview
            if page_num == 0:
                all_text_samples.append(text[:300])

        return jsonify({
            'money_values': money_values,
            'preview': '\n'.join(all_text_samples),
            'pages': len(doc)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    pdf_file = request.files['pdf']
    
    # Get replacements from form data
    finds = request.form.getlist('find[]')
    replaces = request.form.getlist('replace[]')

    if not finds or all(f.strip() == '' for f in finds):
        return jsonify({'error': 'No replacements specified'}), 400

    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        total_replacements = 0

        for old_text, new_text in zip(finds, replaces):
            old_text = old_text.strip()
            new_text = new_text.strip()
            if not old_text:
                continue

            for page in doc:
                instances = page.search_for(old_text)
                for inst in instances:
                    # Get text properties in this area
                    blocks = page.get_text('dict')
                    font_size = 12.0
                    text_color = (0, 0, 0)

                    for block in blocks.get('blocks', []):
                        if block.get('type') != 0:
                            continue
                        for line in block.get('lines', []):
                            for span in line.get('spans', []):
                                if old_text in span.get('text', ''):
                                    font_size = span.get('size', 12.0)
                                    c = span.get('color', 0)
                                    # Convert int color to RGB tuple
                                    r = ((c >> 16) & 0xFF) / 255.0
                                    g = ((c >> 8) & 0xFF) / 255.0
                                    b = (c & 0xFF) / 255.0
                                    text_color = (r, g, b)

                    # Expand the rect to cover any size difference
                    extra_width = max(0, len(new_text) - len(old_text)) * font_size * 0.6
                    cover_rect = fitz.Rect(
                        inst.x0 - 1,
                        inst.y0 - 2,
                        inst.x1 + extra_width + 5,
                        inst.y1 + 2
                    )

                    # Draw white rectangle to erase old text
                    page.draw_rect(cover_rect, color=(1, 1, 1), fill=(1, 1, 1))

                    # Insert new text at same position
                    origin_y = inst.y0 + (inst.y1 - inst.y0) * 0.8
                    page.insert_text(
                        (inst.x0, origin_y),
                        new_text,
                        fontname='helv',
                        fontsize=font_size,
                        color=text_color
                    )
                    total_replacements += 1

        if total_replacements == 0:
            return jsonify({'error': 'Text not found in PDF. Make sure to copy the exact text including $ sign.'}), 404

        # Save result
        output = io.BytesIO()
        doc.save(output, deflate=True, garbage=4)
        output.seek(0)

        original_name = pdf_file.filename.rsplit('.', 1)[0]
        download_name = f"{original_name}_edited.pdf"

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
