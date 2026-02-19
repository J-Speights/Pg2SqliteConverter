import msal
import requests
from typing import Optional


def get_graph_token():
    app_id = ""
    client_secret = ""
    tenant_id = ""
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.ConfidentialClientApplication(
        app_id, authority=authority, client_credential=client_secret
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if not result:
        print("Error obtaining token.")
        return None
    if "access_token" in result:
        return result["access_token"]
    print("Error obtaining token:", result.get("error"))
    return None


def upload_file_to_teams_channel(
    file_path: str, team_id: str, channel_id: str, token: str
) -> tuple[int, Optional[str]]:
    headers = {"Authorization": f"Bearer {token}"}

    site_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/filesFolder"
    response = requests.get(site_url, headers=headers)

    if response.status_code != 200:
        print("Unable to access Teams Files: ", response.json())
        return 1, None

    drive_id = response.json()["parentReference"]["driveId"]
    item_id = response.json()["id"]

    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}:/{file_path.split('/')[-1]}:/content"
    with open(file_path, "rb") as file_data:
        upload_response = requests.put(upload_url, headers=headers, data=file_data)

    if not upload_response.status_code == 201:
        print("Error uploading file:", upload_response.json())
        return 1, None

    print("File uploaded successfully.")
    return 0, upload_response.json()["webUrl"]


def notify_teams(webhook_url: str, s3_url: str) -> int:
    """
    Sends a notification to a Teams channel.
    """
    message = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": "New Database Backup Uploaded.",
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": f"The new database backup can be accessed [here]({s3_url}).",
                            "wrap": True,
                        },
                    ],
                },
            }
        ],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, json=message, headers=headers)

    print(response)
    if response.status_code == 200:
        print("Notification sent successfully.")
        return 0
    if response.status_code == 202:
        print("Notification dispatched for send.")
        return 0
    print("Failed to send notification.")
    return 1
