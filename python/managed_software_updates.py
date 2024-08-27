import datetime as dt
import logging
import requests


def get_token_client_credentials(url, clientId, clientSecret):
    """
    Function to obtain a Bearer token using client credentials from Jamf.

    This function sends a POST request to the specified Jamf API endpoint to obtain a Bearer token
    using client credentials.

    Args:
        url (str): The URL of the Jamf API.
        clientId (str): The client ID for authentication.
        clientSecret (str): The client secret for authentication.

    Returns:
        token (str): The obtained Bearer token. If the request fails for any reason, it returns None.
    """
    api_endpoint = f"{url}/api/oauth/token"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": clientId,
        "client_secret": clientSecret,
        "grant_type": "client_credentials",
    }
    try:
        # This function sends a POST request to the specified Jamf API endpoint
        # to obtain a Bearer token using client credentials.
        response = requests.post(api_endpoint, headers=headers, data=data)
        bearer_token = response.json().get("access_token")
        token_expiration = response.json().get(
            "expires_in"
        )  # Could be used for keep_alive function if I make one
        logging.info("Bearer token generated using OAuth credentials")
        return bearer_token
    except requests.exceptions.RequestException as exception:
        # If the request fails for any reason, it logs an error message and returns None.
        logging.info("Failed to get bearer token:", exception)
        return None


def enable_logging() -> None:
    """
    Enables logging in the program.

    This function sets up a logger and adds a console handler. It then sets the log level
    to INFO and formats the logs with a date, the logger name, the log level, and the message.
    Finally, it enables logging by adding the handler to the logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging enabled")
    return None


def determine_patch_deadline() -> str:
    """
    Determine the patch deadline by calculating the day of the week for today,
    and then calculate the next Saturday. Calculate the patch deadline as 10pm EST on that Saturday.

    Args:
        None

    Returns:
        str: The patch deadline in YYYY-mm-DDTHH:MM:SS format.
    """
    # Get current date/time
    now = dt.datetime.now()
    # Calculate the day of the week for today
    day_of_week = now.weekday()

    if day_of_week != 5:  # If it's not Saturday
        days_until_saturday = (6 - day_of_week) % 7
        next_saturday = now + dt.timedelta(days=days_until_saturday)
    else:
        next_saturday = now

    # Calculate the patch deadline as 10pm EST on the calculated Saturday
    patch_deadline_utc = next_saturday.replace(hour=22, minute=0, second=0)
    patch_deadline = patch_deadline_utc.strftime("%Y-%m-%dT%H:%M:%S")
    logging.info(f"Patch deadline is {patch_deadline}")
    return patch_deadline


def main():
    # Define the Jamf server URL and client credentials
    jamf_server = "https://yourjamfserver.jamfcloud.com"
    client_credentials = {
        "client_name": "",
        "client_id": "", # Add client ID here
        "client_secret": "", #Add client secret here
        "grant_type": "client_credentials",
        "content_type": "application/x-www-form-urlencoded",
    }

    # Determine patch deadline
    patch_deadline = determine_patch_deadline()

    # Update settings
    target_group_id = 1 # Smart group ID number here
    patch_group = {"objectType": "COMPUTER_GROUP", "groupId": f"{target_group_id}"}

    enable_logging()

    # Get bearer token
    API_token = get_token_client_credentials(
        jamf_server,
        client_credentials["client_id"],
        client_credentials["client_secret"],
    )

    # Set the URL for the managed software updates plans endpoint
    url = f"{jamf_server}/api/v1/managed-software-updates/plans/group"

    # Create a payload with the group and configuration details
    payload = {
        "group": patch_group,
        "config": {
            "updateAction": "DOWNLOAD_INSTALL_SCHEDULE",
            "versionType": "LATEST_ANY",
            "specificVersion": "NO_SPECIFIC_VERSION",
            "forceInstallLocalDateTime": patch_deadline,
        },
    }

    # Define the headers with the API token and content type
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + API_token,
    }

    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"HTTP Response Code: {response.status_code}")


if __name__ == "__main__":
    main()
