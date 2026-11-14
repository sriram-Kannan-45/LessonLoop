# Introduction to RAG: Finding Facts for AI

> Approved lesson. Run `b0ba902b21e64ce3a8f38a1ff446ef1d`.

## What you will learn

1. Understand what RAG stands for and why it is useful.
2. Explain the difference between looking up documents and changing the trained model.
3. Recognize retrieval relevance, source freshness, and system limitations.

## Before you start

No prior computer coding, database experience, or artificial intelligence knowledge is needed. This lesson uses simple English for beginners starting an AI career.

## What it is

RAG stands for retrieval-augmented generation. Let us break down these big words into simple ideas. Artificial intelligence, or AI, refers to computer systems designed to think or answer questions like humans. Generation means the AI creates new text or responses. Retrieval means searching through external collections of documents to find specific information. When you put them together, retrieval-augmented generation means the AI searches for relevant text first, and then uses that found text to generate an accurate answer. Think of it like taking an open-book exam. Instead of relying only on memory, the AI looks up the correct page in a file or document collection before writing down its reply. A pipeline is simply a step-by-step process used to prepare and organize files. This process is distinct from fine-tuning, which involves changing the trained model by altering its internal memory settings, often called weights, through heavy machine learning training.

## Why it matters

Standard AI models can sometimes make mistakes or lack up-to-date facts about local or private events because they only know what was in their original training data. RAG helps fix this problem by letting the AI read external material at question time. For example, if a college updates its scholarship rules or fee structures, a standard model would not know the new rules. With RAG, the system searches the newly updated documents and gives the correct, current answer to the student. This helps users trust the system because they can check the original sources.

## How it works

1. A preparation pipeline, which is a step-by-step process of preparing files, takes collection documents, splits them into useful smaller pieces, and puts them into a searchable index, meaning an organized list that makes finding specific text fast.
2. When a user asks a question, the system searches the index to find the most relevant text pieces.
3. The system places the retrieved text into the prompt, which is the input text given to the language model.
4. The language model reads the prompt containing the user question and the retrieved text, then generates a helpful final answer.

## Worked example

**Illustrative context:** Illustrative Indian college example. Asha College and every detail in this notice are invented for learning; they are not real scholarship advice.

**Question:** What is the last date to apply for the Asha College book grant?

**Source passage:** Illustrative Asha College notice: Book grant applications close on 15 July. Students must submit the application form at the college office. This notice does not state the grant amount or eligibility rules.

**What the system retrieves and adds:** Book grant applications close on 15 July. Students must submit the application form at the college office.

**Supported answer:** Based on the retrieved college notice, the last date to apply for the Asha College book grant is 15 July, and students must submit the form at the college office.

**When information is missing:** How much money will I receive from this book grant?

**Honest response:** The provided college notice does not state the grant amount or eligibility rules. Please consult an appropriate official college source for accurate details, as this information is missing.

## Limitations

RAG is very helpful, but it is not perfect. Retrieval quality matters: if the search system finds weak or outdated documents, the final answer can be weak too. Furthermore, documents and searchable indexes need regular maintenance when facts change. Most importantly, RAG can still return wrong or unsupported answers. You should always check important claims against original sources and never assume the AI is infallible.

## Recap

- RAG combines document retrieval with text generation to answer questions using external facts.
- Looking up documents at question time is different from changing the trained model through fine-tuning.
- Relevance, source freshness, and regular maintenance of indexes are vital for good answers.
- RAG is not flawless, so verifying important answers against source citations remains necessary.

## Practice questions and answers

### 1. What does RAG stand for?

RAG stands for retrieval-augmented generation.

### 2. What is the main difference between looking up documents and changing the trained model?

Looking up documents happens at question time using external material without altering the model's internal memory settings or weights, whereas changing the trained model involves retraining or fine-tuning the model itself.

### 3. If a retrieved document does not contain the answer to a learner's question, what should the system do?

The system should state that the information is missing and suggest consulting an appropriate official source, rather than guessing dates or eligibility rules.

## References

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401v4) — accessed 2026-11-13.
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — accessed 2026-11-13.
- [Classic RAG in Azure AI Search](https://github.com/Azure-Samples/azure-search-classic-rag) — accessed 2026-11-13.
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — accessed 2026-11-13.
