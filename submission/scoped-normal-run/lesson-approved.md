# Introduction to Retrieval-Augmented Generation

> Approved lesson. Run `c728d140bcff41a48038721bad7da3b8`.

## What you will learn

1. Define what RAG means in simple terms.
2. Explain the difference between looking up documents and changing the trained model.
3. Describe how retrieval relevance, source freshness, and limitations affect AI answers.

## Before you start

No prior technical knowledge, coding skills, database experience, or machine-learning background is needed. You only need curiosity about how artificial intelligence systems answer questions using external documents.

## What it is

RAG stands for retrieval-augmented generation. In simple terms, it is a method that helps an artificial intelligence (AI), which is a computer system that performs tasks like human thinking or writing, give better answers by looking up outside facts. When you ask a question, the system does two main things. First, it uses retrieval, which means searching an external collection of documents to find facts relevant to your question. Second, it uses generation, which means creating a natural language answer based on those found facts. Think of it like an open-book exam for a computer. Instead of relying only on what it memorized during its initial training, the AI looks at specific pages handed to it at question time.

## Why it matters

Standard AI models can sometimes forget new details or make mistakes about facts they were not trained on. RAG matters because it bridges this gap. By looking up external documents, the system can answer questions using up-to-date facts that are absent from its stored knowledge. Furthermore, searching documents at question time is distinct from fine-tuning, which means changing the trained model weights or internal parameters permanently. With RAG, you do not need to retrain the entire model every time a new document or rule is published. You simply update the searchable documents or index, which is an organized list or catalog of text pieces that makes searching fast and accurate.

## How it works

1. A preparation pipeline loads documents, divides them into smaller pieces, and puts them into a searchable index.
2. When a user asks a question, the system searches the index to find the most relevant pieces of text.
3. The system adds the retrieved text into the prompt, which is the input text given to guide the model.
4. The language model reads the prompt with the added text and generates a helpful answer for the user.

## Worked example

**Illustrative context:** Illustrative Indian college example. Asha College and every detail in this notice are invented for learning; they are not real scholarship advice.

**Question:** What is the last date to apply for the Asha College book grant?

**Source passage:** Illustrative Asha College notice: Book grant applications close on 15 July. Students must submit the application form at the college office. This notice does not state the grant amount or eligibility rules.

**What the system retrieves and adds:** Book grant applications close on 15 July. Students must submit the application form at the college office.

**Supported answer:** Based on the Asha College notice, the last date to apply for the book grant is 15 July.

**When information is missing:** How much money will I receive from this book grant?

**Honest response:** The provided Asha College notice does not state the grant amount. That information is missing, so you should consult an appropriate official source or college office.

## Limitations

Even with RAG, systems have limitations. First, retrieval relevance matters: if the search engine finds poor or unrelated text, the final answer will be weak. Second, source freshness is crucial; if documents and searchable indexes are not updated when facts change, the AI will provide outdated answers. Third, RAG does not promise perfect correctness. Errors remain possible, and the model can still misunderstand or misstate facts. Therefore, you should always check important claims against original sources using citations when possible.

## Recap

- RAG combines document retrieval with text generation to answer questions accurately.
- Looking up documents at question time is different from changing the trained model through training or fine-tuning.
- Retrieval relevance and source freshness directly affect the quality of the AI response.
- Errors remain possible, so important claims should always be checked against original sources.

## Practice questions and answers

### 1. What does RAG stand for, and what are its two main parts?

RAG stands for retrieval-augmented generation. Its two main parts are retrieving relevant external text and generating a text answer based on that text.

### 2. Does using retrieved information at question time mean retraining the entire model?

No. Using retrieved information at question time does not require retraining the model or changing its trained weights.

### 3. Why is it important to check important AI claims against original sources?

Because RAG can still return wrong or unsupported answers, checking sources ensures accuracy and helps verify important facts.

## References

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401v4) — accessed 2026-11-13.
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — accessed 2026-11-13.
- [Classic RAG in Azure AI Search](https://github.com/Azure-Samples/azure-search-classic-rag) — accessed 2026-11-13.
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) — accessed 2026-11-13.
