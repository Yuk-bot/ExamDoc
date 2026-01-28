import google.genai as genai
import os
key=os.getenv("Gemini_API_Key")

client=genai.Client(api_key=key)


def build_prompt(query, context): #both string inputs
    
    return ( #this whole thing based on to the llm to give results
    "You are a helpful assistant.\n"
    "Answer ONLY using the context below.\n"
    "If the answer is not present in the context, say \"I don't know.\"\n\n"
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
    if response.text:
        ans=response.text.strip()
    
    if not ans:
        return "Relevant ans not found"
    
    return ans