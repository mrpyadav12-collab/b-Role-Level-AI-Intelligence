# Design decisions and trade-offs

## Trade-off: AI interpretation vs deterministic scoring
The app uses AI to interpret and explain work, but uses deterministic logic to calculate the final score.

### Why this was selected
- better consistency
- easier to explain
- easier to test
- reduces risk of model drift
- more transparent for evaluator review

### Alternative considered
Let LLM directly calculate the whole role score.

### Why it was rejected
- less auditable
- harder to test
- less deterministic
- fragile to prompt changes

## AI fallback strategy
If AI is unavailable, the app still works using a heuristic fallback model. This preserves functionality without fabricating unsupported outputs.

## Domain choice
Banking was selected because it is realistic, structured, and easy to explain in a live demo.
