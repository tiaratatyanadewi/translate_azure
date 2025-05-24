import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_LOCATION = os.getenv("AZURE_TRANSLATOR_LOCATION")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")

AZURE_OCR_KEY = os.getenv("AZURE_OCR_KEY")
AZURE_OCR_ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT")


@st.cache_data
def load_glossary():
    try:
        df = pd.read_csv("glossary.csv")
        return set(df["term"].str.strip())
    except Exception:
        return set()


GLOSSARY_TERMS = load_glossary()


def azure_translate(text, target_lang="id"):
    glossary_mask = {}
    for term in sorted(GLOSSARY_TERMS, key=len, reverse=True):
        if term in text:
            mask = f"[[[{hash(term)}]]]"
            glossary_mask[mask] = term
            text = text.replace(term, mask)

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_LOCATION,
        "Content-type": "application/json",
    }
    body = [{"text": text}]
    params = {"to": target_lang}
    response = requests.post(
        AZURE_TRANSLATOR_ENDPOINT, params=params, headers=headers, json=body
    )
    response.raise_for_status()
    translated = response.json()[0]["translations"][0]["text"]

    for mask, term in glossary_mask.items():
        translated = translated.replace(mask, term)

    return translated


def azure_ocr(image: Image.Image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    ocr_url = AZURE_OCR_ENDPOINT + "vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_OCR_KEY,
        "Content-Type": "application/octet-stream",
    }

    response = requests.post(ocr_url, headers=headers, data=img_bytes)
    response.raise_for_status()
    operation_url = response.headers["Operation-Location"]

    while True:
        result_response = requests.get(
            operation_url, headers={"Ocp-Apim-Subscription-Key": AZURE_OCR_KEY}
        )
        result = result_response.json()
        if result["status"] == "succeeded":
            break
        elif result["status"] == "failed":
            raise Exception("Azure OCR failed")
        time.sleep(1)

    lines = []
    for read_result in result["analyzeResult"]["readResults"]:
        for line in read_result["lines"]:
            lines.append(
                {
                    "text": line["text"],
                    "boundingBox": line["boundingBox"],
                }
            )
    return lines


def process_image(image):
    ocr_lines = azure_ocr(image)
    new_image = image.copy()
    draw_new = ImageDraw.Draw(new_image)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    translated_texts = []

    for item in ocr_lines:
        original_text = item["text"]
        bounding_box = item["boundingBox"]

        translated = azure_translate(original_text)
        translated_texts.append(translated)

        x_coords = bounding_box[0::2]
        y_coords = bounding_box[1::2]
        left = min(x_coords)
        top = min(y_coords)
        right = max(x_coords)
        bottom = max(y_coords)

        draw_new.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255, 230))

        draw_new.text((left, top), translated, fill=(0, 0, 0), font=font)

    return {
        "original_image": image,
        "translated_image": new_image,
        "translated_text": "\n".join(translated_texts),
    }


def process_pdf(file_bytes):
    images = convert_from_bytes(
        file_bytes, poppler_path=r"C:\poppler-23.11.0\poppler-23.11.0\Library\bin"
    )
    return [process_image(img) for img in images]


def images_to_pdf_bytes(images):
    pdf_bytes = io.BytesIO()
    # Pastikan semua image dalam mode RGB
    rgb_images = [img.convert("RGB") for img in images]
    # Simpan semua halaman images ke 1 PDF
    rgb_images[0].save(
        pdf_bytes, format="PDF", save_all=True, append_images=rgb_images[1:]
    )
    pdf_bytes.seek(0)
    return pdf_bytes


st.title("Demo Document Translator (Version 1)")

file_type = st.radio("Choose file type", ["PDF", "Image"])
uploaded_file = st.file_uploader("Upload file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    with st.spinner("Processing..."):
        try:
            if file_type == "PDF":
                pages = process_pdf(uploaded_file.read())
            else:
                image = Image.open(uploaded_file).convert("RGB")
                pages = [process_image(image)]

            # Tampilkan hasil dan opsi download per halaman
            for idx, page in enumerate(pages):
                st.markdown(f"### Page {idx+1}")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(page["original_image"], caption="Original")
                with col2:
                    st.image(page["translated_image"], caption="Translated")

                    buf = io.BytesIO()
                    page["translated_image"].save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button(
                        label=f"Download Translated Image Page {idx+1}",
                        data=buf,
                        file_name=f"translated_page_{idx+1}.png",
                        mime="image/png",
                    )

                st.markdown("#### Translated Text")
                st.markdown(page["translated_text"].replace("\n", "  \n"))

            # Download 1 file PDF gabungan semua halaman hasil translate (jika file input PDF)
            if file_type == "PDF" and len(pages) > 0:
                translated_images = [p["translated_image"] for p in pages]
                pdf_bytes = images_to_pdf_bytes(translated_images)
                st.download_button(
                    label="Download Translated PDF",
                    data=pdf_bytes,
                    file_name="translated_document.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"Error during processing: {e}")
