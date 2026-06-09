import os
import re
import numpy as np
import pandas as pd

from get_size import LeafAnalyzer

records = []
pics_dir = "pics"

for filename in os.listdir(pics_dir):
    if not filename.lower().endswith(".jpg"):
        continue

    # p12l3.jpg -> plant_id=12, leaf_order=3
    match = re.match(r"p(\d+)l(\d+)\.jpg", filename)

    if match is None:
        print(f"Přeskakuji nevalidní název: {filename}")
        continue

    img_id = int(match.group(1))
    leaf_order = int(match.group(2))
    filepath = os.path.join(pics_dir, filename)

    try:
        analyzer = LeafAnalyzer(filepath)

        width, height = analyzer.get_size()
        inner, outer = analyzer.get_number_of_fenestration()

        records.append({
            "plant_id": img_id,
            "leaf_order": leaf_order,
            "width_cm": width,
            "length_cm": height,
            "outer_fenestration_count": outer,
            "inner_fenestration_count": inner
        })

    except Exception as e:
        print(f"Chyba při zpracování souboru {filename}: {e}")
        continue


df = pd.DataFrame(records)
print(df)

df2 = pd.read_csv("data.csv")
df2 = df2.drop(columns=["Unnamed: 0", "id_x"], errors="ignore")

# i have bad numbers in names of files...
mapping = {
    7: 2,
    8: 4,
    9: 5
}

df["plant_id_src"] = df["plant_id"].map(mapping)

cols_to_add = [c for c in df2.columns if c not in df.columns]

df = df.merge(
    df2[["plant_id", "leaf_order"] + cols_to_add],
    left_on=["plant_id_src", "leaf_order"],
    right_on=["plant_id", "leaf_order"],
    how="left"
)

df = df.drop(columns=["plant_id_src", "plant_id_y"], errors="ignore")

if "plant_id_x" in df.columns:
    df = df.rename(columns={"plant_id_x": "plant_id"})

df3 = pd.concat([df, df2], ignore_index=True)
df3.to_csv("data2.csv", index=False)
