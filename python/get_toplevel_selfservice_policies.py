import csv
import datetime
import json
import logging
import requests


def get_bearer_token(url, user, password):
    """
    Function to get bearer token from Jamf

    This function sends a POST request to the specified Jamf API endpoint to obtain a Bearer token.
    The function takes three parameters: the URL of the Jamf API, the username for authentication,
    and the password for authentication. It returns the obtained Bearer token as a string.

    If the request fails for any reason, it logs an error message and returns None.
    """
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

    # Set up logging to output to terminal
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Get bearer token
    API_token = get_bearer_token(jamf_server, username, password)

    get_policies_endpoint = f"{jamf_server}/JSSResource/policies"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + API_token,
    }
    policies = requests.get(get_policies_endpoint, headers=headers)
    policies_json = json.loads(policies.text)
    policy_ids = []

    for policy in policies_json["policies"]:
        policy_ids.append(policy["id"])

    # Gather relevant from policy JSON to get all self service policies available to MITS
    profile_info = {}
    # Loop through each policy ID and gather necessary information about the policy.
    # This includes checking if the site ID is either -1 (all sites) or site_code,
    # and if the scope is set to all computers. If these conditions are met,
    # then extract additional details such as the policy name, trigger type,
    # frequency, self-service display name, and category.
    for id in policy_ids:
        try:
            url = f"{jamf_server}/JSSResource/policies/id/{id}"
            policy_info = requests.get(url, headers=headers)
            policy_json = json.loads(policy_info.text)
            site_id = policy_json["policy"]["general"]["site"]["id"]
            scope = policy_json["policy"]["scope"]["all_computers"]
            if site_id in [-1, site_code] and scope == True:
                logging.info(f"Processing policy {id}")
                policy_name = policy_json["policy"]["general"]["name"]
                trigger = policy_json["policy"]["general"]["trigger"]
                frequency = policy_json["policy"]["general"]["frequency"]
                in_self_service = policy_json["policy"]["self_service"][
                    "use_for_self_service"
                ]
                name_self_service = policy_json["policy"]["self_service"][
                    "self_service_display_name"
                ]
                category = policy_json["policy"]["general"]["category"]["name"]
                if (
                    category
                    not in [
                        "Printers",
                        "Deployment and Enrollment",
                    ]
                    and in_self_service == True
                    and frequency == "Ongoing"
                ):
                    logging.info(f"Gathering info for policy {policy_name}")
                    # Store the gathered information in a dictionary with the
                    # policy name as the key. This allows for easy access to
                    # the individual policies later.
                    profile_info[policy_name] = {
                        "id": id,
                        "trigger": trigger,
                        "frequency": frequency,
                        "name_self_service": name_self_service,
                        "category": category,
                    }
        except Exception as e:
            logging.info(f"Error processing policy {id}: {e}")

    # Convert the profile_info dictionary to a CSV
    fieldnames = [
        "Policy Name",
        "id" "trigger",
        "frequency",
        "name_self_service",
        "category",
    ]
    today = datetime.date.today()
    timestamped_csv_filename = f"self_service_policies_{today.isoformat()}.csv"
    with open(timestamped_csv_filename, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        for policy_name, details in profile_info.items():
            # Create a dictionary with the necessary data to be written into the CSV file.
            # This includes the policy name and all the gathered information (trigger type, frequency,
            # self-service display name, and category).
            csv_data = {"Policy Name": policy_name}
            csv_data.update({k: v for k, v in details.items()})

            # Write the data into the CSV file.
            writer.writerow(csv_data)


if __name__ == "__main__":
    main()
