from flask import Flask, jsonify
from flask import request
from azure.storage.blob import BlobServiceClient
from typing import List
from flask_cors import CORS
import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})


blob_connection_string = os.getenv('APPSETTING_AzureWebJobsStorage')
if not blob_connection_string:
    raise RuntimeError("Set APPSETTING_AzureWebJobsStorage in environment")
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = os.getenv('APPSETTING_blob_container_name')
if not blob_container_name:
    raise RuntimeError("Set APPSETTING_blob_container_name in environment")

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


def blob_kustutamine(failinimi: str):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=failinimi)
    blob_client.delete_blob()


def blob_raamatute_nimekiri() -> List[str]:
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    blobs = container_client.list_blobs()
    raamatud = [b.name for b in blobs]
    return raamatud


def blob_ules_laadimine_sisu(failinimi: str, sisu: str):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=failinimi)
    blob_client.upload_blob(str(sisu), overwrite=True)
    print(f"Uploaded blob '{failinimi}' with content: {sisu!r}")




@app.route('/raamatud/', methods=['GET'])
def raamatu_nimekiri():
    nimekiri = blob_raamatute_nimekiri()
    raamatud = []
    for failinimi in nimekiri:
        id = failinimi.rstrip(".txt")
        raamatud.append(id)

    tulemus = {}
    tulemus["raamatud"] = raamatud
    vastus = json.dumps(tulemus)

    return vastus, 200


@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allalaadimine(book_id):
    if not book_id.isnumeric():
        return {}, 400

    nimekiri = blob_raamatute_nimekiri()
    for failinimi in nimekiri:
        if int(failinimi.rstrip(".txt")) == int(book_id):
            return blob_alla_laadimine(failinimi), 200
    return {}, 404


@app.route('/raamatud/<book_id>', methods=['DELETE'])
def raamatu_kustutamine(book_id):
    if not book_id.isnumeric():
        return {}, 400
    try:
        if requests.get(f'https://fetch-books-backend-atfma3ccece9bma5.northeurope-01.azurewebsites.net/{book_id}').status_code == 200:
            blob_kustutamine(book_id + ".txt")
            return {}, 204
        else:
            return {}, 404
    except:
        return {}, 500


@app.route('/raamatud/', methods=['POST'])
def raamatu_lisamine():
    data = request.get_json() or {}
    book_id = data.get('raamatu_id')
    if not (book_id and book_id.isnumeric()):
        return jsonify(error="Invalid raamatu_id"), 400

    blob_name = f"{book_id}.txt"
    client = blob_service_client.get_blob_client(container=blob_container_name, blob=blob_name)
    if client.exists():
        return jsonify(error="Raamat juba eksisteerib"), 409

    url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'
    resp = requests.get(url)
    if resp.status_code != 200:
        return jsonify(error="Allalaadimine ebaõnnestus"), resp.status_code

    blob_ules_laadimine_sisu(blob_name, resp.text)
    return jsonify(tulemus="Raamatu loomine õnnestus", raamatu_id=book_id), 201

if __name__ == '__main__':
    # only used if you run `python hs12-flask-api-raamatud.py` locally
    app.run(debug=True, host='0.0.0.0')
