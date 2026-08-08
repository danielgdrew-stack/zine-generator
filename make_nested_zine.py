from pypdf import PageObject, PdfReader, PdfWriter, Transformation


def make_nested_quarter_zine(
    input_pdf_path, output_pdf_path="Buckingham_Nested_Zine.pdf"
):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    pages = list(reader.pages)
    total_pages = len(pages)

    # Pad document to a multiple of 4 (55 -> 56 pages)
    remainder = total_pages % 4
    if remainder != 0:
        padding_needed = 4 - remainder
        w = float(pages[0].mediabox.width)
        h = float(pages[0].mediabox.height)
        for _ in range(padding_needed):
            pages.append(PageObject.create_blank_page(width=w, height=h))

    N = len(pages)  # 56
    num_sheets = N // 4  # 14 sheets

    # Target Sheet: US Letter Landscape (11 x 8.5 inches in points)
    sheet_w, sheet_h = 792.0, 612.0
    panel_w, panel_h = sheet_w / 2.0, sheet_h / 2.0

    for k in range(1, num_sheets + 1):
        sheet = PageObject.create_blank_page(width=sheet_w, height=sheet_h)

        # 0-based page index mapping for sheet k:
        # Top-Left:  Page N - 2k + 1  [Rotated 180]
        # Top-Right: Page 2k          [Rotated 180]
        # Bot-Left:  Page N - 2k + 2  [0 deg]
        # Bot-Right: Page 2k - 1      [0 deg]
        idx_tl = N - (2 * k)
        idx_tr = (2 * k) - 1
        idx_bl = N - (2 * k - 1)
        idx_br = (2 * k - 1) - 1

        quads = [
            (pages[idx_br], 0, False),  # Bottom-Right
            (pages[idx_tl], 1, True),  # Top-Left (Rotated 180)
            (pages[idx_tr], 2, True),  # Top-Right (Rotated 180)
            (pages[idx_bl], 3, False),  # Bottom-Left
        ]

        for page, pos, rotate_180 in quads:
            pw = float(page.mediabox.width)
            ph = float(page.mediabox.height)

            s = min(panel_w / pw, panel_h / ph)
            scaled_w, scaled_h = pw * s, ph * s
            dx = (panel_w - scaled_w) / 2.0
            dy = (panel_h - scaled_h) / 2.0

            if pos == 0:  # Bottom-Right
                t = Transformation().scale(s, s).translate(panel_w + dx, dy)
            elif pos == 1:  # Top-Left
                t = (
                    Transformation()
                    .scale(s, s)
                    .rotate(180)
                    .translate(panel_w - dx, 2 * panel_h - dy)
                )
            elif pos == 2:  # Top-Right
                t = (
                    Transformation()
                    .scale(s, s)
                    .rotate(180)
                    .translate(2 * panel_w - dx, 2 * panel_h - dy)
                )
            elif pos == 3:  # Bottom-Left
                t = Transformation().scale(s, s).translate(dx, dy)

            sheet.merge_transformed_page(page, t)

        writer.add_page(sheet)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"Successfully generated {len(writer.pages)}-page nested zine PDF!")


make_nested_quarter_zine("Buckingham Line Practice - Richard III V3.pdf")
