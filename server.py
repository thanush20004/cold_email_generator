from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from langchain_community.document_loaders import WebBaseLoader
import uvicorn
import os

# Change to the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.chains import Chain
from app.portfolio import Portfolio
from app.utils import clean_text

app = FastAPI(
    title="Cold Email Generator API",
    description="Generate personalized cold emails for job applications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chain and portfolio
chain = Chain()
portfolio = Portfolio()


class EmailRequest(BaseModel):
    your_name: str
    your_email: str
    recipient_name: str = ""
    job_url: str = ""


@app.get("/")
async def root():
    return {
        "message": "Cold Email Generator API is running",
        "endpoints": {
            "POST /generate-email": "Generate a cold email for a job application"
        }
    }


@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    """
    Generate a personalized cold email for a job application.
    
    Args:
        request: Email request with your_name, your_email, recipient_name, and job_url
        
    Returns:
        Generated email as plain text
    """
    try:
        # If no job URL provided, return a basic template
        if not request.job_url:
            return generate_basic_email(
                your_name=request.your_name,
                your_email=request.your_email,
                recipient_name=request.recipient_name
            )
        
        # Scrape the job posting
        loader = WebBaseLoader([request.job_url])
        data = loader.load().pop().page_content
        
        # Clean the scraped text
        cleaned_data = clean_text(data)
        
        if not cleaned_data.strip():
            return generate_basic_email(
                your_name=request.your_name,
                your_email=request.your_email,
                recipient_name=request.recipient_name
            )
        
        # Extract jobs from the page
        portfolio.load_portfolio()
        jobs = chain.extract_jobs(cleaned_data)
        
        if not jobs:
            return generate_basic_email(
                your_name=request.your_name,
                your_email=request.your_email,
                recipient_name=request.recipient_name
            )
        
        # Generate email for the first job
        job = jobs[0]
        skills = job.get('skills', [])
        links = portfolio.query_links(skills)
        
        email = chain.write_mail(
            job,
            links,
            your_name=request.your_name,
            your_email=request.your_email,
            recipient_name=request.recipient_name
        )
        
        return email
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_basic_email(your_name: str, your_email: str, recipient_name: str = "") -> str:
    """Generate a basic email when job scraping fails."""
    greeting = f"Dear {recipient_name}," if recipient_name else "Dear Hiring Manager,"
    
    return f"""Subject: Job Application

{greeting}

I hope this message finds you well.

I am writing to introduce myself and express my interest in connecting with you regarding a position at your company. I recently came across this opportunity and felt that my background and interests align well with the work your team is involved in.

I would appreciate the chance to have a brief conversation at your convenience to discuss how my skills might align with your needs.

Thank you for your time and consideration. I look forward to your response.

Yours sincerely,
{your_name}
{your_email}"""


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

