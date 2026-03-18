"""Tool schemas — what the LLM sees for the hermes-loop plugin."""

LOOP_STATUS = {
    "name": "loop_status",
    "description": (
        "Check the current status of the task execution loop. "
        "Returns whether tasks remain, if completion is reached, and any blocking issues. "
        "Use this when you need to understand the loop state or debug continuation logic."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

COMPLETE_PROMISE = {
    "name": "set_completion_promise",
    "description": (
        "Set a completion promise that defines when the loop should stop. "
        "Use this to specify custom termination conditions beyond automatic task detection. "
        "The loop will continue until either all tasks complete OR this promise is fulfilled."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "promise_type": {
                "type": "string",
                "description": "Type of completion condition: 'task_count', 'file_exists', 'content_match', or 'custom'",
                "enum": ["task_count", "file_exists", "content_match", "custom"]
            },
            "condition": {
                "type": "string",
                "description": "The specific condition to check (e.g., file path, content pattern, task index)"
            },
            "expected_value": {
                "type": "string",
                "description": "Expected value for the condition (optional)"
            }
        },
        "required": ["promise_type", "condition"]
    }
}
