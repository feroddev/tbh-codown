from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def _draw_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (11, 17, 32, 255))
    draw = ImageDraw.Draw(image)

    margin = max(2, size // 10)
    chest_left = margin
    chest_top = size // 4
    chest_right = size - margin
    chest_bottom = size - margin

    draw.rounded_rectangle(
        (chest_left, chest_top, chest_right, chest_bottom),
        radius=max(2, size // 12),
        fill=(26, 38, 64, 255),
        outline=(96, 165, 250, 255),
        width=max(1, size // 32),
    )

    lid_bottom = chest_top + (chest_bottom - chest_top) // 3
    draw.rounded_rectangle(
        (chest_left, chest_top, chest_right, lid_bottom),
        radius=max(2, size // 12),
        fill=(30, 58, 95, 255),
        outline=(147, 197, 253, 255),
        width=max(1, size // 40),
    )

    lock_size = max(4, size // 6)
    lock_x = (size - lock_size) // 2
    lock_y = lid_bottom - lock_size // 3
    draw.rounded_rectangle(
        (lock_x, lock_y, lock_x + lock_size, lock_y + lock_size),
        radius=max(1, size // 24),
        fill=(251, 191, 36, 255),
        outline=(245, 158, 11, 255),
        width=max(1, size // 48),
    )

    band_y = chest_top + (chest_bottom - chest_top) // 2
    draw.line(
        (chest_left + margin // 2, band_y, chest_right - margin // 2, band_y),
        fill=(59, 130, 246, 220),
        width=max(1, size // 24),
    )

    return image


def main() -> None:
    assets_dir = Path(__file__).resolve().parents[1] / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [_draw_icon(size) for size in sizes]
    png_path = assets_dir / "tbh_monitor.png"
    images[-1].save(png_path, format="PNG")

    ico_path = assets_dir / "tbh_monitor.ico"
    images[0].save(
        ico_path,
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=images[1:],
    )
    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
