from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

TEMPLATE = Path('/home/ubuntu/upload/Internship_Report.docx')
OUT = Path('/home/ubuntu/HARVIX---AIBOT/Internship_Report_HARVIX_Template.docx')
SCREENSHOT = Path('/home/ubuntu/HARVIX---AIBOT/docs/dashboard-screenshot.png')
NAVY='17365D'; BLUE='2F75B5'; GRAY='666666'

doc = Document(TEMPLATE)

# Remove everything from the existing Chapter 1 onward, preserving all template content before it.
chapter_start = None
for p in doc.paragraphs:
    if p.text.strip() == 'CHAPTER 1':
        chapter_start = p._p
        break
if chapter_start is None:
    raise RuntimeError('CHAPTER 1 was not found in the supplied template')
body = doc._element.body
children = list(body)
start_index = children.index(chapter_start)
for child in children[start_index:]:
    if child.tag == qn('w:sectPr'):
        break
    body.remove(child)

# Page-number footer is retained from the template; ensure it remains visible.
for section in doc.sections:
    for p in section.footer.paragraphs:
        for r in p.runs:
            r.font.name='Calibri'; r.font.size=Pt(9); r.font.color.rgb=RGBColor.from_string(GRAY)

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), fill); tcPr.append(shd)

def set_cell(cell, text, bold=False, color=None, size=9):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(0)
    r=p.add_run(str(text)); r.font.name='Calibri'; r.font.size=Pt(size); r.bold=bold
    if color: r.font.color.rgb=RGBColor.from_string(color)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def repeat_header(row):
    trPr=row._tr.get_or_add_trPr(); el=OxmlElement('w:tblHeader'); el.set(qn('w:val'),'true'); trPr.append(el)

def heading(text, level=1):
    p=doc.add_paragraph(style=f'Heading {level}'); p.paragraph_format.space_before=Pt(14 if level==1 else 9); p.paragraph_format.space_after=Pt(5); p.add_run(text); return p

def body_text(text):
    p=doc.add_paragraph(style='Body Text'); p.paragraph_format.space_after=Pt(7); p.paragraph_format.line_spacing=1.15; p.add_run(text); return p

def bullet(text):
    p=doc.add_paragraph(style='List Paragraph'); p.paragraph_format.left_indent=Inches(0.25); p.paragraph_format.first_line_indent=Inches(-0.18); p.paragraph_format.space_after=Pt(4); p.add_run('• ' + text); return p

def numbered(text):
    p=doc.add_paragraph(style='List Paragraph'); p.paragraph_format.left_indent=Inches(0.25); p.paragraph_format.first_line_indent=Inches(-0.18); p.paragraph_format.space_after=Pt(4); p.add_run(text); return p

def caption(text):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(8); r=p.add_run(text); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=RGBColor.from_string(GRAY); return p

def table(headers, rows):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    if 'Table Grid' in [s.name for s in doc.styles]:
        t.style='Table Grid'
    repeat_header(t.rows[0])
    for i,h in enumerate(headers): set_cell(t.rows[0].cells[i],h,True,'FFFFFF'); shade(t.rows[0].cells[i],NAVY)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row): set_cell(cells[i],v)
        if ri%2==0:
            for c in cells: shade(c,'F4F8FB')
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t

def code_block(text):
    p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.25); p.paragraph_format.space_after=Pt(5); r=p.add_run(text); r.font.name='Consolas'; r.font.size=Pt(9); return p

# Start Chapter 1 on a new page after the preserved template pages.
doc.add_page_break()

# CHAPTER 1
heading('CHAPTER 1',1); heading('Introduction',2)
heading('Background',5)
body_text('HARVIX is an AI-powered web assistant developed to support users with programming, mathematics, and general queries through a single conversational platform. The system provides programming assistance such as code generation, debugging, code explanation, refactoring, and code conversion. It also supports mathematical problems including equations, derivatives, integrals, and symbolic expressions.')
body_text('The application uses React and Vite for the frontend and FastAPI for the backend. SymPy is integrated to perform exact mathematical calculations instead of depending only on language-model predictions. An optional OpenAI-compatible API can be configured to provide richer conversational and coding responses, while a local fallback keeps the project usable during development and demonstration.')
heading('Problem Statement',5)
body_text('Students, developers, and technical learners often use separate tools for coding assistance, mathematical calculations, and general explanations. This process can be time-consuming and inconvenient. Search engines and documentation require users to find, compare, and understand information on their own, while general AI tools may produce incorrect code or inaccurate mathematical answers. HARVIX addresses this need by identifying the request type and routing it to a suitable processing method.')
heading('Motivation',5)
body_text('The motivation behind HARVIX is to provide quick and convenient support for students, programmers, and learners. The system reduces the time required to search for programming solutions and mathematical explanations by bringing multiple capabilities into one workspace. SymPy improves the reliability of mathematical results, while the optional AI integration supports natural-language explanations and coding assistance. The project also demonstrates practical use of frontend development, backend API design, artificial intelligence integration, symbolic computation, testing, Docker, and continuous integration.')
heading('Objectives of the Project',5)
for x in ['To develop a web-based AI assistant named HARVIX.', 'To create a responsive and user-friendly dashboard using React and Vite.', 'To develop a REST API using Python FastAPI.', 'To automatically classify requests into general, coding, and mathematics categories.', 'To provide code generation, debugging, explanation, refactoring, and code conversion features.', 'To support equations, derivatives, integrals, and symbolic simplification.', 'To integrate SymPy for accurate and exact mathematical calculations.', 'To provide optional OpenAI-compatible language-model integration.', 'To implement input validation, error handling, health monitoring, automated tests, Docker, and GitHub Actions.']: bullet(x)
heading('Scope of the Project',5)
body_text('The project covers the design and development of a responsive conversational dashboard, FastAPI backend, automatic intent-routing system, SymPy-based mathematics engine, optional AI provider integration, testing framework, Docker configuration, GitHub Actions workflow, and project documentation. The current version supports general conversation, programming assistance, mathematical problem solving, and responsive web access. Persistent authentication, server-side chat history, real-time streaming, database integration, and secure execution of untrusted code are outside the current implementation and are reserved for future development.')
heading('Organization of the Report',5)
body_text('Chapter 2 reviews existing approaches and their limitations. Chapter 3 presents the proposed HARVIX architecture and functional modules. Chapter 4 explains the development methodology, technology stack, request routing, mathematics processing, and testing approach. Chapter 5 describes the implementation, project structure, API summary, challenges, and validation. Chapter 6 concludes the report with achievements, results, limitations, future scope, and learning outcomes.')

# CHAPTER 2
heading('CHAPTER 2',1); heading('Existing Method',2)
heading('Overview',5); body_text('Before developing HARVIX, common approaches for obtaining programming and mathematics assistance were considered. Each method provides value but also has limitations related to availability, flexibility, accuracy, or verification.')
heading('Human-Staffed Assistance',5); body_text('Teachers, mentors, and experienced developers can provide context-aware guidance, but their availability is limited. Human support does not scale easily when many users ask repetitive questions, and responses may be delayed during busy periods.')
heading('Search Engines and Documentation',5); body_text('Search engines and documentation provide broad technical information. However, users must select appropriate keywords, compare multiple sources, and adapt the information to their own problem. Beginners may also find it difficult to identify which result is correct or current.')
heading('Rule-Based Chatbots',5); body_text('Rule-based chatbots respond according to manually defined patterns and decision trees. They are predictable but have narrow coverage. A request with unfamiliar wording or multiple requirements may not match an existing rule and may receive an unhelpful fallback response.')
heading('General LLM Chatbots',5); body_text('General language-model chatbots can generate natural explanations and code, but they may produce incorrect code or unsupported calculations. Mathematical responses are especially important to verify because a fluent answer is not proof of a correct result.')
heading('Summary of Limitations',5)
for x in ['Human assistance is limited by time, availability, and scalability.', 'Search and documentation require users to perform the interpretation and verification themselves.', 'Rule-based chatbots have limited flexibility and require continuous manual rule creation.', 'General AI chatbots may hallucinate and should not be the only source for exact mathematical calculations.']: bullet(x)

# CHAPTER 3
heading('CHAPTER 3',1); heading('Proposed Method with Architecture',2)
heading('Overview of the Proposed Solution',5)
body_text('HARVIX combines a responsive conversation dashboard with a FastAPI service and a tool-aware request router. When a user submits a message, the system determines whether the message is a general question, coding request, or mathematics request. Mathematics requests are sent to the SymPy engine, while general and coding requests use the local response layer or an optional OpenAI-compatible provider.')
heading('Why HARVIX over the Alternatives',5)
for x in ['It combines programming, mathematics, and general assistance in one workspace.', 'It automatically routes requests instead of requiring users to select a separate application.', 'It uses SymPy for exact symbolic calculation rather than relying only on generated text.', 'It has a local fallback, making the project demonstrable without a required external API key.', 'It is container-ready, tested, documented, and structured for future expansion.']: bullet(x)
heading('System Architecture',5)
code_block('React/Vite Dashboard  →  FastAPI REST API  →  Intent Router\n                                                     ├── SymPy Math Engine\n                                                     ├── Optional OpenAI Provider\n                                                     └── Local Deterministic Fallback')
caption('Figure 3.1: HARVIX system architecture')
heading('Component Responsibilities',5)
body_text('The React/Vite frontend is responsible for the user interface, message composition, mode controls, suggestions, conversation display, and responsive layout. The FastAPI backend validates requests, exposes REST endpoints, routes messages, calls the mathematics engine, and optionally communicates with an external language-model provider. The SymPy component performs exact symbolic operations. Docker and GitHub Actions support repeatable execution and automated validation.')
heading('Functional Modules of the System',5)
heading('The Intelligent HARVIX Chatbot',6); body_text('The chat module receives user messages, displays the conversation, reports the detected mode, and returns a concise response. It includes a typing indicator and copy control to improve the interaction experience.')
heading('Coding Assistance Module',6); body_text('The coding module is designed for code generation, explanation, debugging, refactoring, and conversion. It accepts natural-language requests and can be extended with a language model for richer code answers.')
heading('Mathematics Solver Module',6); body_text('The mathematics module parses expressions and equations and uses SymPy for simplification, solving, differentiation, and integration. Parse failures are reported as controlled errors instead of guessed answers.')
heading('API and Configuration Module',6); body_text('The API module provides health, chat, and mathematics endpoints. Environment variables control the AI provider, model, database placeholder, and allowed CORS origins. Credentials are kept out of frontend source code.')
heading('Advantages of the Proposed System',5)
for x in ['Unified access to coding and mathematics support.', 'More reliable mathematical results through symbolic computation.', 'Responsive dashboard suitable for desktop and mobile screens.', 'Local fallback for development without mandatory external services.', 'Clear project structure that supports testing, Docker, and future cloud deployment.']: bullet(x)

# CHAPTER 4
heading('CHAPTER 4',1); heading('Methodology',2)
heading('Technology Stack',5)
table(['Layer','Technology','Purpose'], [('Frontend','React, Vite, CSS, Lucide icons','Responsive dashboard and interaction controls'),('Backend','Python, FastAPI, Uvicorn','REST API, routing, validation, and service layer'),('Math engine','SymPy','Exact symbolic simplification, equations, derivatives, and integrals'),('AI provider','OpenAI-compatible API (optional)','Natural-language coding and general responses'),('Testing','Pytest and FastAPI TestClient','Endpoint and routing verification'),('DevOps','Docker, Docker Compose, GitHub Actions','Repeatable execution and continuous integration')])
heading('Request Routing Methodology',5)
for x in ['The frontend sends the message, selected mode, and recent context to the chat endpoint.', 'If a user explicitly selects Coding or Math, the selected mode is used.', 'In Auto mode, code markers, programming terms, and mathematics keywords are inspected.', 'The request is routed to general, coding, or mathematics processing.', 'The response includes the answer, detected mode, elapsed time, and source information.']: numbered(x)
heading('Mathematics Processing Methodology',5)
body_text('The mathematics endpoint accepts an expression and operation. SymPy transformations support implicit multiplication and caret-style exponent input. Equation solving separates the two sides of an equality, derivative requests differentiate with respect to x, integral requests return an antiderivative with the constant C, and ordinary expressions are simplified symbolically. Invalid expressions generate an HTTP 400 response so that the system does not fabricate a result.')
heading('Chat Response Methodology',5)
body_text('For local operation, HARVIX selects a concise response based on the detected intent. When an OpenAI-compatible API key is available, the backend sends the system prompt, recent conversation history, and user message to the configured model. Provider errors are caught so that the local fallback remains available.')
heading('Configuration and Security Methodology',5)
for x in ['Pydantic models validate required fields and restrict input length.', 'CORS origins are read from the CORS_ORIGINS environment variable.', 'API keys remain on the backend and are not exposed in the browser.', 'The .env file is excluded from version control.', 'The application returns controlled errors for invalid input and failed calculations.']: bullet(x)
heading('Testing Methodology',5)
body_text('Testing combines automated API tests, direct endpoint smoke tests, and a frontend production build. The backend tests verify health status, quadratic equation solving, and automatic coding-mode detection. The frontend is validated through npm run build, and the CI workflow repeats the tests and build on pushes and pull requests.')
heading('Containerization and CI Methodology',5)
body_text('The Dockerfile packages the FastAPI service with its Python dependencies. Docker Compose defines API and frontend services for local multi-service execution. GitHub Actions installs dependencies, runs Pytest, installs frontend packages, and generates the production build to catch integration errors early.')

# CHAPTER 5
heading('CHAPTER 5',1); heading('Implementation',2)
heading('Frontend Project Structure',5)
body_text('The frontend is implemented as a Vite-powered React single-page application. The main component manages messages, input, mode selection, loading state, API calls, suggestions, and sidebar visibility. The stylesheet defines the dark workspace, responsive layout, navigation, composer, message bubbles, and status indicators.')
code_block('frontend/\n├── index.html\n├── package.json\n├── vite.config.js\n└── src/\n    ├── main.jsx\n    └── styles.css')
heading('Backend Project Structure',5)
body_text('The backend is intentionally compact and easy to understand. The main module contains the FastAPI application, data models, router, math engine, local responses, and optional language-model adapter. Tests are kept in a separate backend/tests directory.')
code_block('backend/\n├── __init__.py\n├── app/\n│   ├── __init__.py\n│   └── main.py\n└── tests/\n    └── test_api.py')
heading('Chat Endpoint Implementation',5)
body_text('POST /api/chat accepts a message, optional mode, and recent history. The route determines the processing mode, creates a local response, and attempts optional provider generation when the API key is configured. The response includes reply, mode, elapsed_ms, and sources fields.')
heading('Mathematics Endpoint Implementation',5)
body_text('POST /api/math accepts an expression and operation. It returns the original expression, symbolic result, processing steps, and a verification flag. The endpoint covers equation solving, differentiation, integration, and simplification through SymPy.')
heading('Dashboard Features',5)
for x in ['New conversation control and recent-chat sidebar.', 'Auto, Coding, and Math mode buttons.', 'Suggested prompts for mathematics, coding, and concept explanation.', 'Typing indicator while the API request is being processed.', 'Copy control for assistant responses.', 'Responsive layout with mobile sidebar behavior.', 'Operational status indicator and project branding.']: bullet(x)
heading('Dashboard Screenshot',5)
if SCREENSHOT.exists():
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(SCREENSHOT), width=Inches(6.2))
caption('Figure 5.1: HARVIX AI workspace dashboard')
heading('API Summary',5)
table(['Endpoint','Method','Purpose'], [('/api/health','GET','Confirm that the API service is available'),('/api/chat','POST','Route a message and return a HARVIX response'),('/api/math','POST','Evaluate a symbolic expression or operation')])
heading('Development Challenges Encountered and Resolved',5)
for x in ['The GitHub repository was initially an empty scaffold, so the complete frontend, backend, tests, Docker configuration, and documentation were created from the specification.', 'The initial test run required explicit pytest path configuration; pytest.ini was added so package imports work consistently in local and CI environments.', 'The GitHub README architecture diagram produced a rich-rendering chunk error; it was replaced with a GitHub-safe text diagram.', 'The internship template described an unrelated RAG application; the Chapter 1–6 content was rewritten to match the implemented HARVIX project.']: bullet(x)
heading('Testing and Validation',5)
body_text('The completed application was validated through automated tests, direct API smoke tests, a production frontend build, Git integrity checks, and GitHub Actions. The live dashboard was also opened and captured for the report.')
heading('Functional Test Cases',5)
table(['Test Case','Input / Action','Expected Output','Result'], [('Health check','GET /api/health','status = ok','Pass'),('Equation solver','2*x^2 - 5*x + 3 = 0','Roots [1, 3/2]','Pass'),('Coding route','Python coding request','mode = coding','Pass'),('Frontend build','npm run build','Production assets generated','Pass'),('CI workflow','Push to main','Automated test job succeeds','Pass')])

# CHAPTER 6
heading('CHAPTER 6',1); heading('Conclusion',2)
heading('Summary',5)
body_text('The HARVIX internship project delivered a functional AI coding and mathematics assistant with a responsive dashboard, FastAPI backend, exact symbolic mathematics support, optional language-model integration, automated tests, Docker configuration, CI, and documentation. The application demonstrates how a natural-language interface can be combined with deterministic tools to provide more dependable assistance for specialized tasks.')
heading('Key Achievements',5)
for x in ['Developed a responsive React/Vite dashboard with a polished dark-theme interface.', 'Implemented FastAPI endpoints for health, chat, and mathematics processing.', 'Created automatic routing for general, coding, and mathematics requests.', 'Integrated SymPy for exact symbolic calculations.', 'Added optional backend-only OpenAI-compatible integration with a local fallback.', 'Added tests, Docker support, environment configuration, CI, and documentation.', 'Published and verified the completed project on GitHub.']: bullet(x)
heading('Results',5)
body_text('The project passed the backend test suite with three automated tests, successfully built the frontend production bundle, returned valid responses from the health, math, and chat endpoints, and completed the GitHub Actions CI workflow. The dashboard rendered successfully and was included as a project screenshot.')
heading('Limitations',5)
for x in ['Conversation history is currently maintained in the frontend session rather than a persistent user database.', 'Email/password and Google authentication are not implemented in the current version.', 'The typing indicator is not yet a true token-by-token streaming response.', 'User-submitted code is not executed, so the system does not currently provide runtime output.', 'Advanced mathematics such as matrices, statistics, unit conversion, and limits can be expanded in future releases.']: bullet(x)
heading('Future Scope',5)
for x in ['Add PostgreSQL-backed users and conversation history with JWT and OAuth authentication.', 'Implement Server-Sent Events for real-time response streaming.', 'Add a strictly isolated Python and JavaScript code sandbox with resource limits.', 'Expand the mathematics tool layer for matrices, statistics, units, limits, and verification by substitution.', 'Add rate limiting, caching, structured logging, and cloud monitoring.', 'Improve Markdown, code syntax highlighting, and LaTeX rendering in assistant responses.', 'Deploy the frontend and backend to cloud hosting with HTTPS and production secrets management.']: bullet(x)
heading('Learning Outcomes',5)
body_text('The project provided practical experience in full-stack development, React interface design, FastAPI REST services, symbolic mathematics, AI provider integration, environment-based configuration, automated testing, Docker, GitHub Actions, and technical reporting. It also demonstrated the importance of using deterministic tools for exact calculations and clearly separating implemented functionality from future enhancements.')
heading('Real-World Applications',5)
body_text('HARVIX can support programming education, coding bootcamps, developer onboarding, technical support teams, internal engineering assistance, and self-learning platforms. It can also be adapted for mathematics tutoring, software documentation assistants, API support tools, and educational laboratories. With authentication, persistence, and secure execution added, the platform can be extended into a multi-user cloud service.')

# Metadata and save
doc.core_properties.title='HARVIX Internship Report – Template Based'
doc.core_properties.subject='Chapters 1–6 report for HARVIX AI Coding and Mathematics Assistant'
doc.core_properties.author='Mohaneshwari P'
doc.core_properties.keywords='HARVIX, internship, React, FastAPI, SymPy, AI assistant'
doc.save(OUT)
print(OUT)
