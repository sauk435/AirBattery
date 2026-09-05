
from PIL import Image, ImageDraw, ImageFont


def _pick_font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("segoeuib.ttf", "segoeui.ttf", "arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def create_battery_icon(
    percentage: int,
    charging: bool = False,
    size: int = 128,  # Generate at 128x128 by default for better text rendering
) -> Image.Image:

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # -- Colors --
    if percentage < 0:
        fill_color = (100, 100, 100, 255)
    elif percentage <= 20:
        fill_color = (255, 59, 48, 255)    # Apple Red
    elif percentage <= 50:
        fill_color = (255, 204, 0, 255)    # Apple Yellow
    else:
        fill_color = (52, 199, 89, 255)    # Apple Green
        
    outline_color = (220, 220, 220, 255)
    bg_color = (50, 50, 50, 200)

    bw, bh = int(size * 0.86), int(size * 0.68)
    bx, by = int(size * 0.04), (size - bh) // 2
    b_rad = int(size * 0.12)
    
    tw, th = int(size * 0.08), int(size * 0.28)
    tx, ty = bx + bw - 2, (size - th) // 2
    t_rad = int(size * 0.04)
    
    draw.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=t_rad, fill=outline_color)
    
    draw.rounded_rectangle(
        [bx, by, bx+bw, by+bh], 
        radius=b_rad, 
        fill=bg_color, 
        outline=outline_color, 
        width=max(1, int(size*0.03))
    )
    

    if percentage > 0:
        inset = int(size * 0.04)
        fx, fy = bx + inset, by + inset
        max_fw = bw - (inset * 2)
        fw = max(int(max_fw * (percentage / 100.0)), int(size * 0.1))
        fh = bh - (inset * 2)
        f_rad = b_rad - inset + 1
        draw.rounded_rectangle([fx, fy, fx+fw, fy+fh], radius=f_rad, fill=fill_color)
    elif percentage == 0:

        inset = int(size * 0.04)
        draw.rounded_rectangle(
            [bx+inset, by+inset, bx+inset+int(size*0.06), by+bh-inset], 
            radius=2, fill=fill_color
        )
        
 
    text = "-" if percentage < 0 else str(percentage)
    font_size = int(size * 0.48) if len(text) < 3 else int(size * 0.40)
    font = _pick_font(font_size)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    cx, cy = bx + bw//2, by + bh//2
    sw = max(1, int(size * 0.025))
    

    draw.text(
        (cx - text_w//2, cy - text_h//2 - bbox[1]), 
        text, 
        font=font, 
        fill="white", 
        stroke_width=sw, 
        stroke_fill=(0, 0, 0, 200)
    )
    

    if charging and percentage >= 0:
        cr = int(size * 0.12)
        ccx, ccy = bx + bw, by + bh

        draw.ellipse(
            [ccx-cr, ccy-cr, ccx+cr, ccy+cr], 
            fill=(255, 204, 0, 255), 
            outline=(0, 0, 0, 150), 
            width=int(size*0.015)
        )

        bolt_font = _pick_font(int(size * 0.18))
        b_bbox = draw.textbbox((0,0), "⚡", font=bolt_font)
        draw.text(
            (ccx - (b_bbox[2]-b_bbox[0])//2, ccy - (b_bbox[3]-b_bbox[1])//2 - b_bbox[1]), 
            "⚡", 
            font=bolt_font, 
            fill="black"
        )


    if size != 64:

        return img.resize((64, 64), Image.Resampling.LANCZOS)
        
    return img


def create_disconnected_icon(size: int = 128) -> Image.Image:

    return create_battery_icon(-1, size=size)
