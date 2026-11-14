# Introduction to Retrieval-Augmented Generation

> Approved lesson. Run `a791fca8f9004ca1828c59ef1b63794e`.

## What you will learn

1. Define RAG in simple everyday English.
2. Explain how looking up documents differs from changing a trained model.
3. Recognize why retrieval relevance, source freshness, and accuracy checks matter.

## Before you start

This lesson is designed for beginners starting an AI career with no prior technical knowledge, coding background, or database experience.

## What it is

RAG stands for retrieval-augmented generation. In simple terms, it is a method that helps an artificial intelligence (AI), which is a computer system that can think or answer questions like a human, give correct answers by looking up information from external documents instead of guessing from memory. When you ask a question, the system first performs a retrieval, which means searching through a collection of external texts to find the right facts. Then, it uses generation, which is the AI's ability to write a clear, natural answer using the facts it just found. This is different from fine-tuning, which means changing the permanent knowledge inside the trained model itself. With RAG, you keep the model the same and simply hand it the right document at question time.

## Why it matters

AI models often fail when asked about new facts, local rules, or private documents that were not present when the model was first trained. Without RAG, the model might guess or make up an answer that sounds correct but is totally wrong. By using retrieval, the AI can look at current documents, such as college notices, company rules, or news updates. This helps the AI provide useful, fact-based answers while letting readers check the original sources for accuracy.

## How it works

1. A preparation pipeline loads documents, divides them into smaller pieces, and organizes them into a searchable index, which is an organized list that makes finding specific text fast.
2. When a user asks a question, the system searches the index for text that is relevant to that specific question.
3. The system places the relevant retrieved text into the prompt, which is the input text given to the model.
4. The language model reads the prompt with the added text and generates a final, helpful answer.

## Worked example

**Illustrative context:** Illustrative Indian college example. Asha College and every detail in this notice are invented for learning; they are not real scholarship advice.

**Question:** What is the last date to apply for the Asha College book grant?

**Source passage:** Illustrative Asha College notice: Book grant applications close on 15 July. Students must submit the application form at the college office. This notice does not state the grant amount or eligibility rules.

**What the system retrieves and adds:** Illustrative Asha College notice: Book grant applications close on 15 July. Students must submit the application form at the college office.

**Supported answer:** Based on the retrieved notice, the last date to apply for the Asha College book grant is 15 July, and students must submit their forms at the college office.

**When information is missing:** How much money will I receive from this book grant?

**Honest response:** The provided notice does not state the grant amount. That information is missing, and you should consult an appropriate official college source rather than guessing.

## Limitations

RAG is very powerful, but it is not perfect. If the retrieval system brings back poorly matched or outdated documents, the quality of the answer will weaken. Furthermore, RAG does not guarantee 100 percent correctness. The AI can still misread text or return a wrong answer, so it is important to check important claims against the original sources.

## Recap

- RAG combines document retrieval with AI text generation.
- Looking up documents at question time does not require retraining the model.
- Retrieval relevance and source freshness ensure the AI has good facts to work with.
- RAG can still make errors, so users should always check important facts against the source.

## Practice questions and answers

### 1. What does RAG stand for, and what are its two main parts?

RAG stands for retrieval-augmented generation. Its two main parts are retrieval, which searches for relevant external information, and generation, which writes out a clear answer using that information.

### 2. How is looking up documents at question time different from fine-tuning a model?

Looking up documents means feeding external text into the prompt at the moment a question is asked without altering the model's inner weights, whereas fine-tuning changes the trained model itself.

### 3. Why is it important to check the original source when using a RAG system?

RAG does not promise perfect correctness and can still return wrong or unsupported answers, so checking the source helps verify accuracy.

## References

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401v4) — accessed 2026-11-13.
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — accessed 2026-11-13.
- [Classic RAG in Azure AI Search](https://github.com/Azure-Samples/azure-search-classic-rag) — accessed 2026-11-13.
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — accessed 2026-11-13.
