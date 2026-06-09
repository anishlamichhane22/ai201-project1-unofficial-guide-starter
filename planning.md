# Project 1 Planning: The Unofficial Guide

## Domain
Student reviews of professors at Huston-Tillotson University (HBCU in Austin, TX). 
This knowledge is valuable because official course catalogs only list course descriptions 
and prerequisites — they don't reflect teaching style, exam difficulty, grading fairness, 
or workload. Students rely on word-of-mouth to make informed decisions about which 
professors to take, but this knowledge is scattered and hard to find for new students.

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Student review | Jose Mauricio Antunez - Programming Foundations | data/prof_antunez.txt |
| 2 | Student review | Dr. Abina Primo - Java Programming | data/prof_primo.txt |
| 3 | Student review | Alfredo Tirado-Ramos - Web Programming | data/prof_tirado.txt |
| 4 | Student review | James Kraft - Health & Wellness | data/prof_kraft.txt |
| 5 | Student review | Anne Cirella-Urrutia - French | data/prof_cirella.txt |
| 6 | Student review | Ethan Pena - US History | data/prof_pena.txt |
| 7 | Student review | Zoe Rodriguez - Freshman Seminar | data/prof_rodriguez.txt |
| 8 | Student review | Dr. Farzana Hussain - Calculus I | data/prof_hussain.txt |
| 9 | Student review | Engin Topkara - Physics | data/prof_topkara.txt |
| 10 | Student review | Alana King - English Composition | data/prof_king.txt |

## Chunking Strategy

**Chunk size:** 200 characters

**Overlap:** 20 characters

**Reasoning:** Our documents are short student reviews, not long guides or articles. 
Each review is only 3-5 sentences long. Using a small chunk size of 200 characters 
ensures each chunk captures one focused thought (e.g., exam difficulty or teaching style) 
without mixing unrelated topics. A small overlap of 20 characters prevents key information 
from being cut off at chunk boundaries.

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 4

**Production tradeoff reflection:** all-MiniLM-L6-v2 runs locally with no API key or 
cost, which is ideal for this project. For a real production system I would consider 
OpenAI's text-embedding-3-small for higher accuracy, or a multilingual model if HT's 
student body needed support for Spanish speakers. Context length is not a concern here 
since our chunks are short, but latency would matter at scale — a local model avoids 
API round-trip delays.

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Antunez's teaching style? | Explains concepts simply, great professor |
| 2 | How difficult are Dr. Primo's exams? | Exams are very tough, course is challenging |
| 3 | Is Tirado-Ramos good for beginners in web programming? | Yes, starts from basics, good for beginners |
| 4 | What is Dr. Hussain's Calculus class like? | Great professor, covers everything, informs about events |
| 5 | What do students say about the Freshman Seminar? | Very helpful, teaches about campus life, clubs and events |

## Anticipated Challenges

1. **Short reviews may produce weak embeddings** — since each review is only a few 
sentences, chunks may not carry enough semantic signal for the embedding model to 
distinguish between similar queries about different professors.

2. **Missing context at chunk boundaries** — if a review mentions a professor's name 
only at the top and the relevant content is in a later chunk, retrieval may return 
a chunk without enough context to identify which professor it refers to.

## Architecture