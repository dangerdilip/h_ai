import fitz  # PyMuPDF
import docx
import pandas as pd

def extract_pdf_text(uploaded_file) -> str:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return text[:15000] # Cap text to avoid overflowing Gemini limit
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_docx_text(uploaded_file) -> str:
    try:
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text[:15000]
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_csv_text(uploaded_file) -> str:
    try:
        df = pd.read_csv(uploaded_file)
        # Summarize the schema and first 50 rows
        info = f"Dataframe shape: {df.shape}\n"
        info += f"Columns: {', '.join(df.columns.tolist())}\n"
        info += "First 50 rows preview:\n"
        info += df.head(50).to_csv(index=False)
        return info[:15000]
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

def process_file_upload(uploaded_file) -> tuple:
    """Return tuple (content_text, is_image)."""
    if uploaded_file is None:
        return None, False
        
    filename = uploaded_file.name.lower()
    
    if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return None, True
    elif filename.endswith('.pdf'):
        return extract_pdf_text(uploaded_file), False
    elif filename.endswith('.docx'):
        return extract_docx_text(uploaded_file), False
    elif filename.endswith('.csv'):
        return extract_csv_text(uploaded_file), False
    elif filename.endswith('.txt'):
        return uploaded_file.read().decode('utf-8')[:15000], False
    else:
        return "Unsupported file type.", False
