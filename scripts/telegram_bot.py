from notifications.telegram import start_polling_bot

def run():
    """Launching a Telegram bot via django-extensions runscript."""
    print("Starting Telegram bot...")
    start_polling_bot()

if __name__ == "__main__":
    run()
