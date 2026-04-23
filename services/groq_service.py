import os
import json
import re
import random
import requests
from groq import Groq
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _fetch_url_content(self, url):
        """
        Fetch URL content with proper encoding detection
        for all languages including Hindi, Arabic, Chinese etc.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            res = requests.get(url, timeout=10, headers=headers)

            # Auto detect encoding
            if res.encoding and res.encoding.lower() not in ['utf-8', 'utf8']:
                res.encoding = res.apparent_encoding

            text = res.text

            # Remove HTML tags to get clean text
            clean = re.sub(r'<[^>]+>', ' ', text)
            clean = re.sub(r'\s+', ' ', clean).strip()

            return clean[:4000]

        except Exception as e:
            return f"Could not fetch content: {str(e)}"

    def _detect_language(self, text):
        """
        Detect language from text using character ranges.
        Returns language name for prompt context.
        """
        if not text:
            return "English"

        # Count characters from different scripts
        hindi      = len(re.findall(r'[\u0900-\u097F]', text))
        arabic     = len(re.findall(r'[\u0600-\u06FF]', text))
        chinese    = len(re.findall(r'[\u4E00-\u9FFF]', text))
        japanese   = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text))
        korean     = len(re.findall(r'[\uAC00-\uD7AF]', text))
        cyrillic   = len(re.findall(r'[\u0400-\u04FF]', text))  # Russian etc
        bengali    = len(re.findall(r'[\u0980-\u09FF]', text))
        tamil      = len(re.findall(r'[\u0B80-\u0BFF]', text))
        telugu     = len(re.findall(r'[\u0C00-\u0C7F]', text))
        gujarati   = len(re.findall(r'[\u0A80-\u0AFF]', text))
        punjabi    = len(re.findall(r'[\u0A00-\u0A7F]', text))
        malayalam  = len(re.findall(r'[\u0D00-\u0D7F]', text))
        kannada    = len(re.findall(r'[\u0C80-\u0CFF]', text))

        scores = {
            'Hindi':     hindi,
            'Arabic':    arabic,
            'Chinese':   chinese,
            'Japanese':  japanese,
            'Korean':    korean,
            'Russian':   cyrillic,
            'Bengali':   bengali,
            'Tamil':     tamil,
            'Telugu':    telugu,
            'Gujarati':  gujarati,
            'Punjabi':   punjabi,
            'Malayalam': malayalam,
            'Kannada':   kannada,
        }

        best = max(scores, key=scores.get)
        if scores[best] > 10:
            return best

        return "English"

    def analyze_news(self, input_type, content):
        """
        Input types: 'url', 'image', 'video'
        Returns: { result, confidence, virality, explanation, language }
        """
        try:
            messages = []

            if input_type == 'url':
                text_content = self._fetch_url_content(content)
                detected_lang = self._detect_language(text_content)

                prompt = f"""
You are a multilingual fake news detection expert.

The following news content is in **{detected_lang}** language.
Analyze it carefully regardless of the language it is written in.

Your tasks:
1. Determine if the news is 'FAKE' or 'REAL'
2. Provide a confidence score (0-100)
3. Calculate a virality prediction score (0-100)
4. Write a detailed explanation IN ENGLISH regardless of source language
5. Identify the language of the original content

IMPORTANT: You must analyze content in ANY language - Hindi, Arabic, Chinese, Tamil,
Telugu, Bengali, Gujarati, Punjabi, Malayalam, Kannada, Russian, French, Spanish, etc.
Never say you cannot analyze non-English content.

Respond EXCLUSIVELY in this JSON format:
{{
    "result": "FAKE" or "REAL",
    "confidence": float_value,
    "virality": float_value,
    "explanation": "detailed explanation in English",
    "language": "{detected_lang}"
}}

News URL: {content}
Content: {text_content}
"""
                messages = [{"role": "user", "content": prompt}]

            elif input_type == 'image' or input_type == 'video':
                base64_image = self._encode_image(content)
                prompt = """
You are a multilingual fake news detection expert.
Analyze this image/screenshot for fake news regardless of what language it contains.
The image may contain text in Hindi, Arabic, Chinese, Tamil, or any other language.

Respond EXCLUSIVELY in this JSON format:
{
    "result": "FAKE" or "REAL",
    "confidence": float_value,
    "virality": float_value,
    "explanation": "detailed explanation in English",
    "language": "detected language in image"
}
"""
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }]
            else:
                return None

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                response_format={"type": "json_object"}
            )

            response_text = chat_completion.choices[0].message.content
            data = json.loads(response_text)

            return {
                'result':      data.get('result', 'FAKE').upper(),
                'confidence':  float(data.get('confidence', random.uniform(80, 95))),
                'virality':    float(data.get('virality',   random.uniform(50, 90))),
                'explanation': data.get('explanation', 'Analysis complete.'),
                'language':    data.get('language', 'English')
            }

        except Exception as e:
            print(f"Groq API Error: {e}")
            return {
                'result':      "ERROR",
                'confidence':  0,
                'virality':    0,
                'explanation': f"Groq Error: {str(e)}",
                'language':    "Unknown"
            }