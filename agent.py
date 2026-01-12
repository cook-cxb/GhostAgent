import ollama

import vision_tool

import time

def run_ghost_agent(prompt: str):

    print("\n🚀 AGENT STARTING...")

    print("👉 SWITCH TO YOUR BROWSER IN 5 SECONDS!")

    for i in range(5, 0, -1):

        print(f"{i}...", end=" ", flush=True)

        time.sleep(1)

    print("\n🎬 ACTION!")



    # This prompt tells the AI exactly how to behave
    messages = [
        {
            "role": "system", 
            "content": """You are a robotic desktop operator. You communicate ONLY through tool calls.
            
            OPERATING RULES:
            1. FIRST ACTION: Always call scan_screen({}).
            2. To interact, look at the 'ID X: label' list from the scan.
            3. Use ONLY the numeric ID. Example: click_id(id="32"). 
            4. NEVER guess IDs like 'search_1' or 'input_box'. If you don't see the number, scan again.
            5. If you want to type, you MUST click the ID first to focus.
            6. When the task is done, summarize what you did and stop.
            
            IMPORTANT: If you see 'ID 32: search', and you want to click it, your output must be a tool call for click_id with id='32'."""
        },
        {"role": "user", "content": prompt}
    ]

    # Tool definitions for Ollama

    tools = [

        {"type": "function", "function": {"name": "scan_screen", "description": "Scan screen for UI element IDs"}},

        {"type": "function", "function": {"name": "click_id", "parameters": {"type": "object", "properties": {"element_id": {"type": "string"}}}, "required": ["element_id"]}},

        {"type": "function", "function": {"name": "type_text", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}}, "required": ["text"]}}

    ]



    for step in range(15): # Max steps to prevent infinite loops

        print(f"\n--- 🧠 Step {step + 1} ---")

        

        response = ollama.chat(model="llama3.1", messages=messages, tools=tools)

        messages.append(response['message'])



        # Check if the model called a tool

        if not response['message'].get('tool_calls'):

            print(f"🏁 DONE: {response['message']['content']}")

            break



        # Execute the tool calls
# Execute the tool calls
        for tool in response['message']['tool_calls']:
            name = tool['function']['name']
            args = tool['function']['arguments']
            print(f"🛠️ Executing: {name}({args})")
            
            if name == "scan_screen":
                result = vision_tool.scan_screen()
                # If we are "blind", STOP this chain of commands immediately
                if "connected, but NO elements" in result or "ERROR" in result:
                    messages.append({"role": "tool", "content": result, "name": name})
                    print(f"⚠️ VISION GAP: Stopping current chain to retry scan.")
                    break # <--- CHANGED FROM CONTINUE TO BREAK
                                
            elif name == "click_id":
                # This check prevents the KeyError if the LLM uses the wrong name
                eid = args.get('element_id') or args.get('id')
                if eid:
                    result = vision_tool.click_id(eid)
                else:
                    result = "Error: You must provide an ID to click."

            elif name == "type_text":

                result = vision_tool.type_text(args['text'])

            

            print(f"📝 Result: {result[:100]}...")

            messages.append({"role": "tool", "content": result, "name": name})



if __name__ == "__main__":

    task = input("What desktop task should I perform? ")

    run_ghost_agent(task)
