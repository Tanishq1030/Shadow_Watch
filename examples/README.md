# Shadow Watch Examples

Example scripts showing Shadow Watch usage across different industries.

## Run Examples

```bash
# E-commerce example
python examples/ecommerce_example.py

# Social media example  
python examples/social_media_example.py

# Gaming example
python examples/gaming_example.py
```

## Examples Overview

### 📦 E-commerce (`ecommerce_example.py`)

**Use case:** Product recommendations, cart abandonment detection

**Tracks:**
- Product views
- Cart additions
- Purchases (with price/quantity metadata)

**Output:**
- User interest profile
- Product recommendations
- Cross-sell opportunities

---

### 📱 Social Media (`social_media_example.py`)

**Use case:** Bot detection, interest graphing

**Tracks:**
- Likes
- Follows
- Shares
- Searches

**Output:**
- Real user vs bot classification
- Behavior diversity analysis
- Engagement patterns

---

### 🎮 Gaming (`gaming_example.py`)

**Use case:** Playstyle analysis, item recommendations

**Tracks:**
- Character selection
- Level progression
- Item/equipment usage
- Skill activation

**Output:**
- Playstyle classification
- Item recommendations
- Progression analytics

---

## Pattern

All examples follow the same pattern:

```python
from shadowwatch import ShadowWatch

# Initialize (no license for local dev)
sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./demo.db",
    license_key=None  # Local dev mode
)

# Create tables
await sw.init_database()

# Track activity
await sw.track(
    user_id=123,
    entity_id="<ITEM>",     # Product/Post/Character
    action="<VERB>",         # View/Like/Equip
    metadata={}              # Optional context
)

# Get profile
profile = await sw.get_profile(user_id=123)

# Use insights for recommendations, personalization, etc.
```

---

## Industry Mappings

| Industry | entity_id | action | metadata |
|----------|-----------|--------|----------|
| **E-commerce** | `product_123` | `view`, `add_to_cart`, `purchase` | `price`, `quantity` |
| **Social Media** | `post_789`, `user_456` | `like`, `follow`, `share` | `platform` |
| **Gaming** | `character_warrior`, `level_5` | `select`, `complete`, `equip` | `time_taken`, `deaths` |
| **SaaS** | `feature_analytics` | `use`, `enable`, `create` | `duration` |
| **Streaming** | `movie_inception` | `watch`, `favorite`, `skip` | `watch_time` |

**Shadow Watch is domain-agnostic** - it works for any industry by adapting `entity_id` and `action` to your use case.
