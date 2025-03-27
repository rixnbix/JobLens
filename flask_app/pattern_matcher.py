# Used an Aho-Corasick Algorithm for Pattern Searching.
#It is efficient for searching multiple keywords at once. Below is the step by step implementation.
# Building the Trie:
# The add_keyword method inserts each keyword into a trie-like structure (self.adj), marking the end of each keyword in the self.out list.

# Constructing Failure Links:
# The build_fail method uses a breadth-first search (with a deque) to compute fallback pointers for each state, ensuring that the search continues efficiently even when a mismatch occurs.

# Searching the Text:
# The search method processes the input text character by character, following the trie transitions and fallback links. It records every matches of the keywords along with the position where they were found.


from collections import deque

class PatternMatcher:
    def __init__(self, keywords):
        # Each element in 'adj' is a dictionary that maps a character to the next state.
        self.adj = [{}]
        # 'out' stores, for each state, the list of keywords that end at that state.
        self.out = [[]]
        # 'fail' holds the failure (fallback) state for each state.
        self.fail = [0]
        
        for keyword in keywords:
            self.add_keyword(keyword)
        self.build_fail()
    
    def add_keyword(self, keyword):
        state = 0
        for char in keyword:
            if char not in self.adj[state]:
                self.adj[state][char] = len(self.adj)
                self.adj.append({})
                self.out.append([])
                self.fail.append(0)
            state = self.adj[state][char]
        # Mark the end of the keyword at this state.
        self.out[state].append(keyword)
    
    def build_fail(self):
        q = deque()
        # Initialize the failure function for nodes directly reachable from the root.
        for char, state in self.adj[0].items():
            q.append(state)
            self.fail[state] = 0
        
        while q:
            r = q.popleft()
            for char, s in self.adj[r].items():
                q.append(s)
                # Follow the failure link of r to find a state that has an edge for char.
                state = self.fail[r]
                while state and char not in self.adj[state]:
                    state = self.fail[state]
                self.fail[s] = self.adj[state].get(char, 0)
                # Append any keywords from the fallback state.
                self.out[s].extend(self.out[self.fail[s]])

    # Search the given text for keywords.
    # Returns a list of tuples (position, keyword) where position is the starting index of the keyword.
    def search(self, text):
        state = 0
        matches = []
        for i, char in enumerate(text):
            while state and char not in self.adj[state]:
                state = self.fail[state]
            state = self.adj[state].get(char, 0)
            # If any keywords end at this state, record all matches.
            for pattern in self.out[state]:
                matches.append((i - len(pattern) + 1, pattern))
        return matches