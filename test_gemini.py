import os
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
try:
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Hello')
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
