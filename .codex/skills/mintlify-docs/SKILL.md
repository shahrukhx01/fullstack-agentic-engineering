---
name: mintlify-docs
description: Create, review, and maintain high-quality Mintlify documentation following strict standards for accuracy, structure, and Git workflow.
metadata:
  short-description: Write accurate, consistent, and user-focused Mintlify MDX documentation.
---

Use this skill to **author and improve Mintlify documentation** while strictly following documentation standards, project conventions, and safe collaboration practices.

## What this skill does

- Produces Mintlify documentation using **MDX with required YAML frontmatter**
- Ensures documentation is accurate, minimal, and optimized for user success
- Maintains consistency with existing docs, patterns, and components
- Enforces disciplined Git workflows and documentation hygiene
- Prevents assumptions, duplication, and unverified content

## How to use this skill

When applying this skill, you should:

1. Ask clarifying questions before making assumptions  
2. Search existing documentation before adding new content  
3. Make the smallest reasonable change first  
4. Follow established structure, style, and workflow rules  
5. Push back on unclear or incorrect requirements with reasoning and sources  

## Documentation standards enforced by this skill

### Working relationship rules
- You may push back on ideas when it improves documentation quality
- Always cite sources and explain reasoning when pushing back
- Always ask for clarification rather than making assumptions
- Never lie, guess, or fabricate information

### Project context
- Documentation format: **MDX**
- Required frontmatter: **YAML**
- Configuration and navigation: **docs.json**
- UI and layout: **Mintlify components**

### Content strategy
- Document only what is necessary for user success
- Prioritize accuracy and usability over completeness
- Keep content evergreen where possible
- Avoid duplication unless there is a strategic reason
- Follow existing patterns for consistency
- Start with minimal, scoped changes

### Frontmatter requirements
Every MDX page must include:
- `title`: Clear, descriptive page title
- `description`: Concise summary for SEO and navigation

### Writing standards
- Second-person voice (“you”)
- Prerequisites at the start of procedural content
- All code examples must be tested before publishing
- Match existing style and formatting
- Include both basic and advanced use cases when relevant
- Language tags on all code blocks
- Alt text on all images
- Relative paths for all internal links

### Git workflow rules
- Never use `--no-verify`
- Ask how to handle uncommitted changes before starting
- Create a new branch if no suitable branch exists
- Commit frequently during development
- Never skip or disable pre-commit hooks

## What this skill must never do

- Skip YAML frontmatter on any MDX file
- Use absolute URLs for internal links
- Include untested code examples
- Make assumptions instead of asking for clarification
