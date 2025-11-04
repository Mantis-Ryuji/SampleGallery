import os
import json
import re

def export_unique_base_names(images_dir="images", output_path="sample_names.json"):
    # フォルダ内のファイル一覧を取得
    files = sorted(os.listdir(images_dir))

    # 拡張子を除去 & `_数字` を削除してベース名を抽出
    base_names = set()
    for f in files:
        if f.lower().endswith(".jpeg"):
            name = os.path.splitext(f)[0]
            # 末尾の _数字 を除去
            base_name = re.sub(r"_\d+$", "", name)
            base_names.add(base_name)

    # ソートしてJSONに出力
    base_names = sorted(base_names)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(base_names, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(base_names)} 件のベース名を {output_path} に出力しました。")

if __name__ == "__main__":
    export_unique_base_names()