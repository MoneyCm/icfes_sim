from pypdf import PdfReader
import io

def get_pdf_text(file_source):
    """
    Extrae texto de un objeto de archivo PDF (UploadFile o BytesIO).
    Mikey v1.2
    """
    try:
        reader = PdfReader(file_source)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        print(f"Error extrayendo PDF: {e}")
        return ""

def get_pdf_info(file_source):
    """Retorna información básica del documento. Mikey"""
    try:
        reader = PdfReader(file_source)
        return {
            "pages": len(reader.pages),
            "metadata": reader.metadata
        }
    except:
        return {"pages": 0, "metadata": {}}
