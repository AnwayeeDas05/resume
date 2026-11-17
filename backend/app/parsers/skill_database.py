from typing import Dict, List, Set, Optional
import re

# Canonical skill -> list of aliases (lowercased)
SKILL_TAXONOMY: Dict[str, List[str]] = {
    # Cloud & DevOps
    "Amazon Web Services (AWS)": ["aws", "amazon web services", "amazon cloud", "aws cloud", "ec2", "s3", "lambda", "fargate", "ecs", "eks"],
    "Google Cloud Platform (GCP)": ["gcp", "google cloud", "google cloud platform", "bigquery", "cloud run", "gke"],
    "Microsoft Azure": ["azure", "ms azure", "microsoft azure", "azure devops", "blob storage"],
    "Kubernetes": ["kubernetes", "k8s", "kube", "kubectl"],
    "Docker": ["docker", "containerization", "containers", "dockerfile", "docker-compose"],
    "Terraform": ["terraform", "iac", "infrastructure as code", "terragrunt"],
    "CI/CD": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci", "circleci", "argo cd", "argocd"],
    "Linux": ["linux", "unix", "ubuntu", "debian", "centos", "bash", "shell scripting", "posix"],

    # Backend & Programming Languages
    "Python": ["python", "python3", "py", "cpython"],
    "FastAPI": ["fastapi", "fast api", "starlette"],
    "Flask": ["flask", "werkzeug"],
    "Django": ["django", "django rest framework", "drf"],
    "Node.js": ["node", "nodejs", "node.js", "express", "expressjs", "express.js", "nest", "nestjs"],
    "Java": ["java", "java 8", "java 11", "java 17", "java 21", "jvm", "spring", "spring boot", "springboot", "hibernate"],
    "Go / Golang": ["go", "golang"],
    "Rust": ["rust", "rustlang", "cargo"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", ".net", "dotnet", ".net core", "asp.net"],
    "Ruby": ["ruby", "ruby on rails", "rails"],
    "PHP": ["php", "laravel", "symfony"],

    # Frontend
    "React": ["react", "react.js", "reactjs", "react-router"],
    "Next.js": ["nextjs", "next.js", "next"],
    "TypeScript": ["typescript", "ts"],
    "JavaScript": ["javascript", "js", "ecmascript", "es6", "es2020", "es2022"],
    "Vue.js": ["vue", "vue.js", "vuejs", "nuxt", "nuxtjs"],
    "Angular": ["angular", "angularjs", "angular 2+"],
    "HTML5 / CSS3": ["html", "html5", "css", "css3", "sass", "scss", "less"],
    "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
    "Redux": ["redux", "redux toolkit", "rtk", "zustand", "mobx"],

    # Databases & Caching
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MongoDB": ["mongodb", "mongo", "nosql", "documentdb"],
    "MySQL": ["mysql", "mariadb"],
    "Redis": ["redis", "in-memory cache", "key-value store"],
    "Elasticsearch": ["elasticsearch", "elastic search", "opensearch", "elk stack"],
    "SQLite": ["sqlite", "sqlite3"],
    "Cassandra": ["cassandra", "scylladb"],
    "DynamoDB": ["dynamodb", "dynamo"],
    "SQL": ["sql", "rdbms", "relational database", "relational databases"],

    # Architecture, APIs & Messaging
    "RESTful APIs": ["rest", "restful", "rest api", "rest apis", "restful api", "restful apis", "restful web services"],
    "GraphQL": ["graphql", "gql", "apollo"],
    "gRPC": ["grpc", "protobuf", "protocol buffers"],
    "Microservices": ["microservices", "microservice architecture", "distributed systems", "service-oriented"],
    "Apache Kafka": ["kafka", "apache kafka", "event streaming", "event-driven architecture"],
    "RabbitMQ": ["rabbitmq", "amqp", "message queue", "message broker", "celery"],
    "System Design": ["system design", "software architecture", "high availability", "scalability", "load balancing"],

    # AI, Machine Learning & NLP
    "Machine Learning": ["machine learning", "ml", "statistical learning", "predictive modeling"],
    "Deep Learning": ["deep learning", "neural networks", "cnn", "rnn", "lstm"],
    "Natural Language Processing (NLP)": ["nlp", "natural language processing", "text mining", "spacy", "nltk", "named entity recognition", "ner"],
    "Large Language Models (LLMs)": ["llm", "llms", "large language models", "prompt engineering", "langchain", "llamaindex", "rag", "retrieval augmented generation", "vector database", "fine-tuning"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf", "keras"],
    "Scikit-Learn": ["scikit-learn", "sklearn"],
    "Pandas / NumPy": ["pandas", "numpy", "scipy"],
    "Computer Vision": ["computer vision", "cv", "opencv", "yolo"],

    # Testing & Tooling
    "Unit Testing": ["unit test", "unit testing", "pytest", "jest", "unittest", "mocha", "chai", "junit", "tdd", "test driven development"],
    "Git": ["git", "github", "gitlab", "bitbucket", "version control", "gitflow"],
    "Agile / Scrum": ["agile", "scrum", "kanban", "sprints", "jira", "confluence"],
    "Security & Auth": ["oauth", "oauth2", "jwt", "json web token", "sso", "saml", "authentication", "authorization", "rbac", "cryptography"],
    "Monitoring & Observability": ["prometheus", "grafana", "datadog", "new relic", "opentelemetry", "cloudwatch", "sentry"]
}

# Reverse mapping: alias -> Canonical skill name
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, aliases in SKILL_TAXONOMY.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

def normalize_skill(skill_name: str) -> str:
    """
    Normalizes a skill name using alias mapping.
    e.g. 'AWS' -> 'Amazon Web Services (AWS)', 'reactjs' -> 'React'
    """
    cleaned = skill_name.strip().lower()
    cleaned = re.sub(r'[\(\)\[\]]', '', cleaned).strip()
    if cleaned in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[cleaned]
    # Check simple substitutions
    for alias, canonical in ALIAS_TO_CANONICAL.items():
        if cleaned == alias:
            return canonical
    return skill_name.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts recognized technical skills from text using taxonomy and regex boundaries.
    """
    found_canonicals: Set[str] = set()
    # Normalize punctuation at word ends so e.g. "AWS.", "Python,", "Docker;" separate cleanly
    normalized_text = re.sub(r'([a-zA-Z0-9])([,\.;:!?])(?:\s|$)', r'\1 \2 ', text)
    lowered = f" {normalized_text.lower()} "
    
    # Sort aliases by length descending so longer phrases match first
    sorted_aliases = sorted(ALIAS_TO_CANONICAL.keys(), key=lambda x: len(x), reverse=True)

    for alias in sorted_aliases:
        # Regex boundary matching for clean token separation
        pattern = r'(?<![a-zA-Z0-9_\-\#\+])' + re.escape(alias) + r'(?![a-zA-Z0-9_\-\#\+])'
        if re.search(pattern, lowered):
            found_canonicals.add(ALIAS_TO_CANONICAL[alias])

    return sorted(list(found_canonicals))

