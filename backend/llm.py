import google.genai as genai
import os
key=os.getenv("Gemini_API_Key") #directly from the environment variables as it is set there

client=genai.Client(api_key=key)


def build_prompt(query, context): #both string inputs
    
    return ( #this whole thing based on to the llm to give results
    "You are a helpful assistant.\n"
    "Answer ONLY using the context below.\n"
    "If the answer is not present in the context, say \"Sorry, I don't know. The relevant ans doesn't exist in your pdf :( \"\n\n"
    "Context:\n"
    + context + #the top chunks
    "\n\nQuestion:\n"
    + query#the question
    )


def generate_answer(query:str, context: str):

    if not context.strip():
        return "Relevant answer is the not present"
    
    prompt=build_prompt(query, context)

    response=client.models.generate_content(model='gemini-2.5-flash-lite', contents=prompt)
    ans=""
    if response.text: #if response generation is successful 
        ans=response.text.strip()
    
    
    return ans

#to create batch sized to send for summary genration 
def batch_chunks(chunks, batch_size=15):
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]  #gives bachteches of chunks grouped togther- list of list of chunks


def summarize_chunk_batch(chunk_batch):
    text = ""
    for i, chunk in enumerate(chunk_batch, 1):
        text += f"Chunk {i}:\n{chunk['text']}\n\n"

    prompt = f"""
Summarize EACH chunk below in 1-2 concise sentences.
Return numbered summaries matching chunk numbers.
Do not merge chunks.

{text}
"""

    response=client.models.generate_content(model='gemini-2.5-flash-lite', contents=prompt)
    ans=""
    if response.text: #if response generation is successful 
        ans=response.text.strip()

    return ans

def merge_chunks(chunks):
    batch_summaries=[]
    for chunk_batch in batch_chunks(chunks): #for every batch of chunks in the list of batches
        batch_summary=summarize_chunk_batch(chunk_batch)
        batch_summaries.append(batch_summary)

    merged_summary="\n".join(batch_summaries) #merge all the indidvidual batch summaries

    final_prompt= f"""
You are generating a high-quality document summary.

Using the summaries below, produce a coherent,
well-structured summary of the entire document.
Highlight main themes, arguments, and conclusions.


TEXT:
{merged_summary}
"""

    response=client.models.generate_content(model='gemini-2.5-flash-lite', contents=final_prompt)
    ans=""
    if response.text: #if response generation is successful 
        ans=response.text.strip()

    return ans

