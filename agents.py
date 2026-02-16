import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from state import MedicalState

load_dotenv()

# Initialize the Brain (Llama 3)
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.5, 
    api_key=os.getenv("GROQ_API_KEY")
)

# --- AGENT 1: THE DIAGNOSTICIAN ---
def diagnostician_agent(state: MedicalState):
    print("--- 👨‍⚕️ DIAGNOSTICIAN IS THINKING... ---")
    
    # Analyze symptoms
    user_symptoms = state['symptoms']
    
    prompt = f"""
    You are a Senior Medical Diagnostician. 
    Analyze these symptoms: {user_symptoms}
    
    Provide a concise list of potential diagnoses, ranked by probability.
    Focus on clinical reasoning. Do not recommend treatments yet.
    """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    
    # We return ONLY the fields we want to update in the State
    return {
        "diagnosis": response.content,
        "messages": [f"Diagnostician: {response.content}"]
    }

# --- AGENT 2: THE PHARMACIST ---
def pharmacist_agent(state: MedicalState):
    print("--- 💊 PHARMACIST IS THINKING... ---")
    
    diagnosis = state['diagnosis']
    
    prompt = f"""
    You are a Clinical Pharmacist.
    Review this diagnosis: {diagnosis}
    
    Recommend safe, evidence-based medications or treatments.
    List contraindications (who should NOT take these drugs) and potential side effects.
    """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    
    return {
        "treatment_plan": response.content,
        "messages": [f"Pharmacist: {response.content}"]
    }

# --- AGENT 3: THE REVIEWER (The Boss) ---
def reviewer_agent(state: MedicalState):
    print("--- 🧐 REVIEW BOARD IS THINKING... ---")
    
    symptoms = state['symptoms']
    diagnosis = state['diagnosis']
    treatment = state['treatment_plan']
    
    prompt = f"""
    You are the Medical Review Board.
    1. Symptoms: {symptoms}
    2. Diagnosis: {diagnosis}
    3. Treatment: {treatment}
    
    Critique this flow. Is the diagnosis supported by symptoms? Is the treatment safe?
    If it is good, say "APPROVED". If there are risks, say "REJECTED" and explain why.
    """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    
    # Simple logic to check if approved
    is_approved = "APPROVED" in response.content.upper()
    
    return {
        "critique": response.content,
        "approved": is_approved,
        "messages": [f"Reviewer: {response.content}"]
    }