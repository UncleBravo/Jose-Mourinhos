import os
import gradio as gr
import docx
from openai import AzureOpenAI
import PyPDF2

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://minihackathon07newdeployment.openai.azure.com/",
    api_key="aa002ff994a847499e2e24a6775c41d1",  
    api_version="2024-08-01-preview"
)

# Function to extract text from a Word (.docx) file
def extract_text_from_word(docx_file_path):
    doc = docx.Document(docx_file_path)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
    return extracted_text

# Main function that combines everything
def main(files, job_field):
    # Extract the text from the uploaded resume
    if files.name.endswith('.pdf'):
        resume_text = extract_text_from_pdf(files)
    elif files.name.endswith('.docx'):
        resume_text = extract_text_from_word(files)
    else:
        return "Unsupported file format. Please upload a PDF or DOCX file."

    # If no text was extracted, return an error message
    if not resume_text.strip():
        return "No text could be extracted from the file. Please check the file."

    # Prepare the request to Azure OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"""
                
                Job Field: {job_field}

                Evaluation Criteria (with weights in parentheses):
                - Experience (30%): How relevant is the candidate's experience to the job in {job_field}?
                - Skills (25%): How well do the candidate's skills align with the role in {job_field}?
                - Education (20%): Evaluate the candidate's educational background.
                - Cultural Fit and Leadership (15%): Assess the candidate's cultural fit and leadership potential.
                - Technical Proficiency & Communication (10%): Evaluate the candidate's proficiency with modern technologies and communication skills.

                Based on these criteria, provide the following and put in the table format below:
                - Name
                - Role
                - Final Percentage Score (out of 100)(strictly in percentage form)
                - Recommended Role

                ### Summary Evaluation Table:
                | Name            | Role                    | Final Percentage Score  | Recommended Role |
                |-----------------|-------------------------|-------------------------|-----------------|
                
                Resume:
                {resume_text}
                """},
            ],
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred while processing the resume: {str(e)}"

def analyse_resume(job_field, uploaded_file):
    if uploaded_file is not None and job_field:
        print(uploaded_file)
        result = main(files=uploaded_file, job_field=job_field)
        
        # Extract the summary evaluation table row for writing to file
        lines = result.splitlines()
        table_lines = [line for line in lines if '|' in line]

        parsed_table = []
        for line in table_lines:
            row = [item.strip() for item in line.split('|') if item.strip()]
            parsed_table.append(row)

        if parsed_table:
            # Get only the file name from the uploaded file path using os.path.basename()
            file_name = os.path.basename(uploaded_file.name if hasattr(uploaded_file, 'name') else uploaded_file)
            
            # Write the response to a text file, including the job field and file name
            with open("applicants.txt", 'a') as response_file:
                response_file.write(", ".join(parsed_table[-1]) + f", {job_field}, {file_name}")
                response_file.write("\n")

        return result
    else:
        return "Please select a job field and upload a file."

# Launch the Gradio interface
demo = gr.Interface(
    fn=analyse_resume,
    inputs=[
        gr.Dropdown(choices=["Please SELECT a Job Field","Computing", "Business", "Finance", "Human Resource"], label="Job Field"),
        gr.File(type="filepath", label="Upload Resume (PDF or DOCX)")
    ],
    outputs="text",
    title="Resume Analyzer Chatbot",
    description="Select a job field and upload a resume (PDF or DOCX). The chatbot will analyze it based on the selected field and provide insights."
)

demo.launch()
