import os
from pathlib import Path
import docx
import fitz  # PyMuPDF

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    {
        "filename": "01_Alex_Rivera_Senior_Backend.pdf",
        "format": "pdf",
        "name": "Alex Rivera",
        "email": "alex.rivera@techcloud.io",
        "phone": "+1 (415) 892-3491",
        "links": ["https://linkedin.com/in/alex-rivera-backend", "https://github.com/alexrivera"],
        "location": "San Francisco, CA",
        "summary": "Accomplished Senior Backend Engineer with over 7 years of hands-on experience designing and operating high-throughput distributed microservices, scalable RESTful APIs, and cloud-native applications on AWS. Passionate about clean code, high concurrency, and database optimization.",
        "skills": "Python, FastAPI, Django, Amazon Web Services (AWS), Docker, Kubernetes, PostgreSQL, Redis, RESTful APIs, Microservices, CI/CD, Git, Linux, System Design, Unit Testing",
        "experience": [
            ("Senior Backend Engineer", "Veloce Cloud Systems", "2021 - Present",
             "Architected and deployed asynchronous microservices using Python and FastAPI, handling 15,000 requests/sec with p99 latency under 45ms. Designed relational database schemas in PostgreSQL with connection pooling and Redis caching, cutting query execution times by 40%. Led AWS infrastructure migrations leveraging Kubernetes (EKS), Docker containers, and automated CI/CD pipelines via GitHub Actions."),
            ("Software Engineer", "OmniData Tech", "2018 - 2021",
             "Developed core RESTful APIs and distributed task queues using Python, Django, and Celery. Configured AWS EC2, S3, and RDS resources with Terraform. Implemented comprehensive test suites using pytest, achieving 92% code coverage.")
        ],
        "education": "Master of Science in Computer Science, Stanford University, 2018\nBachelor of Science in Computer Engineering, UC Berkeley, 2016",
        "certifications": "AWS Certified Solutions Architect - Associate, Certified Kubernetes Administrator (CKA)",
        "projects": "Distributed Stream Processor: Scalable real-time event pipeline built with Python, Kafka, and Redis.\nOpenAPI Gatekeeper: Open-source FastAPI middleware for JWT authentication and rate-limiting."
    },
    {
        "filename": "02_Sophia_Chen_FullStack_Cloud.docx",
        "format": "docx",
        "name": "Sophia Chen",
        "email": "sophia.chen@devmail.org",
        "phone": "(206) 555-7382",
        "links": ["https://linkedin.com/in/sophiachen-dev", "https://github.com/sophiachen"],
        "location": "Seattle, WA",
        "summary": "Versatile Full Stack Software Engineer with 5.5 years of experience building modern web applications, scalable backend services, and cloud infrastructures. Strong expertise in React, TypeScript, Python, and AWS.",
        "skills": "React, TypeScript, JavaScript, Python, FastAPI, Node.js, Amazon Web Services (AWS), Docker, PostgreSQL, MongoDB, GraphQL, Tailwind CSS, CI/CD, Git",
        "experience": [
            ("Full Stack Engineer", "Strata Innovations", "2021 - Present",
             "Built responsive enterprise web portals using React, TypeScript, and Tailwind CSS. Implemented backend microservices using Python FastAPI and Node.js with MongoDB and PostgreSQL backends. Integrated CI/CD pipelines and deployed serverless containers on AWS Fargate."),
            ("Software Developer", "Apex Web Solutions", "2019 - 2021",
             "Maintained RESTful API endpoints and React single-page applications. Reduced frontend bundle load time by 35% through code splitting.")
        ],
        "education": "Bachelor of Science in Software Engineering, University of Washington, 2019",
        "certifications": "AWS Certified Developer - Associate",
        "projects": "CloudDocs Collaboration App: Real-time collaborative editor with React, WebSockets, and Python backend."
    },
    {
        "filename": "03_Marcus_Johnson_DevOps_Cloud.pdf",
        "format": "pdf",
        "name": "Marcus Johnson",
        "email": "marcus.j@platformops.net",
        "phone": "+1 (512) 402-9811",
        "links": ["https://linkedin.com/in/marcusjohnson-ops", "https://github.com/marcusj-ops"],
        "location": "Austin, TX",
        "summary": "Lead DevOps & Platform Engineer with 8 years of deep expertise in cloud architecture, container orchestration, Kubernetes, CI/CD automation, and infrastructure as code on AWS and GCP.",
        "skills": "Kubernetes, Docker, Amazon Web Services (AWS), Google Cloud Platform (GCP), Terraform, CI/CD, Linux, Python, Prometheus, Grafana, Microservices, Git, System Design",
        "experience": [
            ("Lead Platform Engineer", "HyperScale Cloud", "2020 - Present",
             "Managed multi-cluster Kubernetes infrastructure across AWS and GCP supporting 80+ backend microservices. Built GitOps pipelines using ArgoCD and GitHub Actions. Automated cloud provisioning with Terraform and Terragrunt."),
            ("DevOps Engineer", "CloudForge Networks", "2016 - 2020",
             "Configured monitoring stacks with Prometheus and Grafana. Scripted operational automation tools in Python and Bash.")
        ],
        "education": "Bachelor of Science in Computer Science, University of Texas at Austin, 2016",
        "certifications": "Certified Kubernetes Administrator (CKA), AWS Certified Solutions Architect - Professional",
        "projects": "Terraform AWS Modules: Open-source repository of hardened production EKS modules."
    },
    {
        "filename": "04_Priya_Sharma_Data_AI_Engineer.docx",
        "format": "docx",
        "name": "Priya Sharma",
        "email": "priya.sharma@aimlconsult.com",
        "phone": "+1 (617) 492-8820",
        "links": ["https://linkedin.com/in/priyasharma-ai"],
        "location": "Boston, MA",
        "summary": "Machine Learning and Data Engineer with 4.5 years of experience deploying production ML pipelines, NLP applications, and scalable backend services in Python and PyTorch.",
        "skills": "Python, Machine Learning, Deep Learning, Natural Language Processing (NLP), PyTorch, Scikit-Learn, FastAPI, SQL, PostgreSQL, Docker, Pandas / NumPy, Git",
        "experience": [
            ("Machine Learning Engineer", "Cognitive Insights", "2022 - Present",
             "Fine-tuned Transformer models for semantic search and document classification using PyTorch and HuggingFace. Built FastAPI inference servers deployed inside Docker containers with sub-80ms response times."),
            ("Data Engineer", "Quantix Analytics", "2020 - 2022",
             "Designed ETL pipelines processing 5TB daily using Python and PostgreSQL. Optimized SQL queries and table partitions.")
        ],
        "education": "Master of Science in Data Science & Artificial Intelligence, MIT, 2020\nBachelor of Technology in Information Technology, IIT, 2018",
        "certifications": "TensorFlow Developer Certificate",
        "projects": "Neural Semantic Search: Vector similarity retrieval system built with Sentence Transformers and FastAPI."
    },
    {
        "filename": "05_David_Miller_Mid_Python_Dev.pdf",
        "format": "pdf",
        "name": "David Miller",
        "email": "david.miller@pycraft.dev",
        "phone": "+1 (312) 674-1190",
        "links": ["https://github.com/dmiller-py"],
        "location": "Chicago, IL",
        "summary": "Mid-level Software Developer with 3 years of professional experience building web APIs and database-driven applications using Python and PostgreSQL.",
        "skills": "Python, Django, FastAPI, PostgreSQL, SQLite, RESTful APIs, Docker, Git, Unit Testing, HTML5 / CSS3",
        "experience": [
            ("Backend Developer", "Nexus Web Labs", "2021 - Present",
             "Developed RESTful APIs using Python Django and FastAPI for client billing systems. Wrote automated unit tests with pytest ensuring 85% test coverage. Managed database migrations and indexing in PostgreSQL."),
            ("Junior Developer", "LocalTech Agency", "2020 - 2021",
             "Assisted in building internal dashboard features and writing Python utility scripts.")
        ],
        "education": "Bachelor of Science in Information Technology, University of Illinois, 2020",
        "certifications": "Python Institute Certified Associate Programmer",
        "projects": "Task Tracker API: Lightweight RESTful service with JWT auth and SQLite."
    },
    {
        "filename": "06_Elena_Rostova_Frontend_Specialist.docx",
        "format": "docx",
        "name": "Elena Rostova",
        "email": "elena.rostova@uiengineering.net",
        "phone": "+1 (415) 320-7714",
        "links": ["https://linkedin.com/in/elenarostova-ui", "https://github.com/erostova"],
        "location": "San Francisco, CA",
        "summary": "Senior Frontend Engineer with 6 years of experience engineering high-performance web applications, interactive design systems, and responsive user interfaces with React and TypeScript.",
        "skills": "React, TypeScript, Next.js, JavaScript, Tailwind CSS, Redux, HTML5 / CSS3, Unit Testing, Git, RESTful APIs",
        "experience": [
            ("Senior Frontend Engineer", "PixelWave Studio", "2021 - Present",
             "Spearheaded redesign of core SaaS frontend using Next.js, React, and Tailwind CSS. Implemented micro-frontend architecture and improved Core Web Vitals (LCP reduced by 60%)."),
            ("UI Developer", "OmniCreative Interactive", "2018 - 2021",
             "Built complex data visualizer interfaces with React, D3.js, and TypeScript.")
        ],
        "education": "Bachelor of Science in Computer Engineering, Carnegie Mellon University, 2018",
        "certifications": "Meta Certified Front-End Developer",
        "projects": "Dynamic Dashboard Framework: Modular React widget system with Tailwind CSS."
    },
    {
        "filename": "07_James_Wilson_Junior_Developer.pdf",
        "format": "pdf",
        "name": "James Wilson",
        "email": "jwilson.developer@gmail.com",
        "phone": "+1 (404) 912-3044",
        "links": ["https://github.com/jwilson-code"],
        "location": "Atlanta, GA",
        "summary": "Junior Software Engineer with 1 year of software engineering internship and junior developer experience. Eager to grow backend skills in Python and cloud services.",
        "skills": "Python, JavaScript, React, Git, SQLite, HTML5 / CSS3, RESTful APIs",
        "experience": [
            ("Junior Software Engineer", "BrightStar Startups", "2023 - Present",
             "Built landing pages using React and wrote simple REST API endpoints in Python. Fixed bugs and contributed to weekly sprint code reviews.")
        ],
        "education": "Bachelor of Science in Computer Science, Georgia Tech, 2023",
        "certifications": "",
        "projects": "Recipe Book Web App: React and Python flask mini application."
    },
    {
        "filename": "08_Dr_Amina_Kassid_ML_Research.pdf",
        "format": "pdf",
        "name": "Dr. Amina Kassid",
        "email": "a.kassid@researchlab.ai",
        "phone": "+1 (212) 803-5120",
        "links": ["https://linkedin.com/in/amina-kassid-phd"],
        "location": "New York, NY",
        "summary": "AI Research Scientist holding a Ph.D. in Computer Science with 6 years of experience inventing deep learning architectures, Large Language Models (LLMs), and NLP algorithms.",
        "skills": "Python, Deep Learning, Natural Language Processing (NLP), Large Language Models (LLMs), PyTorch, Machine Learning, Scikit-Learn, C++, Docker, Git",
        "experience": [
            ("Senior AI Research Scientist", "NeuralCore Labs", "2021 - Present",
             "Pioneered novel transformer architectures for contextual language understanding. Published 5 peer-reviewed papers at NeurIPS and ACL. Scaled distributed training on 128 GPUs using PyTorch."),
            ("Doctoral Researcher", "Columbia University AI Lab", "2017 - 2021",
             "Conducted fundamental research on neural representations and cross-lingual embeddings in Python.")
        ],
        "education": "Doctor of Philosophy (Ph.D.) in Computer Science, Columbia University, 2021\nMaster of Science in Computer Science, Columbia University, 2017",
        "certifications": "Deep Learning Specialization (Coursera/Andrew Ng)",
        "projects": "OpenEmbed: Open-source embedding benchmark toolkit for sentence transformers."
    },
    {
        "filename": "09_Robert_Taylor_Legacy_Java_Dev.docx",
        "format": "docx",
        "name": "Robert Taylor",
        "email": "robert.taylor@enterprisejava.com",
        "phone": "+1 (704) 555-8832",
        "links": ["https://linkedin.com/in/rtaylor-java"],
        "location": "Charlotte, NC",
        "summary": "Enterprise Java Software Engineer with 10 years of experience building monolithic and enterprise banking applications with Java, Spring Boot, and Oracle SQL.",
        "skills": "Java, SQL, MySQL, Agile / Scrum, Linux, Git, Unit Testing, System Design",
        "experience": [
            ("Principal Software Engineer", "First Heritage Financial", "2018 - Present",
             "Engineered transaction processing systems in Java and Spring Boot. Managed relational schemas in Oracle and MySQL databases."),
            ("Senior Java Developer", "BluePoint Logistics", "2014 - 2018",
             "Maintained core logistics workflows using Java EE and Hibernate.")
        ],
        "education": "Bachelor of Science in Computer Science, UNC Charlotte, 2014",
        "certifications": "Oracle Certified Professional: Java SE 11 Developer",
        "projects": "Enterprise Transaction Ledger: High integrity accounting module in Java."
    },
    {
        "filename": "10_Chloe_Dupont_Product_Manager.pdf",
        "format": "pdf",
        "name": "Chloe Dupont",
        "email": "chloe.dupont@productworks.co",
        "phone": "+1 (415) 609-2283",
        "links": ["https://linkedin.com/in/chloedupont-pm"],
        "location": "San Francisco, CA",
        "summary": "Senior Technical Product Manager with 6 years leading cross-functional engineering teams, authoring technical specifications, and driving agile roadmap execution.",
        "skills": "Agile / Scrum, System Design, SQL, Git",
        "experience": [
            ("Lead Technical Product Manager", "AppDynamics SaaS", "2020 - Present",
             "Defined product strategy and specifications for cloud observability products. Collaborated with engineering leads on architectural trade-offs."),
            ("Product Owner", "Innovate Mobile", "2018 - 2020",
             "Managed backlog and sprint planning for consumer iOS/Android apps.")
        ],
        "education": "Master of Business Administration (MBA), NYU Stern, 2018\nBachelor of Arts in Economics, NYU, 2015",
        "certifications": "Certified Scrum Product Owner (CSPO), PMP",
        "projects": "SaaS Monetization Funnel: Overhauled billing flow increasing conversions by 22%."
    },
    {
        "filename": "11_Sarah_Kim_Cloud_Native_Backend.pdf",
        "format": "pdf",
        "name": "Sarah Kim",
        "email": "sarah.kim@cloudcraft.io",
        "phone": "+1 (206) 881-4450",
        "links": ["https://linkedin.com/in/sarahkim-backend", "https://github.com/sarahkim-dev"],
        "location": "Seattle, WA",
        "summary": "Cloud-Native Backend Specialist with 5 years of experience architecting distributed microservices, gRPC services, and Kubernetes deployments with Python, Go, and GCP.",
        "skills": "Python, Go / Golang, Google Cloud Platform (GCP), Amazon Web Services (AWS), Kubernetes, Docker, PostgreSQL, Redis, gRPC, Microservices, CI/CD, Git",
        "experience": [
            ("Backend Engineer", "CloudSphere Systems", "2021 - Present",
             "Developed low-latency gRPC services in Python and Go deployed on Google Kubernetes Engine (GKE). Designed cache strategies with Redis and PostgreSQL."),
            ("Software Engineer", "Pacific Data Grid", "2019 - 2021",
             "Built backend pipelines on AWS using Python and Docker.")
        ],
        "education": "Master of Science in Computer Science, University of Washington, 2019",
        "certifications": "Google Professional Cloud Architect",
        "projects": "gRPC Service Mesh: Multi-tenant mesh proxy with automated mTLS."
    },
    {
        "filename": "12_Corrupted_Invalid_Sample.pdf",
        "format": "corrupted",
        "name": "Corrupted Broken File",
        "content": b"%PDF-1.4 %%CORRUPTED HEADER WITHOUT PROPER STREAM DATA"
    }
]

def generate_pdf(filepath: Path, data: dict):
    doc = fitz.open()
    page = doc.new_page()
    
    y = 50
    # Header: Name
    page.insert_text((50, y), data["name"], fontsize=20, fontname="helv", color=(0.05, 0.2, 0.45))
    y += 24
    
    # Contact info
    contact_str = f"{data['email']} | {data['phone']} | {data['location']}"
    page.insert_text((50, y), contact_str, fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    y += 16
    links_str = " | ".join(data.get("links", []))
    if links_str:
        page.insert_text((50, y), links_str, fontsize=9, fontname="helv", color=(0.1, 0.4, 0.8))
        y += 22
    else:
        y += 10

    # Summary
    page.insert_text((50, y), "PROFESSIONAL SUMMARY", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
    y += 14
    page.insert_textbox(fitz.Rect(50, y, 550, y + 45), data["summary"], fontsize=9, fontname="helv")
    y += 50

    # Technical Skills
    page.insert_text((50, y), "TECHNICAL SKILLS", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
    y += 14
    page.insert_textbox(fitz.Rect(50, y, 550, y + 35), data["skills"], fontsize=9, fontname="helv")
    y += 40

    # Experience
    page.insert_text((50, y), "PROFESSIONAL EXPERIENCE", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
    y += 16
    for title, company, dates, desc in data["experience"]:
        page.insert_text((50, y), f"{title} — {company} ({dates})", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.3))
        y += 14
        page.insert_textbox(fitz.Rect(50, y, 550, y + 60), desc, fontsize=8.5, fontname="helv")
        y += 66

    # Education
    page.insert_text((50, y), "EDUCATION", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
    y += 14
    page.insert_textbox(fitz.Rect(50, y, 550, y + 35), data["education"], fontsize=9, fontname="helv")
    y += 40

    # Certifications & Projects
    if data.get("certifications"):
        page.insert_text((50, y), "CERTIFICATIONS", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 14
        page.insert_text((50, y), data["certifications"], fontsize=8.5, fontname="helv")
        y += 22

    if data.get("projects"):
        page.insert_text((50, y), "KEY PROJECTS", fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 14
        page.insert_textbox(fitz.Rect(50, y, 550, y + 40), data["projects"], fontsize=8.5, fontname="helv")

    doc.save(filepath)
    doc.close()

def generate_docx(filepath: Path, data: dict):
    doc = docx.Document()
    
    # Header
    title_p = doc.add_paragraph()
    run = title_p.add_run(data["name"])
    run.bold = True
    run.font.size = docx.shared.Pt(18)
    
    contact_p = doc.add_paragraph(f"{data['email']} | {data['phone']} | {data['location']}")
    contact_p.runs[0].font.size = docx.shared.Pt(9)
    if data.get("links"):
        links_p = doc.add_paragraph(" | ".join(data["links"]))
        links_p.runs[0].font.size = docx.shared.Pt(8.5)

    # Summary
    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(data["summary"])

    # Skills
    doc.add_heading("Technical Skills", level=2)
    doc.add_paragraph(data["skills"])

    # Experience
    doc.add_heading("Work Experience", level=2)
    for title, company, dates, desc in data["experience"]:
        exp_p = doc.add_paragraph()
        r1 = exp_p.add_run(f"{title} – {company} ({dates})\n")
        r1.bold = True
        exp_p.add_run(desc)

    # Education
    doc.add_heading("Education", level=2)
    doc.add_paragraph(data["education"])

    if data.get("certifications"):
        doc.add_heading("Certifications", level=2)
        doc.add_paragraph(data["certifications"])

    if data.get("projects"):
        doc.add_heading("Projects", level=2)
        doc.add_paragraph(data["projects"])

    doc.save(filepath)

def main():
    print(f"Generating sample test resumes in {SAMPLE_DIR}...")
    for item in CANDIDATES:
        filepath = SAMPLE_DIR / item["filename"]
        if item["format"] == "pdf":
            generate_pdf(filepath, item)
            print(f"  [+] Created PDF: {item['filename']}")
        elif item["format"] == "docx":
            generate_docx(filepath, item)
            print(f"  [+] Created DOCX: {item['filename']}")
        elif item["format"] == "corrupted":
            with open(filepath, "wb") as f:
                f.write(item["content"])
            print(f"  [+] Created Corrupted File: {item['filename']} (to test batch error handling)")

    # Also generate sample Job Description files
    jd1_text = """Job Title: Senior Backend Engineer
Company: CloudScale Technologies
Location: Remote / San Francisco, CA

About the Role:
CloudScale Technologies is looking for a Senior Backend Engineer to architect, build, and scale our core cloud-native microservices platform. You will be responsible for designing high-performance RESTful APIs, distributed asynchronous systems, and database architectures handling millions of daily operations.

Core Responsibilities:
• Architect, build, and maintain scalable backend microservices and RESTful APIs using Python and FastAPI.
• Design, optimize, and maintain relational databases (PostgreSQL) and in-memory caches (Redis).
• Deploy, scale, and manage containerized applications using Docker and Kubernetes (EKS) on Amazon Web Services (AWS).
• Implement robust CI/CD pipelines, automated testing (unit and integration tests), and infrastructure as code.
• Participate in architectural design reviews and drive engineering best practices across the team.

Required Qualifications & Skills:
• Minimum 5+ years of relevant backend software engineering experience.
• Strong proficiency in Python and modern frameworks (FastAPI, Django, or Flask).
• Extensive experience with Amazon Web Services (AWS) cloud services (EC2, S3, RDS, ECS/EKS).
• Strong hands-on experience with Docker containerization and Kubernetes orchestration.
• Proven expertise with PostgreSQL schema design, indexing, and query optimization.
• Deep understanding of microservices architecture, RESTful API design, and Redis caching.
• Bachelor's or Master's degree in Computer Science, Software Engineering, or related STEM field.

Preferred / Nice-to-Have Skills:
• Experience with Apache Kafka, event streaming, or RabbitMQ message queues.
• Knowledge of Golang or TypeScript.
• Experience with Terraform for infrastructure automation.
• Professional cloud certification (e.g., AWS Certified Solutions Architect or CKA).
"""
    with open(SAMPLE_DIR / "Sample_JD_Senior_Backend_Engineer.txt", "w") as f:
        f.write(jd1_text)

    jd2_text = """Job Title: Full Stack Developer
Company: NextGen Apps
Location: New York, NY

Overview:
We are seeking a talented Full Stack Developer with experience in React, TypeScript, and modern backend APIs.

Responsibilities:
• Develop responsive, accessible web user interfaces using React, TypeScript, and Tailwind CSS.
• Build secure, scalable backend APIs with Python or Node.js.
• Work with PostgreSQL and MongoDB databases.
• Deploy applications to cloud environments (AWS).

Requirements:
• 3+ years of full stack software engineering experience.
• Strong experience with React, JavaScript, and TypeScript.
• Experience with Python or Node.js backend services.
• Experience with RESTful APIs, HTML5/CSS3, and Git.
• Bachelor's degree in Computer Science or equivalent work experience.
"""
    with open(SAMPLE_DIR / "Sample_JD_Full_Stack_Developer.txt", "w") as f:
        f.write(jd2_text)

    print("All sample files generated successfully!")

if __name__ == "__main__":
    main()

