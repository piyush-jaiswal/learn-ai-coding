---
name: create-and-validate
description: Add a SlopLang example program with an exact-output test, then run the repo's validation checks
---

# Create and Validate

Use when asked to add coverage for a SlopLang language feature and verify the repository in one
pass.

## 1. Create the test program

Load the `create-test-program` skill and follow it. It is the source of truth for reading the spec,
writing the example, capturing exact output, adding the test, and verifying that test.

## 2. Validate

Load the `validate` skill and follow it. It is the source of truth for which checks to run, in what
order, and how to report them.

Do not restate or reorder either skill's steps here. If step 1 stops without producing a test (for
example, because `docs/spec.md` does not describe the feature), report that and skip step 2.
