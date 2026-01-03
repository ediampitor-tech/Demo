# Demo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random
from datetime import datetime

class OneMusicBrandGenerator:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.colors = {
            'primary': (101, 80, 231),    # Purple (#6550E7)
            'secondary': (118, 75, 162),  # Deep Purple (#764BA2)
            'accent': (255, 87, 104),     # Coral (#FF5768)
            'dark': (18, 18, 24),         # Dark (#121218)
            'light': (245, 247, 255),     # Light (#F5F7FF)
            'gradient_start': (101, 80, 231),
            'gradient_end': (118, 75, 162)
        }
    
    def create_gradient_background(self):
        """Create a gradient background"""
        base = Image.new('RGB', (self.width, self.height), self.colors['dark'])
        draw = ImageDraw.Draw(base)
        
        # Draw gradient
        for y in range(self.height):
            # Calculate gradient color
            r = int(self.colors['gradient_start'][0] + 
                   (self.colors['gradient_end'][0] - self.colors['gradient_start'][0]) * y / self.height)
            g = int(self.colors['gradient_start'][1] + 
                   (self.colors['gradient_end'][1] - self.colors['gradient_start'][1]) * y / self.height)
            b = int(self.colors['gradient_start'][2] + 
                   (self.colors['gradient_end'][2] - self.colors['gradient_start'][2]) * y / self.height)
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return base
    
    def create_abstract_wave(self, draw, amplitude=50, frequency=0.02, phase=0):
        """Create abstract sound wave visualization"""
        points = []
        for x in range(0, self.width + 10, 5):
            y = self.height//2 + amplitude * np.sin(frequency * x + phase)
            points.append((x, y))
        
        # Draw wave with gradient
        for i in range(len(points) - 1):
            opacity = int(50 + 150 * (i / len(points)))
            color = (*self.colors['primary'], opacity)
            draw.line([points[i], points[i+1]], fill=self.colors['primary'], width=3)
        
        # Fill under wave
        fill_points = points + [(self.width, self.height), (0, self.height)]
        draw.polygon(fill_points, fill=(*self.colors['primary'], 30))
    
    def create_music_note(self, size=200):
        """Create a stylized music note icon"""
        note_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(note_img)
        
        # Draw the note head (circle)
        head_radius = size // 4
        head_center = (size // 2, size // 3)
        draw.ellipse(
            [head_center[0] - head_radius, head_center[1] - head_radius,
             head_center[0] + head_radius, head_center[1] + head_radius],
            fill=self.colors['accent']
        )
        
        # Draw the stem
        stem_width = size // 12
        stem_start = (head_center[0] + head_radius, head_center[1])
        stem_end = (stem_start[0], stem_start[1] + size // 2)
        draw.rectangle(
            [stem_start[0], stem_start[1],
             stem_start[0] + stem_width, stem_end[1]],
            fill=self.colors['light']
        )
        
        # Draw the flag
        flag_points = [
            (stem_end[0] + stem_width, stem_end[1] - size//6),
            (stem_end[0] + size//4, stem_end[1] - size//8),
            (stem_end[0] + size//6, stem_end[1] + size//8)
        ]
        draw.polygon(flag_points, fill=self.colors['secondary'])
        
        return note_img
    
    def create_spectrum_visualizer(self, draw, num_bars=50):
        """Create audio spectrum visualization"""
        bar_width = self.width // (num_bars + 2)
        spacing = bar_width // 2
        
        for i in range(num_bars):
            x = spacing + i * (bar_width + spacing)
            
            # Random bar height for visual interest
            height = random.randint(20, self.height // 2)
            if i % 4 == 0:
                height = random.randint(self.height // 3, self.height // 2)
            
            # Gradient color based on height
            color_ratio = height / (self.height // 2)
            r = int(self.colors['primary'][0] * color_ratio)
            g = int(self.colors['primary'][1] * color_ratio)
            b = int(self.colors['primary'][2] * color_ratio)
            color = (r, g, b)
            
            # Draw bar with rounded top
            y_top = self.height // 2 + self.height // 4 - height
            y_bottom = self.height // 2 + self.height // 4
            
            # Bar shadow
            draw.rectangle(
                [x + 2, y_top + 2, x + bar_width - 2, y_bottom],
                fill=(*color, 50)
            )
            
            # Main bar
            draw.rectangle(
                [x, y_top, x + bar_width - 4, y_bottom],
                fill=color
            )
            
            # Rounded top
            draw.ellipse(
                [x, y_top - bar_width//2, x + bar_width - 4, y_top + bar_width//2],
                fill=color
            )
    
    def create_app_icon(self, size=512):
        """Create a square app icon"""
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Create gradient background
        for y in range(size):
            r = int(self.colors['gradient_start'][0] + 
                   (self.colors['gradient_end'][0] - self.colors['gradient_start'][0]) * y / size)
            g = int(self.colors['gradient_start'][1] + 
                   (self.colors['gradient_end'][1] - self.colors['gradient_start'][1]) * y / size)
            b = int(self.colors['gradient_start'][2] + 
                   (self.colors['gradient_end'][2] - self.colors['gradient_start'][2]) * y / size)
            draw.line([(0, y), (size, y)], fill=(r, g, b))
        
        # Draw circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, size, size], fill=255)
        
        # Apply mask
        icon.putalpha(mask)
        
        # Create note in center
        note = self.create_music_note(size // 2)
        note_x = (size - note.width) // 2
        note_y = (size - note.height) // 2
        icon.paste(note, (note_x, note_y), note)
        
        # Add "1" in the note head
        try:
            font = ImageFont.truetype("arial.ttf", size // 3)
        except:
            font = ImageFont.load_default()
        
        text = "1"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = note_x + note.width // 2 - text_width // 2
        text_y = note_y + size // 6 - text_height // 2
        
        draw.text((text_x, text_y), text, fill=self.colors['light'], font=font)
        
        # Add glow effect
        glow = icon.filter(ImageFilter.GaussianBlur(10))
        final_icon = Image.alpha_composite(glow, icon)
        
        return final_icon
    
    def create_promo_banner(self):
        """Create a promotional banner for the app"""
        # Create base image with gradient
        image = self.create_gradient_background()
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # Create abstract waves
        self.create_abstract_wave(draw, amplitude=80, frequency=0.015, phase=0)
        self.create_abstract_wave(draw, amplitude=60, frequency=0.025, phase=1.5)
        self.create_abstract_wave(draw, amplitude=40, frequency=0.035, phase=3)
        
        # Create spectrum visualizer
        self.create_spectrum_visualizer(draw, num_bars=40)
        
        # Add app icon
        icon = self.create_app_icon(300)
        image.paste(icon, (100, (self.height - 300) // 2), icon)
        
        # Add app name
        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
            price_font = ImageFont.truetype("arial.ttf", 48)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            price_font = ImageFont.load_default()
        
        # App title
        title = "OneMusic"
        title_x = 450
        title_y = self.height // 3
        
        # Add text shadow
        draw.text((title_x + 3, title_y + 3), title, fill=(0, 0, 0, 150), font=title_font)
        draw.text((title_x, title_y), title, fill=self.colors['light'], font=title_font)
        
        # Tagline
        tagline = "Your Premium Music Hub"
        tagline_x = 450
        tagline_y = title_y + 100
        draw.text((tagline_x, tagline_y), tagline, fill=self.colors['accent'], font=subtitle_font)
        
        # Price points
        prices_y = tagline_y + 100
        
        # Standard Plan
        standard = "Standard: $1.5/month"
        draw.text((tagline_x, prices_y), standard, fill=self.colors['light'], font=price_font)
        
        # Dual Plan
        dual = "Dual: $3/month"
        draw.text((tagline_x, prices_y + 60), dual, fill=self.colors['light'], font=price_font)
        
        # Family Plan
        family = "Family: $8/month"
        draw.text((tagline_x, prices_y + 120), family, fill=self.colors['light'], font=price_font)
        
        # Call to action
        cta = "Stream Smarter. Listen Better."
        cta_y = self.height - 100
        draw.text(
            (self.width//2 - 300, cta_y),
            cta,
            fill=(255, 255, 255, 200),
            font=subtitle_font
        )
        
        return image
    
    def create_social_media_assets(self):
        """Create various social media assets"""
        assets = {}
        
        # Instagram post (1080x1080)
        insta_size = 1080
        insta_image = Image.new('RGB', (insta_size, insta_size), self.colors['dark'])
        insta_draw = ImageDraw.Draw(insta_image)
        
        # Add circular gradient
        center_x, center_y = insta_size // 2, insta_size // 2
        max_radius = insta_size // 2
        
        for r in range(max_radius, 0, -1):
            ratio = r / max_radius
            color = (
                int(self.colors['primary'][0] * ratio),
                int(self.colors['primary'][1] * ratio),
                int(self.colors['primary'][2] * ratio)
            )
            insta_draw.ellipse(
                [center_x - r, center_y - r, center_x + r, center_y + r],
                outline=color,
                width=2
            )
        
        # Add app icon
        icon = self.create_app_icon(400)
        insta_image.paste(icon, (insta_size//2 - 200, insta_size//2 - 200), icon)
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = "OneMusic"
        bbox = insta_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        insta_draw.text(
            (insta_size//2 - text_width//2, insta_size - 150),
            text,
            fill=self.colors['light'],
            font=font
        )
        
        assets['instagram'] = insta_image
        
        # Twitter header (1500x500)
        twitter_header = Image.new('RGB', (1500, 500), self.colors['dark'])
        twitter_draw = ImageDraw.Draw(twitter_header)
        
        # Create wave pattern
        for i in range(20):
            x = i * 75
            amplitude = random.randint(50, 150)
            points = []
            for x2 in range(x, x + 75):
                y = 250 + amplitude * np.sin(0.05 * x2)
                points.append((x2, y))
            
            color = (
                self.colors['primary'][0],
                self.colors['primary'][1],
                self.colors['primary'][2],
                100
            )
            if len(points) > 1:
                twitter_draw.line(points, fill=self.colors['primary'], width=2)
        
        # Add logo and text
        icon = self.create_app_icon(200)
        twitter_header.paste(icon, (100, 150), icon)
        
        try:
            header_font = ImageFont.truetype("arial.ttf", 48)
            sub_font = ImageFont.truetype("arial.ttf", 28)
        except:
            header_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
        
        twitter_draw.text((350, 180), "OneMusic", fill=self.colors['light'], font=header_font)
        twitter_draw.text((350, 240), "Premium music streaming from $1.5/month", 
                         fill=self.colors['accent'], font=sub_font)
        twitter_draw.text((350, 280), "#OneMusic #MusicStreaming #AffordableMusic", 
                         fill=self.colors['light'], font=sub_font)
        
        assets['twitter_header'] = twitter_header
        
        return assets
    
    def generate_all_assets(self):
        """Generate all brand assets"""
        print("🎵 Generating OneMusic brand assets...")
        
        # Create assets
        app_icon = self.create_app_icon(512)
        promo_banner = self.create_promo_banner()
        social_assets = self.create_social_media_assets()
        
        # Save all assets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save app icon
        app_icon.save(f"onemusic_icon_{timestamp}.png", "PNG")
        print(f"✅ App icon saved: onemusic_icon_{timestamp}.png")
        
        # Save promo banner
        promo_banner.save(f"onemusic_banner_{timestamp}.png", "PNG")
        print(f"✅ Promo banner saved: onemusic_banner_{timestamp}.png")
        
        # Save social media assets
        for platform, asset in social_assets.items():
            filename = f"onemusic_{platform}_{timestamp}.png"
            asset.save(filename, "PNG")
            print(f"✅ {platform} asset saved: {filename}")
        
        # Create a color palette image
        palette = Image.new('RGB', (800, 200), self.colors['dark'])
        palette_draw = ImageDraw.Draw(palette)
        
        color_width = 150
        colors_list = [
            ("Primary", self.colors['primary']),
            ("Secondary", self.colors['secondary']),
            ("Accent", self.colors['accent']),
            ("Dark", self.colors['dark']),
            ("Light", self.colors['light'])
        ]
        
        for i, (name, color) in enumerate(colors_list):
            x = 50 + i * (color_width + 20)
            # Color swatch
            palette_draw.rectangle([x, 50, x + color_width, 150], fill=color)
            # Color name
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Add text with contrasting color
            text_color = self.colors['light'] if i == 3 else self.colors['dark']
            palette_draw.text((x + 10, 160), name, fill=text_color, font=font)
            palette_draw.text((x + 10, 180), f"RGB{color}", fill=text_color, font=font)
        
        palette.save(f"onemusic_palette_{timestamp}.png", "PNG")
        print(f"✅ Color palette saved: onemusic_palette_{timestamp}.png")
        
        # Create README with usage guidelines
        self.create_brand_guidelines(timestamp)
        
        print("\n🎉 All assets generated successfully!")
        print("📁 Files created:")
        print("   - App icon (512x512)")
        print("   - Promotional banner (1200x800)")
        print("   - Instagram post (1080x1080)")
        print("   - Twitter header (1500x500)")
        print("   - Brand color palette")
        print("   - Brand guidelines (onemusic_brand_guide.txt)")
        
        return {
            'icon': app_icon,
            'banner': promo_banner,
            'social': social_assets,
            'palette': palette
        }
    
    def create_brand_guidelines(self, timestamp):
        """Create brand guidelines text file"""
        guidelines = f"""OneMusic Brand Guidelines
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

BRAND OVERVIEW
==============
OneMusic is a premium music streaming service offering affordable plans 
starting at $1.5/month. Our brand represents quality, accessibility, 
and modern music enjoyment.

COLOR PALETTE
=============
Primary: RGB{self.colors['primary']} (#6550E7)
Secondary: RGB{self.colors['secondary']} (#764BA2)
Accent: RGB{self.colors['accent']} (#FF5768)
Dark: RGB{self.colors['dark']} (#121218)
Light: RGB{self.colors['light']} (#F5F7FF)

TYPOGRAPHY
==========
Primary Font: Montserrat (or Arial as fallback)
Headings: Bold, 36-80px
Body: Regular, 16-24px
Prices: Bold, 28-48px

LOGO USAGE
==========
- Always maintain minimum clear space around the logo
- Use the full-color version on dark backgrounds
- Use the simplified version for small sizes
- Never stretch or distort the logo

BRAND VOICE
===========
- Professional yet approachable
- Confident but not arrogant
- Clear and direct about value
- Music-focused and passionate

TAGLINES
========
- Your Premium Music Hub
- Stream Smarter. Listen Better.
- Premium music for everyone
- One app, all your music

SOCIAL MEDIA
============
Hashtags: #OneMusic #MusicStreaming #AffordableMusic
Handle: @OneMusicApp
Bio: Premium music streaming from $1.5/month

APP STORE DESCRIPTION
=====================
OneMusic delivers premium music streaming without the premium price. 
Access millions of songs, create playlists, and enjoy high-quality 
audio with our affordable plans starting at just $1.5/month.

PLANS & PRICING
===============
Standard: $1.5/month - Single user, ad-free, downloads
Dual: $3/month - Two users, shared playlists
Family: $8/month - Up to 6 users, family mix

FILE INFORMATION
================
All generated files use the timestamp: {timestamp}
For updates or modifications, rerun the generator script.
"""
        
        with open(f"onemusic_brand_guide_{timestamp}.txt", "w") as f:
            f.write(guidelines)
        print(f"✅ Brand guidelines saved: onemusic_brand_guide_{timestamp}.txt")

# Generate all assets
if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import PIL
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "pillow", "numpy"])
        print("Packages installed successfully!")
    
    # Generate brand assets
    generator = OneMusicBrandGenerator()
    assets = generator.generate_all_assets()
    
    # Optional: Display the images if in an environment that supports it
    try:
        assets['banner'].show()
    except:
        print("\n📝 Note: Images have been saved to disk.")
        print("   To view them, open the generated PNG files.")
