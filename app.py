from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import os
import requests
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()  # Load env variables for local development

app = Flask(__name__)
CORS(app)


# Read Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b-32768"  # or whatever model you prefer


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def generate_flashcards_with_groq(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are an AI tutor. From the following class notes, generate 10 flashcards in Q&A format.
    Format it strictly as:
    Question: ...
    Answer: ...
    (Repeat 10 times)

    Notes:
    {text}
    """

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful flashcard generator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    data = response.json()
    ai_response = data['choices'][0]['message']['content']
    return parse_flashcards(ai_response)


def parse_flashcards(raw_text):
    flashcards = []
    lines = raw_text.strip().split("\n")
    question, answer = None, None

    for line in lines:
        if line.lower().startswith("question:"):
            if question and answer:
                flashcards.append({"question": question.strip(), "answer": answer.strip()})
            question = line[len("Question:"):].strip()
            answer = None
        elif line.lower().startswith("answer:"):
            answer = line[len("Answer:"):].strip()
        elif answer is not None:
            answer += " " + line.strip()

    if question and answer:
        flashcards.append({"question": question.strip(), "answer": answer.strip()})

    return flashcards


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files['pdf']
    try:
        extracted_text = extract_text_from_pdf(pdf_file)
        flashcards = generate_flashcards_with_groq(extracted_text)
        return jsonify({"flashcards": flashcards})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Flashcard Generator API is running!"


if __name__ == "__main__":
    app.run(debug=True)
