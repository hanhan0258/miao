from flask import Flask, request, send_file, abort
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

app = Flask(__name__)

TARGET_H = 200
PAD_X = 24
PAD_Y = 24

FONT_CANDIDATES = ["Arial", "Helvetica", "sans-serif"]

def pick_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()

def measure(text: str, font: ImageFont.FreeTypeFont):
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)  # (l, t, r, b)
    w = bbox - bbox
    h = bbox - bbox
    return bbox, w, h

app.route("/img")
def gen_img():
    raw = (request.args.get("text") or "").strip()
    if not raw:
        abort(400, description="missing ?text=")
    text = raw if raw.endswith("。") else raw + "。"

    max_text_h = TARGET_H - 2 * PAD_Y
    size = max(12, max_text_h)
    while size > 12:
        font = pick_font(size)
        bbox, tw, th = measure(text, font)
        if th <= max_text_h:
            break
        size -= 1
    else:
        font = pick_font(12)
        bbox, tw, th = measure(text, font)

    W = tw + 2 * PAD_X
    H = TARGET_H
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    x = PAD_X - bbox
    y = (H - th) // 2 - bbox
    draw.text((x, y), text, font=font, fill="black")

    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return send_file(bio, mimetype="image/png")

app.route("/")
def index():
    return "GET /img?text=你的文本 -> PNG，白底黑字，高度200"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
