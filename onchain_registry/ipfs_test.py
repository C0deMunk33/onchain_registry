import requests
import json

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"

def upload_and_pin(json_data):
    # Convert JSON data to a string and upload it
    response = requests.post(f"{IPFS_API_URL}/add", files={"file": ("data.json", json.dumps(json_data))})
    if response.status_code == 200:
        cid = response.json()["Hash"]
        print(f"Uploaded JSON and received CID: {cid}")
        return cid
    else:
        print(f"Failed to upload JSON: {response.text}")
        return None

def delete_and_unpin(cid):
    response = requests.post(f"{IPFS_API_URL}/pin/rm?arg={cid}")
    if response.status_code == 200:
        print(f"Unpinned CID: {cid}")
    else:
        print(f"Failed to unpin CID: {response.text}")

def get_file(cid):
    response = requests.post(f"{IPFS_API_URL}/cat?arg={cid}")
    if response.status_code == 200:
        # Parse JSON content from IPFS
        json_data = json.loads(response.content)
        print(f"Retrieved JSON data: {json_data}")
        return json_data
    else:
        print(f"Failed to retrieve JSON: {response.text}")
        return None

if __name__ == "__main__":
    # Step 1: Define the JSON data
    data_to_upload = {
        "message": "Hello, IPFS!",
        "timestamp": "2025-01-21",
        "example": True
    }

    # Step 2: Upload and pin the JSON data
    cid = upload_and_pin(data_to_upload)

    if cid:
        # Step 3: Retrieve the JSON data
        retrieved_data = get_file(cid)

        # Step 4: Unpin and delete the JSON data
        delete_and_unpin(cid)
