import os
import pickle
import pdfplumber
import warnings
import re
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(r"E:\Rafsun\Django Project BEN\projectFolderBEN\.env")


warnings.filterwarnings("ignore")

# ==================== CONFIG ====================
gemini_api_key = os.getenv("GEMINI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_7")

pdf_paths = [
    r"Autism primary schools.pdf",
    r"Behaviour Improving in Primary schools EEF.pdf",
    r"Delivering_school_improvement_through_school_to_school_support_GOV UK May2019.pdf",
    r"EAL Support strategies Primary Bell Foundation.pdf",
    r"EEF Teaching and learning strategies  (1).pdf",
    r"guide_to_the_pupil_premium_EEF-_2024.pdf",
    r"Literacy improvement in KS2 report Second edition EEF.pdf",
    r"Literacy improvements in KS1 Guidance Report 2020 EEF.pdf",
    r"Maths Early Years to KS1 Guidance Report EEF.pdf",
    r"Maths KS2 KS3 improvements 2022 Guidence report Update EEF.pdf",
    r"National_curriculum Primary (1).pdf",
    r"OFSTED Improving_20schools.pdf",
    r"Parental_Engagement_Guidance_Report EEF.pdf",
    r"Primary Effective-Professional-Development-Guidance-Report EEF.pdf",
    r"Primary implementation a_schools_guide_to_.pdf",
    r"Primary policy book.docx.pdf",
    r"School inspection handbook - GOV.UK.pdf",
    r"Science improvement in primary guidance-report-ks1-ks2 EEF.pdf",
    r"SEMH - Primary school Social and Emotional Learning EEF.pdf",
    r"Spending guide Pupil premium EEF_evidence_brief.pdf",
    r"Teacher assessment frameworks KS2.pdf",
    r"Teacher assessment frameworks- Non stat - GOV.UK.pdf",
    r"Teacher-quality-recruitment-and-retention-lit-review-EEF.pdf",
    r"TRAUMA-INFORMED INSTRUCTION - Hanover institute.pdf",
    r"Sample inputs and responses .pdf",
]

PROCESSED_DATA_FILE = "head_gem_data.pkl"

# ==================== GEMINI + RISEN PROMPT ====================
genai.configure(api_key=gemini_api_key)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""🧠 RISEN GPT: Strategic Leadership Assistant for SLT & Headteachers 


🔐 Red Line Rules 
Red Line Detection:
Check all inputs for possible personal identifiers (names, initials, titles). If detected, stop and say:
“This may include personal data. Please anonymise before continuing.”
Plaintext


📊 Output Style:
Always use bullet points, subheadings, or clear section breaks. Avoid unstructured paragraphs unless summ


🚫 No Personal Data 
“Please note: According to school policy, no personal identifying data should be entered into this chat. Would you like to proceed after removing the name(s)?” 
  
🚧 Single Function 
“This tool is for supporting staff with school improvement plans and strategy. —please use separate tools for lesson planning or pupil-facing content.” 
  
⚠️ Inappropriate Language 
“Please rewrite this in line with the professional communication standards of Taught AI Primary.” 
  
📚 Policy & Compliance 
  
All analysis, summaries, and outputs must: 
  
Reflect Taught AI Primary’s school vision and values 
  
Align with school policy in behaviour, inclusion, safeguarding, SEND, and curriculum leadership 
  
Be informed by evidence-based practice and Ofsted’s inspection framework 
  
Use UK educational terminology and be suitable for SLT and governance-level work 
  
🎯 R – Role 
  
You are a senior strategy and leadership advisor for the Taught AI Primary SLT. You support school leaders with: 
  
Strategic improvement planning 
  
Aligning practice with national guidance and Ofsted expectations 
  
Drafting policy summaries, position statements, or SIP actions 
  
Interpreting DfE, Ofsted, EEF, and LA documents 
  
Preparing for governance or inspection 
  
Structuring professional communication (e.g., reports, letters, overviews) 
  
📝 I – Instruction for Leadership Teams 
  
Ask anonymised, strategic questions linked to planning, policy, evaluation, or evidence use. Upload or paste key documents for interpretation. 
  
⚠️ If the input includes capitalised terms that appear to be names (e.g., “Mr. Harris”, “Ben”) or mentions staff initials—pause for manual review. 
  
🧩 S – Steps for Effective Use 
  
Frame the Strategic Aim 
  
What are you trying to review, implement, prepare for, or align with? 
  
Attach or Paste Key Sources 
  
You can include excerpts from new guidance, inspection comments, LA documents, or school policies 
  
Specify Desired Output Format 
  
Do you need a summary, draft policy line, headline action plan, stakeholder wording, or briefing bullet points? 
  
Define the Audience or Context 
  
Is this for SLT review, SIP, staff training, Ofsted prep, or governor briefings? 
  
📚 Evidence-Backed Interpretation & Drafting 
  
Where applicable, RISEN GPT will cite: 
  
DfE national curriculum and assessment policy 
  
Ofsted Education Inspection Framework (EIF) and leadership expectations 
  
EEF reports (e.g., behaviour, parental engagement, curriculum) 
  
Bell Foundation and Hanover for inclusion and trauma-informed models 
  
Taught AI Primary’s internal policies (Behaviour, AI Use, SEND, Inclusion) 
  
💡 E – Example Leadership Prompts 
  
✅ “Summarise the key implications of the new DfE reading framework for our whole-school literacy plan.” 
✅ “Draft a one-paragraph vision statement on inclusion aligned with our current school values.” 
✅ “What are three evidence-based strategies we could add to our next SIP to improve attendance in KS2?” 
✅ “Can you write three bullet points for governors summarising our current approach to assessment?” 
✅ “We’ve received LA guidance on managing behaviour incidents—please summarise and check it against our behaviour policy.” 
  
📊 Output Format Instruction (Standardised for All Taught AI Tools) 
Before generating your output, apply the following formatting rules: 
  
📝 Formatting Style 
Use clear, labelled sections with appropriate headings (e.g. "Lesson Objective", "Strategies", "Impact") 
Use bullet points for steps, strategies, examples, or checklists 
Use subheadings to break content into readable chunks 
Use tables only where appropriate (e.g. weekly plans, comparisons, summaries) 
  
❌ Avoid 
Code formatting (Markdown, HTML, LaTeX, or syntax blocks) 
Overuse of tables — use them only when they enhance clarity 
Complex layouts that won’t copy well into Word or Google Docs 
  
✨ Make it Ready for Use 
Structure your response for easy copying into Word or Docs 
Keep it clean, printable, and staff-friendly 
Prioritise clarity, scannability, and professional presentation 
  
🔄 N – Next Steps for SLT Effectiveness 
  
Copy summaries and drafts into school documents or reports 
  
Use to prepare briefing notes, Ofsted responses, or governor updates 
  
Ask: “Can you adapt this into CPD slides?” or “How would this align with EIF expectations?” 
  
Build a repository of reviewed policy and practice insights.  
  
💬 Follow up by asking if they would like you to expand on any of the above. 

"""
)

# ==================== SAFE EMBEDDING WITH RETRY ====================
def get_embedding(text, retries=5):
    for attempt in range(retries):
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            if "500" in str(e) or "Internal" in str(e):
                print(f"   Google server busy... retry {attempt+1}/{retries} in 3s")
                time.sleep(3)
            else:
                print(f"   Embedding error: {e}")
                return None
    return None

# ==================== CLEAN OUTPUT FUNCTION ====================
def clean_output(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`\n]+`', '', text)
    text = re.sub(r'(\*\*|__|\*|_)(.*?)\1', r'\2', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s•*+-]*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    lines = [line.rstrip() for line in text.splitlines() if line.strip() or line == '']
    return '\n'.join(lines).strip()

# ==================== PINECONE SETUP ====================
pc = Pinecone(api_key=pinecone_api_key)
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
    pc.create_index(name=PINECONE_INDEX_NAME, dimension=768, metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"))
index = pc.Index(PINECONE_INDEX_NAME)

# ==================== PDF & UPLOAD (SAFE MODE) ====================
def extract_text_from_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return text

def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

def process_and_upload():
    if not os.path.exists(PROCESSED_DATA_FILE):
        print("Processing main knowledge base PDFs...")
        data = {}
        for p in pdf_paths:
            if os.path.exists(p):
                name = os.path.basename(p)
                print(f"→ {name}")
                text = extract_text_from_pdf(p)
                data[name] = split_text(text)
        with open(PROCESSED_DATA_FILE, "wb") as f:
            pickle.dump(data, f)
    else:
        print("Loading cached PDF chunks from disk...")
        with open(PROCESSED_DATA_FILE, "rb") as f:
            data = pickle.load(f)

    # === SMART CHECK: Which files are actually missing in Pinecone? ===
    missing_files = []
    for filename in data.keys():
        # Query Pinecone: does this file have at least 1 vector?
        try:
            results = index.query(
                vector=[0.0]*768,
                top_k=1,
                filter={"source": {"$eq": filename}},
                include_metadata=True
            )
            if not results.matches:
                missing_files.append(filename)
        except:
            missing_files.append(filename)  # if error, assume missing

    if not missing_files:
        print("All 14 PDFs are already in Pinecone! Skipping upload.")
        return

    print(f"Found {len(missing_files)} missing/scanned PDFs → uploading now:")
    for f in missing_files: print(f"   → {f}")

    # === Upload ONLY the missing ones (safe batching + retry) ===
    vectors = []
    total_chunks = sum(len(data[f]) for f in missing_files)
    count = 0

    for filename in missing_files:
        chunks = data[filename]
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:
                continue
            emb = get_embedding(chunk)
            if emb is None:
                time.sleep(2)
                emb = get_embedding(chunk)  # retry once
            if emb is None:
                continue
            vectors.append((f"{filename}_{i}", emb, {"text": chunk, "source": filename}))
            count += 1
            print(f"\r   Progress: {count}/{total_chunks} chunks", end="")

            if len(vectors) >= 50:
                index.upsert(vectors=vectors)
                vectors = []
                time.sleep(0.5)

    if vectors:
        index.upsert(vectors=vectors)

    print(f"\nSUCCESS! All missing PDFs uploaded.")
    print("Your knowledge base is now 100% complete (14/14).")

# ==================== LESSON GENERATOR ====================
def generate_head_gp(user_query, uploaded_files=None, history=None):
    if history is None: history = []
    if uploaded_files is None: uploaded_files = []

    uploaded_context = ""
    for file_path in uploaded_files:
        if os.path.exists(file_path):
            print(f"Reading uploaded file: {os.path.basename(file_path)}")
            text = extract_text_from_pdf(file_path)
            if text.strip():
                uploaded_context += f"\n\n=== UPLOADED FILE: {os.path.basename(file_path)} ===\n{text}"

    q_emb = get_embedding(user_query)
    results = index.query(vector=q_emb, top_k=8, include_metadata=True)
    pinecone_context = "\n\n".join([m.metadata["text"] for m in results.matches])

    messages = [
        {"role": "user", "parts": [{"text": f"""
USER REQUEST:
{user_query}

RELEVANT KNOWLEDGE FROM DATABASE:
{pinecone_context.strip() or "None found."}

ADDITIONAL UPLOADED DOCUMENTS:
{uploaded_context.strip() or "None provided."}
        """}]}
    ]

    for h in history[-10:]:
        role = "user" if h["role"] == "user" else "model"
        messages.append({"role": role, "parts": [{"text": h["content"]}]})

    reply = chat_model.generate_content(
        messages,
        generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=6000)
    )
    return reply.text

# ==================== RUN ====================
if __name__ == "__main__":
    print("Taught AI Primary – AUTO HEAD GENERATOR (RISEN Edition)")
    process_and_upload()

    print("\n" + "="*90)
    print("GENERATING YOUR HEAD...")
    print("="*90)

    # CHANGE THIS LINE TO GENERATE ANY LESSON
    query = "I need a school attendance improvment plan. This needs to align with our values and policies, while putting greater pressure on parents who it seems enable absenteeism. The plan should be over three terms, and staged 1,2,3. We are employing an attendance mentor who can wrk directly with families aned even do home visits and bring kigs to schools in the extreme cases, but obviously I need to manage their workload. Please can you draft this police for me."

    extra_uploaded_files = [
        # r"C:\path\to\extra_electricity_guide.pdf",
    ]

    response = generate_head_gp(query, uploaded_files=extra_uploaded_files)
    clean_response = clean_output(response)

    print("\n" + "="*90)
    print("YOUR FINAL CLEAN HEAD")
    print("="*90)
    print(clean_response)