from flask import Flask, request, render_template
from utils.crypto import encrypt_file, generate_doc
from utils.diagram import generate_svg_diagram
from utils.storage import cargar_historial, guardar_historial
import os
from werkzeug.utils import secure_filename
import shutil
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
DESCARGAS_FOLDER = 'static/descargas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DESCARGAS_FOLDER, exist_ok=True)

# Cargar historial desde archivo
capsulas_generadas = cargar_historial()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            encrypted_path = encrypt_file(path)
            doc_path = generate_doc(filename, encrypted_path)
            svg_path = os.path.splitext(encrypted_path)[0] + '_diagram.svg'
            generate_svg_diagram(svg_path, filename)

            public_enc = os.path.join(DESCARGAS_FOLDER, os.path.basename(encrypted_path))
            public_txt = os.path.join(DESCARGAS_FOLDER, os.path.basename(doc_path))
            public_svg = os.path.join(DESCARGAS_FOLDER, os.path.basename(svg_path))
            shutil.copy(encrypted_path, public_enc)
            shutil.copy(doc_path, public_txt)
            shutil.copy(svg_path, public_svg)

            zip_filename = os.path.splitext(os.path.basename(encrypted_path))[0] + '_capsula.zip'
            zip_path = os.path.join(DESCARGAS_FOLDER, zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(public_enc, arcname=os.path.basename(public_enc))
                zipf.write(public_txt, arcname=os.path.basename(public_txt))
                zipf.write(public_svg, arcname=os.path.basename(public_svg))

            capsula_info = {
                "enc": os.path.basename(encrypted_path),
                "txt": os.path.basename(doc_path),
                "svg": os.path.basename(svg_path),
                "zip": os.path.basename(zip_path)
            }
            capsulas_generadas.append(capsula_info)
            guardar_historial(capsulas_generadas)

            resultado_html = f"""
                <div class="alert alert-info fade-in">
                    <h5>📦 Contenido de la cápsula generada</h5>
                    <ul class="list-unstyled">
                        <li>🔐 {capsula_info['enc']}</li>
                        <li>📄 {capsula_info['txt']}</li>
                        <li>🖼️ {capsula_info['svg']}</li>
                        <li>📦 {capsula_info['zip']}</li>
                    </ul>
                </div>

                <div class="mt-3">
                    <a href="/{zip_path}" class="btn btn-outline-warning m-2" download>📦 Descargar todo como ZIP</a>
                    <a href="/{public_enc}" class="btn btn-outline-primary m-2" download>⬇️ Solo archivo cifrado (.enc)</a>
                    <a href="/{public_txt}" class="btn btn-outline-success m-2" download>📄 Solo documentación (.txt)</a>
                    <a href="/{public_svg}" class="btn btn-outline-info m-2" download>🖼️ Solo diagrama (.svg)</a>
                </div>
            """

            return render_template(
                'index.html',
                result=resultado_html,
                capsulas=capsulas_generadas,
                mostrar_formulario=True
            )

    return render_template(
        'index.html',
        capsulas=capsulas_generadas,
        mostrar_formulario=bool(capsulas_generadas)
    )

if __name__ == '__main__':
    app.run(debug=True)
