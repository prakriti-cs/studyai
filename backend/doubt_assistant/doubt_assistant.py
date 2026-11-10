from shared.common.text_utils import preprocess, get_similarity_scores
from shared.common.web_lookup import wikipedia_summary
from shared.common.fuzzy import fuzzy_confidence

# short forms people type, expanded before searching
ABBREVIATIONS = {"ml": "machine learning", "oop": "object oriented programming",
                 "oops": "object oriented programming", "dp": "dynamic programming",
                 "os": "operating system", "dbms": "database management system",
                 "ai": "artificial intelligence", "tfidf": "tf idf"}


def expand_abbreviations(text):
    words = preprocess(text.replace("*", " star ")).split()
    return " ".join(ABBREVIATIONS.get(word, word) for word in words)


# add more entries here
KNOWLEDGE_BASE = [
    {
        "subject": "AI",
        "topic": "BFS",
        "question": "What is Breadth First Search?",
        "keywords": "BFS breadth first search graph traversal queue level",
        "answer": "Breadth First Search is a graph traversal algorithm "
                  "that explores nodes level by level. It uses a queue."
    },
    {
        "subject": "AI",
        "topic": "DFS",
        "question": "What is Depth First Search?",
        "keywords": "DFS depth first search graph traversal stack backtracking",
        "answer": "Depth First Search explores a graph by going as deep "
                  "as possible before backtracking. It uses a stack or recursion."
    },
    {
        "subject": "AI",
        "topic": "A Star",
        "question": "What is the A star algorithm?",
        "keywords": "A star A* heuristic search shortest path",
        "answer": "A* is an informed search algorithm. It uses the cost "
                  "already travelled and a heuristic estimate to find a path."
    },
    {
        "subject": "AI",
        "topic": "Overfitting",
        "question": "What is overfitting?",
        "keywords": "overfitting machine learning model training data test accuracy",
        "answer": "Overfitting happens when a model learns the training data too well, "
                  "including noise, and performs badly on new data."
    },
    {
        "subject": "AI",
        "topic": "Machine Learning",
        "question": "What is machine learning?",
        "keywords": "machine learning ML model data learn patterns training prediction",
        "answer": "Machine learning is a part of AI in which a computer learns patterns "
                  "from data and makes predictions without being told every rule."
    },
    {
        "subject": "AI",
        "topic": "Fuzzy Logic",
        "question": "What is fuzzy logic?",
        "keywords": "fuzzy logic membership degree partial truth low medium high",
        "answer": "Fuzzy logic allows values between true and false. A value can belong "
                  "to more than one set at the same time, for example 0.6 low and 0.4 medium."
    },
    {
        "subject": "AI",
        "topic": "Expert System",
        "question": "What is an expert system?",
        "keywords": "expert system rules IF THEN knowledge base inference engine forward chaining",
        "answer": "An expert system is a program that uses a knowledge base of IF-THEN rules "
                  "and an inference engine to give advice like a human expert."
    },
    {
        "subject": "AI",
        "topic": "TF-IDF",
        "question": "What is TF-IDF?",
        "keywords": "TF-IDF term frequency inverse document frequency cosine similarity bag of words",
        "answer": "TF-IDF gives each word a weight: high if it is frequent in a document "
                  "but rare in other documents. Cosine similarity then compares the vectors."
    },
    {
        "subject": "OOP",
        "topic": "OOP",
        "question": "What is object oriented programming?",
        "keywords": "OOP OOPs object oriented programming class object encapsulation polymorphism abstraction",
        "answer": "Object oriented programming organizes code into classes and objects. "
                  "Its main ideas are encapsulation, inheritance, polymorphism and abstraction."
    },
    {
        "subject": "DSA",
        "topic": "Array",
        "question": "What is an array?",
        "keywords": "array index elements contiguous memory list",
        "answer": "An array stores elements of the same type in continuous memory. "
                  "Any element can be accessed by its index in O(1) time."
    },
    {
        "subject": "DSA",
        "topic": "Stack",
        "question": "What is a stack?",
        "keywords": "stack LIFO push pop last in first out",
        "answer": "A stack is a Last In First Out (LIFO) data structure. "
                  "Elements are added (push) and removed (pop) from the top."
    },
    {
        "subject": "DSA",
        "topic": "Queue",
        "question": "What is a queue?",
        "keywords": "queue FIFO enqueue dequeue first in first out",
        "answer": "A queue is a First In First Out (FIFO) data structure. "
                  "Elements are added at the rear and removed from the front."
    },
    {
        "subject": "DSA",
        "topic": "Binary Search",
        "question": "What is binary search?",
        "keywords": "binary search sorted array divide middle logarithmic",
        "answer": "Binary search finds an element in a sorted array by repeatedly "
                  "halving the search range. Its time complexity is O(log n)."
    },
    {
        "subject": "DSA",
        "topic": "Recursion",
        "question": "What is recursion?",
        "keywords": "recursion function calls itself base case",
        "answer": "Recursion is when a function calls itself to solve a smaller "
                  "version of the problem. It needs a base case to stop."
    },
    {
        "subject": "DBMS",
        "topic": "Primary Key",
        "question": "What is a primary key?",
        "keywords": "primary key unique identify record table",
        "answer": "A primary key is an attribute that uniquely identifies "
                  "each record in a database table. It cannot contain duplicate or NULL values."
    },
    {
        "subject": "DBMS",
        "topic": "Normalization",
        "question": "What is normalization?",
        "keywords": "normalization 1NF 2NF 3NF redundancy database design",
        "answer": "Normalization organizes database tables to reduce data "
                  "redundancy and avoid update problems. Common forms are 1NF, 2NF and 3NF."
    },
    {
        "subject": "OS",
        "topic": "Deadlock",
        "question": "What is a deadlock?",
        "keywords": "deadlock processes resources waiting circular wait",
        "answer": "A deadlock is a situation where processes wait for each other's "
                  "resources forever, so none of them can continue."
    },
    {
        "subject": "OOP",
        "topic": "Inheritance",
        "question": "What is inheritance?",
        "keywords": "inheritance parent child class properties methods",
        "answer": "Inheritance is an OOP concept in which one class "
                  "acquires the properties and methods of another class."
    },
]


def answer_doubt(query, subject=None, threshold=0.25, use_web=True):
    if not query or not query.strip():
        return {"status": "error", "message": "Please enter a question."}

    records = KNOWLEDGE_BASE
    if subject:
        records = [item for item in records
                   if item["subject"].lower() == subject.lower()]

    query = expand_abbreviations(query)

    if not records:
        return {"status": "not_found",
                "message": "No knowledge available for this subject."}

    documents = [
        preprocess(item["question"] + " " + item["keywords"] + " " + item["topic"])
        for item in records
    ]

    scores = get_similarity_scores(documents, query)

    best_index = scores.argmax()
    best_score = float(scores[best_index])

    if best_score < threshold:
        # not in the knowledge base, so try Wikipedia
        if use_web:
            web = wikipedia_summary(query + " computer science")
            if web and web["answer"]:
                return {
                    "status": "success",
                    "source": "Wikipedia (not from the knowledge base)",
                    "topic": web["title"],
                    "question": query,
                    "answer": web["answer"],
                    "link": web["link"],
                }

        closest = scores.argsort()[::-1][:3]
        return {"status": "not_found",
                "message": "Sorry, I could not find a relevant answer. "
                           "Try asking in a different way.",
                "did_you_mean": [records[i]["topic"] for i in closest]}

    result = records[best_index]
    return {
        "status": "success",
        "subject": result["subject"],
        "topic": result["topic"],
        "question": result["question"],
        "answer": result["answer"],
        "similarity_score": round(best_score, 3),
        "confidence": fuzzy_confidence(best_score)
    }


if __name__ == "__main__":
    question = input("Enter your doubt: ")
    result = answer_doubt(question)

    print("\nAI Doubt Assistant:")
    for key, value in result.items():
        print(f"{key}: {value}")