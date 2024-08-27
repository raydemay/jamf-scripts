"""
This script was used to migrate config profiles into a test Jamf instance.
It gets all the top level profiles and all profiles in site_code, and strips the site from those profiles,
to be imported into a different Jamf instance.
"""
import logging
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
    site_code = 1

    # Get bearer token
    API_token = get_bearer_token(jamf_server, username, password)

    get_configprofiles = f"{jamf_server}/JSSResource/osxconfigurationprofiles"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_token,
    }

    config_profiles = requests.get(get_configprofiles, headers=headers)
    configprofiles_list = json.loads(config_profiles.text)
    configprofile_ids = []

    for profiles in configprofiles_list["os_x_configuration_profiles"]:
        configprofile_ids.append(profiles["id"])

    profiles_to_migrate = []
    for id in configprofile_ids:
        try:
            url = f"{jamf_server}/JSSResource/osxconfigurationprofiles/id/{id}/subset/general"
            configprofile_general = requests.get(url, headers=headers)
            configprofile_general_json = json.loads(configprofile_general.text)
            site_id = configprofile_general_json["os_x_configuration_profile"][
                "general"
            ]["site"]["id"]
            if site_id == 1:
                configprofile_general_json["os_x_configuration_profile"]["general"][
                    "site"
                ]["id"] = -1
                configprofile_general_json["os_x_configuration_profile"]["general"][
                    "site"
                ]["name"] = "None"
                profiles_to_migrate.append(configprofile_general_json)
            if site_id == -1:
                profiles_to_migrate.append(configprofile_general_json)
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
            continue
    with open(f"configprofilestomove.txt", "w") as file:
        json.dump(profiles_to_migrate, file)


if __name__ == "__main__":
    main()
