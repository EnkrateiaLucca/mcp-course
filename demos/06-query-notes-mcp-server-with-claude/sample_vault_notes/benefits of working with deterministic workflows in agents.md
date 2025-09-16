#### [**Prioritize deterministic workflows for now**](https://arc.net/l/quote/bmtodmnh)

While AI agents can dynamically react to user requests and the environment, their non-deterministic nature makes them a challenge to deploy. Each step an agent takes has a chance of failing, and the chances of recovering from the error are poor. Thus, the likelihood that an agent completes a multi-step task successfully decreases exponentially as the number of steps increases. As a result, teams building agents find it difficult to deploy reliable agents.

A promising approach is to have agent systems that produce deterministic plans which are then executed in a structured, reproducible way. In the first step, given a high-level goal or prompt, the agent generates a plan. Then, the plan is executed deterministically. This allows each step to be more predictable and reliable. Benefits include:

- Generated plans can serve as few-shot samples to prompt or finetune an agent.
- Deterministic execution makes the system more reliable, and thus easier to test and debug. Furthermore, failures can be traced to the specific steps in the plan.
- Generated plans can be represented as directed acyclic graphs (DAGs) which are easier, relative to a static prompt, to understand and adapt to new situations.

## Related

- [[building-effective-agents]] - Workflow patterns including deterministic approaches
- [[Agentic Workflows]] - Structured workflow design
- [[Chains vs Agents]] - When deterministic chains might be preferred
- [[12 Factors for building agents]] - Factor 12: "Stateless Reducer" for predictability
- [[Evaluation of LLM Agents]] - Easier evaluation with deterministic workflows
- [[Sample principles for good LLM agent implementations from anthropic]] - Simplicity principle
- [[Loop of an LLM Agent]] - Deterministic vs dynamic loop execution
- [[the memory issue with agents]] - Memory management in deterministic workflows