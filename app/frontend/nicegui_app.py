from nicegui import ui, app
import os
from pathlib import Path
import logging
from PIL import Image
import io
import base64
import cv2
import numpy as np

# Import services
from app.services.color_advisor import ColorAdvisor
from app.services.image_processor import ImageProcessor
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# Global variables to store state
current_image_path = None
current_skin_tone = None
modified_image_path = None

@ui.page('/')
def index():
    """Main application page."""
    with ui.card().classes('w-full max-w-3xl mx-auto my-4'):
        ui.label('Skin Tone Color Advisor').classes('text-2xl font-bold text-center')
        ui.label('Upload a photo to get personalized color recommendations').classes('text-center mb-4')
    
    with ui.card().classes('w-full max-w-3xl mx-auto my-4'):
        with ui.row().classes('w-full justify-center'):
            upload = ui.upload(
                label='Upload Image', 
                auto_upload=True,
                on_upload=handle_upload
            ).props('accept=".jpg, .jpeg, .png"')
    
    # Image display area
    with ui.card().classes('w-full max-w-3xl mx-auto my-4'):
        image_container = ui.element('div').classes('w-full flex justify-center')
        
        # This will be populated when an image is uploaded
        global image_display
        image_display = ui.image().classes('max-w-full max-h-80 object-contain')
        image_display.visible = False
    
    # Skin tone detection results
    with ui.card().classes('w-full max-w-3xl mx-auto my-4').style('display: none') as tone_card:
        ui.label('Detected Skin Tone').classes('text-xl font-bold')
        
        with ui.row().classes('w-full'):
            global skin_tone_label
            skin_tone_label = ui.label('').classes('text-lg')
        
        with ui.row().classes('w-full justify-center gap-4'):
            ui.button('Fair', on_click=lambda: change_skin_tone('Fair')).props('outline color=blue-grey')
            ui.button('Light', on_click=lambda: change_skin_tone('Light')).props('outline color=blue-grey')
            ui.button('Medium', on_click=lambda: change_skin_tone('Medium')).props('outline color=blue-grey')
            ui.button('Dark', on_click=lambda: change_skin_tone('Dark')).props('outline color=blue-grey')
            ui.button('Deep', on_click=lambda: change_skin_tone('Deep')).props('outline color=blue-grey')
    
    # Color recommendations
    with ui.card().classes('w-full max-w-3xl mx-auto my-4').style('display: none') as recommendations_card:
        ui.label('Recommended Color Palettes').classes('text-xl font-bold')
        
        global color_palettes_container
        color_palettes_container = ui.element('div').classes('w-full')
        
        ui.label('Colors to Avoid').classes('text-xl font-bold mt-4')
        
        global avoid_colors_container
        avoid_colors_container = ui.element('div').classes('w-full')
    
    # Store references to cards that need to be shown/hidden
    global ui_elements
    ui_elements = {
        'tone_card': tone_card,
        'recommendations_card': recommendations_card,
        'image_display': image_display
    }

async def handle_upload(e):
    """Handle image upload event."""
    try:
        global current_image_path, current_skin_tone, ui_elements
        
        # Get the uploaded file
        file = e.files[0]
        
        # Read file content
        content = await file.read()
        
        # Save the image to disk
        filename = f"{settings.UPLOAD_FOLDER}/{file.name}"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'wb') as f:
            f.write(content)
        
        current_image_path = filename
        logger.info(f"Image saved to {filename}")
        
        # Display the image
        ui_elements['image_display'].set_source(filename)
        ui_elements['image_display'].visible = True
        
        # Detect skin tone
        result = ImageProcessor.detect_skin_tone(filename)
        
        if result['success']:
            current_skin_tone = result['skin_tone']
            skin_tone_label.set_text(f"Detected skin tone: {current_skin_tone}")
            
            # Show the skin tone card
            ui_elements['tone_card'].style('display: block')
            
            # Get and display color recommendations
            display_color_recommendations(current_skin_tone)
            
            # Show recommendations card
            ui_elements['recommendations_card'].style('display: block')
        else:
            ui.notify(f"Error: {result['message']}", type='negative')
    
    except Exception as e:
        logger.error(f"Error handling upload: {str(e)}")
        ui.notify(f"Error processing image: {str(e)}", type='negative')

def change_skin_tone(new_tone):
    """Change the skin tone of the current image."""
    try:
        global current_image_path, current_skin_tone, modified_image_path
        
        if not current_image_path:
            ui.notify("Please upload an image first", type='warning')
            return
        
        # Update the current skin tone
        current_skin_tone = new_tone
        skin_tone_label.set_text(f"Selected skin tone: {current_skin_tone}")
        
        # Modify the image
        modified_image_path = ImageProcessor.modify_skin_tone(current_image_path, new_tone)
        
        # Display the modified image
        ui_elements['image_display'].set_source(modified_image_path)
        
        # Update color recommendations
        display_color_recommendations(new_tone)
        
        ui.notify(f"Skin tone changed to {new_tone}", type='positive')
    
    except Exception as e:
        logger.error(f"Error changing skin tone: {str(e)}")
        ui.notify(f"Error changing skin tone: {str(e)}", type='negative')

def display_color_recommendations(skin_tone):
    """Display color recommendations for the given skin tone."""
    try:
        # Get recommendations
        recommendations = ColorAdvisor.get_color_recommendations(skin_tone)
        
        # Clear previous recommendations
        with color_palettes_container:
            ui.clear()
            
            # Display each palette
            for palette in recommendations['palettes']:
                with ui.card().classes('my-2'):
                    ui.label(palette['name']).classes('font-bold')
                    
                    with ui.row().classes('w-full flex-wrap gap-2'):
                        for color in palette['colors']:
                            with ui.card().classes('p-0 m-0'):
                                ui.element('div').style(f'background-color: {color}; width: 50px; height: 50px; border-radius: 4px;')
                                ui.label(color).classes('text-xs text-center')
        
        # Display colors to avoid
        with avoid_colors_container:
            ui.clear()
            
            with ui.row().classes('w-full flex-wrap gap-2'):
                for color in recommendations['avoid']:
                    with ui.card().classes('p-0 m-0'):
                        ui.element('div').style(f'background-color: {color}; width: 50px; height: 50px; border-radius: 4px;')
                        ui.label(color).classes('text-xs text-center')
    
    except Exception as e:
        logger.error(f"Error displaying recommendations: {str(e)}")
        ui.notify(f"Error displaying recommendations: {str(e)}", type='negative')

# Add a favicon and title
app.add_static_files('/favicon', str(Path(__file__).parent.parent / 'static' / 'favicon.ico'))
ui.run_with(
    title="Skin Tone Color Advisor",
    favicon="favicon.ico"
)