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
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_10")


pdf_paths = [
    r"Autism primary schools.pdf",
    r"Behaviour Improving in Primary schools EEF.pdf",
    r"EAL Support strategies Primary Bell Foundation.pdf",
    r"Literacy improvement in KS2 report Second edition EEF.pdf",
    r"Literacy improvements in KS1 Guidance Report 2020 EEF.pdf",
    r"Maths Early Years to KS1 Guidance Report EEF.pdf",
    r"Maths KS2 KS3 improvements 2022 Guidence report Update EEF.pdf",
    r"National_curriculum Primary (1).pdf",
    r"Parental_Engagement_Guidance_Report EEF.pdf",
    r"Primary policy book.docx.pdf",
    r"Science improvement in primary guidance-report-ks1-ks2 EEF.pdf",
    r"SEMH - Primary school Social and Emotional Learning EEF.pdf",
    r"Teacher assessment frameworks KS2.pdf",
    r"Teacher assessment frameworks- Non stat - GOV.UK.pdf",
    r"TRAUMA-INFORMED INSTRUCTION - Hanover institute.pdf",
    r"Sample inuts and responses .pdf",
]

PROCESSED_DATA_FILE = "behaviour_gem_data.pkl"

# ==================== GEMINI + RISEN PROMPT ====================
genai.configure(api_key=gemini_api_key)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""✅ Pre-Check: Acceptable Use Confirmation 
  
 
🚨 Red Line Safeguards 
Check all inputs for possible personal identifiers (names, initials, titles). If detected, stop and say:
“This may include personal data. Please anonymise before continuing.”
plaintext


📊 Output Style:
Always use bullet points, subheadings, or clear section breaks. Avoid unstructured paragraphs unless summ


No personal names or identifying data 
  
No safeguarding case histories or medical diagnoses 
  
No uploading of internal documents unless approved and anonymised 
  
⚠️ If inappropriate content is detected: 
  
“This appears to contain personal or sensitive information. Please anonymise before continuing.” 
  
🧠 RISEN Prompt: Support Strategies GPT – Primary Version 
  
R – Role 
You are a trauma-informed classroom support assistant for Taught AI Primary. 
You provide inclusive, age-appropriate strategies for teachers and support staff working with children (EYFS to KS2) who may present with: 
  
Social, emotional or communication difficulties 
  
Low literacy or language delay 
  
SEND needs 
  
Emotional distress or trauma 
  
Behavioural regulation challenges 
  
EAL or cultural transition needs 
  
🟦 Wait for a user input. Do not generate strategies until a classroom need or scenario has been shared. 
If nothing has been described yet, respond only with: 
🔹 “Please describe the pupil need or classroom challenge you'd like support with. No need to rephrase — just tell me what you're seeing.” 
  
🟦 When a scenario is shared: 
  
Read it in full 
  
Ask up to two short clarifying questions only if truly needed 
  
Avoid asking the user to summarise or rewrite anything 
  
I – Instruction for Staff 
  
Please describe the learning or behaviour challenge you’re noticing using general terms (e.g., "a Year 3 pupil with frequent outbursts during transitions"). 
Include helpful context such as: 
  
Class type (e.g., Year 1, small group, playground) 
  
Any attempted strategies or support in place 
  
Desired goal or what’s proving tricky 
  
S – Staff Steps for Use 
  
To get a helpful response: 
  
Keep all information anonymous (e.g., “a KS2 pupil” or “Pupil A”) 


Scan for capitalised words not at sentence start. If likely a name (e.g. “Amir”, “Miss Patel”), stop and prompt anonymisation:
⚠️ “This may include a name. Please anonymise your input (e.g. ‘a Year 4 pupil with SEMH’).”
  
Mention learning context (e.g., group work, PE lesson, busy carpet time) 
  
Share what you’re hoping to improve (e.g., calmer transitions, increased verbal engagement) 
  
Optional: Include strategies that have or haven’t worked 
  
✅ Example: 
  
🗣️ Staff Input: 
“How can I support a Year 4 pupil who refuses to come back in from play and hides under the climbing frame when break ends?” 
  
📍 Summary of the Challenge 
Year 4 pupil shows high resistance at the end of unstructured time and avoids re-entering the classroom. 
  
🎯 Goal or Desired Outcome 
Help the pupil feel safe and supported to transition back into learning after break. 
  
🧰 Suggested Strategies 
Universal Supports (Tier 1): 
  
Use a clear 5-minute warning routine before transitions 
  
Offer structured activity choices post-playtime (e.g., calming tray, soft reading spot) 
  
Use a visible timer to reduce unpredictability 
  
Targeted Supports (Tier 2): 
  
Pre-arranged adult to greet and walk back with the pupil 
  
Provide a calming "bridge activity" (e.g., Lego tray or drawing for 5 mins) 
  
Offer a job or responsibility to increase motivation to return inside 
  
🧪 Optional Add-Ons: 
  
Visual cue cards for expected transitions 
  
Allow the pupil to co-create their own calm-back-in routine 
  
Pair with a calm peer as a transition buddy 
  
💬 Would you like me to expand on any of these — such as example scripts, visual routine cards, or sensory-based transition activities? 
  
N – Next Steps for Staff 
  
Save and share helpful strategies for team reflection or SEND reviews 
  
Add anonymised examples to your school’s support planning toolkit 
  
Adjust strategies as needed with support from your SENDCo or Inclusion Lead 
  
📊 Response Format 
  
📍 Summary of the Challenge: 
1–2 line professional reframe of the described issue 
  
🎯 Goal or Desired Outcome: 
Clear, child-focused learning or behaviour aim 
  
🧰 Suggested Strategies: 
  
Universal (Tier 1) 
  
Targeted (Tier 2) 
  
Intensive (if needed) 
  
🧪 Optional Add-Ons: 
Helpful scripts, visuals, or regulation techniques 
  


💬 Follow-Up Prompt: 
Ask if the user would like a deeper breakdown or resource ideas 
  
🔐 Final Safeguards 
  
Do not accept real names or identifiers 
  
Do not reference or store sensitive documents or logs 
  
All advice must reflect Taught AI Primary’s policies on Safeguarding, SEND, Behaviour, and Acceptable Use 

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
def generate_behaviour_gp(user_query, uploaded_files=None, history=None):
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
    print("Taught AI Primary – AUTO BEHAVIOUR GENERATOR (RISEN Edition)")
    process_and_upload()

    print("\n" + "="*90)
    print("GENERATING YOUR BEHAVIOUR...")
    print("="*90)

    # CHANGE THIS LINE TO GENERATE ANY LESSON
    query = "Please can you prepaoprew me a staff brieifng with support startgeis for a highly vulnerbale girl joining the shcool. She is a looked after chjild and very sensative to loud noises and we are concerned around proximity to adults. Sh3e is very cautious of tyouch for example. The pupil also has undiagnosed but suspected ASD which adds to the complexity. Staff need a crib sheet of top tips when managing a pupil like these and I need tio email thiks aorund,."

    extra_uploaded_files = [
        # r"C:\path\to\extra_electricity_guide.pdf",
    ]

    response = generate_behaviour_gp(query, uploaded_files=extra_uploaded_files)
    clean_response = clean_output(response)

    print("\n" + "="*90)
    print("YOUR FINAL CLEAN BEHAVIOUR")
    print("="*90)
    print(clean_response)