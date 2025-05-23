import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set framework to NiceGUI
os.environ["FRAMEWORK"] = "nicegui"

# Import the NiceGUI app
from app.frontend.nicegui_app import ui

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Start NiceGUI
    ui.run(host=host, port=port, title="Skin Tone Color Advisor")