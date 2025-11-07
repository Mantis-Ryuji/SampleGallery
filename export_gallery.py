import json
import re
import csv
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

def make_section_md(base: str, grade: str, image_paths: List[Path], image_root_rel: Path, cols: int = 3) -> str:
    """見出しを '### {base}: {grade}' 形式で出力"""
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

    return f"### {base}: {grade}\n\n{table}\n"

def load_name_grade_list(names_json_path: Path) -> List[Tuple[str, str]]:
    data = json.loads(names_json_path.read_text(encoding="utf-8"))
    result = []
    for i, item in enumerate(data):
        if not isinstance(item, dict) or len(item) != 1:
            raise ValueError(f"names_json[{i}] が不正です: {item}")
        (name, grade), = item.items()
        if grade.upper() not in {"A", "B", "C"}:
            raise ValueError(f"不正な評価値: {grade}")
        result.append((name, grade.upper()))
    return result

def write_grade_csv(rows: List[Tuple[str, str]], csv_path: Path) -> None:
    """CSV出力: grade,samplename"""
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["grade", "samplename"])
        for grade, name in rows:
            writer.writerow([grade, name])

def build_markdown_and_summary(
    names_json="sample_names.json",
    images_dir="images",
    output_md="samples.md",
    output_csv="summary_by_grade.csv",
    exts=(".jpeg", ".jpg", ".png"),
    cols=3,
):
    names_json_path = Path(names_json)
    images_dir = Path(images_dir)
    out_md_path = Path(output_md)
    out_csv_path = Path(output_csv)

    name_grade_list = load_name_grade_list(names_json_path)

    sections_md = []
    csv_rows = []
    order = {"A": 0, "B": 1, "C": 2}
    name_grade_list.sort(key=lambda x: (order.get(x[1], 99), x[0]))

    for base, grade in name_grade_list:
        imgs = find_images_for_name(images_dir, base, exts=exts)
        sections_md.append(make_section_md(base, grade, imgs, Path(images_dir.name), cols=cols))
        csv_rows.append((grade, base))

    # Markdown
    md = "\n\n".join(sections_md).rstrip() + "\n"
    out_md_path.write_text(md, encoding="utf-8")

    # CSV
    csv_rows.sort(key=lambda r: (order.get(r[0], 99), r[1]))
    write_grade_csv(csv_rows, out_csv_path)

    print(f"✅ Wrote {out_md_path} with {len(sections_md)} sections.")
    print(f"✅ Wrote {out_csv_path} with {len(csv_rows)} rows.")

if __name__ == "__main__":
    build_markdown_and_summary(
        names_json="sample_names.json",
        images_dir="images",
        output_md="samples.md",
        output_csv="summary_by_grade.csv",
        exts=(".jpeg", ".jpg", ".png"),
        cols=3,
    )
