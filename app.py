import logging
import os
import json
import re

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
openai.api_key = os.getenv("OPENAI_API_KEY")
phrases = ["Top 5 Missing Skills:","Missing Responsibility from CV:","Existing Experience to be Changed:","New Experience Suggested:"]
pattern = "|".join(map(re.escape, phrases))

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        jd = request.form["jd"]
        cv = request.form["cv"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_prompt(jd, cv),
            temperature=0.6,
        )
        full_res =  json.dumps(response, indent=4)
        app.logger.info(full_res)
        return redirect(url_for("index", result=response['choices'][0]['message']['content']))
    
    result = str(request.args.get("result"))
    parts = re.split(pattern, result)
    parts = [part for part in parts if part.strip()]

    return render_template("index.html", result=parts)


def generate_prompt(jd, cv):
    return [
    { "role" : "user", "content" : """ Job Description:
     {}
     
     CV:
     {}

1. This a Job description and my CV. I want you to analyse both of these and give me the skills that are missing from my CV and show me the top 5 missing skills.
2. I then want you to find out one responsibility which is required as per the job description and is missing from my CV
Then I want you to find out which existing experience aligns the most with this missing responsibility mentioned in the JD.
Then I want you to generate a bullet to help me include the missing responsibility to CV, make sure to keep the language of this new bullet similar to the whole CV. 
Give me previous experince and the new suggested experience.

I want the output very concise. 
First give me just the list of top 5 missing skills
Then give me the missing responsibility from CV, the existing experience to be changed, and the new experience suggested. Do not give any notes or anything else other than the specified things above.""".format(jd,cv)}
    ]
    