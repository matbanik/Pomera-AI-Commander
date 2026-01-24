# Smart Diff Test Cases
# Copy these into the Before/After panes to test modes

## TEST 1: Ignore Order (should show difference when OFF, identical when ON)
### Before:
{"tags": ["python", "javascript", "go"]}

### After:
{"tags": ["go", "python", "javascript"]}

### Expected Results:
- Ignore Order OFF: Shows "modified" (order changed)
- Ignore Order ON: Shows "No differences" (same items)

---

## TEST 2: Case Sensitivity (Semantic vs Strict)
### Before:
{"name": "John", "city": "NEW YORK"}

### After:
{"name": "john", "city": "new york"}

### Expected Results:
- Semantic mode: Shows "No differences" (ignores case)
- Strict mode: Shows "modified" (case sensitive)

---

## TEST 3: Combined (Order + Case)
### Before:
{"users": ["Alice", "Bob", "Charlie"]}

### After:
{"users": ["charlie", "alice", "bob"]}

### Expected Results:
- Semantic + Ignore Order OFF: Shows "modified" (case + order)
- Semantic + Ignore Order ON: Shows "No differences" (ignores both)
- Strict + Ignore Order ON: Shows "modified" (detects case, ignores order)
- Strict + Ignore Order OFF: Shows "modified" (detects both)

---

## TEST 4: Value Changes (Always Detected)
### Before:
{"price": 100, "status": "active"}

### After:
{"price": 150, "status": "active"}

### Expected Results:
- ANY mode: Shows "modified" (value actually changed)
