# ExamDoc – your chill AI doc buddy

okay so this is not some over-engineered enterprise monster.
this is a simple, actually useful AI tool that lets you upload docs and *interrogate them like a detective*.

ever had a 50-page PDF before an exam and thought
“yeah I’m not reading all that”

this fixes that- no generic answers like direct llms. You get answers specific to your document - 
no extra crap no out of portion methods! Just what your teacher wants

---

## what it does

you upload a file
you get a summary for your file
you ask questions
it answers like it actually read the doc (because it did lol)

supports:

* pdf
* docx
* txt

basically:
you = lazy but smart
this app = does the boring part

---

## how it works (no fluff version)

1. you upload a document
2. text gets extracted (cleaned too, because PDFs are messy af)
3. text is split into chunks
4. embeddings are created
5. your question is matched with relevant parts
6. AI gives you an answer that actually makes sense
7. summary is generated for your pdf

boom. knowledge without suffering.

---

## tech stack 

backend:

* fastapi
* langchain
* sentence-transformers
* pdfplumber

frontend:

* streamlit
* requests

ai:

* google generative ai / openai (depending on what you plug in)

---


## setup (yes you have to do this)

clone the repo:
git clone https://github.com/Yuk-bot/ExamDoc.git
cd ExamDoc

---

backend setup:

cd backend
python -m venv myenv
.\myenv\Scripts\activate
pip install -r requirements.txt

run backend:
uvicorn main:app --reload

if this doesn’t work → skill issue (jk check your errors)

---

frontend setup:

cd ../frontend
pip install -r requirements.txt

run it:
streamlit run app.py

---


---

## environment variables (don’t leak your keys pls)

create a .env file in backend:

GOOGLE_API_KEY=your_key
OPENAI_API_KEY=your_key

don’t push this to github unless you enjoy chaos

---

## limitations (aka reality check)

* scanned PDFs? yeah… not yet
  OCR coming soon - docker things uk..

* large files might be slow
  patience is a virtue

* depends on API keys
  no key = no brain

* requires exact prompts..chunking and retreival improvement under process

---

## future plans (if motivation stays alive)

* Reinforcement learning to improve bot intellegence
* better UI (current one is- just functional)
* chat memory
* fast document analysis



