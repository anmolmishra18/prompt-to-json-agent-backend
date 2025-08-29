# BHIV Core Integration Guide

## Agent Interface Compatibility

All agents follow BHIV Core standard:

```python
class Agent:
    def run(self, input_data) -> dict:
        # Process input and return structured output
        pass
```

## Available Agents

### PromptAgent
```python
from app.services.prompt_agent import PromptAgent
agent = PromptAgent()
result = agent.run("design a robot; priority: high")
# Returns: {"title": "...", "description": "...", "priority": "high"}
```

### Evaluator
```python
from app.services.evaluator import Evaluator
evaluator = Evaluator()
result = evaluator.run({"title": "Robot", "description": "Build robot", "priority": "high"})
# Returns: {"score": 0.85, "comments": "Good spec"}
```

### RLAgent
```python
from app.services.rl_agent import RLAgent
rl = RLAgent()
result = rl.run("design a robot", max_iters=2)
# Returns: [{"iteration_number": 1, "before_json": {...}, "after_json": {...}, ...}]
```

### FeedbackEngine
```python
from app.services.feedback import FeedbackEngine
feedback = FeedbackEngine()
result = feedback.run(evaluation_result, json_spec)
# Returns: ["Add title", "Expand description", ...]
```

## Orchestration Example

```python
# For Nisarg - How to orchestrate agents
from app.services.prompt_agent import PromptAgent
from app.services.evaluator import Evaluator
from app.services.rl_agent import RLAgent

def orchestrate_pipeline(prompt: str):
    # Step 1: Generate spec
    generator = PromptAgent()
    spec = generator.run(prompt)
    
    # Step 2: Evaluate
    evaluator = Evaluator()
    evaluation = evaluator.run(spec)
    
    # Step 3: Improve if needed
    if evaluation["score"] < 0.8:
        rl = RLAgent()
        iterations = rl.run(prompt, max_iters=3)
        return iterations[-1]["after_json"]
    
    return spec
```

## Database Schema (BHIV Bucket)

### Tables
- `reports`: Main JSON specs with metadata
- `evaluations`: Scoring results  
- `iterations`: RL improvement history
- `feedback_logs`: Generated feedback
- `hidg_values`: Daily reflection logs

### CRUD Operations
```python
from app import crud
from app.database import get_db

# Create report
report = crud.create_report(db, prompt_text="...", json_spec={...})

# Add evaluation
eval = crud.add_evaluation(db, report.id, score=0.85, comments="Good")

# Log HIDG values
hidg = crud.log_hidg(db, honesty="...", integrity="...", discipline="...", gratitude="...")
```