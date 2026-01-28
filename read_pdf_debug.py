from pypdf import PdfReader
import sys

def extract_pages(pdf_path, start_page, end_page):
    reader = PdfReader(pdf_path)
    text = ""
    for i in range(start_page, min(end_page, len(reader.pages))):
        text += f"\n--- PÁGINA {i+1} ---\n"
        text += reader.pages[i].extract_text()
    return text

if __name__ == "__main__":
    path = r"C:\Users\Usuario\Downloads\02-diciembre-guia-de-orientacion-saber-11-2026.pdf"
    print(extract_pages(path, 0, 10))
