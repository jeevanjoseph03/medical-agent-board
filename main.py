from langgraph.graph import StateGraph, END
from state import MedicalState
from agents import diagnostician_agent, pharmacist_agent, reviewer_agent

# 1. Initialize the Graph
workflow = StateGraph(MedicalState)

# 2. Add the Nodes (The Workers)
workflow.add_node("diagnostician", diagnostician_agent)
workflow.add_node("pharmacist", pharmacist_agent)
workflow.add_node("reviewer", reviewer_agent)

# 3. Define the Flow (The Edges)
# Start -> Diagnostician -> Pharmacist -> Reviewer -> End
workflow.set_entry_point("diagnostician")
workflow.add_edge("diagnostician", "pharmacist")
workflow.add_edge("pharmacist", "reviewer")
workflow.add_edge("reviewer", END)

# 4. Compile the Graph
app = workflow.compile()

# 5. Run the Simulation
if __name__ == "__main__":
    print("🏥 AI MEDICAL BOARD INITIALIZED")
    symptom_input = input("Enter Patient Symptoms: ")
    
    # Initial State
    inputs = {"symptoms": symptom_input, "messages": []}
    
    # FIX: Use .invoke() instead of .stream() to get the FULL state
    # This runs the entire graph and returns the final accumulated dictionary
    final_state = app.invoke(inputs)
    
    # Print Final Report
    print("\n" + "="*50)
    print("FINAL BOARD REPORT")
    print("="*50)
    
    # Now we can access ALL parts of the state because .invoke() preserves history
    print(f"\n📋 DIAGNOSIS:\n{final_state['diagnosis']}")
    print("-" * 30)
    print(f"\n💊 TREATMENT PLAN:\n{final_state['treatment_plan']}")
    print("-" * 30)
    print(f"\n🧐 BOARD CRITIQUE:\n{final_state['critique']}")
    print("-" * 30)
    print(f"\nFINAL VERDICT: {'✅ APPROVED' if final_state['approved'] else '❌ REJECTED'}")