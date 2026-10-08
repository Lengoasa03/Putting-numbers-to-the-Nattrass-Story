"""
ECOH621 Weeks 6-7 assignment: AI-use disclosure statement (PDF).

The brief asks students who use AI tools to say so and to say what for, and to
include a listing of the working directory if an agent setup was used.

Output: report/AI_use_disclosure.pdf
"""

import os
from fpdf import FPDF

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
OUT = BASE / "report" / "AI_use_disclosure.pdf"

SECTIONS = [
    ("Tool used",
     ["Claude (Anthropic), run as a coding agent with access to the project working "
      "directory, able to read and write files and to run Python."]),

    ("What it was used for",
     ["Writing and debugging the Python scripts that build the dataset, run the "
      "regressions and generate the figures and documents.",
      "Reading long primary sources and locating figures inside them, in particular "
      "the SARB Annual Economic Reports for 2000 and 2001 and the 1996 GEAR document.",
      "Cross-checking the supplied csv against those primary sources, which is how the "
      "inflation-target error described in Part 1 was found.",
      "Drafting and editing prose, including checking the Part 4 word count and "
      "rewriting the report for plainer English."]),

    ("What it was not used for",
     ["No figure, coefficient, p-value or table entry in this report was produced by "
      "the model from memory or estimation. Every number comes from running the "
      "included scripts on the supplied data files, or from a named primary source.",
      "Where a figure could not be sourced, it was left blank rather than filled. Two "
      "cases: non-agricultural formal employment growth for 2000, and the 2016 to 2024 "
      "employment years.",
      "The interpretation, the choice of specification, the decision about which vintage "
      "to judge GEAR by, and the conclusions are my own."]),

    ("Verification I carried out",
     ["The 2000 CPI figure and the 2000 nominal Bank rate were each confirmed against "
      "two independent sources before use: the SARB Annual Economic Report 2001 "
      "narrative, and the monthly Bank rate series supplied in the data folder, which "
      "average to 11.81 per cent for 2000 and agree with the report's stated rate "
      "changes.",
      "The corrected GEAR inflation targets were checked directly against the "
      "Integrated Scenario table in South Africa (1996).",
      "All cells flagged as reconstructed from a damaged scan were checked against "
      "Nattrass (2001).",
      "The deficit series was reconciled against its own components: the cash-flow "
      "balance divided by nominal GDP reproduces the supplied ratio."]),

    ("Reproducibility",
     ["All scripts are included with the submission. Running them in the order below "
      "regenerates every table, figure and document from the supplied data files."]),
]

SCRIPT_ORDER = [
    "part1_rebuild_table.py",
    "part1_table_to_docx.py",
    "part2_build_extended_series.py",
    "part2_plot_series.py",
    "part2_analysis_to_docx.py",
    "part3_build_regression_data.py",
    "part3_estimate.py",
    "part3_plot_coefficients.py",
    "part3_analysis_to_docx.py",
    "part4_to_docx.py",
    "build_consolidated_report.py",
    "build_ai_disclosure.py",
]


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120)
        self.cell(0, 6, "ECOH621  |  AI-use disclosure", align="R", new_x="LMARGIN",
                  new_y="NEXT")
        self.set_text_color(0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def main():
    pdf = PDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(20, 18, 20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, "Statement on the use of AI tools")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5,
                   "ECOH621 Development Economics. Assignment: Putting Numbers to the "
                   "Nattrass Story. Submitted alongside the main report and the Python "
                   "scripts.")
    pdf.ln(5)

    for title, items in SECTIONS:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 6, title)
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 10)
        for it in items:
            pdf.multi_cell(0, 5, f"  -  {it}")
            pdf.ln(1)
        pdf.ln(3)

    pdf.set_font("Courier", "", 9)
    for name in SCRIPT_ORDER:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 4.5, f"    python {name}")
    pdf.ln(4)

    # ---- working directory listing (the brief asks for this if an agent is used)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 6, "Working directory contents")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, "Listing of the output directory produced for this assignment.")
    pdf.ln(3)

    pdf.set_font("Courier", "", 8.5)
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in sorted(dirs) if d != "__pycache__"]
        rel = os.path.relpath(root, BASE)
        label = "Development project/output" if rel == "." else rel.replace("\\", "/")
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Courier", "B", 8.5)
        pdf.multi_cell(0, 4.5, f"{label}/")
        pdf.set_font("Courier", "", 8.5)
        for f in sorted(files):
            if f.startswith("~$"):
                continue
            size = os.path.getsize(os.path.join(root, f))
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 4.2, f"    {f}  ({size:,} bytes)")
        pdf.ln(1)

    pdf.output(str(OUT))
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
