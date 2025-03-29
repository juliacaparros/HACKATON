from utils.ipfs import upload_to_ipfs
from flask import Flask, request, render_template
from utils.crypto import encrypt_file, generate_doc, decrypt_file
from utils.diagram import generate_svg_diagram
from utils.storage import cargar_historial, guardar_historial
import os
from werkzeug.utils import secure_filename
import shutil
import zipfile
import requests
import json
from web3 import Web3


app = Flask(__name__)
UPLOAD_FOLDER = 'data'
DESCARGAS_FOLDER = 'static/descargas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DESCARGAS_FOLDER, exist_ok=True)

# Cargar historial desde archivo
capsulas_generadas = cargar_historial()

# 🟢 RUTA PRINCIPAL: solo muestra la caja fuerte cerrada
@app.route('/')
def index():
    return render_template(
        'index.html',
        capsulas=capsulas_generadas,
        mostrar_formulario=False
    )

# 📤 RUTA DE SUBIDA: muestra el formulario y procesa la cápsula
@app.route('/subir', methods=['GET', 'POST'])
def subir():
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

            # Subir archivo cifrado a IPFS
            ipfs_cid = upload_to_ipfs(encrypted_path)

            if ipfs_cid:
                print(f"Archivo subido a IPFS con CID: {ipfs_cid}")

            if ipfs_cid:
                tx_hash = store_ipfs_hash(ipfs_cid)
                print(f"Archivo guardado en Ethereum con TX: {tx_hash}")


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

    # GET: mostrar solo el formulario para subir
    return render_template(
        'index.html',
        capsulas=capsulas_generadas,
        mostrar_formulario=True
    )

# 🔐 RUTA DE DESENCRIPTADO
@app.route('/desencriptar', methods=['GET', 'POST'])
def desencriptar():
    if request.method == 'POST':
        enc_file = request.files['enc_file']
        key_file = request.files['key_file']

        if enc_file and key_file:
            enc_path = os.path.join(UPLOAD_FOLDER, secure_filename(enc_file.filename))
            key_path = os.path.join(UPLOAD_FOLDER, secure_filename(key_file.filename))
            enc_file.save(enc_path)
            key_file.save(key_path)

            try:
                restored_path = decrypt_file(enc_path, key_path)
                restored_public = os.path.join(DESCARGAS_FOLDER, os.path.basename(restored_path))
                shutil.copy(restored_path, restored_public)

                return render_template(
                    'desencriptar.html',
                    result=f"""
                    ✅ Archivo desencriptado correctamente:<br>
                    <a href="/{restored_public}" class="btn btn-success mt-2" download>⬇️ Descargar archivo restaurado</a>
                    """
                )
            except Exception as e:
                return render_template('desencriptar.html', result=f"❌ Error al desencriptar: {str(e)}")

    return render_template('desencriptar.html')




PINATA_API_KEY = "3a0d9fd687440f52ff59"
PINATA_SECRET_API_KEY = "0ea632377be31a58ff94a8fbbabead4d616df2b252c1d8425c8be6356c7c8256"

def upload_to_ipfs(file_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    with open(file_path, "rb") as file:
        files = {"file": file}
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_API_KEY
        }
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        return response.json()["IpfsHash"]  # CID del archivo en IPFS
    else:
        print("Error al subir a IPFS:", response.text)
        return None



INFURA_URL = "https://sepolia.infura.io/v3/c4180dafc227414792e8a33170a52148"
CONTRACT_ADDRESS = Web3.to_checksum_address("0xd938cf33c35d10a8babb5aa5b3e910216bedf818")
PRIVATE_KEY = "cf2acb18fc65c09450cbaf2f0ff25f216c7418b4127e2ffb2b2bbdf2214bec2c"
WALLET_ADDRESS = "0x394aC76B7845eA758D3143660a6Cd956baa6b3CA"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

abi = [
    {
        "constant": False,
        "inputs": [{"name": "_ipfsHash", "type": "string"}],
        "name": "uploadFile",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def store_ipfs_hash(ipfs_hash):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    txn = contract.functions.uploadFile(ipfs_hash).build_transaction({
        "from": WALLET_ADDRESS,
        "gas": 200000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": nonce
    })
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return w3.to_hex(tx_hash)







if __name__ == '__main__':
    app.run(debug=True)
