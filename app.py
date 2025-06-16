from flask import Flask, request, send_file
import tempfile
import subprocess
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get uploaded .note file
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        if not file.filename.endswith('.note'):
            return 'Not a .note file', 400
        
        app.logger.info(f"Converting file: {file.filename}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            note_path = os.path.join(temp_dir, 'input.note')
            file.save(note_path)
            
            # Convert to PDF
            pdf_path = os.path.join(temp_dir, 'output.pdf')
            
            result = subprocess.run([
                'supernote-tool', 'convert', 
                '-t', 'pdf', 
                '--pdf-type', 'raster',
                '-a', note_path, pdf_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                app.logger.error(f"Conversion failed: {result.stderr}")
                return f'Conversion failed: {result.stderr}', 500
            
            if not os.path.exists(pdf_path):
                return 'PDF not generated', 500
            
            app.logger.info("Conversion successful")
            return send_file(pdf_path, as_attachment=True, 
                           download_name='converted.pdf',
                           mimetype='application/pdf')
            
    except subprocess.TimeoutExpired:
        return 'Conversion timeout', 500
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return f'Error: {str(e)}', 500

@app.route('/health')
def health():
    return 'Supernote Converter is running!', 200

@app.route('/')
def home():
    return '''
    <h1>Supernote Converter Service</h1>
    <p>This service converts .note files to PDF.</p>
    <p>POST your .note file to /convert</p>
    <p>Check service health at /health</p>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
