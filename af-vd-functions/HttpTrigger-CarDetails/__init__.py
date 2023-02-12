import logging
import requests
import json
import azure.functions as func
from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    vrm = req.params.get('vrm')
    if not vrm:
        raise ValueError
    
    secret_client = SecretClient(credential=AzureCliCredential(), vault_url= "https://tyreteamkeyvault.vault.azure.net/")
    api_key = secret_client.get_secret("ApiKey").value
    logging.info(api_key)
    logging.info(vrm)

    r = requests.get(f'https://uk1.ukvehicledata.co.uk/api/datapackage/TyreData?v=2&api_nullitems=1&auth_apikey={api_key}&key_VRM={vrm}')
    status_details = r.json().get("Response")
    if status_details.get("StatusCode") != "Success":
        return func.HttpResponse(
            body = json.dumps({"status" : "failed", "message": status_details.get("StatusMessage")}),
            status_code = 400, 
            mimetype = 'application/json',
            charset = 'utf-8'
            )
    
    vechile_details = r.json()['Response']['DataItems']['VehicleDetails']
    raw_tyre_details = r.json()['Response']['DataItems']['TyreDetails']['RecordList'][0]
    tyre_details = {
        "front" : raw_tyre_details.get("Front"),
        "rear" : raw_tyre_details.get("Rear")
    }

    return func.HttpResponse(
        body = json.dumps({"VechileDetails" : vechile_details, "TyreDetails" : tyre_details}), 
        status_code=200,
        mimetype = 'application/json',
        charset = 'utf-8'
        )
