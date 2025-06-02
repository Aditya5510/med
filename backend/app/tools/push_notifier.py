from typing import Dict, Any

def send_push_notification(user_id: str, message: str) -> Dict[str, Any]:

    return {
        "user_id": user_id,
        "message": message,
        "status": "sent (stub)"
    }