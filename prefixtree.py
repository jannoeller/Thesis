def build_apta(
    l: int,
    words_by_label: list[list[str]],
    label_names: list[str] | None = None
) -> tuple[list[tuple[int, int, str]], dict[int, object], set[int]]:
    """
    Builds an APTA (Augmented Prefix Tree Acceptor) from labelled examples,
    supporting an arbitrary number of labels.

    Parameters:
        l: number of labels. Must equal len(words_by_label).
        words_by_label: list of length l, where words_by_label[i] is the
            list of words belonging to label i.
        label_names: optional list of length l giving a name for each label
            (e.g. ['accept', 'reject']).

    Returns:
        edges  : list of (from, to, char) transitions
        labels : dict mapping each labelled (terminal) state to its label
                 (either an int index or the corresponding entry of
                 label_names)
        states : set of all states appearing in the edge list
    """
    if len(words_by_label) != l:
        raise ValueError(f"Expected {l} label groups, got {len(words_by_label)}")
    if label_names is not None and len(label_names) != l:
        raise ValueError(f"label_names must have length {l}")

    # Trie structure: trie[state][char] = next_state
    trie: dict[int, dict[str, int]] = {0: {}}
    labels: dict[int, object] = {}
    state_counter = [0]  # use list so inner function can mutate it

    def get_or_create(state: int, ch: str) -> int:
        if state not in trie:
            trie[state] = {}
        if ch not in trie[state]:
            state_counter[0] += 1
            trie[state][ch] = state_counter[0]
        return trie[state][ch]

    def insert(word: str, label) -> None:
        current = 0
        for ch in word:
            current = get_or_create(current, ch)
        # Label the terminal state, checking for conflicts
        if current in labels and labels[current] != label:
            raise ValueError(
                f"Conflict: state {current} reached by '{word}' "
                f"already labelled '{labels[current]}', cannot relabel to '{label}'"
            )
        labels[current] = label

    for i, words in enumerate(words_by_label):
        label = label_names[i] if label_names is not None else i
        for word in words:
            insert(word, label)

    # Flatten trie into edge list and collect all states
    edges: list[tuple[int, int, str]] = []
    states: set[int] = {0}  # root always exists
    for frm, transitions in trie.items():
        for ch, to in transitions.items():
            edges.append((frm, to, ch))
            states.add(frm)
            states.add(to)

    return edges, labels, states