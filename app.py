from flask import Flask, request, jsonify
import ollama

app = Flask(__name__)

session = {
    "status": "inactive",
    "ingredients_detected": [],
    "actions_detected": [],
    "chef_commands": [],
    "system_responses": []
}

def check_context(user_input):
    response_context = ""
    
    if session["system_responses"]:
        last_response = session["system_responses"][-1].lower()
        if "stir" in last_response and "stirring" not in session["actions_detected"]:
            response_context += "Confirmed: You are following the stirring instruction.\n"
            session["actions_detected"].append("stirring")
    
    return response_context

@app.route("/chat", methods=["POST"])
def chat():
    global session
    
    data = request.get_json()
    user_input = data.get("message", "")
    
    if user_input.lower() == "start session":
        session = {
            "status": "active",
            "ingredients_detected": [],
            "actions_detected": [],
            "chef_commands": [],
            "system_responses": []
        }
        return jsonify({"response": "Cooking session started."})
    
    elif user_input.lower() == "close session":
        session["status"] = "inactive"
        return jsonify({"response": "Cooking session closed."})
    
    
    context_warning = check_context(user_input)
    
    
    chat_history = "\n".join(session["chef_commands"])  
    model_prompt = f"Past Commands: {chat_history}\nCurrent Question: {user_input}"
    response = ollama.chat(model="llama3:8b", messages=[{"role": "user", "content": model_prompt}])
    model_reply = response["message"]["content"]
    

    session["chef_commands"].append(user_input)
    session["system_responses"].append(model_reply)
    
    return jsonify({"response": context_warning + model_reply})

if __name__ == "__main__":
    app.run(debug=True)
