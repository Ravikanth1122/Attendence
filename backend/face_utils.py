import numpy as np
import io
from PIL import Image, ExifTags
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def pil_from_bytes(b):
    return Image.open(io.BytesIO(b)).convert('RGB')

def correct_image_orientation(img_pil):
    try:
        exif = img_pil._getexif()
        if exif is None:
            return img_pil
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        orientation_val = exif.get(orientation, None)
        if orientation_val == 3:
            img_pil = img_pil.rotate(180, expand=True)
        elif orientation_val == 6:
            img_pil = img_pil.rotate(270, expand=True)
        elif orientation_val == 8:
            img_pil = img_pil.rotate(90, expand=True)
    except Exception:
        pass
    return img_pil

def read_image_bytes_safe(file_bytes):
    img_pil = pil_from_bytes(file_bytes)
    img_pil = correct_image_orientation(img_pil)
    return img_pil

def detect_faces_pil(img_pil):
    boxes, probs = mtcnn.detect(img_pil)
    if boxes is None:
        return [], []
    faces = []
    for box in boxes:
        x1, y1, x2, y2 = [int(b) for b in box]
        face = img_pil.crop((x1, y1, x2, y2)).resize((160,160))
        faces.append(face)
    return faces, boxes

def get_embedding_from_pil(face_pil):
    face_np = np.asarray(face_pil).astype(np.float32)
    if face_np.ndim == 2:
        face_np = np.stack([face_np]*3, axis=-1)
    face_np = (face_np - 127.5) / 128.0
    face_t = torch.tensor(face_np.transpose((2,0,1))).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = resnet(face_t).cpu().numpy().flatten()
    emb = emb / (np.linalg.norm(emb) + 1e-10)
    return emb

def embed_from_pil_list(face_pil_list):
    return [get_embedding_from_pil(f) for f in face_pil_list]

def cosine_similarity(a, b):
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))

def embedding_to_bytes(emb):
    return np.asarray(emb, dtype=np.float32).tobytes()

def bytes_to_embedding(b):
    return np.frombuffer(b, dtype=np.float32)