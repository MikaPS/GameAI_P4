# GameAI_P4

Our chosen hueristics:

We decided to focus on making sure no tool would be crafted twice (since that would be a waste of resources). We achieved that using 2 steps:

- First, we looked multiple aspects of the current task. We wanted to make sure that the type of task is `produce` and that the item is part of the `tools` list. Then, we used the state to check if we already produced the tool:

```python
if getattr(state, curr_task[2])[ID] >= 1:
```

- After that, we checked if we some of the future subtasks rely on making the same tool to produce the current tool. So, if we need the current tool to create the tool in the future (need wooden axe to get wood to make a wooden axe).

```python
for task in tasks[1:]:
    if len(task) >= 3 and curr_task[2] == task[2]:
```

Other than looking at the tools, we also sort the items in a way that supports the test cases. We reversed the order of the consume and have a different sorting for the tools.

```python
for item, value in reversed(list(consumes.items())):
```

We tried a lot of other different hueristics but the current ones lead to our best results!
We got inspiration for them from the manualHTN file who employs similar tactics.
