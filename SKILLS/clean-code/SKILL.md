---
name: clean-code
description: >
  Reviews, rewrites, and teaches clean code principles to make any codebase more readable,
  maintainable, and scalable. Use this skill WHENEVER the user asks to: review or improve
  code quality, refactor messy or hard-to-read code, name things better (variables, functions,
  classes), reduce function complexity, improve code structure or readability, apply SOLID
  principles, fix long functions or deeply nested logic, or asks "is this code clean?",
  "how can I improve this code?", "what's wrong with this code?". Also trigger when the user
  shares code and wants feedback before merging or publishing. Covers Python, TypeScript,
  JavaScript, Go, Java, and general language-agnostic principles.
---

# Clean Code Skill

Reviews code and teaches clean code principles with concrete before/after rewrites.
Always shows the problem, explains why it matters, then shows the fix.

---

## Core philosophy

Clean code has one job: **be obvious to the next person who reads it** — including
the author six months later. Performance and cleverness are secondary. Readability
is the primary design constraint.

Three questions to ask about any piece of code:
1. Can I understand what this does in under 10 seconds?
2. Can I change one thing without breaking something unexpected?
3. Does the name tell me the intent, not the implementation?

---

## Workflow

### Step 1 — Read before judging

When the user shares code, scan it first and identify which violations are present.
Don't list every principle mechanically — only address what's actually wrong.

Rank issues by impact:
- **Critical** — makes the code dangerous to change (hidden side effects, misleading names,
  god functions, deep coupling)
- **Major** — slows down reading significantly (long functions, poor names, deep nesting)
- **Minor** — style polish (magic numbers, redundant comments, inconsistent naming)

Fix critical and major first. Only mention minor if the other two are clean.

### Step 2 — Show, don't lecture

For every issue found, provide:
1. The **problematic snippet** (exact excerpt, not paraphrased)
2. The **problem in one sentence** — what makes it hard to read or change
3. The **rewritten version** — clean, working code
4. A **one-line explanation** of what changed and why

Never list principles without showing them applied to the user's actual code.

### Step 3 — Summarize the pattern

After individual fixes, state the underlying principle in one sentence so the user
can recognize the same smell in other files.

---

## The principles — with before/after patterns

### 1. Naming — intention over implementation

Names should answer "what does this do / represent?" not "how is it implemented?".

**Variables and constants:**
```python
# BAD — what is d? what is 86400?
d = n * 86400
if d > 30:
    send()

# GOOD
SECONDS_PER_DAY = 86400
subscription_age_in_days = trial_days * SECONDS_PER_DAY
if subscription_age_in_days > TRIAL_EXPIRY_DAYS:
    send_expiry_notification()
```

**Functions — use verb + noun, describe the outcome:**
```python
# BAD — "process" and "handle" say nothing
def process(data): ...
def handle_it(x, flag): ...

# GOOD — reads like a sentence
def validate_user_email(email: str) -> bool: ...
def send_password_reset_email(user: User) -> None: ...
```

**Booleans — always use is/has/can/should prefix:**
```python
# BAD
if user.active and not user.locked:

# GOOD
if user.is_active and not user.is_locked:
```

**Avoid noise words**: `Manager`, `Helper`, `Processor`, `Handler`, `Utils` in class names
signal the class has no clear identity. Name it after what it actually does.

---

### 2. Functions — small, one job, one level of abstraction

**The single responsibility rule for functions**: if you need "and" or "or" to describe
what a function does, it does too much.

**The 20-line guideline**: a function that doesn't fit on one screen is usually doing
too much. Not a hard rule — but a useful smell detector.

```python
# BAD — this function validates, transforms, persists, and notifies
def save_user(data):
    if not data.get('email') or '@' not in data['email']:
        raise ValueError('bad email')
    if len(data.get('password', '')) < 8:
        raise ValueError('short password')
    data['email'] = data['email'].lower().strip()
    data['password'] = hashlib.sha256(data['password'].encode()).hexdigest()
    db.execute("INSERT INTO users ...", data)
    requests.post(SLACK_URL, json={"text": f"New user: {data['email']}"})
    return data

# GOOD — each function has one job, composes cleanly
def save_user(data: dict) -> User:
    validated = validate_registration_data(data)
    normalized = normalize_user_fields(validated)
    user = persist_user(normalized)
    notify_team_of_new_signup(user)
    return user

def validate_registration_data(data: dict) -> dict: ...
def normalize_user_fields(data: dict) -> dict: ...
def persist_user(data: dict) -> User: ...
def notify_team_of_new_signup(user: User) -> None: ...
```

**One level of abstraction per function** — don't mix high-level orchestration with
low-level implementation detail in the same function:

```python
# BAD — mixes orchestration with string parsing detail
def process_invoice(invoice):
    total = 0
    for line in invoice.split('\n'):
        parts = line.strip().split(',')
        if len(parts) == 3:
            total += float(parts[2])
    send_email(f"Total: {total}")

# GOOD — high level reads like prose
def process_invoice(invoice: str) -> None:
    line_items = parse_invoice_lines(invoice)
    total = calculate_total(line_items)
    send_invoice_summary_email(total)
```

---

### 3. Arguments — fewer is better

**0-2 arguments**: ideal. Easy to call, easy to test.
**3 arguments**: acceptable, consider grouping.
**4+ arguments**: almost always a sign the function does too much, or needs a data class.

```python
# BAD — 6 arguments, impossible to call without looking at the signature every time
def create_report(title, author, date, format, include_charts, send_email):
    ...

# GOOD — group related args into a config object
@dataclass
class ReportConfig:
    title: str
    author: str
    date: date
    format: str = "pdf"
    include_charts: bool = True
    send_email: bool = False

def create_report(config: ReportConfig) -> Report: ...
```

**Boolean flags as arguments are a red flag** — they mean the function has two
behaviors and should be split:

```python
# BAD — caller has no idea what True means without reading the function
render_page(user, True)

# GOOD — intent is explicit
render_page_with_sidebar(user)
render_page_without_sidebar(user)
```

---

### 4. Comments — explain why, not what

If you need a comment to explain what the code does, rewrite the code until it's
self-explanatory. Comments should explain *why* a decision was made, not describe
the mechanics.

```python
# BAD — comment restates the code
# increment i by 1
i += 1

# BAD — comment compensates for a bad name
# check if user can access premium features
if user.type == 2 and user.created_at < cutoff:

# GOOD — code is self-explanatory, comment explains the non-obvious why
if user.is_premium_subscriber and user.joined_before_pricing_change:
    # Grandfathered users keep the old rate per billing agreement 2023-Q2
    apply_legacy_pricing(user)
```

**Delete these comment types entirely:**
- `# end of loop`, `# end of function` — structure the code instead
- `# TODO` older than a sprint — make it a ticket or delete it
- Commented-out code — use git, not comments, for history

---

### 5. Error handling — explicit and specific

```python
# BAD — swallows all errors silently
try:
    result = fetch_user(user_id)
except:
    pass

# BAD — catches too broadly, loses context
try:
    result = fetch_user(user_id)
except Exception as e:
    print(f"Error: {e}")
    return None

# GOOD — specific exception, logged with context, re-raised or handled explicitly
try:
    result = fetch_user(user_id)
except UserNotFoundError:
    logger.warning("User not found", user_id=user_id)
    raise
except DatabaseConnectionError as e:
    logger.error("DB unavailable during user fetch", user_id=user_id, error=str(e))
    raise ServiceUnavailableError("Could not fetch user") from e
```

**Never return None to signal failure** — raise a specific exception or use a
Result/Option type. `None` forces every caller to add a null check and silently
propagates bad state.

---

### 6. Avoid deep nesting — early return / guard clauses

Deep nesting is the #1 cause of "I need to re-read this three times to understand it".
The fix is almost always: invert the condition and return early.

```python
# BAD — "arrow code", reader must track 4 levels of state
def process_order(order):
    if order:
        if order.is_paid:
            if order.items:
                if not order.is_shipped:
                    ship(order)
                else:
                    log("already shipped")
            else:
                log("no items")
        else:
            log("not paid")
    else:
        log("no order")

# GOOD — guard clauses, happy path flows straight down
def process_order(order: Order) -> None:
    if not order:
        logger.warning("process_order called with no order")
        return
    if not order.is_paid:
        logger.info("Order not yet paid", order_id=order.id)
        return
    if not order.items:
        logger.warning("Order has no items", order_id=order.id)
        return
    if order.is_shipped:
        logger.info("Order already shipped", order_id=order.id)
        return

    ship(order)
```

---

### 7. Magic numbers and strings — named constants only

```python
# BAD — what is 7? what is 0.15? what is "admin"?
if days > 7:
    charge(total * 0.15)
if user.role == "admin":
    ...

# GOOD
FREE_TRIAL_DAYS = 7
LATE_FEE_RATE = 0.15
ADMIN_ROLE = "admin"  # or better: an Enum

if days > FREE_TRIAL_DAYS:
    charge(total * LATE_FEE_RATE)
if user.role == UserRole.ADMIN:
    ...
```

---

### 8. Class design — SOLID at a glance

**Single Responsibility**: one class, one reason to change.
```python
# BAD — UserManager does auth, persistence, AND email. Change any one, risk all three.
class UserManager:
    def login(self): ...
    def save_to_db(self): ...
    def send_welcome_email(self): ...

# GOOD — each class has one owner
class AuthService:
    def login(self, credentials: Credentials) -> Session: ...

class UserRepository:
    def save(self, user: User) -> None: ...

class UserNotificationService:
    def send_welcome_email(self, user: User) -> None: ...
```

**Open/Closed**: extend behavior without modifying existing code — use abstractions.
```python
# BAD — adding a new format requires modifying this function
def export_report(report, format):
    if format == "pdf":   ...
    elif format == "csv": ...
    elif format == "xlsx": ...  # keep adding ifs forever

# GOOD — add formats by adding new classes, not modifying existing code
class ReportExporter(ABC):
    @abstractmethod
    def export(self, report: Report) -> bytes: ...

class PdfExporter(ReportExporter): ...
class CsvExporter(ReportExporter): ...
```

**Dependency Inversion**: depend on abstractions, not concretions.
```python
# BAD — hard-coded dependency, impossible to test or swap
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # locked in forever

# GOOD — inject the dependency, test with a mock
class OrderService:
    def __init__(self, db: DatabaseProtocol):
        self.db = db
```

---

## Language-specific notes

Apply all principles above universally, then add these per language:

**Python**: use `dataclasses` or `pydantic` instead of dicts for structured data.
Use type hints everywhere. Prefer `pathlib` over `os.path`. Use `Enum` for fixed sets
of values. Use context managers (`with`) for resources.

**TypeScript/JavaScript**: use `const` by default, `let` only when reassignment is
needed, never `var`. Prefer `interface` over `type` for object shapes. Use optional
chaining (`?.`) and nullish coalescing (`??`) over manual null checks. Async/await
over raw Promise chains.

**Go**: errors are values — always handle them explicitly, never `_`. Keep structs
small and focused. Use interfaces for dependency inversion. Package names are singular
and lowercase.

---

## Output format

When reviewing user code:

1. **Summary** — 1-2 sentences on the overall state of the code
2. **Issues found** — grouped by Critical / Major / Minor, each with:
   - The exact problematic snippet
   - One-sentence problem statement
   - Rewritten version
   - One-line explanation of the change
3. **Clean version** — if the function/file is short enough, provide a full rewrite
   at the end combining all fixes
4. **Pattern to remember** — one sentence naming the underlying principle

When teaching (no code shared):
- Lead with the principle name and a one-sentence definition
- Show a minimal before/after pair
- State when to apply it and when NOT to (over-engineering is a real risk)
