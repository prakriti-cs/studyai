YT = "https://www.youtube.com/watch?v="

TOPICS = {
    "Programming Basics": {
        "level": "beginner", "prerequisites": [],
        "keywords": "programming coding python variables loops functions conditions basics",
        "videos": [("Learn Python - Full Course for Beginners", YT + "rfscVS0vtbw")],
    },
    "Complexity Analysis": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "big o notation time complexity space complexity analysis of algorithms efficiency",
        "videos": [("Big O notation - Data Structures & Algorithms Tutorial #2", YT + "IR_S8BC8KI0"),
                   ("Big-O Notation Explained", YT + "APGPA3nN5a4")],
    },
    "Arrays": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "array list index elements contiguous memory two pointers",
        "videos": [("Data Structures Easy to Advanced Course - Full Tutorial", YT + "RBSGKlAvoiM"),
                   ("Array vs Linked List vs Stack vs Queue Explained", YT + "YFDokjXqi1E")],
    },
    "Recursion": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "recursion recursive function calls itself base case call stack factorial fibonacci",
        "videos": [("Intro to Recursion [Abdul Bari] DSA Course", YT + "XHjrJHNYUm4")],
    },
    "Linked Lists": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "linked list node pointer singly doubly circular",
        "videos": [("Stacks, Queues and LinkedList Complete Tutorial", YT + "BnZLGy3g8y4"),
                   ("Data Structures Easy to Advanced Course - Full Tutorial", YT + "RBSGKlAvoiM")],
    },
    "OOP": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "oop oops object oriented programming class object inheritance polymorphism encapsulation abstraction",
        "videos": [("OOP in 6 Minutes: Encapsulation, Abstraction, Inheritance, Polymorphism", YT + "YkFDStb7Cuc"),
                   ("Python Object Oriented Programming - OOP Principles Explained", YT + "ZVTuWsrjvyU")],
    },
    "Stacks": {
        "level": "beginner", "prerequisites": ["Arrays"],
        "keywords": "stack lifo push pop last in first out",
        "videos": [("Stacks, Queues and LinkedList Complete Tutorial", YT + "BnZLGy3g8y4"),
                   ("Stacks & Queues", YT + "aBR8SxPMbng")],
    },
    "Queues": {
        "level": "beginner", "prerequisites": ["Arrays"],
        "keywords": "queue fifo enqueue dequeue deque first in first out",
        "videos": [("Stacks, Queues and LinkedList Complete Tutorial", YT + "BnZLGy3g8y4"),
                   ("Stacks & Queues", YT + "aBR8SxPMbng")],
    },
    "Hashing": {
        "level": "intermediate", "prerequisites": ["Arrays", "Complexity Analysis"],
        "keywords": "hashing hash table hash map hash function collision dictionary",
        "videos": [("Learn Hash Tables in 13 minutes", YT + "FsfRsGFHuv4"),
                   ("Hash Tables and Hash Functions", YT + "KyUTuwz_b7Q")],
    },
    "Sorting": {
        "level": "beginner", "prerequisites": ["Arrays"],
        "keywords": "sorting sort bubble sort selection sort insertion sort merge sort quick sort",
        "videos": [("Sorting Algorithms: Bubble, Selection, Insertion, Merge, Quick Sort", YT + "6drK7cVIb84")],
    },
    "Binary Search": {
        "level": "beginner", "prerequisites": ["Arrays", "Sorting"],
        "keywords": "binary search sorted array divide and conquer search algorithm",
        "videos": [("Binary Search Algorithm in 100 Seconds", YT + "MFhxShGxHWc"),
                   ("Binary Search Algorithm Explained Visually (with an Example)", YT + "iO_gdw4HZ84")],
    },
    "Trees": {
        "level": "intermediate", "prerequisites": ["Recursion", "Linked Lists"],
        "keywords": "tree binary tree bst inorder preorder postorder traversal root leaf",
        "videos": [("5.5 Binary Tree Traversals (Inorder, Preorder and Postorder)", YT + "-b2lciNd2L4"),
                   ("Binary Tree Traversals - Preorder, Inorder, Postorder, Level Order", YT + "OXy4pLq_XZs")],
    },
    "Graphs": {
        "level": "intermediate", "prerequisites": ["Trees"],
        "keywords": "graph vertex edge adjacency list adjacency matrix directed undirected weighted",
        "videos": [("Data Structures Explained: Arrays, Stacks, Graphs & More", YT + "SuCGoHVoIag")],
    },
    "BFS": {
        "level": "intermediate", "prerequisites": ["Graphs", "Queues"],
        "keywords": "bfs breadth first search graph traversal queue level order shortest path",
        "videos": [("6.2 BFS and DFS Graph Traversals | Breadth First Search and Depth First Search", YT + "vf-cxgUXcMk"),
                   ("Graph Algorithms, Visualized (BFS and DFS)", YT + "uXWReXfeK48"),
                   ("BFS and DFS Graph Traversal Algorithms Explained", YT + "D8ZS32wGs0s")],
    },
    "DFS": {
        "level": "intermediate", "prerequisites": ["Graphs", "Stacks", "Recursion"],
        "keywords": "dfs depth first search graph traversal stack backtracking",
        "videos": [("6.2 BFS and DFS Graph Traversals | Breadth First Search and Depth First Search", YT + "vf-cxgUXcMk"),
                   ("Graph Algorithms, Visualized (BFS and DFS)", YT + "uXWReXfeK48"),
                   ("L-4.15: BFS & DFS", YT + "N2P7w22tN9c")],
    },
    "A Star Search": {
        "level": "advanced", "prerequisites": ["BFS"],
        "keywords": "a star a* astar heuristic informed search shortest path pathfinding",
        "videos": [("A* (A Star) Search Algorithm - Computerphile", YT + "ySN5Wnu88nE"),
                   ("A* algorithm EASY explained (example)", YT + "kEY1OxOj_CY")],
    },
    "Dynamic Programming": {
        "level": "advanced", "prerequisites": ["Recursion", "Arrays"],
        "keywords": "dynamic programming dp memoization tabulation knapsack subproblems",
        "videos": [("Dynamic Programming Complete Course for Beginners", YT + "N_B8-vgkfgw"),
                   ("Dynamic Programming - Learn to Solve Algorithmic Problems & Coding Challenges", YT + "oBt53YbR9Kk")],
    },
    "DBMS Basics": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "dbms database management system relational model table primary key foreign key acid transaction",
        "videos": [("Database Management System Full Course: Introduction & Relational Model", YT + "mh26fgrO-9k"),
                   ("DBMS Full Course for Beginners", YT + "c5HAwKX-suM")],
    },
    "SQL": {
        "level": "beginner", "prerequisites": ["DBMS Basics"],
        "keywords": "sql select join query insert update delete group by database",
        "videos": [("SQL Tutorial - Full Database Course for Beginners", YT + "HXV3zeQKqGY"),
                   ("SQL Tutorial - Full Database Course for Beginners", YT + "b-84RCtduFA")],
    },
    "Normalization": {
        "level": "intermediate", "prerequisites": ["DBMS Basics"],
        "keywords": "normalization normalisation 1nf 2nf 3nf bcnf functional dependency redundancy database design",
        "videos": [("Database Normalization Explained: 1NF, 2NF, 3NF & BCNF", YT + "naktei1cL5Y"),
                   ("Learn Database Normalization - 1NF, 2NF, 3NF, 4NF, 5NF", YT + "GFQaEYEc8_8")],
    },
    "Operating System Basics": {
        "level": "beginner", "prerequisites": ["Programming Basics"],
        "keywords": "operating system os process thread scheduling memory management kernel",
        "videos": [],
    },
    "Deadlock": {
        "level": "intermediate", "prerequisites": ["Operating System Basics"],
        "keywords": "deadlock processes resources circular wait prevention avoidance bankers algorithm",
        "videos": [("Operating Systems: Deadlock, Deadlock Prevention and Avoidance", YT + "miQ55SsU1YA"),
                   ("Deadlock in Operating System", YT + "MYgmmJJfdBg")],
    },
    "Statistics Basics": {
        "level": "beginner", "prerequisites": [],
        "keywords": "statistics mean median variance probability distribution",
        "videos": [],
    },
    "Machine Learning": {
        "level": "intermediate", "prerequisites": ["Programming Basics", "Statistics Basics"],
        "keywords": "machine learning ml supervised unsupervised regression classification clustering model training",
        "videos": [("Machine Learning for Everybody", YT + "i_LwzRVP7bg"),
                   ("Machine Learning Full Course for Beginners", YT + "FP9kL-_k5Ys")],
    },
    "Overfitting": {
        "level": "intermediate", "prerequisites": ["Machine Learning"],
        "keywords": "overfitting underfitting regularization cross validation generalization",
        "videos": [("Overfitting & Underfitting Explained! (Machine Learning Basics)", YT + "1DpOATeWmo8"),
                   ("But What Is Overfitting in Machine Learning?", YT + "Anq4PgdASsc")],
    },
}


# estimated hours and the subtopics to study, in order
DETAILS = {
    "Programming Basics": {"hours": 6, "subtopics": [
        "Variables and data types", "Input and output", "Conditions (if / else)", "Loops (for and while)",
        "Functions", "Lists and dictionaries", "Basic debugging"]},
    "Complexity Analysis": {"hours": 3, "subtopics": [
        "What is time complexity", "Big O, Omega and Theta notation",
        "Common complexities: O(1), O(log n), O(n), O(n log n), O(n^2)", "Analysing loops and nested loops",
        "Space complexity", "Best, average and worst case"]},
    "Arrays": {"hours": 4, "subtopics": [
        "Declaring and indexing", "Traversal", "Insertion and deletion", "Two pointers technique",
        "Prefix sums", "Sliding window", "2D arrays (matrices)"]},
    "Recursion": {"hours": 4, "subtopics": [
        "How recursion works", "Base case and recursive case", "The call stack", "Recursion trees",
        "Classic problems: factorial, Fibonacci, power", "Introduction to backtracking"]},
    "Linked Lists": {"hours": 4, "subtopics": [
        "Nodes and pointers", "Singly linked list", "Insertion and deletion", "Reversing a list",
        "Doubly and circular linked lists", "Fast and slow pointers (find middle, detect cycle)"]},
    "OOP": {"hours": 5, "subtopics": [
        "Classes and objects", "Constructors", "Encapsulation", "Abstraction", "Inheritance",
        "Polymorphism (overloading and overriding)", "Access modifiers"]},
    "Stacks": {"hours": 3, "subtopics": [
        "LIFO principle", "push, pop and peek", "Implementation using array and linked list",
        "Balanced parentheses", "Infix, postfix and expression evaluation", "Next greater element"]},
    "Queues": {"hours": 3, "subtopics": [
        "FIFO principle", "enqueue and dequeue", "Circular queue", "Deque (double-ended queue)",
        "Priority queue (introduction)", "Queue using two stacks"]},
    "Hashing": {"hours": 4, "subtopics": [
        "Hash functions", "Hash tables", "Collision handling: chaining and open addressing", "Load factor",
        "Sets and maps in practice", "Frequency counting problems"]},
    "Sorting": {"hours": 5, "subtopics": [
        "Bubble sort", "Selection sort", "Insertion sort", "Merge sort", "Quick sort",
        "Stable and in-place sorting", "Comparing time complexities"]},
    "Binary Search": {"hours": 3, "subtopics": [
        "Why the array must be sorted", "Iterative and recursive versions", "First and last occurrence",
        "Search in a rotated sorted array", "Binary search on the answer", "Time complexity O(log n)"]},
    "Trees": {"hours": 5, "subtopics": [
        "Tree terminology (root, leaf, height, depth)", "Binary trees", "Inorder, preorder and postorder traversal",
        "Level order traversal", "Binary search tree: insert, search, delete", "Balanced trees (AVL introduction)"]},
    "Graphs": {"hours": 5, "subtopics": [
        "Graph terminology", "Directed, undirected and weighted graphs", "Adjacency matrix",
        "Adjacency list", "Degree of a vertex", "Connected components", "Trees versus graphs"]},
    "BFS": {"hours": 4, "subtopics": [
        "How BFS works (queue)", "Visited array", "Level-by-level traversal",
        "Shortest path in an unweighted graph", "BFS on grids and matrices", "Time complexity O(V + E)"]},
    "DFS": {"hours": 4, "subtopics": [
        "Recursive DFS", "DFS with an explicit stack", "Visited array", "Cycle detection",
        "Topological sort", "Connected components", "Time complexity O(V + E)"]},
    "A Star Search": {"hours": 4, "subtopics": [
        "Informed vs uninformed search", "The cost function f(n) = g(n) + h(n)",
        "Heuristics: Manhattan and Euclidean distance", "Open and closed lists",
        "Admissible heuristics", "A* compared with BFS and Dijkstra"]},
    "Dynamic Programming": {"hours": 8, "subtopics": [
        "Overlapping subproblems", "Optimal substructure", "Memoization (top-down)", "Tabulation (bottom-up)",
        "Fibonacci", "0/1 Knapsack", "Longest common subsequence", "Coin change", "Defining the DP state"]},
    "DBMS Basics": {"hours": 4, "subtopics": [
        "DBMS vs file system", "Relational model", "Keys: primary, foreign, candidate", "ER diagrams",
        "Transactions and ACID properties", "Indexing"]},
    "SQL": {"hours": 5, "subtopics": [
        "SELECT, WHERE and ORDER BY", "Aggregate functions", "GROUP BY and HAVING", "Joins (inner, left, right, full)",
        "Subqueries", "INSERT, UPDATE and DELETE", "CREATE TABLE and constraints"]},
    "Normalization": {"hours": 3, "subtopics": [
        "Insertion, update and deletion anomalies", "Functional dependencies", "First normal form (1NF)",
        "Second normal form (2NF)", "Third normal form (3NF)", "BCNF", "Denormalization"]},
    "Operating System Basics": {"hours": 4, "subtopics": [
        "Functions of an operating system", "Process vs thread", "CPU scheduling algorithms",
        "Memory management", "Paging and virtual memory", "System calls", "File systems"]},
    "Deadlock": {"hours": 3, "subtopics": [
        "What is a deadlock", "The four necessary conditions", "Resource allocation graph",
        "Deadlock prevention", "Deadlock avoidance (Banker's algorithm)", "Detection and recovery"]},
    "Statistics Basics": {"hours": 4, "subtopics": [
        "Mean, median and mode", "Variance and standard deviation", "Probability basics",
        "Normal distribution", "Correlation", "Sampling"]},
    "Machine Learning": {"hours": 6, "subtopics": [
        "Supervised vs unsupervised learning", "Features and labels", "Train / test split", "Regression",
        "Classification", "Evaluation metrics: accuracy, precision, recall, F1",
        "Common algorithms: linear regression, decision tree, KNN"]},
    "Overfitting": {"hours": 3, "subtopics": [
        "Underfitting vs overfitting", "Bias-variance tradeoff", "Training vs validation error",
        "Cross-validation", "Regularization", "Early stopping and getting more data"]},
}

for _name, _details in DETAILS.items():
    TOPICS[_name].update(_details)
