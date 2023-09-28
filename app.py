import streamlit as st
import qrcode
from qrcode.image.pil import PilImage
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image as PlatypusImage, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Spacer
from reportlab.lib.units import inch, cm
from reportlab.platypus.frames import Frame  # Add this import statement

# Function to generate QR code from text
def generate_qr_code_with_text(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white", image_factory=PilImage)

    # Convert PilImage to bytes-like object
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    return img_bytes

# Streamlit app title
st.title("Bulk QR Code Generator and PDF Export")
st.write("This is a simple Streamlit web app for generating QR codes based on user input. You can choose between entering multiple lines of text or multiple URLs, and the app will generate QR codes for each line and save them in a PDF with one QR code per page.")

# Input type selection
input_type = st.radio("Select input type:", ["Text", "URL"])

if input_type == "Text":
    input_label = "Enter your text (one per line)"
else:
    input_label = "Enter your URLs (one per line)"

# Text input for multiple lines
content = st.text_area(input_label, height=150)

# Font size for text in PDF
font_size = st.slider("Select font size for text in PDF", min_value=8, max_value=84, value=40)

# QR code size
#Max 635 second page
#Max 567 same page
qr_size = st.slider("Select QR code size", min_value=100, max_value=635, value=595)

# Checkbox to show/hide text in PDF
show_text = st.checkbox("Show text above QR code", True)

if st.button("Generate QR Codes and Export to PDF"):
    if content:
        contents = content.split("\n")

        # Create a PDF document
        pdf_file_name = "qrcodes.pdf"

        class MyDocTemplate(BaseDocTemplate):
            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                BaseDocTemplate.__init__(self, filename, **kw)

        doc = MyDocTemplate(pdf_file_name, pagesize=A4)

        styles = getSampleStyleSheet()
        text_style = styles["Normal"]
        text_style.fontSize = font_size

        # Define a PageTemplate for adding text and QR code
        class MyPageTemplate(PageTemplate):
            def __init__(self, id):
                frames = [
                    Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame', showBoundary=0),
                ]
                PageTemplate.__init__(self, id, frames=frames, onPage=self.header)

            def header(self, canvas, doc):
                pass  # Remove the header

        doc.addPageTemplates([MyPageTemplate('page_template')])
        qr_code_images = []

        for i, c in enumerate(contents):
            c = c.strip()
            if c:
                # Generate QR code for the line of text or URL
                qr_code_img = generate_qr_code_with_text(c)

                if show_text:
                    # Create a Paragraph with the text to display
                    text_paragraph = Paragraph(c, text_style)

                # Convert image bytes to a stream
                img_stream = io.BytesIO(qr_code_img)
                img = PlatypusImage(img_stream, width=qr_size, height=qr_size)

                if show_text:
                    #qr_code_images.append(Spacer(1, 1*cm))  # Add 1cm gap
                    qr_code_images.append(text_paragraph)
                qr_code_images.append(Spacer(1, 1*cm))  # Add 1cm gap
                qr_code_images.append(img)
                qr_code_images.append(PageBreak())

        # Build the PDF with one QR code, text, and gap per page
        doc.build(qr_code_images)

        # Provide a download link for the generated PDF
        st.success("QR Codes generated successfully! You can download the PDF below:")
        st.markdown(f'<a href="{pdf_file_name}" download="{pdf_file_name}">Download QR Codes PDF</a>', unsafe_allow_html=True)
    else:
        st.error("Please enter content for the QR codes.")

