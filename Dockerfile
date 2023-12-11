FROM python:3.10.11-slim-buster

WORKDIR /app

# torch CPU
# ----------------------
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# sentence transformers deps
# ----------------------
RUN pip install transformers tqdm numpy scikit-learn scipy nltk sentencepiece

# install git
# ----------------------
RUN apt-get update && apt-get install -y git

# install ffmpeg
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# install lang-segment
# ----------------------
# RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && cd GroundingDINO
# RUN pip install -e GroundingDINO

RUN cd ..
RUN git clone https://github.com/luca-medeiros/lang-segment-anything && cd lang-segment-anything
RUN pip install -e lang-segment-anything

# install sentence transformers no deps
# ----------------------
RUN pip install --no-deps sentence-transformers

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Bake the model into the image
RUN python -c 'from sentence_transformers import SentenceTransformer; embedder = SentenceTransformer("clip-ViT-B-32")'

WORKDIR /app
# copy the folder app including to the container without any other folders
COPY app app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
