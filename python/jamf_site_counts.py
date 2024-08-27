import logging
import csv
import json
import requests
import datetime as dt


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
    csv_header = ["Site", "Computers", "Mobile Devices", "Apple TVs"]
    site_ids = {}
    object_ids = []

    timestamp = dt.datetime.now().isoformat(timespec="seconds").replace(":", "")
    with open(f"jamf_device_counts_{timestamp}.csv", "a", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(csv_header)

    # Get bearer token
    API_token = get_bearer_token(jamf_server, username, password)

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_token,
    }
    sites_api_endpoint = f"{jamf_server}/api/v1/sites"

    site_codes_response = requests.get(sites_api_endpoint, headers=headers)
    site_codes = json.loads(site_codes_response.text)
    site_ids = {item["id"]: item["name"] for item in site_codes}
    
    # Get jssids from each site and count them
    for id, site_name in site_ids.items():
        site_computer_count = site_mobile_device_count = site_apple_tv_count = 0
        for i in range(0, 3): # This was done multiple sites have over 1500 devices, which is the max the API returns per page
            site_computer_object_api_endpoint = f"{jamf_server}/api/v1/sites/{id}/objects?page={i}&page-size=1500&sort=objectType%3Aasc&filter=objectType%3D%3D%22Computer%22"
            site_computer_objects = requests.get(
                site_computer_object_api_endpoint, headers=headers
            )
            site_mobile_device_object_api_endpoint = f"{jamf_server}/api/v1/sites/{id}/objects?page={i}&page-size=1500&sort=objectType%3Aasc&filter=objectType%3D%3D%22Mobile%20Device%22"
            site_mobile_device_objects = requests.get(
                site_mobile_device_object_api_endpoint, headers=headers
            )
            site_apple_tv_object_api_endpoint = f"{jamf_server}/api/v1/sites/{id}/objects?page={i}&page-size=1500&sort=objectType%3Aasc&filter=objectType%3D%3D%22Apple%20TV%22"
            site_apple_tv__objects = requests.get(
                site_apple_tv_object_api_endpoint, headers=headers
            )
            site_computer_count += len(site_computer_objects.json())
            object_ids += [item["objectId"] for item in site_computer_objects.json()]
            site_mobile_device_count += len(site_mobile_device_objects.json())
            site_apple_tv_count += len(site_apple_tv__objects.json())
        csv_row = [
            site_name,
            site_computer_count,
            site_mobile_device_count,
            site_apple_tv_count,
        ]
        with open(
            f"jamf_device_counts_{timestamp}.csv", "a", newline=""
        ) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(csv_row)
    with open(f"jamf_computer_object_ids_{timestamp}.txt", "a") as object_ids_file:
        for item in object_ids:
            object_ids_file.write(item)


if __name__ == "__main__":
    main()
