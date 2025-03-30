from flask import Flask, request, jsonify

from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app=app)

TEST_IPN = "4889fcb1-8fbb-4a7f-90cd-dc2c7a7d2b9b"
# CALLBACK_URL = "http://localhost:5173/payment-status"
CALLBACK_URL = "https://verseresidence.com/payment-status"

# Getting access token
def get_access_token():
    # url = "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
    url = "https://pay.pesapal.com/v3/api/Auth/RequestToken"  
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


    payload = {
        "consumer_key": "RbHilRmFzIuGiTqmTD/NWyMFHc8/K1wb",
        "consumer_secret": "+/OSjta7tgObAG6c+iDI+c3cAAw="
    }



    # payload = {
    #     "consumer_key": "qkio1BGGYAXTu2JOfm7XSXNruoZsrqEW",
    #     "consumer_secret": "osGQ364R49cXKeOYSpaOnT++rHs="
    # }

    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    print("Access token:", response_data)

    return response_data.get("token")

@app.route('/api/payment-process', methods=['POST'])
def process_payment():
    token = get_access_token()
    if not token:
        return jsonify({"error": "Failed to obtain access token"}), 500

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # url = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
    url = "https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest"  # Live URL
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        payload = {
            "id": data.get("reference"),
            "amount": data.get("price"),
            "currency": "USD",
            "description": "Payment for Electronics",
            "callback_url": CALLBACK_URL,
            # "notification_id": "90456f7b-db1e-42b3-88aa-dc2cc47994b3",
            "notification_id": "87872e18-8735-4c16-ad19-dbfc6e9344ce",
            "billing_address": {
                "email": data.get("email"),
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print("Response from initiation route:", response_data)

        if response.status_code == 200:
            return jsonify(response_data)
        else:
            return jsonify({"error": "Payment request failed", "details": response_data}), response.status_code

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
