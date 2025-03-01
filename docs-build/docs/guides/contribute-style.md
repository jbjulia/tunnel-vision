---
sidebar_position: 2
---

# Contributing to Tunnel Vision

# Overview

This page contains the guidelines of the documentation and code for Tunnel
Vision.

The intended audience: **Everyone!**

## Writing and contributing

We welcome any contributions to the documentation or code. Contributions must
follow the same processes. Documentation contributions can be part of your code
contributions or separate documentation improvements.

The documentation follows the Google developer documentation style guide for any
new documentation:

* [Google developer documentation style guide](https://developers.google.com/style)
* [Word list](https://developers.google.com/style/word-list)
* [Style and tone](https://developers.google.com/style/tone)
* [Writing for a global audience](https://developers.google.com/style/translation)
* [Present tense](https://developers.google.com/style/tense)

The Google guidelines include more material than listed here, and are used as a
guide that enable easy decision making about proposed document changes.

## Viewing documentation

Tunnel Vision's documentation is written in Markdown.

You can build the docs locally, [learn how](./how-to-build.html)!

## Workflow

The procedure to add a documentation contribution is the same as for a code
contribution:

1. Request access to contribute.
2. Identify improvements or issues and use [GitHub
   Issues](https://github.com/jbjulia/tunnel-vision/issues) to add or work an
   issue.
3. Create a fork of the
   [Tunnel-Vision](https://github.com/jbjulia/tunnel-vision) repository.
4. Create a working branch in **your** fork. The branch should begin with your
   initials. For example:

```bash
git checkout -b jg/working-branch-name
```

5. Make changes and improvements.
6. Check and preview changes.
7. Commit changes. For example, `git commit -m "This is a comment"`. Do not
   include periods in your message.
8. Push them to your fork. `git push origin <branch name>`.
9. In a browser, open your fork in GitHub, create a GitHub pull request as
   described in the [GitHub
   documentation](https://docs.github.com/en/get-started).

> **Note:** Do not edit the files in the `build` folder only the markdown files.

## Pull request template

The following is a template to use when creating a Pull Request on GitHub:

```markdown
<!-- Tag someone from the team as a reviewer (Request reviewer) -->
<!-- This helps us find and prioritize your request more quickly -->

## Description

*
*

## Related issues and pull requests

*

## Types of changes
<!--- What types of work are covered in this PR? Put an `x` in all the boxes that apply: -->

- [ ] Existing documentation modification
- [ ] Create new documentation

## Checklist:
<!--- Go over all the following points, and put an `x` in all the boxes that apply -->

- [ ] Changes have been locally tested
- [ ] Line lengths do not exceed 80 characters

## Documentation resources

* https://developers.google.com/style

```
