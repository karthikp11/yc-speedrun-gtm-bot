from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import config

class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=config.SLACK_BOT_TOKEN)
        self.channel_id = config.SLACK_CHANNEL_ID

    def send_signal_alert(self, signal: dict):
        is_early = signal["official_status"] == "EARLY_FOUNDER_SIGNAL"
        
        if is_early:
            header_text = "🔥 EARLY YC SIGNAL — Founder Announced Before YC"
            status_desc = "⚡ Founder announced / not yet officially announced by YC"
        else:
            header_text = "NEW YC COMPANY"
            status_desc = "✅ Confirmed by YC"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Company:*\n{signal['company_name']}"},
                    {"type": "mrkdwn", "text": f"*Batch:*\n{signal['batch_identifier']}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{signal['source_platform']}"}
                ]
            }
        ]

        if signal.get("founder_info"):
            blocks[1]["fields"].append({"type": "mrkdwn", "text": f"*Founder:*\n{signal['founder_info']}"})

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Status:* {status_desc}\n\n*Original post:*\n> \"{signal['description']}\""
            }
        })

        if signal.get("source_url"):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Original post"},
                        "url": signal["source_url"],
                        "style": "primary" if is_early else "default"
                    }
                ]
            })

        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"New Signal: {signal['company_name']} ({signal['batch_identifier']})"
            )
        except SlackApiError as e:
            print(f"[ERROR] Slack API dispatch failed: {e.response['error']}")
