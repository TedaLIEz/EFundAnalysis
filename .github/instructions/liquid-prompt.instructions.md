---
applyTo: prompt/**/*.liquid
description: This rule is helpful for creating LLM prompt template based on Liquid syntax
---
# Liquid Prompt Template Guide for GitHub Copilot

This guide is for creating LLM prompt templates using Liquid syntax.

## Key Principles

- Use Liquid syntax for creating dynamic, reusable prompt templates.
- Store all prompt templates in the `prompt/` directory with `.liquid` file extension.
- Design templates to be flexible and configurable through variables.
- Use clear, descriptive variable names that indicate their purpose.
- Keep templates readable and well-structured with proper indentation.
- Document template variables and their expected types/values in comments.

## Liquid Syntax Basics

### Output Variables

Use `{{ }}` to output variable values:

```liquid
You are a helpful assistant named {{ assistant_name }}.
Today is {{ current_date }}.
```

### Tags and Logic

Use `{% %}` for logic operations (conditionals, loops, assignments):

```liquid
{% if user_role == "admin" %}
You have administrative privileges.
{% endif %}
```

### Comments

Use `{% comment %}` for comments:

```liquid
{% comment %}
This template is for financial analysis prompts.
Variables: user_query, context_data, analysis_type
{% endcomment %}
```

## Core Liquid Features for Prompt Templates

### Variables

- Access nested variables using dot notation: `{{ user.profile.name }}`
- Use default values: `{{ variable | default: "fallback" }}`
- Check if variable exists: `{% if variable %}...{% endif %}`

### Conditionals

```liquid
{% if condition %}
  Content when true
{% elsif other_condition %}
  Content when other condition is true
{% else %}
  Content when false
{% endif %}
```

### Loops

```liquid
{% for item in items %}
  - {{ item.name }}: {{ item.value }}
{% endfor %}
```

### Filters

Common filters for prompt templates:

- `capitalize`: Capitalize first letter
- `downcase`: Convert to lowercase
- `upcase`: Convert to uppercase
- `strip`: Remove leading/trailing whitespace
- `truncate`: Limit string length: `{{ text | truncate: 50 }}`
- `default`: Provide default value: `{{ variable | default: "N/A" }}`
- `join`: Join array elements: `{{ items | join: ", " }}`
- `size`: Get array/string length: `{{ items | size }}`

## Prompt Template Structure

### Standard Template Structure

```liquid
{% comment %}
Template: system_prompt.liquid
Purpose: System-level instructions for LLM
Variables:
  - role: The role of the assistant (e.g., "financial advisor", "data analyst")
  - tone: Communication tone (e.g., "professional", "friendly", "technical")
  - constraints: List of constraints or guidelines
{% endcomment %}

You are a {{ role | capitalize }} assistant.

{% if tone %}
Your communication style should be {{ tone }}.
{% endif %}

{% if constraints.size > 0 %}
Please follow these guidelines:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}
```

### Context-Aware Templates

```liquid
{% comment %}
Template: rag_query.liquid
Purpose: RAG query prompt with context
Variables:
  - context: Retrieved context documents
  - query: User query
  - max_length: Maximum response length
{% endcomment %}

Context information is below.
---------------------
{% for doc in context %}
{{ doc.content }}
{% endfor %}
---------------------

You are a helpful assistant. Use the above pieces of retrieved context to answer the question.

{% if max_length %}
Keep your answer concise, within {{ max_length }} words.
{% endif %}

Query: {{ query | strip }}

Answer:
```

### Multi-Turn Conversation Templates

```liquid
{% comment %}
Template: chat_with_history.liquid
Purpose: Chat prompt with conversation history
Variables:
  - system_message: System instructions
  - conversation_history: List of previous messages
  - current_message: Current user message
{% endcomment %}

{% if system_message %}
{{ system_message }}
{% endif %}

{% if conversation_history.size > 0 %}
Previous conversation:
{% for message in conversation_history %}
{% if message.role == "user" %}
User: {{ message.content }}
{% elsif message.role == "assistant" %}
Assistant: {{ message.content }}
{% endif %}
{% endfor %}
{% endif %}

Current message:
User: {{ current_message | strip }}

A:
```

## Best Practices

### 1. Variable Validation

Always provide defaults and validate variables:

```liquid
{% assign user_name = user.name | default: "Guest" %}
{% assign max_tokens = max_tokens | default: 1000 %}
```

### 2. Conditional Content

Use conditionals to make templates flexible:

```liquid
{% if include_examples %}
Here are some examples:
{% for example in examples %}
Example {{ forloop.index }}: {{ example }}
{% endfor %}
{% endif %}
```

### 3. Template Composition

Break complex templates into reusable components:

```liquid
{% comment %} Include system prompt {% endcomment %}
{% include 'system_prompt.liquid' role: role, tone: tone %}

{% comment %} Main content {% endcomment %}
{{ main_content }}
```

### 4. Error Handling

Handle missing or invalid data gracefully:

```liquid
{% if data and data.size > 0 %}
{% for item in data %}
{{ item }}
{% endfor %}
{% else %}
No data available.
{% endif %}
```

### 5. Formatting and Readability

- Use proper indentation for nested structures
- Add comments explaining template purpose and variables
- Keep lines readable (wrap long lines appropriately)
- Use whitespace to separate logical sections

## Common Patterns

### Pattern 1: System Instructions with Dynamic Role

```liquid
You are a {{ domain }} expert specializing in {{ specialization }}.

{% if expertise_areas.size > 0 %}
Your areas of expertise include:
{% for area in expertise_areas %}
- {{ area }}
{% endfor %}
{% endif %}

{% if constraints %}
Important constraints:
{{ constraints | join: "\n" }}
{% endif %}
```

### Pattern 2: Few-Shot Learning Template

```liquid
{% comment %}
Template: few_shot.liquid
Purpose: Few-shot prompt with examples
{% endcomment %}

Task: {{ task_description }}

Examples:
{% for example in examples %}
Input: {{ example.input }}
Output: {{ example.output }}
{% endfor %}

Now, solve the following:
Input: {{ user_input }}
Output:
```

### Pattern 3: Structured Output Template

```liquid
{% comment %}
Template: structured_output.liquid
Purpose: Request structured JSON output
{% endcomment %}

Analyze the following {{ data_type }} and provide your response in JSON format.

Data:
{{ data }}

{% if schema %}
Required JSON schema:
{{ schema }}
{% endif %}

Please provide your analysis as a valid JSON object:
```

## File Naming Conventions

- Use descriptive, lowercase names with underscores: `system_prompt.liquid`
- Group related templates: `rag_query.liquid`, `rag_summary.liquid`
- Use prefixes for organization: `chat_system.liquid`, `chat_user.liquid`
- Document template purpose in filename or comments

## Template Testing

When creating templates:

1. Test with various variable combinations
2. Verify conditionals work correctly
3. Check edge cases (empty arrays, null values, etc.)
4. Ensure output is properly formatted for LLM consumption
5. Validate that all required variables are documented

## Common Pitfalls to Avoid

- ❌ Don't use Liquid syntax that conflicts with LLM prompt formatting
- ❌ Don't create overly complex nested structures that are hard to debug
- ❌ Don't forget to handle missing variables (use defaults)
- ❌ Don't hardcode values that should be variables
- ❌ Don't create templates that are too long (consider breaking into components)

## Example: Complete RAG Template

```liquid
{% comment %}
Template: prompt/rag_complete.liquid
Purpose: Complete RAG prompt with context, query, and instructions
Variables:
  - context_docs: Array of context documents with 'content' field
  - user_query: User's question
  - response_style: Style of response (e.g., "concise", "detailed", "technical")
  - max_words: Maximum word count for response
{% endcomment %}

You are an expert assistant that answers questions based on provided context.

{% if context_docs.size > 0 %}
Context Information:
---------------------
{% for doc in context_docs %}
Document {{ forloop.index }}:
{{ doc.content | strip }}

{% endfor %}
---------------------
{% else %}
No context information available.
{% endif %}

Instructions:
- Use the context information above to answer the question
- {% if response_style == "concise" %}Provide a concise answer{% elsif response_style == "detailed" %}Provide a detailed, comprehensive answer{% else %}Provide a clear and informative answer{% endif %}
- {% if max_words %}Keep your response under {{ max_words }} words{% endif %}
- If the context doesn't contain enough information, say "I don't have enough information to answer this question"

Question: {{ user_query | strip }}

Answer:
```

Refer to the [official Liquid documentation](https://shopify.github.io/liquid/) for advanced features and syntax details.
