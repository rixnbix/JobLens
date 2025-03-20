# RUNICE: Python Project

# JobLens

A University group project for the Object-Oriented Software Development Course

## How to Execute the Program

1. **Clone the repository:**
   `git clone https://github.com/rixnbix/JobLens.git`

2. **Navigate to the project directory:**
   `cd <project-directory>`

3. **Create a virtual environment:**
   `python -m venv joblens`

4. **Activate the virtual environment:**

   - For Windows:
     `joblens\Scripts\activate`
   - For macOS/Linux:
     `source joblens/bin/activate`

5. **Install the required dependencies:**
   `pip install -r requirements.txt`

6. **Run the application:**
   `python app.py`

## Entity Relationship Diagram

```mermaid
---
title: Joblens Resume
---
erDiagram
    EMPLOYER {
        int employer_id PK
        string company_name
        string email
        string password
    }

    JOB_LISTING {
        int job_id PK
        int employer_id FK
        string job_title
        string job_description
        string requirements
    }

    CANDIDATE {
        int candidate_id PK
        string name
        string email
        string phone
    }

    RESUME {
        int resume_id PK
        int candidate_id FK
        text content
    }

    APPLICATION {
        int application_id PK
        int job_id FK
        int candidate_id FK
        int resume_id FK
        string status
    }

    KEYWORD {
        int keyword_id PK
        int job_id FK
        string keyword
    }

    MATCH_SCORE {
        int match_id PK
        int application_id FK
        float score
    }

    EMPLOYER ||--o{ JOB_LISTING : posts
    JOB_LISTING ||--o{ KEYWORD : contains
    JOB_LISTING ||--o{ APPLICATION : receives
    CANDIDATE ||--o{ APPLICATION : submits
    CANDIDATE ||--|{ RESUME : uploads
    RESUME ||--|{ APPLICATION : attached
    APPLICATION ||--o| MATCH_SCORE : has
```
