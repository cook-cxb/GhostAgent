# GhostAgent
An agent, that uses omniparser v2, as eyes, a locally ollam runned llama3.1 (use later version of llama if picked) as brain and python pygui as hands
  
# 👻 GhostAgent: Vision-Based Desktop Automation

GhostAgent is an autonomous desktop assistant that "sees" the screen like a human and interacts with it using a mouse and keyboard. By combining the **Llama 3.1** reasoning engine with **OmniParser** for screen comprehension, GhostAgent can navigate complex GUIs, find search bars, and perform tasks across different applications.


 
---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Reasoning Engine** | Llama 3.1 (via Ollama or API) |
| **Vision/Screen Parsing** | Microsoft OmniParser (YOLOv8 + Florence-2) |
| **Automation Controller** | PyAutoGUI |
| **Environment** | Linux (Ubuntu 20.04/22.04 recommended) |
| **Package Management** | Miniconda / Python 3.12 |
| **Communication** | Gradio Client API |

----

## 📋 Prerequisites

Before running GhostAgent, ensure you have the following installed:
* **Python 3.12+**
* **Cuda-capable GPU** (For OmniParser inference)
* **OmniParser Server**: Running locally on `http://127.0.0.1:7861/`
* **X11/GNOME Desktop**: (Standard on Ubuntu)

---

## 🚀 Installation & Setup

1. **Clone the OmniParser Repository** (The "Eyes"):
   ```bash
   git clone [https://github.com/microsoft/OmniParser.git](https://github.com/microsoft/OmniParser.git)
   cd OmniParser
   # Follow OmniParser setup instructions to start the Gradio server
   python app.py
