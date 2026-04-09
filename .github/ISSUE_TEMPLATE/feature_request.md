---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: Mukhopadhyay

---

> Please check existing issues before submitting new requests.
> Well-structured feature requests are more likely to be implemented 🚀

### 1. What problem are you trying to solve?
Describe the use-case clearly.

Example:
_"I want to generate realistic user profiles with nested address + company data, but currently I have to combine multiple generators manually"_

---

### 2. What would you like to see added?
Describe the feature or API you'd like.

Example:
- New generator (e.g. `dummy.company.name()`)
- Support for a new data type
- Better integration with Pydantic models
- Performance improvement
- New configuration option

---

### 3. Proposed API (if applicable)
Show how you'd like to use this feature.

```python
from pyfake import fake

fake.company.name()
fake.user(profile=True)
```

### 4. How is this different from existing functionality?
Explain why current features are not sufficient.

### 5. Example output (if applicable)
Show what kind of data you'd expect.
```json
{
    "company": "Company Inc.",
    "role": "Software Engineer"
}
```

### Additional context
* Links to similar features (e.g., Faker)
* Screenshots/references
* Any edge cases or constraints
