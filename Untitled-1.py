from pathlib import Path
from PIL import Image, ImageOps

def compress_images(folder="images", max_size=800, quality=75):
    """
    images/ 下の JPEG 画像を軽量化して上書きする。

    Parameters
    ----------
    folder : str
        画像フォルダのパス
    max_size : int
        長辺の最大ピクセル数
    quality : int
        JPEG 圧縮品質（0–100）
    """
    path = Path(folder)
    files = list(path.glob("*.jpeg"))

    print(f"{len(files)} files found in {folder}")
    for f in files:
        try:
            with Image.open(f) as im:
                # EXIF の回転補正 + RGB 化
                im = ImageOps.exif_transpose(im).convert("RGB")
                # 長辺を max_size に縮小
                im.thumbnail((max_size, max_size), Image.LANCZOS)
                # 上書き保存（EXIF削除・最適化・プログレッシブ）
                im.save(f, format="JPEG", quality=quality,
                        optimize=True, progressive=True)
                print(f"Compressed: {f.name}")
        except Exception as e:
            print(f"Failed {f.name}: {e}")

# 実行
if __name__ == "__main__":
    compress_images("images", max_size=800, quality=75)