source: https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-1-natural-language-to-tool-calls.md
The **12-Factor Agents** approach is a set of best practices for building **reliable, production-ready AI agent applications** using LLMs. It’s modeled after the original [12-Factor App](https://12factor.net/) methodology that helped developers write scalable, maintainable software for the cloud. These 12 factors focus on building *modular, observable, and controllable* agents that play nicely with the rest of your software stack.



---

### **1. Natural Language to Tool Calls**

Let the LLM interpret plain language and output *structured actions* (e.g. JSON) that your app can run.
**Why:** It turns messy language into clean code-like actions.

---

### **2. Own Your Prompts**

Write and manage your own prompts instead of relying on black-box frameworks.
**Why:** You need full control over what the model sees and does.

---

### **3. Own Your Context Window**

Design how to feed history, state, and context into the model efficiently.
**Why:** LLMs are stateless—good context = good decisions.

---

### **4. Tools Are Just Structured Outputs**

Think of tools as JSON payloads the model outputs. Your code interprets and acts on them.
**Why:** Keeps logic cleanly separated between the model and your software.

---

### **5. Unify Execution and Business State**

Treat your LLM's interaction history as your source of truth.
**Why:** No need for messy sync between model state and app state.

---

### **6. Launch / Pause / Resume with Simple APIs**

Agents should be stoppable and resumable by events or APIs.
**Why:** Agents run in workflows that sometimes need to pause or wait.

---

### **7. Contact Humans with Tool Calls**

Model should “call” humans when it needs help, via structured messages.
**Why:** This enables safe use of LLMs in high-stakes workflows.

---

### **8. Own Your Control Flow**

Don't blindly loop LLM calls. Use your own rules to decide when to continue, pause, or branch.
**Why:** Helps avoid infinite loops and makes your app more predictable.

---

### **9. Compact Errors into the Context**

If something fails, summarize it and give it to the model to try again.
**Why:** Models can sometimes fix their own mistakes.

---

### **10. Small, Focused Agents**

Keep agents scoped to short, specific tasks.
**Why:** Long context = higher error rates.

---

### **11. Trigger from Anywhere**

Agents should be easy to start from Slack, cron, webhooks, etc.
**Why:** Meet users where they are and allow external integrations.

---

### **12. Make Your Agent a Stateless Reducer**

Treat your agent like a functional reducer: input + history = next action.
**Why:** Keeps the model logic pure and composable.

---

### **Bonus: 13. Pre-Fetch Context**

If you know the model will need some info—fetch it ahead of time and include it.
**Why:** Saves token round trips and speeds things up.

---

## Related

- [[building-effective-agents]] - Anthropic's comprehensive guide that complements these factors
- [[Sample principles for good LLM agent implementations from anthropic]] - Core principles that align with these factors
- [[prompting for agents]] - Factor 2 "Own Your Prompts" in detail
- [[Potential tools for useful agents]] - Factor 4 "Tools Are Just Structured Outputs"
- [[benefits of working with deterministic workflows in agents]] - Related to Factor 12 "Stateless Reducer"
- [[the memory issue with agents]] - Factor 3 "Own Your Context Window"
- [[Evaluation of LLM Agents]] - Testing and validating these factors
- [[Loop of an LLM Agent]] - Factor 8 "Own Your Control Flow"
- [[ambient agents]] - Factor 11 "Trigger from Anywhere"