from langgraph.graph import StateGraph, END
from state import MedicalState
from agents import diagnostician_agent, pharmacist_agent, reviewer_agent

# --- CONDITIONAL LOGIC ---
def should_continue(state: MedicalState):
    """Return the next node to execute"""
    
    # 1. If approved, we are done.
    if state['approved']:
        print("✅ Board Approved. Case Closed.")
        return END
    
    # 2. Safety Valve: Prevent infinite loops (Max 3 retries)
    if state['revision_number'] > 3:
        print("⚠️ Max Revisions Reached. Stopping to prevent infinite costs.")
        return END
    
    # 3. Otherwise, send it back to the start
    print("❌ Board Rejected. Sending back to Diagnostician...")
    return "diagnostician"

# --- BUILD GRAPH ---
workflow = StateGraph(MedicalState)

workflow.add_node("diagnostician", diagnostician_agent)
workflow.add_node("pharmacist", pharmacist_agent)
workflow.add_node("reviewer", reviewer_agent)

workflow.set_entry_point("diagnostician")
workflow.add_edge("diagnostician", "pharmacist")
workflow.add_edge("pharmacist", "reviewer")

# THE UPGRADE: Conditional Edge
# After 'reviewer', look at 'should_continue' to decide where to go next.
workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        END: END,
        "diagnostician": "diagnostician"
    }
)

app = workflow.compile()

if __name__ == "__main__":
    print("\n🏥 AI MEDICAL BOARD INITIALIZED\n")
    symptoms = input("Enter Symptoms: ")
    
    # Initialize with revision 1
    initial_state = {
        "symptoms": symptoms, 
        "revision_number": 1,
        "approved": False,
        "messages": []
    }
    
    # Run the loop
    final_state = app.invoke(initial_state, {"recursion_limit": 10})
    
    print("\n" + "="*50)
    print(f"FINAL RESULT (After {final_state['revision_number']-1} Revisions)")
    print("="*50)
    print(f"STATUS: {'APPROVED' if final_state['approved'] else 'FAILED'}")
    print(f"DIAGNOSIS: {final_state['diagnosis']}")
    print(f"CRITIQUE: {final_state['critique']}")