from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import uuid
from pathlib import Path
import re
import fitz  # PyMuPDF
load_dotenv()  


def organize(resume_text):
    system_prompt = """

    You are a professional at organizing text from a resume.

    Make sure to also follow the following rules:
    - Some text chunk might be out of order, make sure each text chunk belong to the correct place.
    - Make sure to highlight the section name with "**" at the beginning and the end.
    - Format the output as plain text with clear bullet points (•). 
    - Avoid redundancy, and keep the tone professional.

    """
    prompt = f"""
    Organize (do not summarize) the following resume's sections into concise bullet points highlighting the person's.

    Resume text:
    ---
    {resume_text}
    ---
    """

    send_text = [
            ("system", system_prompt),
            ("human", f"{prompt}"),
        ]
    global generator
    result= generator.invoke(send_text)

    return result


def change_resume(resume_text, job_desc):

    prompt = f"""
    You are an expert resume editor and career coach.

    Your task is to adjust and enhance each section of the following resume so it better aligns with the provided job description without fabricating information.

    Follow these rules:
    - Keep all original experiences factual (do not invent roles, companies, or achievements).
    - Reword or emphasize details that match the skills, responsibilities, or qualifications in the job description.
    - Maintain a professional, clear tone and consistent formatting.
    - Keep the structure of the resume sections (Summary, Experience, Skills, Education, Projects, etc.).
    - Use concise bullet points and strong action verbs.

    Job Description:
    ---
    {job_desc}
    ---

    Original Resume:
    ---
    {resume_text}
    ---

    Output:
    A rewritten version of the resume with improved alignment to the job description.
    """

    send_text = [
            ("assistant", "You are an assistant for tailoring resume based on job description."),
            ("human", f"{prompt}"),
        ]
    global generator
    result= generator.invoke(send_text)

    return result



def change_section(resume_text, job_desc):

    system_prompt = """
    You are an expert resume editor and career coach.

    Follow these rules:
    - Only include the section name and the new section text, nothing else.
    - Make sure the length of the adjusted text is similar to the original content.
    - Keep all original experiences factual (do not invent roles, companies, or achievements).
    - Maintain a professional, clear tone and consistent formatting.
    - Use concise bullet points and strong action verbs.
    """

    prompt = f"""

    Your task is to adjust and enhance the current section of the resume so it better aligns with the provided job description without fabricating information.

    Job Description:
    ---
    {job_desc}
    ---

    Original Resume:
    ---
    {resume_text}
    ---

    Output:
    A rewritten version of the resume with improved alignment to the job description.
    """

    send_text = [
            ("system", system_prompt),
            ("human", f"{prompt}"),
        ]
    global generator
    result= generator.invoke(send_text)

    return result.content


def key_skill_extraction(job):
    system_prompt = """
    You are an expert on data extraction.

    Follow these rules:
    - Keep the skills extracted precise. 
    - Make sure the points are below 8 words.
    - Make sure all techonologies are mentioned.

    """
    prompt = f"""
    Your task is to extract both techincal and soft skills required in the job description.

    Job Description:
    ---
    {job}
    ---

    Output:
    Skills mentioned in the job description:
    """

    send_text = [
            ("system", system_prompt),
            ("human", f"{prompt}"),
        ]
    global generator
    result= generator.invoke(send_text)

    return result.content

def process_resume_summary(text):
    try:
        data = {}
        current_title = None
        lines = list(filter(lambda x: x != "",text.splitlines()))
        for line in lines:
            stripped = line.strip()

            # Check if line is a title (starts and ends with **)
            if re.match(r"^\*\*.*\*\*$", stripped):
                # Extract the title text (without the **)
                current_title = stripped.strip("*").strip()             
                data[current_title] = []
            elif current_title:
                # Add content line as-is (keep bullets or symbols)
                data[current_title].append(stripped)

        return data

    except: 
        return {}
    


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_KEY")
EMBED_MODEL = "openai/gpt-oss-120b" 
generator = ChatGroq(model=EMBED_MODEL)



app = Flask(__name__)
CORS(app)  # allow requests from any origin

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Backend is running!"}), 200

@app.route('/process', methods=['POST'])
def process_strings():
    #data = request.get_json()  # get JSON body

    # Extract strings safely
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Read PDF directly from memory
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    resume = ""
    for page in doc:
        resume += page.get_text()
    print(resume)
    text = organize(resume)#get_prompt_resume(resume, job)
    organized_text = process_resume_summary(text.content)



    # Return JSON response
    return jsonify({
        'resume_text': text.content,
        #'new_resume': final_result.content, 
        'organized_text': organized_text
    }), 200

@app.route('/extract_skills', methods=['POST'])
def extract_skills():
    data = request.get_json()
    job = data.get('job') 
    skills = key_skill_extraction(job)
    # Return JSON response
    return jsonify({
        'result': skills
    }), 200

@app.route('/tailor', methods=['POST'])
def tailor():
    data = request.get_json()
    title = data.get('title')
    texts = data.get('texts')
    job = data.get('job')

    resume_section = "Section Name:\n" + title + "\n" + "Section Text:\n" + "\n".join(texts)

    result = change_section(resume_section, job )

    # Return JSON response
    return jsonify({
        'result': result
    }), 200

if __name__ == '__main__':
    app.run(debug=False)   