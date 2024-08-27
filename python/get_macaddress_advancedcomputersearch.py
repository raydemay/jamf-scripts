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
    username = "api-username"
    password = "api-password"
    search_id = 81 # Change this to the id of the search that you are targeting 

    # Get bearer token
    API_token = get_bearer_token(jamf_server, username, password)

    get_computer_list_url = f"{jamf_server}/JSSResource/advancedcomputersearches/id/{search_id}"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_token,
    }
    advanced_search = requests.get(get_computer_list_url, headers=headers)
    computer_list = json.loads(advanced_search.text)
    jssids = []
    for computer in computer_list["advanced_computer_search"]["computers"]:
        jssids.append(computer["id"])

    data = {}
    for id in jssids:
        try:
            get_computer_url = (
                f"{jamf_server}/JSSResource/computers/id/{id}/subset/General"
            )
            get_inventory_response = requests.get(get_computer_url, headers=headers)
            computer_inventory = json.loads(get_inventory_response.text)
            general_data = computer_inventory["computer"]["general"]
            primary_adapter = general_data["network_adapter_type"]
            alt_adapter = general_data["alt_network_adapter_type"]
            if primary_adapter == "IEEE80211":
                data[general_data["serial_number"]] = general_data["mac_address"]
            elif alt_adapter == "IEEE80211":
                data[general_data["serial_number"]] = general_data["alt_mac_address"]
            else:
                print("No wireless adapter found")
        except json.decoder.JSONDecodeError:
            continue

    with open("wireless_macs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerows(data.items())


if __name__ == "__main__":
    main()
