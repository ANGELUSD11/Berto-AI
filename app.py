from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)

@app.route('/')
def index():
    print("Ruta / llamada, intentando acceder a index.html")
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        prompt = request.form.get('message', '')

        if 'image' in request.files:
            image_file = request.files['image']

            if not image_file.content_type.startswith('image/'):
                return jsonify({'reply': 'El archivo debe ser una imagen'})

            if image_file.filename == '':
                return jsonify({'reply': 'No se subió ninguna imagen.'})

            try:
                image = Image.open(BytesIO(image_file.read()))
                response = model.generate_content([prompt or "define esta imagen", image])
                return jsonify({'reply': response.text})
            except Exception as e:
                return jsonify({'reply': f'Hubo un error al procesar la imagen: {e}'})

        # Si no hay imagen, usa solo el prompt
        contexto_base = (
            "Eres un asistente de IA diseñado para ayudar a agricultores con consejos y/o información útil sobre como manejar sus cultivos de manera adecuada. "
            "Estás integrado dentro de una página chatbot interactiva para garantizar datos fáciles de acceder. "
            "Responde siempre de manera respetuosa brindando información de valor."
        )

        prompt_final = f"{contexto_base}\nUsuario: {prompt}"
        response = model.generate_content(prompt_final)
        return jsonify({'reply': response.text})

    except Exception as e:
        print("Error inesperado en /chat:", e)
        return jsonify({'reply': f'Error inesperado: {e}'})
    
if __name__ == '__main__':
    app.run(debug=False)