
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
# === Configuración de Supabase ===
SUPABASE_URL = os.getenv('SUPABASE_URL')      
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
SUPABASE_BUCKET = "documents"                         

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def subir_pdf_a_supabase(pdf_name: str):
    supabase.auth.sign_in_with_password({"email": "python@gmail.com", "password": "python"})

    with open(f'./files/{pdf_name}', 'rb') as f:
        response = supabase.storage.from_("documents").upload(
            file=f,
            path=f"rutines/{pdf_name}",
            file_options={"cache-control": "3600", "upsert": "false"},
        )