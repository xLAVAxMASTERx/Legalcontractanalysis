import pandas as pd
import fitz  # PyMuPDF

# Step 1: Read the CSV file
csv_file = 'risk.csv'  # Path to your CSV file
words_df = pd.read_csv(csv_file)
words = words_df.iloc[:, 0].tolist()  # List of words from the first column
values = words_df.iloc[:, 1].tolist()  # List of values from the second column

# Step 2: Read the PDF file
pdf_file = 'doc.pdf'  # Path to your PDF file
doc = fitz.open(pdf_file)

# Dictionary to keep track of the sum of values for each word
word_sums = {word: 0 for word in words}

# Create a new PDF for sections marked red
red_sections_pdf = fitz.open()

# Helper function to find section boundaries
def find_section_boundaries(page):
    text = page.get_text("text")
    lines = text.split('\n')
    section_starts = []
    for i, line in enumerate(lines):
        if line.strip().startswith("Section "):
            section_starts.append((i, line.strip()))
    return section_starts, lines

# Step 3: Highlight words in the PDF, calculate the sum of values, and extract red-marked sections
for page_num in range(len(doc)):
    page = doc[page_num]
    section_starts, lines = find_section_boundaries(page)

    for word, value in zip(words, values):
        text_instances = page.search_for(word)
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.update()
            word_sums[word] += value

    # Identify and extract sections containing words and marked red
    for start_idx, section_title in section_starts:
        section_text = '\n'.join(lines[start_idx:])
        if any(word in section_text for word in words):
            section_instances = page.search_for(section_title)
            for inst in section_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=(1, 0, 0), fill=(1, 0.8, 0.8))
                highlight.update()
                
                # Extract and add the section to the new PDF
                new_page = red_sections_pdf.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_text((10, 10), section_text, fontsize=12, fontname="helv")

# Save the highlighted PDF
highlighted_pdf_file = 'highlighted_document.pdf'
doc.save(highlighted_pdf_file)

# Save the PDF with red-marked sections
red_sections_pdf_file = 'red_sections_document.pdf'
red_sections_pdf.save(red_sections_pdf_file)

print(f"Highlighted PDF saved as '{highlighted_pdf_file}'")
print(f"PDF with red-marked sections saved as '{red_sections_pdf_file}'")
print("Sum of values for each word:")
for word, total in word_sums.items():
    print(f"{word}: {total}")
