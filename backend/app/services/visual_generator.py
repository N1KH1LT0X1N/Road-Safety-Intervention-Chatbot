"""Visual generator for road signs and markings."""
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Dict, Any, Optional, Tuple
import logging
import math

logger = logging.getLogger(__name__)


class VisualGenerator:
    """Generate visual representations of road signs and markings."""

    # Color mappings
    COLORS = {
        "red": "#FF0000",
        "white": "#FFFFFF",
        "yellow": "#FFFF00",
        "black": "#000000",
        "blue": "#0000FF",
        "green": "#00FF00",
        "orange": "#FFA500",
    }

    def __init__(self):
        """Initialize visual generator."""
        logger.info("Visual generator initialized")

    def generate_road_sign(
        self,
        sign_type: str,
        shape: str,
        colors: list,
        dimensions: str,
        text: Optional[str] = None,
        size: int = 400,
    ) -> str:
        """Generate road sign image and return as base64."""
        try:
            # Create image with white background
            img = Image.new("RGB", (size, size), self.COLORS.get("white", "#FFFFFF"))
            draw = ImageDraw.Draw(img)

            # Draw based on shape
            if "octagonal" in shape.lower() or "STOP" in sign_type:
                self._draw_octagon(draw, size, colors)
                text = text or "STOP"
            elif "triangular" in shape.lower() or "triangle" in shape.lower():
                self._draw_triangle(draw, size, colors)
            elif "circular" in shape.lower() or "circle" in shape.lower():
                self._draw_circle(draw, size, colors)
            elif "rectangular" in shape.lower() or "rectangle" in shape.lower():
                self._draw_rectangle(draw, size, colors)
            else:
                # Default to circle
                self._draw_circle(draw, size, colors)

            # Add text if provided
            if text:
                self._add_text(draw, size, text, colors)

            # Add dimensions label
            if dimensions:
                self._add_dimension_label(draw, size, dimensions)

            # Convert to base64
            return self._image_to_base64(img)

        except Exception as e:
            logger.error(f"Error generating road sign: {e}")
            return ""

    def _draw_octagon(self, draw: ImageDraw, size: int, colors: list):
        """Draw octagonal STOP sign."""
        center = size // 2
        radius = size // 2 - 20

        # Calculate octagon points
        points = []
        for i in range(8):
            angle = math.pi / 4 * i
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append((x, y))

        # Get colors
        bg_color = self.COLORS.get(colors[0] if colors else "red", "#FF0000")
        border_color = self.COLORS.get(colors[1] if len(colors) > 1 else "white", "#FFFFFF")

        # Draw octagon
        draw.polygon(points, fill=bg_color, outline=border_color, width=10)

    def _draw_triangle(self, draw: ImageDraw, size: int, colors: list):
        """Draw triangular warning sign."""
        padding = 30
        points = [
            (size // 2, padding),  # Top
            (padding, size - padding),  # Bottom left
            (size - padding, size - padding),  # Bottom right
        ]

        # Get colors
        bg_color = self.COLORS.get(colors[1] if len(colors) > 1 else "white", "#FFFFFF")
        border_color = self.COLORS.get(colors[0] if colors else "red", "#FF0000")

        # Draw triangle
        draw.polygon(points, fill=bg_color, outline=border_color, width=8)

    def _draw_circle(self, draw: ImageDraw, size: int, colors: list):
        """Draw circular sign."""
        padding = 30
        bbox = [padding, padding, size - padding, size - padding]

        # Get colors
        bg_color = self.COLORS.get(colors[1] if len(colors) > 1 else "white", "#FFFFFF")
        border_color = self.COLORS.get(colors[0] if colors else "red", "#FF0000")

        # Draw circle
        draw.ellipse(bbox, fill=bg_color, outline=border_color, width=8)

        # For prohibitory signs, add diagonal line
        if "prohibited" in str(colors).lower() or "no" in str(colors).lower():
            center = size // 2
            radius = (size - 2 * padding) // 2
            offset = int(radius * 0.7)
            draw.line(
                [(center - offset, center - offset), (center + offset, center + offset)],
                fill=border_color,
                width=8,
            )

    def _draw_rectangle(self, draw: ImageDraw, size: int, colors: list):
        """Draw rectangular informatory sign."""
        padding = 30
        bbox = [padding, size // 4, size - padding, 3 * size // 4]

        # Get colors
        bg_color = self.COLORS.get(colors[0] if colors else "blue", "#0000FF")
        text_color = self.COLORS.get(colors[1] if len(colors) > 1 else "white", "#FFFFFF")

        # Draw rectangle
        draw.rectangle(bbox, fill=bg_color, outline=text_color, width=5)

    def _add_text(self, draw: ImageDraw, size: int, text: str, colors: list):
        """Add text to sign."""
        try:
            # Try to use a better font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            except:
                font = ImageFont.load_default()

            # Get text color
            text_color = self.COLORS.get(colors[1] if len(colors) > 1 else "white", "#FFFFFF")

            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Center text
            x = (size - text_width) // 2
            y = (size - text_height) // 2

            # Draw text
            draw.text((x, y), text, fill=text_color, font=font)

        except Exception as e:
            logger.warning(f"Could not add text: {e}")

    def _add_dimension_label(self, draw: ImageDraw, size: int, dimensions: str):
        """Add dimension label at bottom."""
        try:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font = ImageFont.load_default()

            text = f"Dimensions: {dimensions[:50]}"
            draw.text((10, size - 25), text, fill="#666666", font=font)

        except Exception as e:
            logger.warning(f"Could not add dimension label: {e}")

    def _image_to_base64(self, img: Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_base64}"

    def generate_road_marking_diagram(
        self, marking_type: str, colors: list, dimensions: str, size: Tuple[int, int] = (600, 200)
    ) -> str:
        """Generate road marking diagram."""
        try:
            img = Image.new("RGB", size, "#333333")  # Dark gray road
            draw = ImageDraw.Draw(img)

            if "broken" in marking_type.lower() or "dashed" in marking_type.lower():
                self._draw_broken_line(draw, size, colors)
            elif "continuous" in marking_type.lower() or "solid" in marking_type.lower():
                self._draw_continuous_line(draw, size, colors)
            elif "arrow" in marking_type.lower():
                self._draw_arrow(draw, size, colors)
            elif "zebra" in marking_type.lower() or "crossing" in marking_type.lower():
                self._draw_zebra_crossing(draw, size, colors)
            elif "chevron" in marking_type.lower():
                self._draw_chevron(draw, size, colors)
            else:
                self._draw_continuous_line(draw, size, colors)

            # Add dimension label
            if dimensions:
                self._add_dimension_label(draw, size[0], dimensions)

            return self._image_to_base64(img)

        except Exception as e:
            logger.error(f"Error generating road marking: {e}")
            return ""

    def _draw_broken_line(self, draw: ImageDraw, size: Tuple[int, int], colors: list):
        """Draw broken/dashed line."""
        y = size[1] // 2
        dash_length = 40
        gap_length = 20
        x = 50

        color = self.COLORS.get(colors[0] if colors else "white", "#FFFFFF")

        while x < size[0] - 50:
            draw.line([(x, y), (x + dash_length, y)], fill=color, width=8)
            x += dash_length + gap_length

    def _draw_continuous_line(self, draw: ImageDraw, size: Tuple[int, int], colors: list):
        """Draw continuous solid line."""
        y = size[1] // 2
        color = self.COLORS.get(colors[0] if colors else "white", "#FFFFFF")
        draw.line([(50, y), (size[0] - 50, y)], fill=color, width=8)

    def _draw_arrow(self, draw: ImageDraw, size: Tuple[int, int], colors: list):
        """Draw arrow marking."""
        center_x = size[0] // 2
        center_y = size[1] // 2
        color = self.COLORS.get(colors[0] if colors else "white", "#FFFFFF")

        # Arrow shaft
        draw.line([(center_x, center_y + 40), (center_x, center_y - 30)], fill=color, width=12)

        # Arrowhead
        points = [(center_x, center_y - 40), (center_x - 25, center_y - 10), (center_x + 25, center_y - 10)]
        draw.polygon(points, fill=color)

    def _draw_zebra_crossing(self, draw: ImageDraw, size: Tuple[int, int], colors: list):
        """Draw zebra crossing stripes."""
        stripe_width = 30
        gap = 10
        x = 50
        color = self.COLORS.get(colors[0] if colors else "white", "#FFFFFF")

        while x < size[0] - 50:
            draw.rectangle([x, 50, x + stripe_width, size[1] - 50], fill=color)
            x += stripe_width + gap

    def _draw_chevron(self, draw: ImageDraw, size: Tuple[int, int], colors: list):
        """Draw chevron marking."""
        center_y = size[1] // 2
        color = self.COLORS.get(colors[0] if colors else "white", "#FFFFFF")

        # Draw multiple chevrons
        for x in range(100, size[0] - 100, 150):
            points = [(x, center_y), (x + 50, center_y - 40), (x + 60, center_y - 40), (x + 10, center_y)]
            draw.polygon(points, fill=color)
