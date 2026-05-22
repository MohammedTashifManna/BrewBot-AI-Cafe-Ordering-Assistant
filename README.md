# ☕ BrewBot – AI Cafe Ordering Assistant

BrewBot is an AI-powered cafe ordering chatbot built using **Streamlit**, **LangGraph**, **LangChain**, and **Google Gemini**. It simulates an interactive coffee shop experience where users can browse a menu, customize drinks, manage orders, and place them through a conversational interface.

---

## 🚀 Features

✅ Interactive chat-based cafe ordering experience  
✅ AI-powered conversation using Gemini 2.5 Flash  
✅ Dynamic menu retrieval  
✅ Add drinks with modifiers/customizations  
✅ View current order  
✅ Confirm order before placing  
✅ Clear order functionality  
✅ Random order ETA generation  
✅ Streaming typing effect for realistic responses  
✅ State management with LangGraph  

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.5 Flash
- **Framework:** LangChain
- **Workflow Engine:** LangGraph
- **Environment Management:** python-dotenv

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone https://github.com/yourusername/BrewBot.git

cd BrewBot
```

### 2. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Add environment variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

### 5. Run application

```bash
streamlit run app.py
```

---

## 🧠 Workflow Architecture

```text
User Input
      ↓
Streamlit Chat UI
      ↓
LangGraph State Flow
      ↓
Gemini LLM + Tool Calling
      ↓
Order Management Logic
      ↓
Response Generation
```

---
