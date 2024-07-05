import json,base64
import google.generativeai as genai # type: ignore
import streamlit as st # type: ignore
import plotly.graph_objects as go #type: ignore
from PyPDF2 import PdfReader # type: ignore
from dotenv import load_dotenv # type: ignore
from streamlit_option_menu import option_menu # type: ignore

load_dotenv()  # Load all our environment variables

def get_gemini_pro():
    genai.configure(api_key="AIzaSyDuSXCV2lmkL5XWYZ_CpWv2kPbgCe8S84A")
    return genai.GenerativeModel('gemini-pro')

def pdf_to_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Function to save results to JSON file
def save_results_to_json(results, filename):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)


# Function to load results from JSON file
def load_results_from_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def parse_table_to_dict(table_string):
    rows = table_string.strip().split('\n')
    columns = [column.strip() for column in rows[0].split('|') if column.strip()]
    data = []

    for row in rows[2:]:
        cells = [cell.strip() for cell in row.split('|') if cell.strip()]
        if cells:
            row_data = dict(zip(columns, cells))
            data.append(row_data)

    return data

def load_results_from_json(filename):
    try:
        with open(filename, "r") as file:
            feedback_results_dict = json.load(file)
        return feedback_results_dict
    except FileNotFoundError:
        # If the file does not exist, return an empty dictionary
        return {}
    
# def resume_analysis(resume,job_description):

#     analysis_prompt = ''' Act as a HR Manager with 20 years of experience who worked with various technologies in the market.
#     Compare the resume provided below with the job description below.
#     Review the entire resume for the overall presentation and formatting.
#     Check for readability, length and relevance of the information provided.
#     Highlight any areas that need improvement.
#     Describe the analysis report in detail from the resume.
#     I just need overall resume analysis.
#     Here is the Resume text: {resume}
#     Here is the Job description: {job_description}

#     I want the response as a detailed report analysis of given resume'''.format(resume=resume, job_description=job_description)

#     return analysis_prompt

def resume_analysis(resume, job_description):
    # analysis_prompt = '''Act as an HR Manager with 20 years of experience in various technologies.
    # Compare the resume below with the provided job description.
    # Review the resume for overall presentation, formatting, readability, length, and relevance.
    # Provide a detailed analysis covering the following sections based on the job description:
    
    # 1. Overall presentation and formatting
    # 2. Contact information
    # 3. Professional summary or objective
    # 4. Work experience 
    # 5. Skills (match with job requirements)
    # 6. Education 
    # 7. Additional sections (certifications, projects, publications, etc., relevance to the job description)
    
    # Highlight areas needing improvement and suggest specific changes to better match the job description.
    
    # Resume text: {resume}
    # Job description: {job_description}
    
    # Response format: Detailed report analysis of the given resume, covering all the specified sections and focusing on the job description requirements.'''.format(resume=resume, job_description=job_description)

    analysis_prompt = '''Act as an HR Manager with 20 years of experience in various technologies.
    Compare the resume below with the provided job description.
    Provide detailed suggestions for improving the resume to better match the job description.
    Present the analysis in the form of a table with the following columns:

    1. Area
    2. Current Status
    3. Suggested Improvements

    Focus on the following areas:

    1. Overall presentation and formatting
    2. Professional summary or objective
    3. Work experience (clarity, relevance, and achievements)
    4. Skills (relevance and proficiency level)
    5. Education (relevance and completeness)
    6. Additional sections (certifications, projects, publications, etc.)
    7. Readability, length, and relevance of information

    Resume text: {resume}
    Job description: {job_description}

    Response format:
    | Area                        | Current Status                                             | Suggested Improvements                                                                 |
    |-----------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------|
    | Overall presentation        | [Briefly describe the current presentation]               | [Suggest improvements for presentation]                                                |
    | Professional summary        | [Briefly describe the current professional summary]       | [Suggest improvements for professional summary]                                        |
    | Work experience             | [Briefly describe the current work experience]            | [Suggest improvements for work experience]                                             |
    | Skills                      | [Briefly describe the current skills]                     | [Suggest improvements for skills]                                                      |
    | Education                   | [Briefly describe the current education]                  | [Suggest improvements for education]                                                   |
    | Additional sections         | [Briefly describe the current additional sections]        | [Suggest improvements for additional sections]                                         |
    | Readability and relevance   | [Briefly describe readability and relevance]              | [Suggest improvements for readability and relevance]                                   |'''.format(resume=resume, job_description=job_description)


    return analysis_prompt


def construct_skills_prompt(resume, job_description):

    # skill_prompt = '''Act as a HR Manager with 20 years of experience.
    # Compare the resume provided below with the job description given below.
    # Check for key skills in the resume that are related to the job description.
    # List the missing key skillset from the resume.
    # I just need the extracted missing skillset.
    # Here is the Resume text: {resume}
    # Here is the Job Description: {job_description}

    # I want the response as a list of missing skill word'''.format(resume=resume, job_description=job_description)
    skill_prompt = '''Act as an HR Manager with 20 years of experience.
    Compare the resume provided below with the job description given below.
    Check for key skills in the resume that are related to the job description.
    List the missing key skills from the resume. Under missing skills, include necessary technologies and tech stacks to match the job description.
    The missing skill are to be missing pieces to match the job description. 
    Don't display the tech stack that is already present in the resume.You can recommend other tech stack, if missing one is already present in the resume.
    Present the missing skills and necessary tech stacks which aren't present in the resume,in the form of a table with the following columns:

    | Skill        | Status   | Necessary Tech Stack |
    |--------------|----------|----------------------|
    | Skill name 1 | Missing  | Tech Stack 1         |
    | Skill name 2 | Missing  | Tech Stack 2         |
    | ...          | Missing  | Tech Stack ...       |

    Here is the Resume text: {resume}
    Here is the Job Description: {job_description}

    I want the response as a table of missing skills and necessary tech stacks.'''.format(resume=resume, job_description=job_description)
    
    return skill_prompt

def construct_resume_score_prompt(resume, job_description):
    resume_score_prompt = '''Act as a HR Manager with 20 years of experience.
    Compare the resume provided below with the job description given below.
    Check for key skills in the resume that are related to the job description.
    Rate the resume out of 100 based on the matching skill set.
    Assess the score with high accuracy.
    Here is the Resume text: {resume}
    Here is the Job Description: {job_description}

    I want the response as a single string in the following structure score:%'''.format(resume=resume, job_description=job_description)

    return resume_score_prompt

def get_suggestions(resume,job_description):
    
    suggestion_prompt = '''Act as an HR Manager with 20 years of experience in various technologies.
Compare the resume below with the provided job description.
Provide detailed suggestions for improving the resume to better match the job description. 
Focus on the following areas:

1. Overall presentation and formatting
2. Professional summary or objective
3. Work experience (relevance to the job description)
4. Skills (specific skills to add, remove, or enhance)
5. Education (relevance to the job description)
6. Additional sections (certifications, projects, publications, etc., relevance to the job description)

For projects, suggest specific types of projects or experiences that should be highlighted or added to match the job description.

Here is the Resume text: {resume}
Here is the Job description: {job_description}

Response format: Table which includes each category with its brief suggestion enough to better match the job description.

| Category                       | Suggestions                                                                                                   |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Overall Presentation           | - Improve the layout and design to make the resume visually appealing.                                         |
|                                | - Use consistent formatting for headings, bullet points, and text alignment.                                    |
| Professional Summary/Objective | - Tailor the summary/objective to highlight relevant skills and experiences for the job.                        |
| Work Experience               | - Emphasize experiences that directly relate to the job requirements listed in the job description.            |
| Skills                         | - Add missing skills that are essential for the job role.                                                      |
|                                | - Remove any outdated or irrelevant skills.                                                                    |
|                                | - Enhance existing skills by providing examples or achievements that demonstrate proficiency.                   |
| Education                      | - Highlight education credentials that align with the job requirements.                                          |
|                                | - Include any relevant certifications or courses completed.                                                     |
| Additional Sections           | - Include additional sections (e.g., certifications, projects, publications) that showcase relevant experiences. |
|                                | - Ensure each additional section adds value to the resume and aligns with the job description.                  |


'''.format(resume=resume, job_description=job_description)
# Response format: Detailed suggestions for improving the resume, covering all specified areas to better match the job description.
    return suggestion_prompt

def get_feedback(resume,job_description):
    
    feedback_prompt = '''Act as an HR Manager with 20 years of experience in various technologies.
        Review the resume below and provide detailed feedback to improve it. 
        Focus on the following areas:

        1. Overall presentation and formatting
        2. Professional summary or objective
        3. Work experience (clarity, relevance, and achievements)
        4. Skills (relevance and proficiency level)
        5. Education (relevance and completeness)
        6. Additional sections (certifications, projects, publications, etc.)
        7. Readability, length, and relevance of information

        Provide specific suggestions for each area, highlighting strengths and areas for improvement in the form of tabular format given below.

        | Area                           | Feedback                                                                                                      |
        |--------------------------------|---------------------------------------------------------------------------------------------------------------|
        | Overall Presentation           | - Improve the layout and design to make the resume visually appealing.                                         |
        |                                | - Use consistent formatting for headings, bullet points, and text alignment.                                    |
        | Professional Summary/Objective | - Tailor the summary/objective to highlight relevant skills and experiences for the job.                        |
        | Work Experience               | - Provide clear descriptions of job roles, emphasizing achievements and relevance to the job description.       |
        | Skills                         | - Ensure skills listed are relevant to the job and accurately reflect proficiency level.                        |
        | Education                      | - Highlight education credentials that align with the job requirements.                                          |
        | Additional Sections           | - Include additional sections (e.g., certifications, projects, publications) that showcase relevant experiences. |
        |                                | - Ensure each additional section adds value to the resume and aligns with the job description.                  |
        | Readability, Length, Relevance| - Ensure the resume is easy to read and concise, focusing on relevant information.                             |

        Resume text: {resume}
        '''.format(resume=resume, job_description=job_description)
# Response format: Detailed feedback on each specified area with suggestions for improvement.

    return feedback_prompt


@st.cache_data
def get_result(input):
    model = get_gemini_pro()
    response = model.generate_content(input)
    return response.text

st.set_page_config(page_title='ATS Scanner', page_icon=':technologist:', layout='wide')

st.title('ATS Tool 📄🔍')

job_description = ''

# Initialize a dictionary to store feedback results for each resume
feedback_results_dict = {}

with st.container():
    col1, col2 = st.columns([1, 1])
    job_description = col1.text_area('Enter the Job Description')
    uploaded_file = col2.file_uploader('Upload Your Resume', type=['pdf'])

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=['🕵Analyze resume','📝 Resume feedback','🧑‍💻Score Checker', '🧰 Missing Skills','🗒️ Suggestions'],
        icons=['bi-search', 'bi-chat-text','bi-check-circle','bi-puzzle','bi-stickies']
    )

if selected == '🧑‍💻Score Checker':
    submit = st.button('Get Score')

    if submit:
        if job_description == '':
            st.error('Enter Job Description')
        elif uploaded_file is None:
            st.error('Upload your Resume')
        else:
            # try:
            #     resume = pdf_to_text(uploaded_file)
            #     score_prompt = construct_resume_score_prompt(resume, job_description)
            #     result = get_result(score_prompt)
            #     final_result = result.split(":")[1]
            #     print(final_result)
            #     if '%' not in final_result:
            #         final_result = final_result + '%'
            #     result_str = f"""
            #     <style>
            #     p.a {{
            #         font: bold 25px Arial;
            #     }}
            #     </style>
            #     <p class="a">Your Resume matches {final_result} with the Job Description</p>
            #     """
            #     st.markdown(result_str, unsafe_allow_html=True)
            # except Exception as e:
            #     print(f'{type(e).__name__}: {e}')
            try:
                resume = pdf_to_text(uploaded_file)
                score_prompt = construct_resume_score_prompt(resume, job_description)
                result = get_result(score_prompt)
                score = int(result.split(":")[1].replace('%', ''))
                
                # Display score as a single metric
                # st.metric(label="Resume Match Score", value=f"{score}%")

                # Display score as a gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': "Resume Match Score", 'font': {'size': 24, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}},
                    number={'font': {'size': 70, 'color': 'black', 'family': 'Arial', 'weight': 'bold'}},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "red",'name':"poor"},
                               {'range': [50, 75], 'color': "yellow"},
                               {'range': [75, 100], 'color': "green"}]}))
                
                st.plotly_chart(fig)

                # Display score as a bar chart
                # st.bar_chart({"Score": [score], "Target": [100]})

            except Exception as e:
                st.error(f'{type(e).__name__}: {e}')

elif selected == '🧰 Missing Skills':
    submit = st.button('Get Missing Skills')
    if submit:
        if job_description == '':
            st.error('Enter Job Description')
        elif uploaded_file is None:
            st.error('Upload your Resume')
        else:
            # try:
            #     resume = pdf_to_text(uploaded_file)
            #     skil_prompt = construct_skills_prompt(resume, job_description)
            #     result = get_result(skil_prompt)
            #     st.write('Your Resume misses the following keywords:')
            #     st.markdown(result, unsafe_allow_html=True)
            # except Exception as e:
            #     print(f'{type(e).__name__}: {e}')

            try:
                resume = pdf_to_text(uploaded_file)
                skill_prompt = construct_skills_prompt(resume, job_description)
                result = get_result(skill_prompt)
                st.write('Your Resume misses the following keywords:')
                st.markdown(result, unsafe_allow_html=True)

                filename = "resume_feedback_results.json"
                existing_results = load_results_from_json(filename)
                missing_skills_data = parse_table_to_dict(result)

                if uploaded_file.name not in existing_results:
                    existing_results[uploaded_file.name] = {}

                if 'missing_skills' not in existing_results[uploaded_file.name] or existing_results[uploaded_file.name]['missing_skills'] != missing_skills_data:
                    existing_results[uploaded_file.name]['missing_skills'] = missing_skills_data
                    save_results_to_json(existing_results, filename)
                    st.success("Missing skills results have been updated.")
                else:
                    st.warning("The missing skills result has not changed. No update to JSON file.")

            except Exception as e:
                st.error(f"Error: {e}")

elif selected == '🕵Analyze resume':
    submit = st.button('Get Analysis')
    if submit:
        if job_description == '':
            st.error('Enter Job Description')
        elif uploaded_file is None:
            st.error('Upload your Resume')
        else:
            # try:
            #     resume = pdf_to_text(uploaded_file)
            #     skil_prompt = resume_analysis(resume, job_description)
            #     result = get_result(skil_prompt)
            #     st.write('Here is the detailed Resume Analysis:')
            #     st.markdown(result, unsafe_allow_html=True)
            # except Exception as e:
            #     print(f'{type(e).__name__}: {e}')
            try:
                resume = pdf_to_text(uploaded_file)
                analysis_prompt = resume_analysis(resume, job_description)
                result = get_result(analysis_prompt)
                st.write('Here is the detailed Resume Analysis:')
                st.markdown(result, unsafe_allow_html=True)

                filename = "resume_feedback_results.json"
                existing_results = load_results_from_json(filename)
                analysis_data = parse_table_to_dict(result)

                if uploaded_file.name not in existing_results:
                    existing_results[uploaded_file.name] = {}

                if 'analysis' not in existing_results[uploaded_file.name] or existing_results[uploaded_file.name]['analysis'] != analysis_data:
                    existing_results[uploaded_file.name]['analysis'] = analysis_data
                    save_results_to_json(existing_results, filename)
                    st.success("Analysis results have been updated.")
                else:
                    st.warning("The analysis result has not changed. No update to JSON file.")

            except Exception as e:
                st.error(f"Error: {e}")

elif selected == '🗒️ Suggestions':
    submit = st.button('Get Suggestions')
    if submit:
        if job_description == '':
            st.error('Enter Job Description')
        elif uploaded_file is None:
            st.error('Upload your Resume')
        else:
            # try:
            #     resume = pdf_to_text(uploaded_file)
            #     skil_prompt = get_suggestions(resume, job_description)
            #     result = get_result(skil_prompt)
            #     st.write('Here are the Resume Suggestions:')
            #     st.markdown(result, unsafe_allow_html=True)
            # except Exception as e:
            #     print(f'{type(e).__name__}: {e}')
            try:
                resume = pdf_to_text(uploaded_file)
                suggestion_prompt = get_suggestions(resume, job_description)
                result = get_result(suggestion_prompt)
                st.write('Here are the Resume Suggestions:')
                st.markdown(result, unsafe_allow_html=True)

                filename = "resume_feedback_results.json"
                existing_results = load_results_from_json(filename)
                suggestion_data = parse_table_to_dict(result)

                if uploaded_file.name not in existing_results:
                    existing_results[uploaded_file.name] = {}

                if 'suggestions' not in existing_results[uploaded_file.name] or existing_results[uploaded_file.name]['suggestions'] != suggestion_data:
                    existing_results[uploaded_file.name]['suggestions'] = suggestion_data
                    save_results_to_json(existing_results, filename)
                    st.success("Suggestion results have been updated.")
                else:
                    st.warning("The suggestion result has not changed. No update to JSON file.")

            except Exception as e:
                st.error(f"Error: {e}")

elif selected == '📝 Resume feedback':
    submit = st.button('Get Feedback')
    if submit:
        if job_description == '':
            st.error('Enter Job Description')
        elif uploaded_file is None:
            st.error('Upload your Resume')
        else:
            try:
                resume = pdf_to_text(uploaded_file)
                feedback_prompt = get_feedback(resume, job_description)
                result = get_result(feedback_prompt)
                st.write('Here is the Feedback:')
                st.markdown(result, unsafe_allow_html=True)
                
                filename = "resume_feedback_results.json"
                existing_results = load_results_from_json(filename)
                feedback_data = parse_table_to_dict(result)

                if uploaded_file.name not in existing_results:
                    existing_results[uploaded_file.name] = {}

                if 'feedback' not in existing_results[uploaded_file.name] or existing_results[uploaded_file.name]['feedback'] != feedback_data:
                    existing_results[uploaded_file.name]['feedback'] = feedback_data
                    save_results_to_json(existing_results, filename)
                    st.success("Feedback results have been updated.")
                else:
                    st.warning("The feedback result has not changed. No update to JSON file.")

            except Exception as e:
                st.error(f"Error: {e}")


            


