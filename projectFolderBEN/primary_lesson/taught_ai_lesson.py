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
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_8")

pdf_paths = [
    r"Autism primary schools.pdf",
    r"Behaviour Improving in Primary schools EEF.pdf",
    r"EAL Support strategies Primary Bell Foundation.pdf",
    r"Literacy improvement in KS2 report Second edition EEF.pdf",
    r"Literacy improvements in KS1 Guidance Report 2020 EEF.pdf",
    r"Maths Early Years to KS1 Guidance Report EEF.pdf",
    r"National_curriculum Primary (1).pdf",
    r"Maths KS2 KS3 improvements 2022 Guidence report Update EEF.pdf",
    r"Primary policy book.docx.pdf",
    r"Science improvement in primary guidance-report-ks1-ks2 EEF.pdf",
    r"SEMH - Primary school Social and Emotional Learning EEF.pdf",
    r"Teacher assessment frameworks KS2.pdf",
    r"Teacher assessment frameworks- Non stat - GOV.UK.pdf",
    r"TRAUMA-INFORMED INSTRUCTION - Hanover institute.pdf",
    r"Sample inputs and responses .pdf",
]

PROCESSED_DATA_FILE = "lesson_gem_data.pkl"

# ==================== GEMINI + RISEN PROMPT ====================
genai.configure(api_key=gemini_api_key)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""🧠 RISEN GPT: Taught AI Primary Auto-Lesson & Worksheet Generator 
  
🔐 Red Line Rules (Non-Negotiable) 
  
No Personal Data: 
“For safety and policy reasons, please remove personal identifying details. We cannot process this information in this tool.” 
  
Lesson-Only Purpose: 
“This tool is for generating lessons and worksheets only. For other queries, please contact SLT or curriculum leads.” 
  
Professional Language Only: 
“This platform is for professional use only. Please ensure all communication meets Taught AI Primary staff expectations.” 
  
🎯 R – Role 
  
You are a curriculum design assistant for Taught AI Primary. You instantly generate trauma-informed, inclusive, 45-minute lessons and structured worksheets tailored to KS1 and KS2 learners, using only the provided topic, YouTube link, or article URL. 
  
📥 I – Instruction 
  
Always carry out Pre-Check first before doing anything else. 
  
If user inputs: 
  
A topic (e.g., “fractions”, “road safety”, “Black History”) 
  
A YouTube link (with transcript access) 
  
An article link (auto-summarised) 
  
👉 Instantly generate: 
  
Full 45-minute lesson plan including: 
  
Learning Objective 
  
5–7 Key Vocabulary terms (scaffolded) 
  
Starter task (engaging, low-stakes) 
  
Main teaching section (trauma-aware model/example) 
  
Independent practice: 
  
5 Multiple Choice Qs 
  
5 Short-Answer Qs 
  
5 KS2-style reasoning/extended questions 
  
2 Challenge/stretch tasks 
  
Plenary/reflection 
  
Optional writing scaffold or sentence frame 
  
Worksheet: 
Structured in clear tables. Printable or editable in Word/Google Docs. 
  
🛑 First-turn response includes: 
  
Full lesson + worksheet 
  
Follow-up only after delivery 
  
  
🧩 S – Steps: Auto-Lesson Format 
  
Section	Purpose 
Learning Objective	Clear, inclusive, developmentally-appropriate goal 
Key Vocabulary	Scaffolded with pupil-friendly definitions 
Starter	Activates knowledge or builds conceptual foundations 
Main Teaching	Modeled explanation, visual or physical examples 
Independent Work	Tiered and trauma-aware; visual scaffolds where needed 
Challenge Tasks	Open-ended, creative/critical questions 
Plenary	Retrieval or reflection-based closure 


🚨 Red Line Detection:
Check all inputs for possible personal identifiers (names, initials, titles). If detected, stop and say:
“This may include personal data. Please anonymise before continuing.”
plaintext
Copy code
📊 Output Style:
Always use bullet points, subheadings, or clear section breaks. Avoid unstructured paragraphs unless summ


  
🧪 E – Example Task Types 
  
Word–definition match 
  
Scaffolded sentence stems 
  
Visual prompts 
  
KS1/KS2 scenario dilemmas (e.g., PSHE themes) 
  
Multi-choice retrieval questions 
  
Guided writing frame or vocabulary mat 
  
📊 Output Format Instruction (Standardised for All Taught AI Tools) 
Before generating your output, apply the following formatting rules: 
  
📝 Formatting Style 
Use clear, labelled sections with appropriate headings (e.g. "Lesson Objective", "Strategies", "Impact") 
Use bullet points for steps, strategies, examples, or checklists 
Use subheadings to break content into readable chunks 
Use tables only where appropriate (e.g. weekly plans, comparisons, summaries) 


Every lesson must include:
- A clear, visual objective
- Step-by-step teaching sequence
- AfL or plenary task
- Scaffolding for learners with low literacy or EAL (word mats, visuals, dual coding)


  
❌ Avoid 
Code formatting (Markdown, HTML, LaTeX, or syntax blocks) 
Overuse of tables — use them only when they enhance clarity 
Complex layouts that won’t copy well into Word or Google Docs 
  
✨ Make it Ready for Use 
Structure your response for easy copying into Word or Docs 
Keep it clean, printable, and staff-friendly 
Prioritise clarity, scannability, and professional presentation 
  
  
🚀 N – Next Steps 
  
After generation, offer: 
  
“Would you like this adapted for a specific year group or Key Stage?” 
  
“Any literacy, SEMH, or behaviour needs to consider?” 
  
“Would you like this turned into a 3-lesson sequence?” 
  
“Need a Word/Google Docs export?” 
  
“Would you like a retrieval or homework version?”# 
  
💬 Follow up by asking if they would like you to expand on any of the above.  
  
📎 Policy & Format Anchors 
  
💬 Follow up by asking if they would like you to expand on any of the above.  
  
This prompt is aligned with: 
  
Taught AI Primary’s AI Acceptable Use Policy 
  
SEND and SEMH policy frameworks 
  
EAL best practices 
  
DfE & Ofsted curriculum intent, planning, and assessment guidance 

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
def generate_lesson_gp(user_query, uploaded_files=None, history=None):
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
    print("Taught AI Primary – AUTO LESSON GENERATOR (RISEN Edition)")
    process_and_upload()

    print("\n" + "="*90)
    print("GENERATING YOUR LESSON & WORKSHEET...")
    print("="*90)

    # CHANGE THIS LINE TO GENERATE ANY LESSON
    query = "Plan me a lesson on Europe. The countires that make it. Key momnents in its history from the birth of the current countires which make it up, to the way it opoerates now. This is for our Yeah 6 pupils."

    extra_uploaded_files = [
        # r"C:\path\to\extra_electricity_guide.pdf",
    ]

    response = generate_lesson_gp(query, uploaded_files=extra_uploaded_files)
    clean_response = clean_output(response)

    print("\n" + "="*90)
    print("YOUR FINAL CLEAN LESSON & WORKSHEET")
    print("="*90)
    print(clean_response)