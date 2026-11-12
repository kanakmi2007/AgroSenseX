from dotenv import load_dotenv
load_dotenv()

import io
import os
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

import keras
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AgroSenseX")

# ---------------------------------------------------------------------------
# Standard 38 PlantVillage Class Names (Alphabetically ordered)
# ---------------------------------------------------------------------------
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

# ---------------------------------------------------------------------------
# Pydantic Response Schema
# ---------------------------------------------------------------------------
class DiagnosisResponse(BaseModel):
    crop: str = Field(description="Name of the crop/plant identified (e.g., Tomato, Apple, Corn)")
    disease: str = Field(description="Specific disease name, or 'Healthy' if no disease is present")
    is_healthy: bool = Field(description="True if the crop is healthy, False if diseased")
    confidence: float = Field(description="Model confidence percentage (0.0 to 100.0)")
    summary: str = Field(description="Clear explanation of the disease, causes, and impacts in English")
    sensor_insight: str = Field(description="Analysis of how live sensor readings (moisture, pH, temp) correlate with or influence this disease")
    treatment_steps: List[str] = Field(description="Actionable, prioritized treatment or preventive steps for the farmer")
    hindi_summary: str = Field(description="Simple, practical explanation and treatment advice translated into Hindi for local farmers")

# Global model container
model = None

# ---------------------------------------------------------------------------
# FastAPI Lifespan (Model Loading on Startup)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    logger.info("Loading pre-trained MobileNetV2 PlantVillage model from Hugging Face...")
    try:
        # Load directly from Hugging Face via Keras 3 integration
        model = keras.saving.load_model("hf://rarfileexe/Plant-Disease-Detector")
        logger.info("Successfully loaded model from 'hf://rarfileexe/Plant-Disease-Detector'")
    except Exception as e:
        logger.warning(f"Direct load from 'hf://rarfileexe/Plant-Disease-Detector' encountered: {e}")
        try:
            from huggingface_hub import hf_hub_download
            logger.info("Attempting fallback download via huggingface_hub...")
            model_file = hf_hub_download(repo_id="rarfileexe/Plant-Disease-Detector", filename="model_4_mobilenet_finetuned.keras")
            model = keras.saving.load_model(model_file)
            logger.info(f"Successfully loaded fallback model from '{model_file}'")
        except Exception as fallback_err:
            logger.error(f"Failed to load model from Hugging Face: {fallback_err}")
            logger.info("Will attempt to reload on first request if model is needed.")
    yield

# ---------------------------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AgroSenseX Crop Leaf Disease Detection & AI Summarization",
    description="Zero-training MobileNetV2 Deep Learning Inference paired with Gemini 2.5 Flash for multimodal crop diagnosis and IoT sensor correlation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static Files & Jinja2 Templates (kalyanijha445 UI Integration)
# ---------------------------------------------------------------------------
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# Custom url_for helper supporting both path and filename parameters
def custom_url_for(name: str, **params):
    if name == "static":
        path = params.get("path") or params.get("filename") or ""
        return f"/static/{path.lstrip('/')}"
    return f"/{name}"

templates.env.globals["url_for"] = custom_url_for

# Helper function to parse label
def parse_label(label: str):
    if "___" in label:
        parts = label.split("___", 1)
        crop = parts[0].replace("_", " ").strip()
        disease = parts[1].replace("_", " ").strip()
    else:
        crop = label
        disease = "Healthy" if "healthy" in label.lower() else label
    
    is_healthy = "healthy" in disease.lower()
    return crop, disease, is_healthy

# ---------------------------------------------------------------------------
# Primary Frontend Routes (kalyanijha445 Design)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Primary Landing Page matching teammate's UI design."""
    home_file = os.path.join(templates_path, "home.html")
    if os.path.exists(home_file):
        return templates.TemplateResponse(request, "home.html", {"user": "Farmer Ramesh"})
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, tab: str = "overview"):
    """Main SaaS Farm Dashboard with interactive tabs."""
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": "Farmer Ramesh",
        "active_tab": tab
    })

@app.get("/dashboard/disease", response_class=HTMLResponse)
async def dashboard_disease_page(request: Request):
    """Direct route into the AI Plant Disease Detection diagnostic lab."""
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": "Farmer Ramesh",
        "active_tab": "disease"
    })

@app.get("/dashboard/{tab_name}", response_class=HTMLResponse)
async def dashboard_tab_page(request: Request, tab_name: str):
    """Direct route for any specific dashboard section."""
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": "Farmer Ramesh",
        "active_tab": tab_name
    })

@app.get("/check")
async def check_get():
    """Authentication gateway."""
    return RedirectResponse(url="/dashboard")

@app.post("/check")
async def check_post():
    """Form auth redirection into dashboard."""
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
async def logout():
    """Logout redirect back to home."""
    return RedirectResponse(url="/")

@app.get("/test", response_class=HTMLResponse)
async def serve_test_ui():
    """Backup standalone route for test_ui.html."""
    ui_path = os.path.join(os.path.dirname(__file__), "test_ui.html")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>test_ui.html not found</h2>")

# ---------------------------------------------------------------------------
# Analyze Leaf Endpoint
# ---------------------------------------------------------------------------
@app.post("/analyze-leaf", response_model=DiagnosisResponse)
async def analyze_leaf(
    file: UploadFile = File(..., description="Leaf image file (JPEG/PNG)"),
    moisture: Optional[float] = Form(None, description="Soil moisture percentage from sensor"),
    ph: Optional[float] = Form(None, description="Soil pH level from sensor"),
    temp: Optional[float] = Form(None, description="Ambient temperature (°C) from sensor")
):
    global model

    # Ensure model is loaded
    if model is None:
        try:
            logger.info("Attempting to load model on first demand...")
            model = keras.saving.load_model("hf://rarfileexe/Plant-Disease-Detector")
        except Exception as e:
            try:
                from huggingface_hub import hf_hub_download
                model_file = hf_hub_download(repo_id="rarfileexe/Plant-Disease-Detector", filename="model_4_mobilenet_finetuned.keras")
                model = keras.saving.load_model(model_file)
            except Exception as fallback_err:
                raise HTTPException(
                    status_code=503,
                    detail=f"Model could not be loaded from Hugging Face. Check internet connectivity. Error: {fallback_err}"
                )

    # 1. Read uploaded leaf image bytes
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    except Exception as img_err:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {img_err}")

    # Pass raw [0, 255] float32 pixel values to MobileNetV2 with NO / 255.0 division
    img_array = np.expand_dims(np.array(img, dtype=np.float32), axis=0)

    # 2. Run model prediction
    predictions = model.predict(img_array)
    pred_idx = int(np.argmax(predictions[0]))
    confidence_pct = float(np.max(predictions[0])) * 100.0

    raw_label = CLASS_NAMES[pred_idx] if pred_idx < len(CLASS_NAMES) else f"Unknown_class_{pred_idx}"
    crop_detected, disease_detected, is_healthy = parse_label(raw_label)

    logger.info(f"MobileNetV2: {raw_label} ({confidence_pct:.2f}%) | Crop: {crop_detected}, Disease: {disease_detected}")

    # -------------------------------------------------------------------------
    # 3. Multimodal Analysis with Gemini 2.5 Flash
    # Send image bytes directly to gemini-2.5-flash alongside IoT telemetry
    # -------------------------------------------------------------------------
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        load_dotenv()
        gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if gemini_api_key:
        try:
            client = genai.Client(api_key=gemini_api_key)

            # Convert uploaded leaf image bytes into a multimodal Gemini Part
            mime_type = file.content_type if file.content_type and file.content_type.startswith("image/") else "image/jpeg"
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            sensor_text = []
            if moisture is not None:
                sensor_text.append(f"Soil Moisture: {moisture:.1f}%")
            else:
                sensor_text.append("Soil Moisture: Not provided")

            if ph is not None:
                sensor_text.append(f"Soil pH: {ph:.1f}")
            else:
                sensor_text.append("Soil pH: Not provided")

            if temp is not None:
                sensor_text.append(f"Ambient Temperature: {temp:.1f}°C")
            else:
                sensor_text.append("Ambient Temperature: Not provided")

            prompt = f"""You are an elite agricultural AI and plant pathologist.
Analyze this uploaded plant leaf image visually and cross-reference with the deep learning model and IoT sensor telemetry:

DEEP LEARNING (MobileNetV2 PlantVillage) PREDICTION:
- Detected Crop: {crop_detected}
- Detected Status / Disease: {disease_detected}
- Model Confidence: {confidence_pct:.2f}%
- Is Healthy: {is_healthy}

LIVE ARDUINO IOT FIELD SENSORS:
{chr(10).join('- ' + s for s in sensor_text)}

INSTRUCTIONS:
1. Visually examine the actual leaf image carefully. Validate, refine, or confirm the disease diagnosis using your visual expertise.
2. In 'crop' and 'disease', specify the identified crop and disease name (or 'Healthy').
3. In 'is_healthy', return true if the leaf has no disease symptoms, or false if infected/diseased.
4. In 'confidence', return the diagnosis confidence percentage (0.0 to 100.0).
5. In 'summary', provide a comprehensive English diagnosis detailing visual leaf symptoms observed, disease cause, and crop impact.
6. In 'sensor_insight', analyze how the live IoT sensor metrics (moisture, pH, temp) correlate with this disease (e.g. high moisture promoting fungal spore germination, heat stress, pH nutrient lock) or maintain health. If readings are missing, mention ideal ranges.
7. In 'treatment_steps', provide prioritized, actionable management steps (cultural, organic, and chemical).
8. In 'hindi_summary', provide a simple, respectful, and practical diagnosis and treatment advice in Hindi (हिंदी) so Indian farmers can immediately understand and take action.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DiagnosisResponse,
                ),
            )

            diagnosis = DiagnosisResponse.model_validate_json(response.text)
            return diagnosis

        except Exception as gemini_err:
            logger.error(f"Gemini API generation error: {gemini_err}")
            # Fall back to structured response with error notice

    # 4. Fallback if GEMINI_API_KEY is not set or Gemini API is temporarily unavailable
    logger.info("Generating standard diagnosis response (Gemini API key not configured or unavailable).")
    
    sensor_summary_parts = []
    if moisture is not None:
        sensor_summary_parts.append(f"Moisture: {moisture}%")
    if ph is not None:
        sensor_summary_parts.append(f"pH: {ph}")
    if temp is not None:
        sensor_summary_parts.append(f"Temp: {temp}°C")
    sensor_str = ", ".join(sensor_summary_parts) if sensor_summary_parts else "No sensor readings provided"

    if is_healthy:
        summary_text = f"The {crop_detected} leaf appears healthy with {confidence_pct:.2f}% confidence. No visible symptoms of disease were detected."
        sensor_insight_text = f"Sensor status: {sensor_str}. Maintain balanced irrigation and monitor temperature to sustain healthy growth."
        treatments = [
            "Continue standard watering and nutrient schedule.",
            "Maintain soil drainage to prevent fungal root rot.",
            "Inspect foliage weekly for early signs of pests or disease."
        ]
        hindi_text = f"{crop_detected} का पौधा पूरी तरह स्वस्थ दिख रहा है (सटीकता: {confidence_pct:.2f}%)। सामान्य सिंचाई और देखभाल जारी रखें।"
    else:
        summary_text = f"The {crop_detected} plant is affected by {disease_detected} (Confidence: {confidence_pct:.2f}%). Prompt intervention is recommended to prevent spread."
        sensor_insight_text = f"Current field conditions ({sensor_str}) should be reviewed. High moisture combined with moderate temperatures often accelerates fungal and bacterial outbreaks."
        treatments = [
            f"Prune and destroy severely infected leaves showing {disease_detected}.",
            "Avoid overhead irrigation to minimize leaf wetness duration.",
            "Apply recommended organic copper-based or bio-fungicide spray if necessary.",
            "Ensure adequate plant spacing for improved airflow."
        ]
        hindi_text = f"{crop_detected} में {disease_detected} की पुष्टि हुई है (सटीकता: {confidence_pct:.2f}%)। रोगग्रस्त पत्तियों को हटा दें और जल निकासी में सुधार करें।"

    if not gemini_api_key:
        sensor_insight_text += " [Note: Add GEMINI_API_KEY to your .env file to activate full Gemini 2.5 Flash analysis]."

    return DiagnosisResponse(
        crop=crop_detected,
        disease=disease_detected,
        is_healthy=is_healthy,
        confidence=round(confidence_pct, 2),
        summary=summary_text,
        sensor_insight=sensor_insight_text,
        treatment_steps=treatments,
        hindi_summary=hindi_text
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
