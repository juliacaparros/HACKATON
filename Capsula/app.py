from flask import Flask, request, render_template
from utils.crypto import encrypt_file
import os
from werkzeug.utils import secure_filename
from utils.crypto import encrypt_file, generate_doc
from utils.diagram import generate_svg_diagram


app = Flask(__name__)
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            # Cifrado
            encrypted_path = encrypt_file(path)

            # Documentación
            doc_path = generate_doc(filename, encrypted_path)

            # Diagrama SVG visual
            svg_path = os.path.splitext(encrypted_path)[0] + '_diagram.svg'
            generate_svg_diagram(svg_path, filename)

            # Mostrar resultados
            return render_template('index.html', result=f"""
                Archivo cifrado guardado como: <code>{encrypted_path}</code><br>
                Documentación generada en: <code>{doc_path}</code><br>
                Diagrama visual generado en: <code>{svg_path}</code>
            """)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
