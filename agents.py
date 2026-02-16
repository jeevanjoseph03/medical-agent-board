import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from state import MedicalState

load_dotenv()

# Temperature 0.5 for creativity, but not hallucinations
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, api_key=os.getenv("GROQ_API_KEY"))

def diagnostician_agent(state: MedicalState):
    print(f"--- 👨‍⚕️ DIAGNOSTICIAN (Revision {state.get('revision_number', 1)}) ---")
    
    symptoms = state['symptoms']
    
    # CHECK: Is this a retry?
    previous_critique = state.get('critique', '')
    
    if previous_critique and state.get('revision_number', 1) > 1:
        # RETRY MODE: Fix the mistakes
        prompt = f"""
        You are a Senior Diagnostician. 
        Your previous diagnosis was REJECTED by the Board.
        
        Symptoms: {symptoms}
        Board's Feedback: {previous_critique}
        
        Update your diagnosis. Address the feedback specifically.
        """
    else:
        # FIRST RUN MODE
        prompt = f"""
        You are a Senior Diagnostician. 
        Symptoms: {symptoms}
        Provide a concise diagnosis.
        """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    
    return {
        "diagnosis": response.content,
        "messages": [f"Diagnostician: {response.content}"],
        "revision_number": state.get("revision_number", 1) + 1
    }

def pharmacist_agent(state: MedicalState):
    print("--- 💊 PHARMACIST IS UPDATING PLAN... ---")
    diagnosis = state['diagnosis']
    
    prompt = f"""
    You are a Pharmacist. 
    Diagnosis: {diagnosis}
    Recommend a safe treatment plan. Check for contraindications.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    
    return {
        "treatment_plan": response.content,
        "messages": [f"Pharmacist: {response.content}"]
    }

def reviewer_agent(state: MedicalState):
    print("--- 🧐 REVIEWER IS EVALUATING... ---")
    
    symptoms = state['symptoms']
    diagnosis = state['diagnosis']
    treatment = state['treatment_plan']
    
    prompt = f"""
    Review this case.
    Symptoms: {symptoms}
    Diagnosis: {diagnosis}
    Treatment: {treatment}
    
    If the logic is sound and safe, output 'APPROVED'.
    If there are errors (e.g. missing symptoms, dangerous drugs), output 'REJECTED' and explain why.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    
    is_approved = "APPROVED" in response.content.upper()
    
    return {
        "critique": response.content,
        "approved": is_approved,
        "messages": [f"Reviewer: {response.content}"]
    }