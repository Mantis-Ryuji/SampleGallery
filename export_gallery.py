import json
import re
from pathlib import Path
from typing import List, Tuple

def find_images_for_name(images_dir: Path, base: str, exts=(".jpeg", ".jpg", ".png")) -> List[Path]:
    pat = re.compile(rf"^{re.escape(base)}_(\d+)\.({'|'.join(e.lstrip('.') for e in exts)})$", re.IGNORECASE)
    pairs: List[Tuple[int, Path]] = []
    for p in images_dir.iterdir():
        if p.is_file():
            m = pat.match(p.name)
            if m:
                pairs.append((int(m.group(1)), p))
    pairs.sort(key=lambda t: t[0])
    return [p for _, p in pairs]

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def make_table_row(cells: List[str], n_cols: int) -> str:
    padded = cells + [""] * (n_cols - len(cells))
    return "| " + " | ".join(padded) + " |"

def make_section_md(base: str, image_paths: List[Path], image_root_rel: Path, cols: int = 3) -> str:
    if not image_paths:
        table = "_No images found_"
    else:
        header = make_table_row([""] * cols, cols)
        sep = make_table_row(["---"] * cols, cols)

        rows = []
        for chunk_paths in chunk(image_paths, cols):
            cells = [f'<img src="{image_root_rel / p.name}">' for p in chunk_paths]
            rows.append(make_table_row(cells, cols))

        table = "\n".join([header, sep] + rows)

    section = f"""### {base}

{table}
"""
    return section

def build_markdown_from_json(
    names_json="sample_names.json",
    images_dir="images",
    output_md="samples.md",
    exts=(".jpeg", ".jpg", ".png"),
    cols=3,
):
    names = json.loads(Path(names_json).read_text(encoding="utf-8"))
    images_dir = Path(images_dir)
    out_path = Path(output_md)

    sections = []
    for base in names:
        imgs = find_images_for_name(images_dir, base, exts=exts)
        sections.append(make_section_md(base, imgs, Path(images_dir.name), cols=cols))

    md = "\n\n".join(sections).rstrip() + "\n"
    out_path.write_text(md, encoding="utf-8")
    print(f"✅ Wrote {out_path} with {len(sections)} sections.")

if __name__ == "__main__":
    build_markdown_from_json(
        names_json="sample_names.json",
        images_dir="images",
        output_md="samples.md",
        exts=(".jpeg", ".jpg", ".png"),
        cols=3,
    )
