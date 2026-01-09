import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links, your_name="Your Name", your_email="your.email@example.com", recipient_name=""):
        # Personalize the greeting based on recipient name
        greeting = f"Dear {recipient_name}," if recipient_name else "Dear Hiring Manager,"
        
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are {your_name}, an individual job applicant. Write a personalized cold email applying for the position described above.
            
            Your task is to:
            - Introduce yourself as an individual applicant
            - Highlight your relevant skills and experience that match the job requirements
            - Show enthusiasm for the role and company
            - Explain why you're a good fit for this position
            
            {greeting}
            
            I am writing to express my interest in the position mentioned above. After reviewing the job description, I believe my skills and experience align well with your requirements.

            Here are some of my relevant projects and work samples: {link_list}

            I am confident that my background and skills make me a strong candidate for this role. I would welcome the opportunity to discuss how I can contribute to your team.

            Please find my contact information below:
            - Name: {your_name}
            - Email: {your_email}
            
            I look forward to hearing from you.
            
            Best regards,
            {your_name}
            
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job), 
            "link_list": links,
            "your_name": your_name,
            "your_email": your_email,
            "greeting": greeting
        })
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
