# ATS_Gemini

A Generative AI based prompt-tuning of the Gemini-Pro model to Assess Resumes.

## Overview

**ATS_Gemini** is designed to enhance resume assessment using advanced generative AI and prompt-tuning techniques. It aims to improve the accuracy and relevance of resume evaluations, enabling the candidates to strengthen their resume and their chances of hiring.

## Media

![Homepage](https://github.com/mr-nobody15/ATS_Gemini/blob/fc51764509c1469696dc89fa28de00f1d09c2693/Gemini_ATS_App/Media/homepage.png)

![Resume Analysis](https://github.com/mr-nobody15/ATS_Gemini/blob/fc51764509c1469696dc89fa28de00f1d09c2693/Gemini_ATS_App/Media/Resumeanalysis.png)

![Score Checker](https://github.com/mr-nobody15/ATS_Gemini/blob/fc51764509c1469696dc89fa28de00f1d09c2693/Gemini_ATS_App/Media/scorechecker.png)

[Demo Video](https://github.com/mr-nobody15/ATS_Gemini/blob/fc51764509c1469696dc89fa28de00f1d09c2693/Gemini_ATS_App/Media/DEMO_VID.mp4)

## Installation Steps:

1) Create a Virtual environment:
After opening VS Code from the Anaconda navigator, navigate to this current folder, and in the terminal type:
>> python -m venv <name>

To activate the environment = .\<name>\Scripts\Activate

2)After activating the environment, type the command:
>> pip install -r requirements.txt

3) Upload your Gemini-API key from the site - https://aistudio.google.com/app/apikey

4) After uploading the API key, run the command in the terminal
   >> streamlit run app.py

Note: If you face this error - cannot import name 'cygrpc' from 'grpc._cython'...try to delete the virtual environment and re-create the venv and install the modules.

## Results:
You can find the generated results in the JSON file format under the same directory.
