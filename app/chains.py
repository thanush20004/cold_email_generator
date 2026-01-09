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
        # Extract job details for personalization
        role = job.get('role', 'the position')
        experience = job.get('experience', 'relevant experience')
        skills = job.get('skills', [])
        description = job.get('description', '')
        
        # Personalize the greeting based on recipient name
        greeting = f"Dear {recipient_name}," if recipient_name else "Dear Hiring Manager,"
        
        # Format skills for better prompting
        skills_text = ", ".join(skills) if isinstance(skills, list) else str(skills)
        
        # Format portfolio links with context
        link_list = ""
        if links:
            link_list = "\n".join([f"• {link.get('links', '')}" for link in links if link.get('links')])
        
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### REQUIRED SKILLS:
            {skills_text}

            ### CANDIDATE INFORMATION:
            Name: {your_name}
            Email: {your_email}
            
            ### INSTRUCTION:
            You are {your_name}. Write a professional, personalized cold email that introduces yourself and expresses interest in connecting regarding the {role} position at the company. The tone should be warm, professional, and genuine - like the reference template provided.

            CRITICAL RULES FOR HIGH RESPONSE RATE:
            
            1. PROFESSIONAL TONE:
               - Warm and friendly, not sales-like or aggressive
               - Professional opening: "I hope this message finds you well"
               - Sincere and authentic language
               - Not overly formal or stiff
               - Match the style of the reference template exactly
            
            2. PERSONALIZATION:
               - Reference specific aspects of the role or team
               - Show genuine interest in their work/initiatives
               - Connect your background to their specific needs
               - Mention something specific about the company
            
            3. BACKGROUND & SKILLS:
               - Briefly mention relevant experience and skills
               - Focus on alignment between your background and their work
               - Be specific about your expertise areas
               - Mention years of experience naturally
            
            4. VALUE PROPOSITION:
               - What you can contribute or learn
               - How your skills align with their initiatives
               - Any relevant achievements (briefly, with context)
               - Focus on contribution potential, not just credentials
            
            5. STRUCTURE & FORMAT:
               - Clear subject line
               - Professional greeting
               - Brief introduction of yourself
               - Skills and experience alignment
               - Soft CTA for connection
               - Professional closing
               - Complete signature block
            
            6. PROHIBITED ELEMENTS:
               - Overly sales-like language
               - Generic placeholders like "[Insert...]"
               - Aggressive CTAs or false urgency
               - More than 150 words total
               - Overly formal or stiff language
               - Apologetic language ("I know you're busy...")
            
            ### EMAIL OUTPUT FORMAT:
            
            Subject: Introduction - {role} at Your Company
            
            {greeting}
            
            I hope this message finds you well.
            
            I am writing to introduce myself and express my interest in connecting with you regarding the {role} position at your company. I recently came across this opportunity and felt that my background and interests align well with the work your team is involved in.
            
            I have experience in {skills_text} with {experience}. [Generate 1-2 sentences about specific relevant achievements or background that directly relates to the role - be specific but concise, e.g., "I have led multiple projects delivering scalable solutions" or "My recent work has focused on building high-performance applications that handle millions of users".]
            
            I am keen to explore whether there may be an opportunity to contribute to your team's success and learn more about your current initiatives. I would appreciate the chance to have a brief conversation at your convenience to discuss how my skills might align with your needs.
            
            My portfolio and work samples: {link_list}
            
            Thank you for your time and consideration. I look forward to your response.
            
            Yours sincerely,
            {your_name}
            {your_email}
            
            ### VALIDATION CHECKLIST:
            ☐ Professional and warm tone
            ☐ Company/role personalization is specific
            ☐ Skills and experience mentioned
            ☐ Soft CTA for connection
            ☐ Email is under 150 words
            ☐ No placeholder text remains
            ☐ Professional signature included
            
            Do not provide a preamble. Do not include the validation checklist in the output.
            ### EMAIL (PROFESSIONAL CONNECTION OPTIMIZED):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job), 
            "link_list": link_list,
            "your_name": your_name,
            "your_email": your_email,
            "greeting": greeting,
            "role": role,
            "skills_text": skills_text,
            "experience": experience
        })
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))

