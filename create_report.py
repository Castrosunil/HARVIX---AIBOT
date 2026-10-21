from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from pathlib import Path

OUT = Path('/home/ubuntu/HARVIX---AIBOT/Internship_Report_HARVIX.docx')
SCREENSHOT = Path('/home/ubuntu/HARVIX---AIBOT/docs/dashboard-screenshot.png')

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.8)
sec.bottom_margin = Inches(0.75)
sec.left_margin = Inches(0.9)
sec.right_margin = Inches(0.9)

# Helpers
NAVY = '17365D'
BLUE = '2F75B5'
LIGHT = 'D9EAF7'
GRAY = '666666'

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), fill); tcPr.append(shd)

def set_cell_text(cell, text, bold=False, color=None, size=10):
    cell.text = ''
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold; r.font.name = 'Calibri'; r.font.size = Pt(size)
    if color: r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr(); rep = OxmlElement('w:tblHeader'); rep.set(qn('w:val'), 'true'); trPr.append(rep)

def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run('Page ')
    fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText'); instrText.set(qn('xml:space'), 'preserve'); instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1); run._r.append(instrText); run._r.append(fldChar2)

def add_heading(text, level=1):
    p = doc.add_paragraph(style=f'Heading {level}')
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    p.add_run(text)
    return p

def add_body(text, bold_prefix=None):
    p = doc.add_paragraph(style='Body Text')
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p

def add_bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    p.add_run(text)
    return p

def add_number(text):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.space_after = Pt(4)
    p.add_run(text)
    return p

def add_caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor.from_string(GRAY)
    return p

def add_table(headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'; table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0]; set_repeat_table_header(hdr)
    for i, h in enumerate(headers):
        set_cell_text(hdr.cells[i], h, bold=True, color='FFFFFF', size=9); shade(hdr.cells[i], NAVY)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], str(value), size=9)
            if len(table.rows) % 2 == 0: shade(cells[i], 'F4F8FB')
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table

# Styles
styles = doc.styles
styles['Normal'].font.name = 'Calibri'; styles['Normal'].font.size = Pt(11)
for name, size, color in [('Heading 1', 18, NAVY), ('Heading 2', 14, BLUE), ('Heading 3', 12, NAVY)]:
    st = styles[name]; st.font.name = 'Calibri'; st.font.size = Pt(size); st.font.bold = True; st.font.color.rgb = RGBColor.from_string(color)
styles['Body Text'].font.name = 'Calibri'; styles['Body Text'].font.size = Pt(11)
styles['List Bullet'].font.name = 'Calibri'; styles['List Bullet'].font.size = Pt(11)
styles['List Number'].font.name = 'Calibri'; styles['List Number'].font.size = Pt(11)

# Footer
for section in doc.sections:
    footer = section.footer.paragraphs[0]
    footer.text = 'HARVIX – AI Coding & Mathematics Assistant  |  '
    footer.runs[0].font.size = Pt(9); footer.runs[0].font.color.rgb = RGBColor.from_string(GRAY)
    add_page_number(footer)

# Cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(55)
r = p.add_run('SUMMER INTERNSHIP REPORT'); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = RGBColor.from_string(NAVY)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(30)
r = p.add_run('HARVIX'); r.bold = True; r.font.size = Pt(28); r.font.color.rgb = RGBColor.from_string(BLUE)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('AI Coding & Mathematics Assistant'); r.bold = True; r.font.size = Pt(18); r.font.color.rgb = RGBColor.from_string(NAVY)
for _ in range(2): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Submitted by').bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('MOHANESWARI P (711724UCB128)').bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Under the guidance of Mrs SIVARANJINI V')
for _ in range(2): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('In partial fulfilment for the award of the degree of').bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('BACHELOR OF TECHNOLOGY')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('in COMPUTER SCIENCE AND BUSINESS SYSTEMS').bold = True
for _ in range(3): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('KGISL INSTITUTE OF TECHNOLOGY').bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('(Affiliated to Anna University)')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Saravanampatti, Coimbatore – 641035')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Academic Year 2026–2027')
# Heading 1 starts the next logical page in the generated document; avoid an extra blank page here.

# Certificate
add_heading('BONAFIDE CERTIFICATE', 1)
add_body('This is to certify that the report entitled “HARVIX – AI CODING & MATHEMATICS ASSISTANT” is a bonafide record of the internship work carried out by MOHANESWARI P, in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Business Systems during the academic year 2026–2027.')
add_body('The project involved the design and implementation of a responsive AI workspace with a React/Vite frontend, FastAPI backend, SymPy mathematics engine, optional OpenAI integration, Docker support, automated tests, and a GitHub Actions continuous-integration workflow.')
for _ in range(4): doc.add_paragraph()
add_body('Project Guide: Mrs SIVARANJINI V')
add_body('Head of the Department: Department of CSBS')
doc.add_page_break()

# Abstract
add_heading('ABSTRACT', 1)
add_body('HARVIX is a cloud-ready AI assistant designed to support programming and mathematics learning through a single conversational workspace. The application can automatically route user requests to general chat, coding assistance, or mathematics processing. In coding mode, HARVIX supports code generation, explanation, debugging, refactoring, and language conversion prompts. In mathematics mode, requests are processed through a SymPy-backed symbolic engine so that expressions, equations, derivatives, and integrals are calculated exactly rather than guessed by a language model.')
add_body('The system uses a React and Vite dashboard on the frontend and a Python FastAPI service on the backend. The dashboard provides conversation history, mode selection, new-chat controls, suggested prompts, typing feedback, and a responsive dark interface. The backend provides health, chat, and mathematics REST endpoints with input validation and configurable CORS. An optional OpenAI adapter can be enabled using environment variables, while a deterministic local fallback keeps the project runnable without an external API key.')
add_body('The project also includes Docker and Docker Compose configuration, a requirements file, an environment template, a GitHub Actions CI workflow, automated API tests, and documentation for local execution and deployment. Validation confirmed that the backend tests pass, the frontend builds successfully, the API endpoints respond correctly, and the dashboard renders as expected.')
doc.add_page_break()

# Contents (manual, robust across viewers)
add_heading('TABLE OF CONTENTS', 1)
contents = [
('1', 'Introduction', '5'), ('2', 'Existing Method', '7'), ('3', 'Proposed Method with Architecture', '9'), ('4', 'Methodology', '13'), ('5', 'Implementation and Testing', '18'), ('6', 'Conclusion and Future Scope', '24')]
add_table(['Chapter No.', 'Title', 'Page'], contents, [1.2, 4.5, 0.8])
doc.add_page_break()

# Chapter 1
add_heading('CHAPTER 1', 1); add_heading('Introduction', 2)
add_heading('Background', 3)
add_body('Programming and mathematics are two areas where learners and developers frequently need immediate, reliable assistance. Conventional search requires users to combine several sources, while a basic chat interface may provide fluent but unverified answers. HARVIX addresses this gap by combining a conversational user experience with intent routing and a dedicated symbolic mathematics engine.')
add_body('The system is designed around a simple principle: general language generation is useful for explanations and coding guidance, but exact mathematical operations should be delegated to a real calculation engine. This separation improves trustworthiness and makes the assistant suitable for educational demonstrations, coding practice, and early-stage development support.')
add_heading('Problem Statement', 3)
add_body('Users need one accessible workspace that can understand whether a request is related to programming, mathematics, or general conversation, then provide a useful response in the appropriate mode. The application must also remain safe, configurable, testable, and easy to run locally or in a containerized environment.')
add_heading('Objectives of the Project', 3)
for x in ['Build a responsive AI assistant dashboard branded as HARVIX.', 'Implement automatic routing between general, coding, and mathematics requests.', 'Use SymPy for exact symbolic mathematics instead of relying on unsupported guesses.', 'Provide a FastAPI REST service with validation, CORS, health monitoring, and optional LLM integration.', 'Add automated tests, Docker support, GitHub Actions CI, and clear project documentation.', 'Create a clean dashboard suitable for desktop and mobile use.']: add_bullet(x)
add_heading('Scope of the Project', 3)
add_body('The delivered scope covers the web dashboard, API layer, intent router, deterministic mathematics engine, optional OpenAI provider, tests, container configuration, CI, and documentation. Advanced production features such as persistent multi-user authentication, server-side conversation storage, full token-by-token streaming, and isolated code execution are identified as future extensions rather than claimed as completed features in the current version.')
add_heading('Organization of the Report', 3)
add_body('Chapter 2 reviews existing approaches. Chapter 3 presents the proposed HARVIX architecture. Chapter 4 explains the development methodology and request-processing flow. Chapter 5 describes implementation, project structure, testing, and deployment support. Chapter 6 summarizes the results, limitations, and future scope.')

# Chapter 2
add_heading('CHAPTER 2', 1); add_heading('Existing Method', 2)
add_heading('Human-Only Assistance', 3); add_body('Human mentoring provides context and judgment but is not continuously available and does not scale for repetitive questions. Response time depends on the availability of a teacher, colleague, or support engineer.')
add_heading('Search Engines and Documentation', 3); add_body('Documentation and search engines provide broad coverage, but users must select suitable keywords, compare sources, and translate the result into a working solution. This is especially difficult when the question combines code and mathematics.')
add_heading('Rule-Based Chatbots', 3); add_body('Rule-based assistants are predictable but depend on manually authored patterns. They struggle with unfamiliar phrasing, multi-step programming requests, and follow-up questions.')
add_heading('General LLM Chatbots', 3); add_body('A general language model can explain concepts and generate code fluently, but it may produce incorrect calculations or untested code. Mathematical accuracy is particularly sensitive because a plausible-looking answer is not evidence that the calculation is correct.')
add_heading('Summary of Limitations', 3)
for x in ['Human-only support is limited by time and availability.', 'Search requires users to perform the interpretation and verification themselves.', 'Rule-based systems have narrow coverage and poor flexibility.', 'General LLMs can hallucinate and should not be trusted as the sole calculation engine.']: add_bullet(x)

# Chapter 3
add_heading('CHAPTER 3', 1); add_heading('Proposed Method with Architecture', 2)
add_heading('Overview of the Proposed Solution', 3)
add_body('HARVIX combines a responsive conversation dashboard with a backend intent router. Each request is inspected for mathematical, coding, or general language signals. Mathematical requests are sent to SymPy-backed processing. Coding and general requests use a concise local response or the optional OpenAI provider when the environment is configured with a valid API key.')
add_heading('System Architecture', 3)
arch = 'React/Vite Dashboard  →  FastAPI REST API  →  Intent Router\n                                                     ├── SymPy Math Engine\n                                                     ├── Optional OpenAI Provider\n                                                     └── Local Deterministic Fallback'
p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.25); r=p.add_run(arch); r.font.name='Consolas'; r.font.size=Pt(9)
add_caption('Figure 3.1: HARVIX system architecture')
add_heading('Key Design Decisions', 3)
for x in ['Separate mathematical computation from language generation so exact operations are handled by SymPy.', 'Keep API keys on the backend and load them only through environment variables.', 'Provide a deterministic local mode so the dashboard remains demonstrable without paid external services.', 'Use REST endpoints with Pydantic validation for a small, understandable integration surface.', 'Package the application with Docker and validate changes through GitHub Actions.']: add_bullet(x)
add_heading('HARVIX System Prompt', 3)
add_body('The backend includes the following system instruction for the optional language model: “You are HARVIX, an intelligent cloud-based assistant specialized in programming and mathematics. Write clean, correct, well-commented code. For math, use the provided calculation tools, show steps, and verify results. Be concise, ask for clarification when a request is ambiguous, and never fabricate results.”')

# Chapter 4
add_heading('CHAPTER 4', 1); add_heading('Methodology', 2)
add_heading('Technology Stack', 3)
add_table(['Layer', 'Technology', 'Purpose'], [
('Frontend', 'React, Vite, CSS, Lucide icons', 'Responsive chat dashboard and interaction controls'),
('Backend', 'Python, FastAPI, Uvicorn', 'REST API, routing, validation, and service layer'),
('Math engine', 'SymPy', 'Exact symbolic simplification, equations, derivatives, and integrals'),
('AI provider', 'OpenAI-compatible API (optional)', 'Natural-language coding and general responses'),
('Testing', 'Pytest, FastAPI TestClient', 'Endpoint and routing verification'),
('DevOps', 'Docker, Docker Compose, GitHub Actions', 'Repeatable execution and continuous integration'),
], [1.1, 2.1, 3.3])
add_heading('Request Routing Methodology', 3)
for x in ['The client sends a message, selected mode, and recent conversation context to POST /api/chat.', 'If the user selects a mode explicitly, that mode is respected.', 'In Auto mode, keywords and code markers are evaluated to identify math, coding, or general intent.', 'Math requests receive symbolic processing and a structured result when the expression is parseable.', 'Coding and general requests use the local assistant response or optional OpenAI provider.', 'The response returns the answer, detected mode, elapsed time, and source metadata.']: add_number(x)
add_heading('Mathematics Methodology', 3)
add_body('The math endpoint accepts an expression and operation. SymPy parsing transformations support implicit multiplication and caret-style exponent input. Equation solving splits the expression at the equality sign, derivative requests use differentiation with respect to x, integral requests return an antiderivative plus the constant C, and ordinary expressions are simplified symbolically. Parsing errors are returned as a controlled HTTP 400 response instead of an invented answer.')
add_heading('Security and Configuration Methodology', 3)
for x in ['Input length is bounded with Pydantic field validation.', 'CORS origins are configured through the CORS_ORIGINS environment variable.', 'API credentials are never placed in frontend source code.', 'The .env file is excluded from Git through .gitignore.', 'The optional model adapter catches provider failures and preserves a local response path.']: add_bullet(x)
add_heading('Development Procedure', 3)
for x in ['Create the backend health and chat endpoints.', 'Integrate exact mathematics through SymPy.', 'Build the React dashboard and connect it to the API.', 'Add tests for health, equation solving, and coding intent routing.', 'Add Docker, environment configuration, CI, and documentation.', 'Run local tests and a production frontend build before pushing to GitHub.']: add_number(x)

# Chapter 5
add_heading('CHAPTER 5', 1); add_heading('Implementation and Testing', 2)
add_heading('Frontend Implementation', 3)
add_body('The frontend is implemented as a Vite-powered React single-page application. It contains a collapsible workspace sidebar, HARVIX branding, recent chat items, mode controls, suggestion prompts, message bubbles, typing feedback, copy action, and a bottom composer. CSS media queries adapt the layout for smaller screens. The visual design uses a dark navy background, violet accents, rounded panels, and clear contrast for readable conversations.')
add_heading('Backend Implementation', 3)
add_body('The main FastAPI module defines the application, CORS middleware, request and response models, routing logic, the SymPy math engine, the optional OpenAI adapter, and the health endpoint. The implementation is intentionally compact so that the architecture is easy to study and extend.')
add_heading('Project Structure', 3)
structure = 'HARVIX---AIBOT/\n├── backend/app/main.py          # FastAPI API, routing, math engine\n├── backend/tests/test_api.py    # API and math tests\n├── frontend/src/main.jsx        # React dashboard\n├── frontend/src/styles.css      # Responsive dashboard styles\n├── Dockerfile                   # Backend container\n├── docker-compose.yml           # Local multi-service setup\n├── requirements.txt             # Python dependencies\n├── .env.example                 # Configuration template\n├── .github/workflows/ci.yml     # Automated CI\n├── README.md                    # Setup and architecture guide\n└── REPORT.md                    # Project summary report'
p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.25); r=p.add_run(structure); r.font.name='Consolas'; r.font.size=Pt(9)
add_caption('Figure 5.1: HARVIX project structure')
add_heading('Dashboard Screenshot', 3)
if SCREENSHOT.exists():
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(SCREENSHOT), width=Inches(6.3))
add_caption('Figure 5.2: HARVIX responsive AI workspace dashboard')
add_heading('API Summary', 3)
add_table(['Endpoint', 'Method', 'Purpose'], [
('/api/health', 'GET', 'Confirm that the API service is available'),
('/api/chat', 'POST', 'Route a message and return a HARVIX response'),
('/api/math', 'POST', 'Evaluate a symbolic expression or operation'),
], [1.5, 1.0, 4.0])
add_heading('Testing and Validation', 3)
add_body('The automated test suite uses FastAPI TestClient and includes health verification, quadratic equation solving, and automatic coding-mode routing. The frontend was validated with a Vite production build. Additional smoke tests were performed against the health, math, and chat endpoints.')
add_table(['Test Case', 'Input / Action', 'Expected Result', 'Result'], [
('Health check', 'GET /api/health', 'status = ok', 'Pass'),
('Equation solver', '2*x^2 - 5*x + 3 = 0', 'Roots [1, 3/2]', 'Pass'),
('Coding route', 'Python debugging request', 'mode = coding', 'Pass'),
('Frontend build', 'npm run build', 'Production assets generated', 'Pass'),
('CI workflow', 'Push to main', 'Automated test job succeeds', 'Pass'),
], [1.4, 2.3, 2.0, 0.8])
add_heading('Development Challenges and Resolutions', 3)
for x in ['The initial empty repository required the complete project scaffold to be created from the specification.', 'The first test run revealed that pytest needed an explicit project path; pytest.ini was added so local and CI imports resolve consistently.', 'The supplied report template described a different application; its technical claims were replaced so that the final report matches the implemented HARVIX features.', 'GitHub README rich-diagram rendering produced a chunk-loading error; the architecture section was replaced with a GitHub-safe text diagram.']: add_bullet(x)

# Chapter 6
add_heading('CHAPTER 6', 1); add_heading('Conclusion and Future Scope', 2)
add_heading('Summary', 3)
add_body('The internship project delivered HARVIX, a working AI coding and mathematics assistant with a responsive dashboard, FastAPI backend, exact symbolic math support, optional language-model integration, automated tests, Docker configuration, CI, and documentation. The implementation demonstrates how a practical AI application can combine a language interface with deterministic tools for higher confidence in specialized tasks.')
add_heading('Key Achievements', 3)
for x in ['Built a complete React/Vite dashboard with a polished responsive interface.', 'Implemented automatic routing for general, coding, and mathematics requests.', 'Integrated SymPy for exact symbolic calculations and controlled parse errors.', 'Added optional backend-only OpenAI integration with a local fallback.', 'Delivered tests, Docker files, environment configuration, CI, and documentation.', 'Published the completed project to GitHub and verified a clean synchronized main branch.']: add_bullet(x)
add_heading('Current Limitations', 3)
for x in ['Conversation history is currently maintained in the frontend session rather than a persistent user database.', 'Email/password and Google authentication are not yet implemented in the current version.', 'Streaming responses are represented by a typing indicator; token-by-token SSE streaming is future work.', 'Code execution is not enabled; the current coding mode provides assistance without running untrusted code.', 'The local fallback is intentionally concise and becomes more capable when an external LLM provider is configured.']: add_bullet(x)
add_heading('Future Scope', 3)
for x in ['Add PostgreSQL-backed users and conversation history with JWT and OAuth authentication.', 'Implement Server-Sent Events for true token-by-token response streaming.', 'Add a separately isolated Python/JavaScript sandbox with strict time, memory, and network limits.', 'Expand the math tool layer for matrices, statistics, units, limits, and verified substitutions.', 'Add rate limiting, structured logging, caching, observability, and cloud deployment manifests.', 'Introduce richer Markdown, syntax highlighting, and LaTeX rendering in assistant responses.']: add_bullet(x)
add_heading('Learning Outcomes', 3)
add_body('The project provided practical experience in full-stack application development, REST API design, React interface development, symbolic mathematics, environment-based configuration, AI provider integration, automated testing, containerization, GitHub workflows, and technical documentation. It also reinforced the importance of distinguishing implemented features from future scope and validating AI outputs with deterministic tools wherever possible.')
add_heading('References', 3)
for x in ['FastAPI documentation – https://fastapi.tiangolo.com/', 'React documentation – https://react.dev/', 'Vite documentation – https://vite.dev/', 'SymPy documentation – https://docs.sympy.org/', 'OpenAI API documentation – https://platform.openai.com/docs/', 'GitHub Actions documentation – https://docs.github.com/actions']: add_bullet(x)

# Save
doc.core_properties.title = 'HARVIX – AI Coding & Mathematics Assistant Internship Report'
doc.core_properties.subject = 'Internship report for the HARVIX project'
doc.core_properties.author = 'Mohaneshwari P'
doc.core_properties.keywords = 'HARVIX, AI assistant, React, FastAPI, SymPy, internship report'
doc.save(OUT)
print(OUT)
