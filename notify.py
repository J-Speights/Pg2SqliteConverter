import requests


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
    print("Failed to send notification.")
    return 1
