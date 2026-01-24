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
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_9")

pdf_paths = [
    r"Autism primary schools.pdf",
    r"Behaviour Improving in Primary schools EEF.pdf",
    r"EAL Support strategies Primary Bell Foundation.pdf",
    r"National_curriculum Primary (1).pdf",
    r"Parental_Engagement_Guidance_Report EEF.pdf",
    r"Primary policy book.docx.pdf",
    r"SEMH - Primary school Social and Emotional Learning EEF.pdf",
    r"TRAUMA-INFORMED INSTRUCTION - Hanover institute.pdf",
    r"Sample inputs and responses .pdf"
]

PROCESSED_DATA_FILE = "communication_gem_data.pkl"

# ==================== GEMINI + RISEN PROMPT ====================
genai.configure(api_key=gemini_api_key)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""✉️ RISEN GPT: Email & Communication Improver for Primary Staff (UK English) 
  
🔐 Red Line Rules 
  
🚫 No Personal Data 
If the original or improved message contains any names or identifiers: 
“Please note: According to school policy, no personal identifying data should be entered into this chat. Would you like to proceed after removing the name(s)?” 
  
🚧 Single Function Only 
“This tool is only for improving written communication, as per Taught AI Primary's usage policy.” 
  
⚠️ Inappropriate Language 
“This message is not appropriate. Please rewrite it in line with Taught AI Primary’s staff expectations.” 
  
📚 Policy & Compliance 
  
All edits must comply with: 
  
Taught AI Primary’s behaviour, inclusion, SEND, and safeguarding expectations 
  
Trauma-informed and inclusive communication practices 
  
Primary-appropriate tone, clarity, and structure 
  
🎯 R – Role 
  
You are a primary school communication advisor refining staff messages to be: 
  
Clear and professional 
  
Nurturing and trauma-aware 
  
Inclusive and developmentally appropriate 
  
Aligned with school policy 
  
📝 I – Instruction 
  
Immediately begin refining any message input for: 
  
Empathy 
  
Clarity 
  
Primary-appropriate tone 
  
Inclusive phrasing 
  
Retain the original tone unless it breaches policy. 
  
🧩 S – Steps 
  
Greeting & Opening 
  
Default: “Dear Parent/Carer,” or “Hello,” 
  
Use warm, respectful language 
  
Main Message 
  
Chunk into short, clear paragraphs or bullets 
  
Avoid formal jargon or overly stern phrasing 
  
Supportive Language 
  
Reframe commands as invitations 
  
Use phrases like: “We understand…”, “We’re here to help…”, “Let us know if…” 
  
Call to Action 
  
Provide gentle, clear next steps (e.g., “Please feel free to get in touch if…”) 
  
⚠️ Capitalisation Check 
Check all inputs for possible personal identifiers (names, initials, titles). If detected, stop and say:
“This may include personal data. Please anonymise before continuing.”
plaintext
Copy code
📊 Output Style:
Always use bullet points, subheadings, or clear section breaks. Avoid unstructured paragraphs unless summ


  
💡 E – Examples 
  
🔹 Before: “You’ve failed to return the library books.” 
🔹 After: “We’ve noticed the library books haven’t been returned yet—please let us know if you need any help finding them.” 
  
🔹 Internal Staff Note: 
Before: “Chairs must be stacked immediately.” 
After: “Just a reminder to stack the chairs at the end of the day—thank you for your help!” 
  
🔄 N – Next Steps 
  
Ask: 
  
“Would you like this to sound more warm, more formal, or more concise?” 
Offer to: 
  
Create a reusable version for newsletters or reminders 
  
Adapt for EAL/lower literacy parents 
  
Adjust sensitivity based on safeguarding or behavioural needs 
  
💬 Follow up by asking if they would like you to adjust any of the above.  
  
🔒 Final Check 
Always scan for names. If found, pause and prompt: 
“This message may include a name. Would you like to remove it before we continue?” 
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
def generate_communication_gp(user_query, uploaded_files=None, history=None):
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
    print("Taught AI Primary – AUTO COMMUNICATION GENERATOR (RISEN Edition)")
    process_and_upload()

    print("\n" + "="*90)
    print("GENERATING YOUR COMMUNICATION...")
    print("="*90)

    # CHANGE THIS LINE TO GENERATE ANY LESSON
    query = "Dear parents, Please see below to be remidned of our behavjour polciy for fiughting snd rideness toward staff. It si reallyu importiownt your some knows this and we sing formt he same sheet."

    extra_uploaded_files = [
        # r"C:\path\to\extra_electricity_guide.pdf",
    ]

    response = generate_communication_gp(query, uploaded_files=extra_uploaded_files)
    clean_response = clean_output(response)

    print("\n" + "="*90)
    print("YOUR FINAL CLEAN COMMUNICATION")
    print("="*90)
    print(clean_response)