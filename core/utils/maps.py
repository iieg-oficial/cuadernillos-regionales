from pathlib import Path

DRAFT_DIR = Path("output/maps")
DRAFT_MAX_HEIGHT = 2000
DRAFT_QUALITY = 82


def _compress_map(src, dest):
    from PIL import Image

    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        if im.height > DRAFT_MAX_HEIGHT:
            ratio = DRAFT_MAX_HEIGHT / im.height
            new_size = (int(im.width * ratio), DRAFT_MAX_HEIGHT)
            im = im.resize(new_size, Image.LANCZOS)
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3])
            im = bg
        im.save(dest, "JPEG", quality=DRAFT_QUALITY, optimize=True)


def get_draft_path(original, section, key):
    draft_path = DRAFT_DIR / section / f"{key}.jpg"
    if draft_path.exists():
        return draft_path
    _compress_map(original, draft_path)
    return draft_path
