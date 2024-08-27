import logging
import csv
import json
import requests


def get_bearer_token(url, user, password):
    """Function to get bearer token from Jamf"""
    api_endpoint = f"{url}/api/v1/auth/token"
    headers = {"accept": "application/json"}
    try:
        response = requests.post(api_endpoint, headers=headers, auth=(user, password))
        bearer_token = response.json().get("token")
        logging.info("Bearer token generated")
        return bearer_token
    except requests.exceptions.RequestException as exception:
        logging.info("Failed to get bearer token:", exception)
        return None


def main() -> None:
    jamf_server = "https://yourserver.jamfcloud.com"
    username = "api-user"
    password = "api-password"
    search_id = 579 # Change this to the id of the advanced mobile device search

    # Get bearer token
    API_token = get_bearer_token(jamf_server, username, password)

    get_mobile_device_list_url = (
        f"{jamf_server}/JSSResource/advancedmobiledevicesearches/id/{search_id}"
    )

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_token,
    }
    advanced_search = requests.get(get_mobile_device_list_url, headers=headers)
    mobile_device_list = json.loads(advanced_search.text)
    jssids = []
    for mobile_device in mobile_device_list["advanced_mobile_device_search"][
        "mobile_devices"
    ]:
        jssids.append(mobile_device["id"])

    data = {}
    for id in jssids:
        try:
            get_mobile_device_url = f"{jamf_server}/api/v2/mobile-devices/{id}/detail"
            get_inventory_response = requests.get(
                get_mobile_device_url, headers=headers
            )
            mobile_device_inventory = json.loads(get_inventory_response.text)
            serialnumber = mobile_device_inventory["serialNumber"]
            wifi_mac_address = mobile_device_inventory["wifiMacAddress"]
            data[serialnumber] = wifi_mac_address
        except json.decoder.JSONDecodeError:
            continue

    with open("mits_ipad_wireless_macs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerows(data.items())


if __name__ == "__main__":
    main()
