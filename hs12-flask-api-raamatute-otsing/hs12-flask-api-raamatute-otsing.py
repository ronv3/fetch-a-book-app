from flask import Flask, jsonify
from flask import request
from azure.storage.blob import BlobServiceClient
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})


blob_connection_string = os.getenv('AZURE_BLOB_CONNECTION_STRING')
if not blob_connection_string:
    raise RuntimeError("Set AZURE_BLOB_CONNECTION_STRING in environment")
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = "vahtra-konteiner-hs10"

def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)
        print(f"Container '{konteineri_nimi}' created.")
    else:
        print(f"Container '{konteineri_nimi}' already exists.")

blob_konteineri_loomine(blob_container_name)

def blob_alla_laadimine(faili_nimi: str) -> str:
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    return blob_client.download_blob().content_as_text()

@app.route('/raamatu_otsing/', methods=['POST'])
def raamatutest_sone_otsimine():
    data = request.get_json() or {}
    sone = data.get('sone')
    if not sone:
        return jsonify(error="Invalid input"), 400

    pattern = re.compile(rf"\b{re.escape(sone)}\b", flags=re.IGNORECASE)

    container_client = blob_service_client.get_container_client(container=blob_container_name)
    tulemused = []

    for blob in container_client.list_blobs():
        if not blob.name.lower().endswith('.txt'):
            continue

        content = blob_alla_laadimine(blob.name)
        if content is None:
            continue

        matches = pattern.findall(content)
        count = len(matches)
        if count > 0:
            raamatu_id = os.path.splitext(blob.name)[0]
            tulemused.append({
                "raamatu_id": int(raamatu_id),
                "leitud": count
            })

    return jsonify(sone=sone, tulemused=tulemused), 200

@app.route('/raamatu_otsing/<book_id>', methods=['POST'])
def raamatust_sone_otsimine(book_id):
    data = request.get_json() or {}
    sone = data.get('sone')
    if not (sone and book_id and book_id.isnumeric()):
        return jsonify(error="Invalid input"), 400

    blob_name = f"{book_id}.txt"
    content = blob_alla_laadimine(blob_name)
    if content is None:
        return jsonify(error="Raamat puudub"), 404

    pattern = re.compile(rf"\b{re.escape(sone)}\b", flags=re.IGNORECASE)
    matches = pattern.findall(content)
    count = len(matches)

    return jsonify(raamatu_id=book_id, sone=sone, leitud=count), 200

if __name__ == '__main__':
    # only used if you run `python hs12-flask-api-raamatute-otsing.py` locally
    app.run(debug=True, host='0.0.0.0')
