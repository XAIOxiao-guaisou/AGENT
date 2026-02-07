try:
    from plyer import notification
except ImportError:
    notification = None

def send_notification(title, message):
    """
    Send a system notification and print to console.
    """
    # Console alert (Red text)
    print(f"\033[91m[{title}] {message}\033[0m")
    
    # System Toast
    if notification:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Antigravity',
                timeout=5
            )
        except Exception as e:
            print(f"Failed to send toast notification: {e}")
    else:
        print("plyer not installed, skipping toast notification.")

def alert_critical(message):
    send_notification("ANTIGRAVITY SHERIFF ALERT", message)
