# Introduction to Retrieval-Augmented Generation

> Approved lesson. Run `d7f428ad985b4aceba7b8a17610bfeef`.

## What you will learn

1. Define what RAG means in simple terms.
2. Explain how searching external documents helps an AI answer questions.
3. Understand the difference between looking up documents and changing a trained model.

## Before you start

You only need curiosity about artificial intelligence and a willingness to learn basic concepts. No prior technical knowledge, coding skills, or database experience is required.

## What it is

Welcome to your first lesson on artificial intelligence, or AI. AI refers to computer systems designed to perform tasks that normally require human thinking, such as answering questions or writing text. Today we will learn about RAG, which stands for retrieval-augmented generation. Let us break down these big words into everyday language. Generation means creating text using a language model, which is a computer program trained to understand and reply to human writing. Retrieval means looking up information from a collection of documents stored outside the model. When a user asks a question, the system first searches through external files to find matching notes. This found material is placed into a prompt, which is the exact input text given to the model so it knows what to talk about. By combining search results with text generation, RAG helps answer questions using fresh facts that the model might not have memorized during its initial training.

## Why it matters

Standard language models can only rely on what they learned when they were first built. If a school, company, or government releases new guidelines, the model will not know them automatically. RAG matters because it bridges this gap. Instead of guessing or making things up, the system reads real external documents and uses those exact facts to form a helpful response. This approach allows everyday users and organizations to get accurate answers from private or changing information without needing to rebuild the entire AI system from scratch.

## How it works

1. First, documents are prepared and split into smaller, useful pieces so they can be searched easily.
2. These pieces are stored in a searchable index, which acts like an organized filing cabinet for text.
3. When a user asks a question, the system searches the index to find the most relevant text passages.
4. The system adds those relevant passages into the prompt alongside the user's original question.
5. Finally, the language model reads the prompt with the retrieved text and generates a clear answer for the user.

## Worked example

**Illustrative context:** An Indian college scholarship notice states: The Swami Vivekananda Merit Scholarship provides financial help for grade 12 graduates joining undergraduate courses. Eligible students must score at least eighty percent in their board exams and have a family annual income below two lakh rupees. Applications close on July 31.

**Question:** What income limit applies to the Swami Vivekananda Merit Scholarship?

**Source passage:** The Swami Vivekananda Merit Scholarship provides financial help for grade 12 graduates joining undergraduate courses. Eligible students must score at least eighty percent in their board exams and have a family annual income below two lakh rupees. Applications close on July 31.

**What the system retrieves and adds:** Eligible students must score at least eighty percent in their board exams and have a family annual income below two lakh rupees.

**Supported answer:** Based on the retrieved notice, the family annual income must be below two lakh rupees.

**When information is missing:** Who is eligible for the Swami Vivekananda Merit Scholarship?

**Honest response:** The provided text does not mention eligibility details beyond income and board exam scores. Please consult an appropriate official source or notice board for complete criteria.

## Limitations

RAG does not promise perfect correctness and can still return wrong or unsupported answers. If the retrieved documents contain old, irrelevant, or incorrect facts, the final response will be weakened. Furthermore, looking up information at question time is entirely separate from fine-tuning or retraining model weights, meaning RAG relies heavily on the quality and freshness of the external source documents.

## Recap

- RAG stands for retrieval-augmented generation, combining external search with AI text generation.
- Retrieval means finding relevant text from external documents before the model replies.
- A prompt is the input text given to the model, which now includes the searched information.
- Looking up documents at question time is different from retraining or fine-tuning the model weights.
- Always verify important answers against trusted sources because errors can still occur.

## Practice questions and answers

### 1. What does RAG stand for, and what are its two main parts?

RAG stands for retrieval-augmented generation. Its two main parts are retrieval, which looks up relevant external documents, and generation, which creates a text answer using those documents.

### 2. Why is adding retrieved text to the prompt helpful for an AI model?

Adding retrieved text to the prompt gives the model fresh facts and specific information that might be missing from its general training knowledge, helping it give a more accurate answer.

### 3. If the retrieved documents contain old or incorrect facts, what happens to the final answer?

Poorly retrieved or outdated information can weaken the final response, which is why retrieval quality and source maintenance are very important.

## References

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401v4) — accessed 2026-11-13.
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — accessed 2026-11-13.
- [Classic RAG in Azure AI Search](https://github.com/Azure-Samples/azure-search-classic-rag) — accessed 2026-11-13.
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — accessed 2026-11-13.
