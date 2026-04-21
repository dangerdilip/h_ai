from PIL import Image
import io

def load_image(uploaded_file) -> Image.Image:
    """Safely construct a PIL Image from a Streamlit UploadFile."""
    if uploaded_file is None:
        return None
    try:
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        # Ensure RGB format for Gemini compatibility
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    except Exception as e:
        return None
