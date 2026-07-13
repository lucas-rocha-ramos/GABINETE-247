from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import shutil
import os

app = FastAPI(title="NeuralSync Audio API")

# Permite que o seu frontend (na Vercel ou localhost) converse com esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, coloque a URL do seu site Vercel aqui
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega o modelo de IA na memória
# "base" é rápido e leve. Para mais precisão, mude para "medium" ou "large-v3" (exige mais RAM/GPU)
print("Carregando o modelo Neural. Aguarde...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Modelo pronto para processar!")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # 1. Salva o arquivo gigante (até 2GB) temporariamente no disco do servidor
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Inicia a transcrição com a IA local
        print(f"Processando: {file.filename}")
        segments, info = model.transcribe(temp_file_path, beam_size=5, language="pt")
        
        # 3. Formata os dados para enviar ao seu Frontend iOS 26
        formatted_segments = []
        for segment in segments:
            formatted_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "speaker": "Orador" # Nota: Diarização real (separar vozes) exige Pyannote, um módulo extra pesado.
            })
            
        # 4. Limpa o arquivo temporário para não lotar o servidor
        os.remove(temp_file_path)
        
        return {
            "status": "success",
            "language": info.language,
            "segments": formatted_segments
        }
        
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
