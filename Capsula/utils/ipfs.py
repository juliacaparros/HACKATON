import ipfshttpclient

def upload_to_ipfs(file_path):
    client = ipfshttpclient.connect()  # Asegúrate de que tu nodo IPFS está corriendo
    res = client.add(file_path)
    return res['Hash']  # Devuelve el CID del archivo

