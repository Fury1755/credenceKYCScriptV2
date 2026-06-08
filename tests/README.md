## Purpose
This is the testing module. I aim to learn how to write and implement unit tests for my code.

## Notes

### Why are unit tests important if I am going to refactor anyways?
1. They document and capture the current behaviour.
From inputs and outputs to error handling and edge cases. Even if you refactor/rewrite internally, their external behaviour shouldn't change. This prevents regressions.

2. They force you to write modular, testable code.
If a function is too hard to test, it is a sign of poor implementation.

### But doesn't that mean everytime I update a function's external behaviour, I have to rewrite tests?
Better to rewrite tests than to chase hidden bugs.