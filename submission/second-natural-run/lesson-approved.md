# Introduction to RAG: Finding Facts for AI

> Approved lesson. Run `9d8c5b6391ed485aa5806045ca0ae0ae`.

## What you will learn

1. Understand what RAG stands for and why it is useful.
2. Explain how retrieval-augmented generation differs from changing a trained model.
3. Recognize retrieval relevance, source freshness, and system limitations.

## Before you start

No prior knowledge of artificial intelligence, programming, databases, or machine learning is needed. This lesson is written for a beginner starting an AI career.

## What it is

RAG stands for retrieval-augmented generation. It is a method used in artificial intelligence, which we will call AI, to help computer programs answer questions accurately using outside information. An AI is a computer system designed to do tasks that usually need human thinking. A language model is a type of AI that reads and writes text based on patterns it learned during its initial training. However, a standard language model can forget recent facts, make up details, or lack local information. Retrieval means looking up documents in an external collection or library of text. Generation means creating a helpful text answer. Therefore, RAG combines retrieval with text generation. When you ask a question, the system searches an index, which is an organized list of documents, to find relevant text passages. It then adds those passages to your prompt, which is the input text given to the model, so the AI can read them and write a correct answer based on those real facts.

## Why it matters

A language model alone has fixed internal knowledge. When facts change, or when you need specific local details like college announcements or company guides, the model may guess incorrectly. RAG solves this problem without needing fine-tuning, which is the process of training or changing the internal numerical settings, known as weights, of a trained model to teach it new skills. Instead of rebuilding the entire AI model every time a new document is published, you simply update the searchable index of documents. This ensures that the AI reads current information at question time, giving you trustworthy answers grounded in real sources.

## How it works

1. A preparation pipeline, meaning an automated sequence of steps, loads documents, divides them into smaller pieces, and organizes them into a searchable index.
2. A user asks a question to the system.
3. The system performs a search to find text passages relevant to the user's question.
4. The retrieved text passages are added to the prompt given to the language model.
5. The language model reads the prompt with the retrieved text and formulates a clear answer.

## Worked example

**Illustrative context:** Illustrative Indian college example. Asha College and every detail in this notice are invented for learning; they are not real scholarship advice.

**Question:** What is the last date to apply for the Asha College book grant?

**Source passage:** Illustrative Asha College notice: Book grant applications close on 15 July. Students must submit the application form at the college office. This notice does not state the grant amount or eligibility rules.

**What the system retrieves and adds:** Book grant applications close on 15 July. Students must submit the application form at the college office.

**Supported answer:** Based on the retrieved notice, the last date to apply for the Asha College book grant is 15 July.

**When information is missing:** How much money will I receive from this book grant?

**Honest response:** The retrieved notice does not state the grant amount or eligibility rules. This information is missing, and you should consult an appropriate official source or college office for accurate details.

## Limitations

Even with RAG, systems are not perfect. Retrieval relevance matters greatly: if the search tool finds poor or irrelevant text, the answer quality will weaken. Source freshness is also important because documents and searchable indexes need regular maintenance when facts change. Furthermore, RAG can still return wrong or unsupported answers. You should always check important claims against original sources using citations, which let a reader return to the original source to verify accuracy.

## Recap

- RAG stands for retrieval-augmented generation and combines document lookup with text creation.
- Looking up documents at question time is different from changing a trained model through retraining or fine-tuning.
- Search relevance and document maintenance are crucial for obtaining accurate answers.
- RAG does not guarantee perfection, so checking important claims against original sources is necessary.

## Practice questions and answers

### 1. What are the two main parts of RAG?

RAG combines retrieval, which is searching for and looking up relevant documents, with generation, which is using a language model to write an answer based on those documents.

### 2. Does using retrieved information at question time mean you are retraining the model?

No. Using retrieved information at question time is distinct from changing model weights through training or fine-tuning. The model reads the retrieved text in the prompt without needing a full model retraining.

### 3. What should you do if the retrieved documents do not contain the answer to your question?

If the supplied text lacks an answer, state that the information is missing and consult an appropriate official source. Never invent dates, amounts, or eligibility rules.

## References

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401v4) — accessed 2026-11-13.
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — accessed 2026-11-13.
- [Classic RAG in Azure AI Search](https://github.com/Azure-Samples/azure-search-classic-rag) — accessed 2026-11-13.
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — accessed 2026-11-13.
