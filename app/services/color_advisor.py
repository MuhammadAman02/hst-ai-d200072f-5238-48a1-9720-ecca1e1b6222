from typing import Dict, List, Tuple, Any
import colorsys
import numpy as np
import logging

# Get logger
logger = logging.getLogger(__name__)

class ColorAdvisor:
    """Service for recommending colors based on skin tone."""
    
    # Color palettes for different skin tones
    SKIN_TONE_PALETTES = {
        "Fair": {
            "recommended": [
                {"name": "Soft pastels", "colors": ["#E6B3B3", "#B3E6CC", "#B3CCE6", "#E6CCB3"]},
                {"name": "Cool blues", "colors": ["#6699CC", "#336699", "#003366", "#99CCFF"]},
                {"name": "Soft pinks", "colors": ["#FFB6C1", "#FF69B4", "#FFC0CB", "#DB7093"]},
                {"name": "Emerald greens", "colors": ["#2E8B57", "#3CB371", "#00FF7F", "#66CDAA"]}
            ],
            "avoid": ["#FFA500", "#FF8C00", "#FF7F50", "#FF4500"]  # Bright oranges
        },
        "Light": {
            "recommended": [
                {"name": "Jewel tones", "colors": ["#9932CC", "#8A2BE2", "#4B0082", "#800080"]},
                {"name": "Soft neutrals", "colors": ["#D2B48C", "#DEB887", "#F5DEB3", "#FFDEAD"]},
                {"name": "Dusty pinks", "colors": ["#DBB2D1", "#C9A9C9", "#DDA0DD", "#D8BFD8"]},
                {"name": "Olive greens", "colors": ["#808000", "#6B8E23", "#556B2F", "#BDB76B"]}
            ],
            "avoid": ["#FFFF00", "#FFFFE0", "#FFFACD", "#FAFAD2"]  # Pale yellows
        },
        "Medium": {
            "recommended": [
                {"name": "Earth tones", "colors": ["#CD853F", "#D2691E", "#8B4513", "#A0522D"]},
                {"name": "Coral shades", "colors": ["#FF7F50", "#FF6347", "#FA8072", "#E9967A"]},
                {"name": "Teals", "colors": ["#008080", "#20B2AA", "#5F9EA0", "#00CED1"]},
                {"name": "Rich purples", "colors": ["#800080", "#8B008B", "#9400D3", "#9932CC"]}
            ],
            "avoid": ["#F0E68C", "#EEE8AA", "#FAFAD2", "#FFFFE0"]  # Light yellows
        },
        "Dark": {
            "recommended": [
                {"name": "Bright colors", "colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]},
                {"name": "Orange shades", "colors": ["#FFA500", "#FF8C00", "#FF7F50", "#FF4500"]},
                {"name": "Warm reds", "colors": ["#FF0000", "#DC143C", "#B22222", "#8B0000"]},
                {"name": "Gold tones", "colors": ["#FFD700", "#DAA520", "#B8860B", "#CD853F"]}
            ],
            "avoid": ["#000080", "#00008B", "#191970", "#2F4F4F"]  # Very dark colors
        },
        "Deep": {
            "recommended": [
                {"name": "Vibrant colors", "colors": ["#FF1493", "#00FFFF", "#FF4500", "#7FFF00"]},
                {"name": "Bright yellows", "colors": ["#FFFF00", "#FFD700", "#FFA500", "#FFFF54"]},
                {"name": "Fuchsia pinks", "colors": ["#FF00FF", "#FF69B4", "#FF1493", "#C71585"]},
                {"name": "Bright blues", "colors": ["#1E90FF", "#00BFFF", "#87CEEB", "#00FFFF"]}
            ],
            "avoid": ["#A9A9A9", "#696969", "#808080", "#778899"]  # Muted grays
        }
    }
    
    @classmethod
    def get_color_recommendations(cls, skin_tone: str) -> Dict[str, Any]:
        """
        Get color recommendations based on skin tone.
        
        Args:
            skin_tone: Detected skin tone (Fair, Light, Medium, Dark, Deep)
            
        Returns:
            Dictionary with recommended and colors to avoid
        """
        try:
            if skin_tone not in cls.SKIN_TONE_PALETTES:
                logger.warning(f"Unknown skin tone: {skin_tone}, defaulting to Medium")
                skin_tone = "Medium"
            
            return {
                "skin_tone": skin_tone,
                "palettes": cls.SKIN_TONE_PALETTES[skin_tone]["recommended"],
                "avoid": cls.SKIN_TONE_PALETTES[skin_tone]["avoid"]
            }
        except Exception as e:
            logger.error(f"Error getting color recommendations: {str(e)}")
            return {
                "skin_tone": skin_tone,
                "palettes": [],
                "avoid": []
            }
    
    @staticmethod
    def generate_complementary_colors(base_color: Tuple[int, int, int], num_colors: int = 4) -> List[str]:
        """
        Generate complementary colors based on color theory.
        
        Args:
            base_color: Base RGB color tuple
            num_colors: Number of colors to generate
            
        Returns:
            List of hex color codes
        """
        try:
            # Convert RGB to HSV
            r, g, b = [x/255.0 for x in base_color]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Generate colors with evenly spaced hues
            colors = []
            for i in range(num_colors):
                # Shift hue by equal amounts around the color wheel
                new_h = (h + i/num_colors) % 1.0
                # Convert back to RGB
                new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
                # Convert to hex
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(new_r * 255), 
                    int(new_g * 255), 
                    int(new_b * 255)
                )
                colors.append(hex_color)
            
            return colors
        except Exception as e:
            logger.error(f"Error generating complementary colors: {str(e)}")
            return ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]  # Fallback colors