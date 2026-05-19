---
name: dry-principles
description: >
  Identifies and eliminates code duplication by applying DRY (Don't Repeat Yourself)
  and related principles: abstraction, single source of truth, and reusable design.
  Use this skill WHENEVER the user asks to: remove duplicated code, refactor repeated
  logic, create reusable functions or components, identify copy-paste patterns, apply
  DRY or SSOT principles, reduce boilerplate, generalize repeated patterns, or asks
  "this code is repetitive", "I keep writing the same thing", "how do I avoid repeating
  this?", "should I extract this?". Also trigger when reviewing code that has obvious
  copy-paste sections, near-identical functions, or duplicated business rules. Covers
  Python, TypeScript, JavaScript, and language-agnostic patterns.
---

# DRY Principles Skill

Finds duplication, explains the cost, and provides the right abstraction to eliminate it.
The goal is always the *right* abstraction — not the *maximum* abstraction.

---

## Core philosophy

DRY stands for **Don't Repeat Yourself**: every piece of knowledge or logic should
have a single, unambiguous, authoritative representation in the codebase.

The real cost of duplication is not the extra lines — it's the **maintenance trap**:
when a rule changes, you must find and update every copy. Miss one and you have a bug.

But over-abstraction is just as dangerous as duplication. The goal is not zero
repetition — it's **zero duplication of logic and knowledge**. Similar-looking code
that represents different concepts should stay separate.

The test before extracting anything:
> "If this rule changes, how many places do I have to update?"
> If the answer is more than one — extract. If the answer is one — leave it alone.

---

## Workflow

### Step 1 — Identify the type of duplication

Not all repetition is the same. Diagnose it before prescribing a fix:

| Type | Example | Fix |
|------|---------|-----|
| **Exact duplication** | Same code copy-pasted verbatim | Extract a function |
| **Near duplication** | Same logic with tiny variations | Parameterize the function |
| **Conceptual duplication** | Same business rule in different forms | Single source of truth |
| **Structural duplication** | Same boilerplate pattern repeated | Helper, decorator, or base class |
| **Accidental similarity** | Looks the same but means different things | Leave it — do NOT abstract |

### Step 2 — Apply the right fix

Match the duplication type to the correct abstraction level. Don't reach for the
most complex tool first.

**Hierarchy of abstractions** (use the simplest that works):
1. Extract a **function** — for repeated logic blocks
2. Extract a **constant** — for repeated values or strings
3. Extract a **class or module** — for repeated stateful behavior
4. Use a **decorator / middleware** — for repeated cross-cutting concerns
5. Use a **generic / template** — for repeated structural patterns across types

### Step 3 — Show before/after with the cost made explicit

For every fix, show:
1. The duplicated code (both/all copies)
2. The specific cost: "if X changes, you update N files"
3. The extracted version
4. How callers look after the refactor

---

## Patterns and fixes

### Pattern 1 — Exact duplication → extract a function

The most common case. Same block appears 2+ times.

```python
# BAD — same validation logic in two routes
@app.post("/users")
def create_user(data: dict):
    if not data.get("email") or "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")
    if len(data.get("password", "")) < 8:
        raise HTTPException(400, "Password too short")
    # ... create user

@app.post("/admin/users")
def create_admin_user(data: dict):
    if not data.get("email") or "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")
    if len(data.get("password", "")) < 8:
        raise HTTPException(400, "Password too short")
    # ... create admin user

# Cost: password policy changes → update 2 places. Add a new field → update 2 places.

# GOOD — single source of truth for validation
def validate_user_credentials(data: dict) -> None:
    """Raises HTTPException if credentials are invalid."""
    if not data.get("email") or "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")
    if len(data.get("password", "")) < 8:
        raise HTTPException(400, "Password too short")

@app.post("/users")
def create_user(data: dict):
    validate_user_credentials(data)
    # ... create user

@app.post("/admin/users")
def create_admin_user(data: dict):
    validate_user_credentials(data)
    # ... create admin user
```

---

### Pattern 2 — Near duplication → parameterize

Functions that are 90% identical with one variation. The variation becomes a parameter.

```python
# BAD — three nearly identical functions
def get_active_users(db):
    return db.query(User).filter(User.status == "active").all()

def get_banned_users(db):
    return db.query(User).filter(User.status == "banned").all()

def get_pending_users(db):
    return db.query(User).filter(User.status == "pending").all()

# Cost: adding pagination, sorting, or a new field → update 3 functions.

# GOOD — parameterize the variation
def get_users_by_status(db, status: UserStatus) -> list[User]:
    return db.query(User).filter(User.status == status).all()

# Callers are just as readable:
active_users  = get_users_by_status(db, UserStatus.ACTIVE)
banned_users  = get_users_by_status(db, UserStatus.BANNED)
pending_users = get_users_by_status(db, UserStatus.PENDING)
```

**TypeScript variant:**
```typescript
// BAD
const formatUserName = (user: User) => `${user.firstName} ${user.lastName}`;
const formatAdminName = (admin: Admin) => `${admin.firstName} ${admin.lastName}`;
const formatGuestName = (guest: Guest) => `${guest.firstName} ${guest.lastName}`;

// GOOD — generic over any object with a name
const formatFullName = (person: { firstName: string; lastName: string }): string =>
  `${person.firstName} ${person.lastName}`;
```

---

### Pattern 3 — Conceptual duplication → single source of truth

The most dangerous type. The same **business rule** expressed in multiple places,
possibly in different forms. No obvious copy-paste, but they all encode the same fact.

```python
# BAD — "what makes a user premium?" is scattered across the codebase
# In api/routes.py:
if user.plan == "pro" or user.plan == "enterprise":
    allow_export()

# In services/billing.py:
if user.subscription_type in ["pro", "enterprise"]:
    apply_discount()

# In workers/email.py:
if user.plan != "free":
    send_premium_newsletter()

# Cost: adding a new "team" plan → hunt through the entire codebase for every check.
# Miss one → "team" users get the wrong newsletter.

# GOOD — the rule lives in one place
class User:
    @property
    def is_premium(self) -> bool:
        """Single source of truth for premium status."""
        return self.plan in {Plan.PRO, Plan.ENTERPRISE}

# All callers use the same concept:
if user.is_premium:
    allow_export()

if user.is_premium:
    apply_discount()

if user.is_premium:
    send_premium_newsletter()

# Adding "team" plan: update User.is_premium in one place. Done.
```

---

### Pattern 4 — Structural duplication → decorator or middleware

Repeated scaffolding around different logic: logging, auth checks, error handling,
retry logic, timing. Extract the scaffolding, leave the logic.

```python
# BAD — logging + timing duplicated across every service method
class OrderService:
    def create_order(self, data):
        logger.info("create_order started")
        start = time.time()
        try:
            result = self._do_create_order(data)
            logger.info(f"create_order completed in {time.time()-start:.2f}s")
            return result
        except Exception as e:
            logger.error(f"create_order failed: {e}")
            raise

    def cancel_order(self, order_id):
        logger.info("cancel_order started")
        start = time.time()
        try:
            result = self._do_cancel_order(order_id)
            logger.info(f"cancel_order completed in {time.time()-start:.2f}s")
            return result
        except Exception as e:
            logger.error(f"cancel_order failed: {e}")
            raise

# GOOD — extract the scaffolding into a decorator
import functools

def logged_operation(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"{func.__name__} started")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed in {time.time()-start:.2f}s")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper

class OrderService:
    @logged_operation
    def create_order(self, data): ...

    @logged_operation
    def cancel_order(self, order_id): ...
```

**TypeScript variant — higher-order function:**
```typescript
// Wraps any async operation with retry logic
const withRetry = <T>(
  operation: () => Promise<T>,
  maxAttempts = 3,
  delayMs = 1000
): Promise<T> => { ... }

// Instead of copy-pasting retry logic into every API call:
const user    = await withRetry(() => fetchUser(id));
const orders  = await withRetry(() => fetchOrders(userId));
const invoice = await withRetry(() => generateInvoice(orderId));
```

---

### Pattern 5 — Configuration duplication → config objects

Repeated literals that represent configuration, not logic.

```python
# BAD — API settings scattered everywhere
response = requests.get(
    "https://api.example.com/v2/users",
    headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    timeout=30
)

response = requests.post(
    "https://api.example.com/v2/orders",
    headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    timeout=30
)

# GOOD — one configured client
class ApiClient:
    BASE_URL = "https://api.example.com/v2"
    TIMEOUT = 30

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    def get(self, path: str, **kwargs):
        return self.session.get(f"{self.BASE_URL}{path}", timeout=self.TIMEOUT, **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f"{self.BASE_URL}{path}", timeout=self.TIMEOUT, **kwargs)

# Callers:
client = ApiClient(token)
client.get("/users")
client.post("/orders", json=order_data)
```

---

### Pattern 6 — Data duplication → derived values

When the same information is stored in two places, one will eventually be wrong.
Always derive from a single source.

```python
# BAD — total is stored alongside items, they can diverge
@dataclass
class Cart:
    items: list[CartItem]
    total: float          # duplicates information already in items

cart.items.append(item)
cart.total += item.price  # easy to forget this. Now they're out of sync.

# GOOD — total is always derived, never stored separately
@dataclass
class Cart:
    items: list[CartItem]

    @property
    def total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

# total is always correct, by construction. No sync needed.
```

---

### Pattern 7 — Test duplication → fixtures and factories

Repeated setup code across tests is duplication too — and it's the most commonly
ignored kind.

```python
# BAD — user creation repeated in every test
def test_user_can_login():
    user = User(email="test@example.com", password=hash("secret"), is_active=True)
    db.save(user)
    ...

def test_user_can_update_profile():
    user = User(email="test@example.com", password=hash("secret"), is_active=True)
    db.save(user)
    ...

# GOOD — factory function or fixture creates the canonical test user
# conftest.py
@pytest.fixture
def active_user(db) -> User:
    return UserFactory.create(is_active=True)

# Tests just declare what they need:
def test_user_can_login(active_user): ...
def test_user_can_update_profile(active_user): ...

# Need a premium user? Extend the factory, not the test:
@pytest.fixture
def premium_user(db) -> User:
    return UserFactory.create(is_active=True, plan=Plan.PRO)
```

---

## When NOT to apply DRY

This is as important as knowing when to apply it.

**Accidental similarity** — two things that look the same but represent different
concepts. Merging them creates false coupling: changing one forces a change in the other
even when they should diverge.

```python
# These look the same — should they be merged?
def calculate_shipping_cost(weight, distance): ...
def calculate_insurance_cost(weight, value): ...

# NO. They share a parameter name but represent different business domains.
# Shipping cost and insurance cost will evolve differently.
# Merging them would make both harder to change.
```

**The rule**: before abstracting, ask "do these represent the same *concept*?".
If yes — extract. If they just look similar — leave them separate.

**Too early abstraction** — if you've seen the pattern exactly twice, consider waiting.
Three occurrences is a much stronger signal that the abstraction is real and stable.
Abstracting at two occurrences often produces the wrong abstraction because you haven't
seen enough variation yet.

**WET is sometimes fine** — Write Everything Twice. Two short, clear, concrete functions
are often better than one abstract, parameterized, hard-to-understand function that tries
to cover both cases.

---

## The Rule of Three

A practical heuristic for when to extract:
- **Once**: write it inline
- **Twice**: note the duplication, but leave it — you don't know the full shape yet
- **Three times**: extract — the pattern is real

---

## Output format

When reviewing user code for DRY violations:

1. **Duplication inventory** — list each instance of duplication found, typed by category
   (exact / near / conceptual / structural)
2. **Cost statement** — for each: "if X changes, you update N files/functions"
3. **Proposed abstraction** — the specific function/class/decorator to extract, with
   the full before/after code
4. **Caller view** — show how the calling code looks after the refactor (it should
   be simpler or equally readable — if it's more complex, reconsider the abstraction)
5. **Warning if over-engineering** — if the code looks similar but represents different
   concepts, say so explicitly and recommend leaving it as-is

When teaching (no code shared):
- Name the pattern, show the minimal before/after, state the cost of not fixing it,
  then state when NOT to apply the fix
