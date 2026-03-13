"""
Prompts Package Documentation

Location: backend/prompts/

Purpose:
========
Centralized location for all LLM system prompts used by AI agents.
Prompts are organized by agent type for better maintainability and clarity.

Structure:
==========

backend/prompts/
├── __init__.py              # Package initialization, exports all prompts
├── patient.py               # Patient agent system prompts
├── evaluation.py            # Evaluation agent system prompts
└── README.md                # This documentation

Prompts Included:
=================

1. PATIENT AGENT PROMPTS (patient.py)
   ├── PATIENT_AGENT_SYSTEM_PROMPT
   │   └── Core system instructions for patient simulation
   │       - Never reveals disease name
   │       - Answers based on actual symptoms
   │       - Natural, conversational tone
   │
   └── PATIENT_BACKGROUND_TEMPLATE
       └── Patient context template
           - Demographic info (age, gender)
           - Personal symptoms list
           - Severity and duration
           - Instructions for authentic responses

2. EVALUATION AGENT PROMPTS (evaluation.py)
   ├── EVALUATION_AGENT_SYSTEM_PROMPT
   │   └── Core system instructions for evaluation
   │       - 4-dimensional scoring framework
   │       - Scoring criteria explained (0-10 each)
   │       - Evaluation rules and principles
   │       - JSON output format
   │
   └── EVALUATION_PROMPT_TEMPLATE
       └── Specific evaluation prompt template
           - Case context (disease, symptoms, treatments)
           - Conversation history
           - Evaluation questions
           - JSON response requirements

Usage:
======

Import all prompts via package __init__.py:

    from backend.prompts import (
        PATIENT_AGENT_SYSTEM_PROMPT,
        PATIENT_BACKGROUND_TEMPLATE,
        EVALUATION_AGENT_SYSTEM_PROMPT,
        EVALUATION_PROMPT_TEMPLATE,
    )

Or import specific modules:

    from backend.prompts.patient import PATIENT_AGENT_SYSTEM_PROMPT
    from backend.prompts.evaluation import EVALUATION_AGENT_SYSTEM_PROMPT

Usage in Agents:
================

PATIENT AGENT (backend/agents/patient_agent.py):
    prompt = ChatPromptTemplate.from_messages([
        ("system", PATIENT_AGENT_SYSTEM_PROMPT + "\n\n" + background),
        ("human", "{input}")
    ])

EVALUATION AGENT (backend/agents/evaluation_agent.py):
    evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(
        disease=disease,
        symptoms=", ".join(symptoms),
        ...
    )
    response = llm.invoke(evaluation_prompt)

Structure Benefits:
===================

✓ Organized: Prompts grouped by agent type
✓ Maintainable: Easy to find and update specific prompts
✓ Scalable: Simple to add new agents/prompts
✓ Clear: Each file has single responsibility
✓ Documented: Inline comments in each prompt
✓ Importable: Central __init__.py for easy access

Adding New Prompts:
===================

When adding a new agent with prompts:

1. Create new file (e.g., my_agent.py)
2. Define your prompts (e.g., MY_AGENT_SYSTEM_PROMPT)
3. Add imports to __init__.py
4. Update __all__ list in __init__.py
5. Import in your agent module

Example:

    # backend/prompts/my_agent.py
    MY_AGENT_SYSTEM_PROMPT = """Your system instructions here"""
    MY_AGENT_TEMPLATE = """Your template here"""

    # Update __init__.py
    from backend.prompts.my_agent import (
        MY_AGENT_SYSTEM_PROMPT,
        MY_AGENT_TEMPLATE,
    )
    
    __all__ = [
        ...,
        "MY_AGENT_SYSTEM_PROMPT",
        "MY_AGENT_TEMPLATE",
    ]

Prompt Design Guidelines:
=========================

When writing prompts:

1. Be Clear: Use simple, direct language
2. Be Specific: Give detailed instructions
3. Use Examples: Show what you want
4. Use Structure: Format with numbered lists, sections
5. Set Constraints: "ONLY respond with JSON", etc.
6. Be Consistent: Use consistent terminology

Example Pattern:

    """ACTION: [What to do]
    
    RULES:
    1. [Important rule]
    2. [Another rule]
    
    FORMAT:
    [Expected output format]
    
    [Additional context or examples]
    """

Versioning and Testing:
=======================

To test a modified prompt:

1. Update the prompt in the .py file
2. Test with your agent
3. Verify the LLM response
4. Check performance metrics
5. Commit changes with description

Example workflow:

    def test_patient_prompt():
        from backend.prompts import PATIENT_AGENT_SYSTEM_PROMPT
        agent = PatientAgent(disease_info)
        response = agent.respond_to_doctor("How long have symptoms?")
        assert len(response) > 0
        assert agent.disease_name not in response.lower()

Development Notes:
==================

Current Prompts:

1. PATIENT_AGENT_SYSTEM_PROMPT
   - 300 words baseline instructions
   - Emphasis on authenticity and symptom consistency
   - Trust in LLM to generate natural responses

2. PATIENT_BACKGROUND_TEMPLATE
   - 150 words template
   - Customizable for each case
   - Provides context without revealing diagnosis

3. EVALUATION_AGENT_SYSTEM_PROMPT
   - 400 words with 4-D scoring framework
   - Explicit criteria for each dimension
   - JSON output format requirements

4. EVALUATION_PROMPT_TEMPLATE
   - 200 words specific prompt
   - Case-specific information injected
   - 9 specific evaluation questions

All prompts follow best practices:
✓ Clear structure and formatting
✓ Explicit constraints and rules
✓ Example outputs where applicable
✓ Balanced detail (specific but not verbose)

Performance Tips:
=================

- Shorter prompts = faster LLM responses
- More examples = better prompt adherence
- Clearer structure = higher quality outputs
- Constraints = fewer errors and invalid responses

FAQs:
=====

Q: Why separate prompts into different files?
A: Better organization, easier to maintain and modify specific agent prompts.

Q: Can I import directly from files instead of __init__.py?
A: Yes, both work. Using __init__.py is preferred for cleaner imports.

Q: How do I add a parameter to a prompt?
A: Use string formatting: TEMPLATE.format(param_name=value)

Q: How do I version prompts?
A: Keep old versions as comments or in separate branches.

Q: What if I need different prompts for different scenarios?
A: Create multiple constants (e.g., PATIENT_BRIEF_PROMPT, PATIENT_DETAILED_PROMPT)

Next Steps:
===========

1. Review prompts in development
2. Test with real LLM responses
3. Gather feedback from users
4. Iterate and improve prompts
5. Document any changes

For more information, see:
- backend/agents/patient_agent.py
- backend/agents/evaluation_agent.py
- EVALUATION_PROMPT_TEMPLATE usage in evaluation_agent.py
"""
