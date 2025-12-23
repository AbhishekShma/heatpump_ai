from docx import Document
import csv
import os

def extract_tables_to_csv(docx_path, output_dir):
    """
    Extract all tables from a .docx file and save each as a CSV.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    document = Document(docx_path)

    for table_index, table in enumerate(document.tables, start=1):
        csv_path = os.path.join(output_dir, f"table_{table_index}.csv")

        with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    # Normalize whitespace and line breaks
                    text = cell.text.replace("\n", " ").strip()
                    row_data.append(text)

                writer.writerow(row_data)

        print(f"Saved: {csv_path}")

if __name__ == "__main__":
    DOCX_FILE = "beg_waermepumpen_pruef_effizienznachweis.docx"      # Path to your Word document
    # DOCX_FILE ="test.docx"
    OUTPUT_DIR = "tables_csv"     # Folder for CSV outputs

    extract_tables_to_csv(DOCX_FILE, OUTPUT_DIR)
