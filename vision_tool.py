import pyautogui
from gradio_client import Client, handle_file
import ast
import os
import re

LAST_SCREEN_ELEMENTS = {}
OMNI_SERVER_URL = "http://127.0.0.1:7861/" 

def scan_screen():
    global LAST_SCREEN_ELEMENTS
    screenshot_path = os.path.abspath("current_screen.png")
    pyautogui.screenshot(screenshot_path)
    width, height = pyautogui.size()
    
    try:
        client = Client(OMNI_SERVER_URL)
        result = client.predict(handle_file(screenshot_path), 0.01, 0.1, False, 640, api_name="/process")
        
        parsed_content = result[1]
        elements_for_llm = []
        prioritized_elements = [] # Search bars go here
        LAST_SCREEN_ELEMENTS = {}
        
        lines = parsed_content.split('\n')
        for line in lines:
            match = re.search(r'(?:\w+\s+)?(\d+):\s*({.*})', line)
            if match:
                item_id = match.group(1)
                try:
                    data = ast.literal_eval(match.group(2))
                    bbox = data.get('bbox')
                    if bbox:
                        cx = ((bbox[1] + bbox[3]) / 2) * width
                        cy = ((bbox[0] + bbox[2]) / 2) * height
                        LAST_SCREEN_ELEMENTS[item_id] = (cx, cy)
                        
                        label = (data.get('content') or data.get('type') or "element").lower()
                        entry = f"ID {item_id}: {label}"
                        
                        # PRIORITIZATION LOGIC: Put search-related stuff at the top
                        search_keywords = ['search', 'input', 'text', 'address', 'query', 'google']
                        if any(key in label for key in search_keywords):
                            prioritized_elements.append(entry)
                        else:
                            elements_for_llm.append(entry)
                except: continue

        # Combine: Prioritized items first, then the rest
        final_list = prioritized_elements + elements_for_llm
        
        if not final_list:
            return "Vision connected, but NO elements detected."
            
        print(f"✅ Found {len(final_list)} elements ({len(prioritized_elements)} prioritized).")
        # Only return the top 50 elements to avoid confusing the AI with too much data
        return "\n".join(final_list[:50])

    except Exception as e:
        return f"CRITICAL VISION ERROR: {str(e)}"

#def scan_screen():
#    global LAST_SCREEN_ELEMENTS
#    screenshot_path = os.path.abspath("current_screen.png")
#    pyautogui.screenshot(screenshot_path)
#    width, height = pyautogui.size()
#    
#    try:
#        client = Client(OMNI_SERVER_URL)
#        result = client.predict(
#            handle_file(screenshot_path), 
#            0.01, # Threshold
#            0.1,  
#            False, # paddleOCR
#            640,  
#            api_name="/process"
#        )
#        
#        parsed_content = result[1]
#        elements_for_llm = []
#        LAST_SCREEN_ELEMENTS = {}
#        
#        # Split by lines and look for the icon/text data
#        lines = parsed_content.split('\n')
#        for line in lines:
            # Matches "icon 0: {...}" or "text 5: {...}"
#            match = re.search(r'(?:\w+\s+)?(\d+):\s*({.*})', line)
#            if match:
#                item_id = match.group(1)
#                try:
#                    # USE ast.literal_eval instead of json.loads
#                    # This handles 'False', 'True', and single quotes correctly
#                    data = ast.literal_eval(match.group(2))
#                    
#                    bbox = data.get('bbox')
#                    if bbox:
#                        # Normalized [ymin, xmin, ymax, xmax]
#                        cx = ((bbox[1] + bbox[3]) / 2) * width
#                        cy = ((bbox[0] + bbox[2]) / 2) * height
#                        
#                        LAST_SCREEN_ELEMENTS[item_id] = (cx, cy)
#                        
#                        # Get a descriptive label
#                        label = data.get('content') or data.get('type') or "element"
#                        elements_for_llm.append(f"ID {item_id}: {label}")
#                except Exception as e:
#                    continue

#        if not elements_for_llm:
#            return "Vision connected, but NO elements detected. Please ensure the browser is visible."
            
#        print(f"✅ Found {len(elements_for_llm)} elements.")
#        return "\n".join(elements_for_llm)

#    except Exception as e:
#        return f"CRITICAL VISION ERROR: {str(e)}"

def click_id(eid):
    # Clean the input
    orig_eid = str(eid)
    eid = re.sub(r'[^0-9]', '', orig_eid) # Remove anything that isn't a number
    
    if eid in LAST_SCREEN_ELEMENTS:
        x, y = LAST_SCREEN_ELEMENTS[eid]
        print(f"🖱️ [ACTION] Clicking ID {eid} at ({int(x)}, {int(y)})")
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        return f"Successfully clicked ID {eid}. You can now type."
    
    # If the AI sent a name instead of a number
    return f"REJECTED: '{orig_eid}' is not a valid numeric ID. Please pick a number from the last scan_screen result."
    
def type_text(text):
    pyautogui.write(text, interval=0.05)
    pyautogui.press('enter')
    return f"Typed: {text}"
