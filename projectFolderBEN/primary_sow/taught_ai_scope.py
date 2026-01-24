# =====================================================
# TAUGHT AI PRIMARY – SCHEME OF WORK GENERATOR (RISEN)
# Query hard-coded + uploaded_files support
# =====================================================

import os
import pickle
import pdfplumber
import warnings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
import re
import time
from dotenv import load_dotenv

load_dotenv(r"E:\Rafsun\Django Project BEN\projectFolderBEN\.env")


warnings.filterwarnings("ignore")

# ==================== CONFIG ====================
gemini_api_key = os.getenv("GEMINI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_12")

pdf_paths = [
    r"Autism primary schools.pdf",
    r"Behaviour Improving in Primary schools EEF.pdf",
    r"EAL Support strategies Primary Bell Foundation.pdf",
    r"Literacy improvement in KS2 report Second edition EEF.pdf",
    r"Literacy improvements in KS1 Guidance Report 2020 EEF.pdf",
    r"Maths Early Years to KS1 Guidance Report EEF.pdf",
    r"Maths KS2 KS3 improvements 2022 Guidence report Update EEF.pdf",
    r"National_curriculum Primary (1).pdf",
    r"Primary policy book.docx.pdf",
    r"Science improvement in primary guidance-report-ks1-ks2 EEF.pdf",
    r"SEMH - Primary school Social and Emotional Learning EEF.pdf",
    r"Teacher assessment frameworks KS2.pdf",
    r"Teacher assessment frameworks- Non stat - GOV.UK.pdf",
    r"TRAUMA-INFORMED INSTRUCTION - Hanover institute.pdf",
    r"Sample input and responses .pdf",
]

PROCESSED_DATA_FILE = "scope_gem_data.pkl"

# ==================== GEMINI + RISEN PROMPT ====================
genai.configure(api_key=gemini_api_key)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""🧠 RISEN Prompt: Scheme of Work Generator – Taught AI Primary Edition  
 
 
🎯 R – Role 
You are a specialist curriculum designer for Taught AI Primary, skilled in designing inclusive, sequenced, evidence-informed schemes of work for Key Stage 1 and Key Stage 2. Your outputs are aligned with the Ofsted EIF, promote cognitive retention, and meet the developmental needs of primary-aged learners. 
 
🎯 I – Intent 
You will generate a bespoke, age-appropriate Scheme of Work aligned with the user’s chosen subject, year group, and context. All outputs must reflect the Intent–Implementation–Impact framework and support inclusive practice, cultural capital, and knowledge retention. 
 
🎯 S – Structure 
Ask these setup questions first: 
What is the subject and topic? 
What is the year group or key stage? 
What is the level? (Early Years, KS1, KS2, 11+) 
What is the duration of the unit? (e.g. half-term, full term) 
Is this for mainstream, alternative provision, or SEND learners? 
Are there any inclusion priorities? (e.g. EAL, ADHD, SEMH, low literacy) 
Would you like to include any of the following: 
✅ 11+ exam preparation 
✅ Catch-up for lower prior attainers 
✅ Real-life applications 
✅ Embedded literacy or numeracy 
 
🎯 E – Evidence & Impact 
Design your scheme using: 
Ofsted EIF principles (intent, implementation, impact) 
EEF guidance (e.g. scaffolding, retrieval, oracy, inclusion) 
Bell Foundation and other SEND/EAL-inclusive strategies 
Trauma-informed and developmentally appropriate pedagogy 
 
📊 Output Format: 
The weekly plan must be presented in a clear table with the following columns: 
Week 
Lesson 
Topic 
Learning Objective 
Key Activities 
Resources 
Assessment (formative/summative) 
Additionally, include: 
Unit Title and Overview 
Curriculum Intent 
Implementation Plan (summarised) 
Impact & Assessment strategy 
Inclusive Strategies & Support 
 
📝 Formatting Style 
Use clear headings and sections 
Use bullet points for steps and strategies 
Use tables where appropriate (especially for weekly lesson planning) 
Avoid Markdown or code formatting 
 
❌ Avoid 
Personal or identifiable data 
Overuse of tables outside of planning structure 
Complex layouts that don’t copy well to Word/Google Docs 

Always include:
- Subject-specific skills progression (e.g. sentence structure, number fluency)
- Literacy/numeracy links in **every lesson**, especially for vulnerable learners
- Differentiation examples (SEND, EAL, stretch tasks) per week

🚨 Red Line Detection:
Check all inputs for possible personal identifiers (names, initials, titles). If detected, stop and say:
“This may include personal data. Please anonymise before continuing.”
plaintext
Copy code
📊 Output Style:
Always use bullet points, subheadings, or clear section breaks. Avoid unstructured paragraphs unless summ

 
✨ Ready for Use 
Ensure it’s: 
Clean and printable 
Easy to copy into Word/Docs 
Clear, readable, and staff-friendly 
 
🎯 N – Next Steps 
Prompt at the end: 
“Would you like to generate another scheme of work, or adapt this one for a different learner group or level?” 
 “Would you like me to expand any part of the scheme (e.g. formative assessment, resources, or inclusive strategies)?” 
"""
)
def clean_output(text: str) -> str:
    """
    Cleans Gemini output for perfect copy-paste into Word/Docs.
    Removes:
    - Markdown bold/italics (**text**, __text__, *text*, _text_)
    - Headings (##, ###, etc.)
    - Code blocks (```...```)
    - Backticks (`code`)
    - Extra asterisks, hashes, dashes used as bullets
    - Multiple blank lines
    - Leading/trailing whitespace
    """
    if not text:
        return ""

    # 1. Remove code blocks (```...```) and their content
    text = re.sub(r'```[\s\S]*?```', '', text)

    # 2. Remove inline code (`code`)
    text = re.sub(r'`[^`\n]+`', '', text)

    # 3. Remove Markdown bold/italics
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)   # **bold** or __bold__
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)       # *italic* or _italic_

    # 4. Remove Markdown headings (#, ##, ### etc.)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # 5. Clean up list markers that Gemini sometimes adds (•, -, *, numbers)
    text = re.sub(r'^[\s•*+-]*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)

    # 6. Remove extra asterisks or hashes used as decoration
    text = re.sub(r'(\*\*|##+)\s*', '', text)

    # 7. Collapse multiple blank lines into one
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # 8. Remove leading/trailing whitespace and extra spaces
    lines = [line.rstrip() for line in text.splitlines() if line.strip() or line == '']
    text = '\n'.join(lines).strip()

    return text

def get_embedding(text):
    result = genai.embed_content(model="models/embedding-001", content=text, task_type="retrieval_document")
    return result['embedding']

def get_chat_response(messages):
    response = chat_model.generate_content(
        messages,
        generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=6000),
        safety_settings=[{"category": c, "threshold": "BLOCK_NONE"} for c in
                         ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                          "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
    )
    return response.text

# ==================== PINECONE ====================
pc = Pinecone(api_key=pinecone_api_key)
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(name=PINECONE_INDEX_NAME, dimension=768, metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"))
index = pc.Index(PINECONE_INDEX_NAME)

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
    # Step 1: Load or create cached chunks from PDFs
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

    # Step 2: SMART CHECK – Which files are actually missing in Pinecone?
    missing_files = []
    for filename in data.keys():
        try:
            results = index.query(
                vector=[0.0] * 768,                 # dummy vector
                top_k=1,
                filter={"source": {"$eq": filename}},
                include_metadata=True
            )
            if not results.matches:                  # No vectors found for this file
                missing_files.append(filename)
        except Exception as e:
            print(f"   Query error for {filename}: {e} → treating as missing")
            missing_files.append(filename)

    if not missing_files:
        print("All PDFs already fully uploaded to Pinecone! Skipping upload.")
        return

    print(f"Found {len(missing_files)} missing or incomplete PDFs → uploading now:")
    for f in missing_files:
        print(f"   → {f}")

    # Step 3: Upload ONLY the missing files (with progress bar + safe batching)
    vectors = []
    total_chunks = sum(len(data[f]) for f in missing_files)
    uploaded = 0

    for filename in missing_files:
        chunks = data[filename]
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:
                continue
            emb = get_embedding(chunk)
            if emb is None:
                print(f"\n   Embedding failed for chunk {i} in {filename}, retrying once...")
                time.sleep(2)
                emb = get_embedding(chunk)
            if emb is None:
                print(f"   Skipping chunk {i} in {filename}")
                continue

            vectors.append((f"{filename}_{i}", emb, {"text": chunk, "source": filename}))
            uploaded += 1
            print(f"\r   Progress: {uploaded}/{total_chunks} chunks", end="")

            if len(vectors) >= 50:                     # Safe batch size
                index.upsert(vectors=vectors)
                vectors = []
                time.sleep(0.5)                         # Be gentle

    if vectors:
        index.upsert(vectors=vectors)

    print(f"\nSUCCESS! All missing PDFs uploaded.")
    print(f"Your knowledge base is now 100% complete ({len(data)}/{len(data)}).")

# ==================== MAIN GENERATOR WITH uploaded_files ====================
def generate_scheme_gp(user_query, uploaded_files=None, history=None):
    if history is None: history = []
    if uploaded_files is None: uploaded_files = []

    # Read extra uploaded files (sent to AI only, NOT stored in Pinecone)
    uploaded_context = ""
    for file_path in uploaded_files:
        if os.path.exists(file_path):
            print(f"Reading uploaded file: {os.path.basename(file_path)}")
            text = extract_text_from_pdf(file_path)
            if text.strip():
                uploaded_context += f"\n\n=== UPLOADED FILE: {os.path.basename(file_path)} ===\n{text}"

    # Retrieve from Pinecone
    q_emb = get_embedding(user_query)
    results = index.query(vector=q_emb, top_k=8, include_metadata=True)
    pinecone_context = "\n\n".join([m.metadata["text"] for m in results.matches])

    full_context = pinecone_context + uploaded_context

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

    reply = get_chat_response(messages)
    history.extend([{"role": "user", "content": user_query}, {"role": "assistant", "content": reply}])
    return reply

# ==================== RUN – QUERY IS HARD-CODED HERE ====================
if __name__ == "__main__":
    print("Taught AI Primary – Scheme of Work Generator (RISEN + File Upload)")
    process_and_upload()

    print("\n" + "="*90)
    print("GENERATING YOUR SCHEME OF WORK...")
    print("="*90)

    # CHANGE THIS LINE TO YOUR DESIRED REQUEST
    query = "I want a One month long creative SoW linked to blac history month. We will cover art, music, history and crafts as a part of this SoW which is for all of our KS1 pupils. Focus on our setting in Wandsworrth and look at our local history and famous faces."

    # OPTIONAL: ADD EXTRA PDFs HERE (they will be used only for this run)
    extra_uploaded_files = [
        # r"C:\path\to\your_extra_document.pdf",
        # r"C:\path\to\another_guide.pdf",
    ]

    response = generate_scheme_gp(query, uploaded_files=extra_uploaded_files)

# CLEAN THE OUTPUT — THIS IS THE MAGIC LINE
    clean_response = clean_output(response)
    
    print("\n" + "="*90)
    print("YOUR CLEAN SCHEME OF WORK")
    print("="*90)
    print(clean_response)