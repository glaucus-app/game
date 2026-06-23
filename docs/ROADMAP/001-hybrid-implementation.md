# 001-Hybrid-Implementation.md

## Prototype ActionType Enum

```python
from enum import Enum

class ActionType(Enum):
    INTERACT = "interact"        # Free-form MUD (text)
    ALLOCATE = "allocate"        # Civil-Sim resource allocation
    GOVERN = "govern"            # Civil-Sim policy decision
    COOPERATE = "cooperate"      # GT cooperation-dominant
    DEFECT = "defect"            # GT defection
    BID = "bid"                  # Economy bidding
    TRADE = "trade"              # Economy OTC trade
    INVEST = "invest"            # Economy/Civil-Sim investment
```

Each type maps to a JSON schema published at turn start and a resolution function in the corresponding sub-encounter engine.
