from pathlib import Path
from io import BytesIO
import requests
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'brand'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://www.metrc.com/wp-content/uploads/2026/03/Metrc-Logo-Deep-Forest-400-scaled-1-2-1024x240.png'

r = requests.get(URL, timeout=45, headers={'User-Agent': 'Mozilla/5.0 candidate-asset-retrieval'})
r.raise_for_status()
source = r.content
(OUT / 'metrc-logo-source.webp').write_bytes(source)

im = Image.open(BytesIO(source)).convert('RGB')
a = np.asarray(im).astype(np.int16)
bg = a[0, 0]
diff = np.max(np.abs(a - bg), axis=2)
alpha = np.clip((diff - 1) * 34, 0, 255).astype(np.uint8)
rgba = np.zeros((a.shape[0], a.shape[1], 4), dtype=np.uint8)
rgba[..., 0] = 0x21
rgba[..., 1] = 0x3F
rgba[..., 2] = 0x39
rgba[..., 3] = alpha
Image.fromarray(rgba, 'RGBA').save(OUT / 'metrc-logo-forest.png', optimize=True)
print('brand assets prepared', im.size)
