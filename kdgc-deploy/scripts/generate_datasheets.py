#!/usr/bin/env python3
"""Generate simple product datasheet PDFs into frontend/dist/assets/docs/."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "dist" / "assets" / "docs"

SHEETS = [
    {
        "slug": "kd0100-02s-t1",
        "title": "KD0100-02S-T1 Oxygen Sensor Datasheet",
        "lines": [
            "Model: KD0100-02S (probe / T1)",
            "Controller: KD0100-03",
            "O2 partial pressure: 0.5-101 kPa",
            "Gas temperature: -50 to 200 C",
            "Gas flow: 0-10 m/s",
            "Probe weight: <=35 g (excl. harness)",
            "Heater: ~4.5 V / 9 V optional",
            "Wiring: White Vh- / Blue Vh+ / Red Sense / Gray Common / Green Pump",
        ],
    },
    {
        "slug": "kd0100-02s-to",
        "title": "KD0100-02S-TO Oxygen Sensor Datasheet",
        "lines": [
            "Model: KD0100-02S (pin / TO)",
            "Controller: KD0100-03",
            "O2 partial pressure: 0.5-101 kPa",
            "Gas temperature: -50 to 200 C",
            "Gas flow: 0-10 m/s",
            "Probe weight: <=5 g (excl. harness)",
            "Size tolerance: <=0.5 mm",
            "Heater: ~4.5 V / 9 V optional",
        ],
    },
    {
        "slug": "mask-o2-sensor",
        "title": "Mask Low-Temperature O2 Sensor Datasheet",
        "lines": [
            "Type: Aviation mask low-temperature VF O2 sensor",
            "O2 partial pressure: 0.5-101 kPa (design direction)",
            "Application: Pilot mask breathing oxygen monitoring",
            "Status: Prototype verified; project qualification required",
            "Notes: Not an automotive exhaust sensor",
        ],
    },
]


def build(sheet: dict) -> Path:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, sheet["title"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Anhui ZK Guoci / kdgc.cc", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "Public specification summary for engineering evaluation.")
    pdf.ln(4)
    for line in sheet["lines"]:
        pdf.cell(0, 8, f"- {line}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Contact: guanwn@kdgc.cc / 153-8588-4309", new_x="LMARGIN", new_y="NEXT")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{sheet['slug']}-datasheet.pdf"
    pdf.output(str(path))
    return path


def main() -> None:
    for sheet in SHEETS:
        p = build(sheet)
        print("wrote", p, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
