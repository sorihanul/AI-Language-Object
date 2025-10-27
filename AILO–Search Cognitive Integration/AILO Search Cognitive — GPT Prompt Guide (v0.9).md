# 🔍 AILO Search Cognitive — GPT Prompt Guide (v0.9)

> **Purpose:**  
> To perform deep, structured, and nuance-aware internet searches directly inside ChatGPT or any LLM that supports natural language input.

AILO Search Prompts enable **natural language commands** that are internally interpreted as **structured semantic actions** — no plugins, no setup.

---

## 🧠 Philosophy

Humans should **command in natural language** and **see results in natural language**.  
AILO handles the structure, logic, and validation internally.

When you write:

```
search{obj:"AI ethics" rule:verifiable conf:0.9 nuance:{tone:neutral}}!
```

the LLM interprets it as:

> “Find trustworthy sources about AI ethics, summarize them neutrally, and only include data with confidence ≥ 0.9.”

---

## ⚙️ Structure

```
search{obj:TOPIC rule:CONDITION conf:THRESHOLD nuance:{tone:TONE, scope:SCOPE}}!
```

|Slot|Meaning|Example|
|---|---|---|
|`obj`|What to search|`"AI regulation"`|
|`rule`|Search filter or constraint|`verifiable`, `recent`, `peer-reviewed`|
|`conf`|Confidence threshold (0–1)|`0.9`|
|`nuance`|Desired tone or scope|`{tone:neutral, scope:legal}`|
|`!`|Execution (perform search)|—|

---

## 🔧 Example Prompts

### 1️⃣ Factual search

```ailo
search{obj:"AI regulation" rule:verifiable conf:0.9 nuance:{tone:neutral, scope:legal}}!
```

→ Returns verified, up-to-date information about AI laws and policies.

---

### 2️⃣ Comparative analysis

```ailo
search{obj://EU AI Act//US AI Bill// rule:compare conf:0.85 nuance:{tone:analytical}}!
```

→ Compares and summarizes differences between two legal frameworks.

---

### 3️⃣ Research / academic search

```ailo
search{obj:"neural-symbolic AI" rule:recent conf:0.9 nuance:{tone:technical, scope:academic}}!
```

→ Finds latest research or reviews, focusing on scholarly context.

---

### 4️⃣ Ethical / social perspective

```ailo
search{obj:"AI surveillance ethics" rule:balanced conf:0.88 nuance:{tone:critical, scope:social}}!
```

→ Provides balanced discussion of ethical implications of AI surveillance.

---

### 5️⃣ Tool / implementation discovery

```ailo
search{obj:"open-source AI safety toolkit" rule:usable conf:0.92 nuance:{tone:practical}}!
```

→ Lists reliable open-source tools related to AI safety and risk mitigation.

---

## 🧩 How It Works in GPT

1. You type an **AILO sentence** into ChatGPT.
    
2. GPT recognizes its structure and intention.
    
3. It performs web or contextual retrieval.
    
4. It summarizes, filters, and outputs results in **natural language**.
    

**You never need to code or configure anything.**

---

## 💬 Style & Usage Tips

|Goal|Example|
|---|---|
|Get official sources|`rule:verifiable`|
|Get recent studies|`rule:recent`|
|Compare two ideas|`rule:compare`|
|Control tone|`tone:neutral` / `tone:critical` / `tone:optimistic`|
|Focus scope|`scope:academic` / `scope:policy` / `scope:social`|

Natural text like

> “Find reliable sources on AI ethics”  
> automatically maps to

```ailo
search{obj:"AI ethics" rule:verifiable conf:0.9}!
```

---

## ✅ Summary

- **Input:** Natural language
    
- **Processing:** Structured AILO interpretation
    
- **Output:** Natural-language summary with traceable logic
    
- **No setup:** Works directly in GPT chat
    
- **Purpose:** Make search intelligent, contextual, and verifiable
    

---

## 🪶 License

MIT License © 2025 [sorihanul](https://github.com/sorihanul)  
Part of the **AILO-SCP Project (v0.9E+)**

---
