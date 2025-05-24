# Eksploarsi Document Translation Tools
## Deskripsi Proyek

Proyek ini bertujuan melakukan eksplorasi dan evaluasi berbagai tools untuk penerjemahan dokumen, khususnya menggunakan layanan dari Azure dan DeepL. Proses penerjemahan meliputi:

- **Document Translation**:  
  Menggunakan **Azure Computer Vision OCR** untuk mengekstrak teks dari dokumen gambar, lalu menerjemahkan teks tersebut dengan layanan Azure Translator. Di sini juga diterapkan **custom glossary** untuk memastikan istilah tertentu diterjemahkan secara konsisten.

- **Text Translation**:  
  Untuk file berbentuk `.txt`, hanya dilakukan penerjemahan teks biasa menggunakan Azure Translator.

- **Evaluasi Hasil Terjemahan**:  
  Membandingkan hasil terjemahan antara Azure Translator dan DeepL (menggunakan versi demo website DeepL). Evaluasi dilakukan dengan menggunakan dua metrik utama:
  - **BLEU (Bilingual Evaluation Understudy)** — mengukur kesamaan n-gram antara hasil terjemahan dengan teks target.
  - **ROUGE (Recall-Oriented Understudy for Gisting Evaluation)** — mengukur kesamaan dengan pendekatan recall, lebih menyoroti kesesuaian makna keseluruhan.

### Hasil Evaluasi

- Azure Translator **unggul pada metrik ROUGE**, yang menunjukkan hasil terjemahan Azure lebih baik dalam menangkap keseluruhan makna dan konteks dokumen.
- DeepL **unggul pada metrik BLEU**, yang mengindikasikan hasil terjemahan DeepL lebih presisi dalam kesamaan kata/frasa secara literal.

## Struktur File

- `.env` — konfigurasi environment variables untuk API Azure dan lainnya.
- `doc_translate.py` — script untuk melakukan penerjemahan dokumen dengan OCR dan Azure Translator, termasuk penerapan custom glossary.
- `text_translate.py` — script untuk menerjemahkan file `.txt` menggunakan Azure Translator.
- `evaluate.py` — script untuk mengevaluasi hasil terjemahan menggunakan metrik BLEU dan ROUGE.
- `input.txt` — contoh file teks input yang diterjemahkan.
- `target_bahasa.txt` — teks target dalam Bahasa Indonesia sebagai referensi evaluasi.
- `translated_azure.txt` — hasil terjemahan menggunakan Azure Translator.
- `translated_deepL.txt` — hasil terjemahan menggunakan DeepL.
- `perbandingan_evaluasi_dengan_keterangan.png` — visualisasi perbandingan hasil evaluasi
- `glossary.csv` - custom glossary yang dipanggil pada document translation

## Eksplorasi Document Translation using Azure Power Automate
![image](https://github.com/user-attachments/assets/aa07d7b0-e126-4b7e-b62f-9f25c57b1ab8)
