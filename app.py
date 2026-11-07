
import re
import math
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="RAG Academy | Learn by Doing", page_icon="🧠", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {background:#0b1020;color:#eef2ff}
.block-container{max-width:1250px;padding-top:1.5rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#111827}
.hero{padding:2rem 2.2rem;border-radius:20px;background:linear-gradient(120deg,#172554,#312e81,#581c87);border:1px solid #6554bd}
.hero h1{color:#fff;font-size:2.6rem}
.hero p{color:#e0e7ff;font-size:1.08rem}
.tile{background:#151f33;border:1px solid #334155;border-radius:15px;padding:1rem 1.1rem;min-height:135px}
.tile h3{color:#c4b5fd;margin-top:0}
.codebox{background:#101827;border:1px solid #334155;border-radius:12px;padding:1rem}
div.stButton>button{background:#6d28d9;color:white;border:1px solid #8b5cf6;border-radius:9px;font-weight:600}
div.stButton>button:hover{background:#7c3aed;color:white}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
def words(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())

def make_chunks(text, size, overlap):
    tokens = re.findall(r"\S+", text)
    if not tokens:
        return []
    size = max(1, int(size))
    overlap = min(max(0, int(overlap)), size - 1)
    step = size - overlap
    result = []
    for start in range(0, len(tokens), step):
        result.append(" ".join(tokens[start:start + size]))
        if start + size >= len(tokens):
            break
    return result

def keyword_retrieve(query, passages, k=3):
    """Simple transparent baseline: ranks passages by query-word overlap."""
    q = set(words(query))
    ranked = []
    for passage in passages:
        p = set(words(passage))
        score = len(q & p) / max(1, len(q))
        ranked.append((score, passage))
    return sorted(ranked, reverse=True)[:k]

def mark_done(key):
    st.session_state.setdefault("completed", set())
    st.session_state["completed"].add(key)

def lesson_header(number, title, goal, minutes):
    st.caption(f"MODULE {number}  •  {minutes} MINUTES")
    st.title(title)
    st.info("🎯 Learning goal: " + goal)

def code_task(title, instruction, code, blank_label, answer, explanation, output):
    st.markdown(f"### 💻 Code mission: {title}")
    st.write(instruction)
    st.code(code, language="python")
    entry = st.text_input(blank_label, key=f"blank_{title}")
    if st.button("Check my code", key=f"check_{title}"):
        cleaned = entry.strip().replace('"', "'")
        expected = answer.strip().replace('"', "'")
        if cleaned == expected:
            st.success("Correct! You filled the missing code.")
            st.write("**Why it works:** " + explanation)
            st.code(output, language="text")
            mark_done(title)
        else:
            st.error("Not quite. Try again. Hint: " + explanation.split(".")[0] + ".")

SAMPLE_DOC = """University Placement Handbook
Internship applications are submitted through the university career portal.
Applicants should upload an updated resume and their latest academic transcript.
Students must complete the academic credits required by the recruiting company.
Each company may publish additional eligibility requirements.
The placement process may include an aptitude test, technical interview and HR discussion.
Students should contact the placement office if they need help with the application process.
The exact application deadline is announced separately by each recruiting company.
"""

# ---------- NAV ----------
modules = [
    "🏠 Home",
    "1. RAG in real life",
    "2. Explore the pipeline",
    "3. Chunking code lab",
    "4. Embeddings made simple",
    "5. Search & retrieval lab",
    "6. Build a mini RAG app",
    "7. Debug the RAG system",
    "8. Final challenge & quiz",
]

st.sidebar.title("🧠 RAG ACADEMY")
st.sidebar.caption("Learn it. Code it. Test it.")
page = st.sidebar.radio("YOUR LEARNING PATH", modules)
done = st.session_state.get("completed", set())
st.sidebar.divider()
st.sidebar.metric("Missions completed", f"{len(done)}/5")
st.sidebar.progress(min(len(done)/5, 1.0))
st.sidebar.caption("Designed as a 45-minute self-learning lesson")
st.sidebar.caption("Tip: Try the code before reading the hint.")

# ---------- HOME ----------
if page == "🏠 Home":
    st.markdown("""
    <div class="hero">
      <h1>RAG Academy 🧠</h1>
      <p>Build an AI assistant that can find answers inside documents.</p>
      <p><b>Learn → Experiment → Complete code → Run → Reflect</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns(3)

    for col, title, body in [
        (a,"📚 Learn","Short explanations, diagrams and everyday examples."),
        (b,"⌨️ Code","Fill in missing Python lines and check your answer."),
        (c,"🚀 Build","Upload a PDF, retrieve evidence and inspect the result.")
    ]:
        with col:
            st.markdown(
                f'<div class="tile"><h3>{title}</h3><p>{body}</p></div>',
                unsafe_allow_html=True
            )

    st.subheader("Your 45-minute learning path")

    rows = [
        ("1","RAG in real life","Understand the problem RAG solves","5 min"),
        ("2","Explore the pipeline","Follow a question through the system","5 min"),
        ("3","Chunking code lab","Split text by writing one missing line","7 min"),
        ("4","Embeddings made simple","Understand vectors with a visual analogy","5 min"),
        ("5","Search & retrieval lab","Rank passages and complete retrieval code","7 min"),
        ("6","Build a mini RAG app","Ask questions about sample text or a PDF","8 min"),
        ("7","Debug the RAG system","Find and repair common mistakes","4 min"),
        ("8","Final challenge & quiz","Show what you learned","4 min"),
    ]

    for n,title,desc,t in rows:
        st.markdown(f"**{n}. {title}** · {t}  \n{desc}")

    st.success("Start with **1. RAG in real life** in the sidebar.")

# ---------- INTRO ----------
elif page == "1. RAG in real life":
    lesson_header(
        "01",
        "RAG in real life",
        "Explain why an AI assistant may need to search your documents before answering.",
        "5"
    )

    st.write(
        "Imagine asking a new student: **“What is my university's internship "
        "application process?”** The student may not know your private placement handbook."
    )

    x,y = st.columns(2)

    with x:
        st.markdown("### 🤖 LLM without RAG")
        st.warning("The model may guess because the handbook was not provided.")
        st.write("It has language skills, but it may not have your latest private information.")

    with y:
        st.markdown("### 📚 LLM with RAG")
        st.success("The app searches the handbook, finds relevant passages and gives them to the model.")
        st.write("The answer can be grounded in evidence and linked to a source.")

    with st.expander("Important: does RAG guarantee a correct answer?"):
        st.write(
            "No. It can retrieve the wrong passage, miss important information, "
            "or the language model can misunderstand the evidence. We must inspect sources and test the system."
        )

    st.subheader("Quick check")

    answer = st.radio(
        "What does RAG add to a language-model application?",
        [
            "A way to retrieve relevant external information",
            "A faster computer processor",
            "A replacement for all databases"
        ],
        key="intro_q"
    )

    if st.button("Check answer",key="intro_btn"):
        if answer.startswith("A way"):
            st.success("Correct! Retrieval supplies useful external context.")
            mark_done("intro")
        else:
            st.error("Try again. Think about where the assistant gets information it was not given.")

# ---------- PIPELINE ----------
elif page == "2. Explore the pipeline":
    lesson_header(
        "02",
        "Explore the RAG pipeline",
        "Put the seven main stages in the right order and understand each stage.",
        "5"
    )

    stages = [
        ("1. Load documents","Read files such as PDFs and extract their text.","A placement handbook is uploaded."),
        ("2. Chunk text","Split long text into smaller passages.","The handbook is divided into short sections."),
        ("3. Create embeddings","Convert each passage into a numerical vector.","Each chunk gets a vector representation."),
        ("4. Store and index","Keep vectors with their text and metadata.","The app stores chunks so it can search them."),
        ("5. Retrieve","Find passages related to the user's question.","The eligibility section is ranked highly."),
        ("6. Build context","Pass the best evidence to the language model.","The prompt includes retrieved passages and page numbers."),
        ("7. Generate answer","The model writes an answer using the supplied context.","The assistant explains the policy and cites evidence."),
    ]

    for i in range(0,7,2):
        cols = st.columns(2)
        for col,item in zip(cols,stages[i:i+2]):
            with col:
                st.markdown(
                    f'<div class="tile"><h3>{item[0]}</h3><p>{item[1]}</p><i>{item[2]}</i></div>',
                    unsafe_allow_html=True
                )
                st.write("")

    chosen = st.selectbox("Explore a stage",[s[0] for s in stages])
    current = next(s for s in stages if s[0] == chosen)

    st.info(current[1])
    st.write("**Example:** " + current[2])

    order = st.radio(
        "Which stage turns text into vectors?",
        ["Chunking","Embedding generation","Answer generation"],
        key="pipe_q"
    )

    if st.button("Check pipeline answer"):
        if order == "Embedding generation":
            st.success("Exactly. Embedding models map text to numerical vectors.")
            mark_done("pipeline")
        else:
            st.error("Hint: this stage creates numerical representations of meaning.")

# ---------- CHUNKING LAB ----------
elif page == "3. Chunking code lab":
    lesson_header(
        "03",
        "Chunking code lab",
        "Complete a small Python function and see how chunk size changes the result.",
        "7"
    )

    text = st.text_area(
        "Try this document text",
        "RAG helps an AI assistant answer questions using trusted documents. "
        "First the document is loaded. Then the text is split into chunks. "
        "Each chunk is converted into an embedding. The system searches for "
        "relevant chunks when a user asks a question. Finally, the language "
        "model uses the retrieved context to answer.",
        height=130
    )

    size = st.slider("Chunk size (words)",3,18,8)
    overlap = st.slider("Overlap (words)",0,5,2)

    st.markdown("### Your code completion")
    st.write("A chunking function moves forward by `chunk_size - overlap` words each time.")

    st.code("""words = text.split()
step = _________
chunks = []
for start in range(0, len(words), step):
    chunks.append(words[start:start + chunk_size])""",language="python")

    code_task(
        "chunk-step",
        "Fill in the missing expression. It decides how far the next chunk starts from the previous one.",
        "step = _________",
        "Missing expression",
        "chunk_size - overlap",
        "The step is chunk_size minus overlap. This makes neighbouring chunks share a few words.",
        f"step = {size - overlap}\n# The next chunk begins {size-overlap} words after the previous start."
    )

    chunks = make_chunks(text,size,overlap)

    st.subheader("Live chunk preview")

    m1,m2,m3 = st.columns(3)
    m1.metric("Words",len(text.split()))
    m2.metric("Chunks",len(chunks))
    m3.metric("Words of overlap",overlap)

    for i,ch in enumerate(chunks,1):
        with st.expander(f"Chunk {i} · {len(ch.split())} words",expanded=(i==1)):
            st.write(ch)

    st.caption(
        "This learning lab uses word-based chunking for clarity. "
        "Production systems may split by tokens, sentences, headings or document structure."
    )

# ---------- EMBEDDINGS ----------
elif page == "4. Embeddings made simple":
    lesson_header(
        "04",
        "Embeddings made simple",
        "Understand how text can be represented by numbers for similarity search.",
        "5"
    )

    st.write(
        "Think of an embedding as a set of coordinates that helps a computer "
        "compare the meaning of sentences. The vector is not a dictionary definition; "
        "it is a learned numerical representation."
    )

    examples = [
        ("How do I apply for an internship?",[0.82,0.14,0.55]),
        ("What is the internship application process?",[0.79,0.18,0.51]),
        ("How do I cook rice?",[0.08,0.91,0.12]),
    ]

    st.subheader("Illustrative 3-number vectors")
    st.caption("These numbers are made-up teaching examples, not outputs from a real embedding model.")

    for sentence,vec in examples:
        st.write("**" + sentence + "**")
        st.code(f"[{vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f}]")

    st.write(
        "The first two sentences discuss similar topics, so a well-trained "
        "embedding model may place their vectors closer together than the cooking sentence."
    )

    st.subheader("Complete the code")

    st.code("""# A text embedding is a numerical _________
embedding = model.encode(sentence)""",language="python")

    code_task(
        "embedding-word",
        "What is the usual name for the numerical list that represents text?",
        "embedding = model.encode(sentence)",
        "Missing word",
        "vector",
        "An embedding is a vector: an ordered list of numerical values.",
        "embedding = model.encode(sentence)\n# Example output shape: (384,) for one sentence with a 384-dimensional model."
    )

    q = st.radio(
        "Are embedding values probabilities?",
        ["Yes, always","No, they are coordinates/features in a learned vector space"],
        key="emb_q"
    )

    if st.button("Check embedding concept"):
        if q.startswith("No"):
            st.success("Correct. Similarity scores are not automatically probabilities.")
            mark_done("embedding")
        else:
            st.error("Not quite. An embedding is a vector representation, not a probability distribution.")

# ---------- SEARCH ----------
elif page == "5. Search & retrieval lab":
    lesson_header(
        "05",
        "Search & retrieval lab",
        "Rank candidate passages and complete the key retrieval line.",
        "7"
    )

    passages = [
        "Internship applications are submitted through the university career portal.",
        "Students must upload an updated resume and academic transcript.",
        "The library closes at 8 PM on weekdays.",
        "Each recruiting company publishes its own eligibility requirements.",
    ]

    query = st.text_input(
        "Ask a question",
        "Where do I submit my internship application?"
    )

    st.code("""query_words = set(query.lower().split())
passage_words = set(passage.lower().split())
overlap = len(query_words & passage_words)""",language="python")

    code_task(
        "retrieval-overlap",
        "Fill in the missing Python operator that finds words present in both sets.",
        "overlap = len(query_words ___ passage_words)",
        "Missing operator",
        "&",
        "The ampersand performs set intersection: it returns items shared by both sets.",
        "overlap = len(query_words & passage_words)\n# This counts the words shared by the query and passage."
    )

    if st.button("Run simple retrieval"):
        results = keyword_retrieve(query,passages,4)

        st.subheader("Ranked passages")

        for rank,(score,p) in enumerate(results,1):
            st.write(f"**{rank}. Match score: {score:.2f}**")
            st.write(p)
            st.progress(min(score,1.0))

        st.caption(
            "This is a transparent keyword-overlap baseline, not semantic vector search. "
            "Real embedding retrieval can match related meanings even when exact words differ."
        )

        mark_done("retrieval")

# ---------- MINI RAG APP ----------
elif page == "6. Build a mini RAG app":
    lesson_header(
        "06",
        "Build a mini RAG app",
        "Ask questions about a sample placement handbook or upload a text-based PDF.",
        "8"
    )

    st.write(
        "This beginner-friendly version uses transparent keyword overlap for retrieval. "
        "It shows evidence passages instead of pretending an LLM generated an answer."
    )

    uploaded = st.file_uploader(
        "Optional: upload a text-based PDF",
        type=["pdf"]
    )

    source_text = SAMPLE_DOC
    source_name = "Sample Placement Handbook"

    if uploaded:
        try:
            reader = PdfReader(uploaded)
            extracted = []

            for pno,p in enumerate(reader.pages,1):
                txt = p.extract_text() or ""
                if txt.strip():
                    extracted.append(f"[Page {pno}] {txt}")

            source_text = "\n".join(extracted)
            source_name = uploaded.name

            if not source_text.strip():
                st.warning(
                    "No selectable text found. Scanned PDFs need OCR; use the sample handbook for now."
                )
                source_text = SAMPLE_DOC
                source_name = "Sample Placement Handbook"

        except Exception as e:
            st.error(f"Could not read PDF: {e}")
            source_text = SAMPLE_DOC

    st.success(f"Knowledge source: {source_name}")

    chunks = make_chunks(source_text,70,12)

    question = st.text_input(
        "Ask the handbook a question",
        "Where do students submit internship applications?"
    )

    if st.button("Find evidence",type="primary"):
        ranked = keyword_retrieve(question,chunks,3)

        st.subheader("Retrieved evidence")

        if ranked and ranked[0][0] > 0:
            for i,(score,passage) in enumerate(ranked,1):
                st.write(f"**Passage {i} · keyword match {score:.2f}**")
                st.info(passage)

            st.subheader("Evidence-based response")
            st.write("The retrieved handbook text says: " + ranked[0][1])

            st.caption(
                "This is an extractive demonstration. It is not an LLM-generated summary."
            )
        else:
            st.warning(
                "I could not find matching evidence. The assistant should not invent an answer."
            )

        mark_done("mini-rag")

    with st.expander("What would a production RAG app add?"):
        st.write(
            "A production system would use a suitable embedding model, a vector index, "
            "careful chunk metadata, a prompt to ground the answer, source citations, and evaluation tests."
        )

# ---------- DEBUG ----------
elif page == "7. Debug the RAG system":
    lesson_header(
        "07",
        "Debug the RAG system",
        "Diagnose common mistakes and choose the best repair.",
        "4"
    )

    cases = [
        (
            "The uploaded PDF is scanned and text extraction returns nothing.",
            ["Increase chunk overlap","Use OCR to read text from page images","Increase top_k"],
            1,
            "OCR converts page images into text that can be processed."
        ),
        (
            "A chunk combines unrelated policy sections.",
            ["Try smaller or structure-aware chunks","Ask the model to guess","Remove the document"],
            0,
            "Better chunk boundaries preserve topic coherence."
        ),
        (
            "The assistant invents a deadline that is not in the document.",
            ["Tell it to make a reasonable guess","Require it to say when evidence is missing","Hide retrieved passages"],
            1,
            "A grounded assistant should abstain when the source does not contain the answer."
        ),
    ]

    for i,(case,options,correct,why) in enumerate(cases):
        st.markdown(f"### Bug {i+1}")
        st.write(case)

        choice = st.radio(
            "Choose the repair",
            options,
            key=f"debug_{i}"
        )

        if st.button("Fix this bug",key=f"debug_btn_{i}"):
            if choice == options[correct]:
                st.success("Bug fixed! " + why)
                mark_done(f"debug{i}")
            else:
                st.error("Not quite. Hint: think about which pipeline stage caused the problem.")

        st.divider()

# ---------- FINAL CHALLENGE & MCQ ----------
elif page == "8. Final challenge & quiz":
    lesson_header(
        "08",
        "Final challenge & quiz",
        "Apply the pipeline to a university placement assistant and check your understanding.",
        "4"
    )

    st.subheader("Your final mini-project challenge")

    st.write(
        "A university wants an assistant that answers questions using its placement handbook. "
        "Complete this plan:"
    )

    quiz_questions = [
        {
            "question": "1. What should happen first in the RAG pipeline?",
            "options": [
                "Generate an answer",
                "Load the handbook and extract its text",
                "Ask the LLM to guess",
            ],
            "correct": "Load the handbook and extract its text",
        },
        {
            "question": "2. What helps preserve nearby context across chunk boundaries?",
            "options": [
                "Chunk overlap",
                "Temperature",
                "A larger screen"
            ],
            "correct": "Chunk overlap",
        },
        {
            "question": "3. What should happen if no evidence answers the question?",
            "options": [
                "Invent an answer",
                "Say the document does not provide the answer",
                "Cite a random page",
            ],
            "correct": "Say the document does not provide the answer",
        },
    ]

    st.subheader("Knowledge-check MCQ")

    # MCQ answers are deliberately not marked or revealed.
    for i, question in enumerate(quiz_questions):
        st.write(f"**{question['question']}**")

        st.radio(
            "Choose one answer:",
            question["options"],
            key=f"final_mcq_{i}",
            index=None,
        )

    if st.button("Submit quiz",type="primary",key="submit_final_quiz"):

        unanswered = [
            i for i in range(len(quiz_questions))
            if st.session_state.get(f"final_mcq_{i}") is None
        ]

        if unanswered:
            st.warning("Please answer all three questions before submitting.")

        else:
            score = sum(
                st.session_state.get(f"final_mcq_{i}") == question["correct"]
                for i, question in enumerate(quiz_questions)
            )

            st.metric("Your score",f"{score}/{len(quiz_questions)}")

            if score == len(quiz_questions):
                mark_done("challenge")

    st.divider()

    st.subheader("Reflection")

    reflection = st.text_area(
        "In one or two sentences, explain how RAG is different from asking an LLM a question without documents."
    )

    if st.button("Save reflection in this session"):
        if len(reflection.strip()) > 20:
            st.success(
                "Reflection saved for this session. Be ready to explain it in your own words."
            )
        else:
            st.info("Add a little more detail so your explanation is clear.")

st.sidebar.divider()
st.sidebar.caption("RAG Academy · Learn by doing")
st.sidebar.caption("Code tasks validate a specific missing line; they do not run arbitrary code.")
