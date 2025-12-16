# 🎨 Visual Guide - Corrective RAG System

## 📊 Kiến trúc hệ thống (System Architecture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CORRECTIVE RAG SYSTEM FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

                           ┌──────────────┐
                           │ User Query   │
                           └──────┬───────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ 1. Retrieve Documents   │
                    │    (Vector Search)      │
                    └──────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ 2. Grade Each Document  │
                    │    (LLM-based)          │
                    └──────────┬──────────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
          ┌──────────────┐          ┌─────────────┐
          │  RELEVANT    │          │ IRRELEVANT  │
          │  Documents   │          │ Documents   │
          └──────┬───────┘          └─────────────┘
                 │                         │
                 │                         ▼
                 │                   ┌─────────┐
                 │                   │ DISCARD │
                 │                   └─────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Calculate          │
        │ Relevance Ratio    │
        └─────────┬──────────┘
                  │
     ┌────────────┴─────────────┐
     │                          │
     ▼                          ▼
Ratio ≥ Threshold        Ratio < Threshold
     │                          │
     │                          ▼
     │                  ┌───────────────┐
     │                  │ 3. Web Search │
     │                  │    (Fallback) │
     │                  └───────┬───────┘
     │                          │
     └──────────┬───────────────┘
                │
                ▼
    ┌───────────────────────┐
    │ 4. Combine Context    │
    │    (Relevant + Web)   │
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │ 5. Generate Answer    │
    │    (LLM)              │
    └───────────┬───────────┘
                │
                ▼
         ┌──────────────┐
         │ Final Answer │
         │ + Diagnostics│
         └──────────────┘
```

## 🔄 Quy trình xử lý (Processing Flow)

### Scenario 1: High Quality Documents (Tài liệu chất lượng cao)

```
Query: "What is Python?"

Step 1: Retrieve
┌────────────────────────────────────┐
│ Doc 1: Python programming intro... │ ← From Vector DB
│ Doc 2: Python features...          │
│ Doc 3: Python syntax guide...      │
│ Doc 4: Python best practices...    │
└────────────────────────────────────┘

Step 2: Grade Relevance
┌────────────────────────────────────┐
│ Doc 1: ✓ Relevant (score: yes)    │
│ Doc 2: ✓ Relevant (score: yes)    │
│ Doc 3: ✓ Relevant (score: yes)    │
│ Doc 4: ✓ Relevant (score: yes)    │
└────────────────────────────────────┘
Relevance Ratio: 4/4 = 100%

Step 3: Decision
┌────────────────────────────────────┐
│ Ratio (100%) ≥ Threshold (60%)    │
│ ✓ Use all relevant docs            │
│ ✗ No web search needed             │
└────────────────────────────────────┘

Step 4: Generate
┌────────────────────────────────────┐
│ Context: All 4 documents           │
│ Answer: Python is a high-level...  │
└────────────────────────────────────┘
```

### Scenario 2: Mixed Quality (Chất lượng hỗn hợp)

```
Query: "Explain machine learning"

Step 1: Retrieve
┌────────────────────────────────────┐
│ Doc 1: ML algorithms explained...  │ ← From Vector DB
│ Doc 2: Weather forecast data...    │
│ Doc 3: Deep learning basics...     │
│ Doc 4: Random unrelated text...    │
└────────────────────────────────────┘

Step 2: Grade Relevance
┌────────────────────────────────────┐
│ Doc 1: ✓ Relevant (score: yes)    │
│ Doc 2: ✗ Not relevant (score: no) │
│ Doc 3: ✓ Relevant (score: yes)    │
│ Doc 4: ✗ Not relevant (score: no) │
└────────────────────────────────────┘
Relevance Ratio: 2/4 = 50%

Step 3: Decision
┌────────────────────────────────────┐
│ Ratio (50%) < Threshold (60%)     │
│ ✓ Use 2 relevant docs              │
│ ✓ TRIGGER WEB SEARCH               │
└────────────────────────────────────┘

Step 4: Web Search
┌────────────────────────────────────┐
│ Searching: "machine learning"      │
│ Results: [Web snippet 1, 2, 3]    │
└────────────────────────────────────┘

Step 5: Generate
┌────────────────────────────────────┐
│ Context: 2 relevant docs + web     │
│ Answer: Machine learning is...     │
└────────────────────────────────────┘
```

### Scenario 3: Poor Documents (Tài liệu kém chất lượng)

```
Query: "Latest quantum computing news"

Step 1: Retrieve
┌────────────────────────────────────┐
│ Doc 1: Classic computing basics... │ ← From Vector DB
│ Doc 2: Software engineering...     │
│ Doc 3: Database design...          │
│ Doc 4: Web development...          │
└────────────────────────────────────┘

Step 2: Grade Relevance
┌────────────────────────────────────┐
│ Doc 1: ✗ Not relevant (score: no) │
│ Doc 2: ✗ Not relevant (score: no) │
│ Doc 3: ✗ Not relevant (score: no) │
│ Doc 4: ✗ Not relevant (score: no) │
└────────────────────────────────────┘
Relevance Ratio: 0/4 = 0%

Step 3: Decision
┌────────────────────────────────────┐
│ Ratio (0%) << Threshold (60%)     │
│ ✗ No relevant docs to use          │
│ ✓ RELY ON WEB SEARCH               │
└────────────────────────────────────┘

Step 4: Web Search
┌────────────────────────────────────┐
│ Searching: "quantum computing 2024"│
│ Results: [Latest news & articles]  │
└────────────────────────────────────┘

Step 5: Generate
┌────────────────────────────────────┐
│ Context: Web search only           │
│ Answer: Recent advances include... │
└────────────────────────────────────┘
```

## 📈 So sánh trực quan (Visual Comparison)

### Traditional RAG
```
┌──────────────────────────────────────────────────────┐
│                  TRADITIONAL RAG                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Query → Retrieve → Generate                         │
│                                                      │
│  Problems:                                           │
│  ❌ Uses ALL documents (even bad ones)              │
│  ❌ No quality check                                │
│  ❌ No fallback mechanism                           │
│  ❌ Can't tell if docs are relevant                 │
│                                                      │
│  Example:                                            │
│  Query: "Python programming"                         │
│  Retrieved:                                          │
│    • Python intro ✓                                  │
│    • Weather data ✗                                  │
│    • Random text ✗                                   │
│    • Sports news ✗                                   │
│  Used: ALL 4 docs (including 3 irrelevant)          │
│  Result: Answer contaminated with noise             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Corrective RAG
```
┌──────────────────────────────────────────────────────┐
│                   CORRECTIVE RAG                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Query → Retrieve → Grade → Filter → Generate       │
│                        ↓                             │
│                   Low Quality?                       │
│                        ↓                             │
│                   Web Search                         │
│                                                      │
│  Advantages:                                         │
│  ✅ Grades each document                            │
│  ✅ Filters out irrelevant info                     │
│  ✅ Web search fallback                             │
│  ✅ Transparent diagnostics                         │
│                                                      │
│  Example:                                            │
│  Query: "Python programming"                         │
│  Retrieved:                                          │
│    • Python intro ✓ (keep)                          │
│    • Weather data ✗ (discard)                       │
│    • Random text ✗ (discard)                        │
│    • Sports news ✗ (discard)                        │
│  Used: 1 relevant doc                               │
│  + Web search (triggered due to low ratio)          │
│  Result: Clean, accurate answer                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 🎯 Quyết định thông minh (Decision Making)

```
Relevance Threshold: 60%

┌─────────────────────────────────────────────────┐
│         DECISION TREE                           │
└─────────────────────────────────────────────────┘

                Relevance Ratio?
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
      0-40%        40-70%        70-100%
    (Very Low)    (Medium)      (High)
        │             │             │
        ▼             ▼             ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │  ✓ Web  │   │ ✓ Docs  │   │ ✓ Docs  │
  │    only │   │ ✓ Web   │   │ ✗ No web│
  └─────────┘   └─────────┘   └─────────┘

Examples:

Ratio = 100% (4/4 relevant)
  → Use: All documents
  → Web: Not needed
  → Quality: Excellent

Ratio = 50% (2/4 relevant)
  → Use: 2 relevant docs
  → Web: Yes (boost quality)
  → Quality: Good + Enhanced

Ratio = 0% (0/4 relevant)
  → Use: None (all bad)
  → Web: Yes (only source)
  → Quality: Web-based
```

## 🔍 Diagnostic Information

```
┌──────────────────────────────────────────────────────┐
│              DIAGNOSTIC OUTPUT                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Query: "What is machine learning?"                  │
│                                                      │
│  📊 Retrieval Metrics:                              │
│    • Total Retrieved: 4                             │
│    • Relevant: 3                                    │
│    • Irrelevant: 1                                  │
│    • Relevance Ratio: 75%                           │
│                                                      │
│  ✅ Document Grading:                               │
│    ✓ Doc 1: "ML uses algorithms..." (Relevant)     │
│    ✓ Doc 2: "AI and ML differ..." (Relevant)       │
│    ✓ Doc 3: "Deep learning is..." (Relevant)       │
│    ✗ Doc 4: "Weather forecast..." (Not Relevant)   │
│                                                      │
│  🌐 Web Search:                                     │
│    • Triggered: No (ratio above threshold)          │
│                                                      │
│  📝 Final Context:                                  │
│    • Sources Used: 3 documents                      │
│    • Quality: High                                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 🎮 Interactive Usage

### CLI with Diagnostics

```bash
$ uv run python cli.py query "What is Python?" --diagnostics

Processing query with self-correction...

┌─────────────────────────────────────────┐
│              ANSWER                     │
├─────────────────────────────────────────┤
│ Python is a high-level programming      │
│ language known for its simplicity...    │
└─────────────────────────────────────────┘

🔍 Diagnostics Information:

Self-Correction Process
┌────────────────────┬─────────┐
│ Metric             │ Value   │
├────────────────────┼─────────┤
│ Total Retrieved    │ 4       │
│ Relevant Documents │ 4       │
│ Irrelevant Docs    │ 0       │
│ Relevance Ratio    │ 100%    │
│ Used Web Search    │ ✗ No    │
└────────────────────┴─────────┘

Document Grading Results:
  ✓ Doc 1: Python is a programming...
  ✓ Doc 2: Python features include...
  ✓ Doc 3: Python syntax basics...
  ✓ Doc 4: Python best practices...

Relevant Sources:
  1. examples/sample_documents/python_intro.txt
     Python is a high-level programming...
```

## 📱 API Response

```json
{
  "answer": "Python is a high-level programming language...",
  "sources": [
    "Source: python_intro.txt",
    "Source: python_basics.txt"
  ],
  "diagnostics": {
    "total_retrieved": 4,
    "relevant_count": 3,
    "irrelevant_count": 1,
    "relevance_ratio": 0.75,
    "used_web_search": false,
    "grading_results": [
      {
        "content_preview": "Python is a programming...",
        "is_relevant": true,
        "grade_response": "{\"score\": \"yes\"}"
      }
    ]
  }
}
```

## 🎯 Use Case Examples

### Use Case 1: Technical Documentation

```
Scenario: Company technical docs + latest updates

Configuration:
  relevance_threshold: 0.7 (high quality needed)
  use_web_search: true (get latest info)

Flow:
  1. Search internal docs
  2. Grade for relevance
  3. If missing latest info → web search
  4. Combine internal + external

Result: Accurate + up-to-date answers
```

### Use Case 2: Customer Support

```
Scenario: Help articles + FAQ

Configuration:
  relevance_threshold: 0.5 (balanced)
  use_web_search: false (internal only)

Flow:
  1. Search help articles
  2. Grade relevance
  3. Filter poor matches
  4. Answer from best articles

Result: Focused, policy-compliant answers
```

### Use Case 3: Research Assistant

```
Scenario: Research papers + web

Configuration:
  relevance_threshold: 0.6 (balanced)
  use_web_search: true (comprehensive)

Flow:
  1. Search local papers
  2. Grade relevance
  3. Add web sources if needed
  4. Synthesize answer

Result: Comprehensive research answers
```

## 🚀 Quick Commands

```bash
# Test installation
python test_installation.py

# Add documents
uv run python cli.py add-directory examples/sample_documents

# Query with diagnostics
uv run python cli.py query "Your question" --diagnostics

# Interactive mode
uv run python cli.py interactive

# Run comparison demo
uv run python examples/comparison_demo.py

# Start API server
uv run python main.py
```

## 📚 Learn More

- **Full Docs**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Technical Details**: [CORRECTIVE_RAG.md](CORRECTIVE_RAG.md)
- **Changes**: [CHANGELOG_CORRECTIVE_RAG.md](CHANGELOG_CORRECTIVE_RAG.md)

---

**Happy Correcting! 🎯**

