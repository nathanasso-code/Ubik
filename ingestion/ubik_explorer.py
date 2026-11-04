"""Build Ubik's private explorer page from the public export of the data model (ubik/docs/modello-dati.md).

Usage: python -m ingestion.ubik_explorer EXPORT_MODEL.json OUT.html
"""
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "templates" / "explorer.html"


def main(model_path, out_path):
    data = json.loads(Path(model_path).read_text())
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.read_text().replace("/*DATA*/null", blob, 1)
    Path(out_path).write_text(page)
    print(json.dumps({"out": str(out_path), "kb": round(len(page.encode()) / 1024)}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
