import cv2
import numpy as np
from PIL import Image
import os
from typing import Tuple, List, Dict, Any, Optional
import logging
from pathlib import Path
import uuid
from datetime import datetime
from ..core.config import settings

# Get logger
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Service for processing and analyzing images."""
    
    @staticmethod
    def save_uploaded_image(image_data: bytes) -> str:
        """
        Save an uploaded image to disk.
        
        Args:
            image_data: Raw image data in bytes
            
        Returns:
            Path to the saved image
        """
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"upload_{timestamp}_{unique_id}.jpg"
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # Save path
        save_path = os.path.join(settings.UPLOAD_FOLDER, filename)
        
        # Convert bytes to image and save
        try:
            image = Image.open(Image.io.BytesIO(image_data))
            image.save(save_path)
            logger.info(f"Image saved to {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise
    
    @staticmethod
    def detect_skin_tone(image_path: str) -> Dict[str, Any]:
        """
        Detect the dominant skin tone in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with skin tone information
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")
            
            # Convert to RGB (OpenCV uses BGR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to HSV for better skin detection
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            # This is a simplified range and may need adjustment
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create skin mask
            skin_mask = cv2.inRange(image_hsv, lower_skin, upper_skin)
            
            # Apply mask to get only skin pixels
            skin_pixels = cv2.bitwise_and(image_rgb, image_rgb, mask=skin_mask)
            
            # Get non-zero pixels (skin pixels)
            non_zero_pixels = skin_pixels[np.where((skin_pixels != [0, 0, 0]).all(axis=2))]
            
            if len(non_zero_pixels) == 0:
                return {
                    "success": False,
                    "message": "No skin detected in the image",
                    "skin_tone": None,
                    "rgb": None,
                    "hsv": None
                }
            
            # Calculate average color of skin pixels
            avg_color = np.mean(non_zero_pixels, axis=0).astype(int)
            
            # Convert RGB to HSV for skin tone classification
            avg_color_rgb = tuple(avg_color)
            avg_color_hsv = cv2.cvtColor(np.uint8([[avg_color_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
            
            # Classify skin tone based on HSV values
            # This is a simplified classification
            h, s, v = avg_color_hsv
            
            # Simple skin tone classification
            if v < 100:
                skin_tone = "Deep"
            elif v < 140:
                skin_tone = "Dark"
            elif v < 170:
                skin_tone = "Medium"
            elif v < 200:
                skin_tone = "Light"
            else:
                skin_tone = "Fair"
            
            return {
                "success": True,
                "skin_tone": skin_tone,
                "rgb": avg_color_rgb.tolist(),
                "hsv": avg_color_hsv.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error detecting skin tone: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing image: {str(e)}",
                "skin_tone": None,
                "rgb": None,
                "hsv": None
            }
    
    @staticmethod
    def modify_skin_tone(image_path: str, target_tone: str) -> str:
        """
        Modify the skin tone in an image.
        
        Args:
            image_path: Path to the image file
            target_tone: Target skin tone (Fair, Light, Medium, Dark, Deep)
            
        Returns:
            Path to the modified image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")
            
            # Convert to HSV for better skin detection and modification
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create skin mask
            skin_mask = cv2.inRange(image_hsv, lower_skin, upper_skin)
            
            # Define target HSV adjustments based on desired skin tone
            # These values are approximate and may need fine-tuning
            tone_adjustments = {
                "Fair": {"v_factor": 1.3, "s_factor": 0.7},
                "Light": {"v_factor": 1.2, "s_factor": 0.8},
                "Medium": {"v_factor": 1.0, "s_factor": 1.0},
                "Dark": {"v_factor": 0.8, "s_factor": 1.2},
                "Deep": {"v_factor": 0.6, "s_factor": 1.3}
            }
            
            if target_tone not in tone_adjustments:
                raise ValueError(f"Invalid target tone: {target_tone}")
            
            # Get adjustment factors
            v_factor = tone_adjustments[target_tone]["v_factor"]
            s_factor = tone_adjustments[target_tone]["s_factor"]
            
            # Create a copy of the image
            modified_hsv = image_hsv.copy()
            
            # Apply adjustments only to skin pixels
            skin_pixels = np.where(skin_mask == 255)
            
            # Adjust saturation (S channel)
            modified_hsv[skin_pixels, 1] = np.clip(
                modified_hsv[skin_pixels, 1] * s_factor, 0, 255).astype(np.uint8)
            
            # Adjust value/brightness (V channel)
            modified_hsv[skin_pixels, 2] = np.clip(
                modified_hsv[skin_pixels, 2] * v_factor, 0, 255).astype(np.uint8)
            
            # Convert back to BGR
            modified_image = cv2.cvtColor(modified_hsv, cv2.COLOR_HSV2BGR)
            
            # Create a unique filename for the modified image
            original_path = Path(image_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            modified_filename = f"{original_path.stem}_{target_tone}_{timestamp}{original_path.suffix}"
            modified_path = os.path.join(settings.UPLOAD_FOLDER, modified_filename)
            
            # Save the modified image
            cv2.imwrite(modified_path, modified_image)
            
            return modified_path
            
        except Exception as e:
            logger.error(f"Error modifying skin tone: {str(e)}")
            raise