Title: Humanloop Documentation and API Reference

URL Source: http://humanloop.com/docs/v5/guides/observability/logging-through-api

Markdown Content:
v5.0
Search/
Sign inBook a demo
Docs
API Reference
Changelog
Docs
API Reference
Changelog
Getting Started
Overview
Quickstart
Explanation
Key Concepts
Tutorials
Evaluate a RAG app
Evaluate an agent
Capture user feedback
How-To Guides
Evaluation
Prompt Management
Observability
Monitor production Logs
Capture user feedback
Logging through API
Organization Management
Reference
Deployment Options
Supported Models
Prompt file format
Humanloop Runtime Environment
Security and Compliance
Data Management
Access roles (RBACs)
SSO and Authentication
Sign inBook a demo
On this page
Prerequisites
Create a Humanloop Account
Add an OpenAI API Key
Create the chat agent
Log to Humanloop
Initialize the trace
Add logging
Complete the trace
Run the code
Check your workspace
Change the agent and rerun
Next steps
How-To GuidesObservability

Logging through API

Instrument your AI project with any programming language using the API.

Our SDK offers high-level utilities for integrating Humanloop in your project. You can use the API to the same effect with any language you use or if you prefer more control.

This guide revisits our logging quickstart tutorial: we’ll use API actions instead of the SDK decorators, showing you how Humanloop instrumentation works step-by-step.

By the end, we’ll have a chat agent project integrated with Humanloop logging. The example uses the Python SDK, but the verbs map directly to our API.

Prerequisites
Account setup
Install dependencies
Create the chat agent

We start with a simple chat agent that answers math and science questions.

Python
TypeScript

Create an agent.py file and add the following:

agent.py
1	import os
2	import json
3	import datetime
4	
5	from humanloop import Humanloop
6	from openai import OpenAI
7	
8	openai = OpenAI(api_key="YOUR_OPENAI_KEY")
9	humanloop = Humanloop(api_key="YOUR_HUMANLOOP_KEY")
10	
11	
12	def calculator(operation: str, num1: int, num2: int) -> str:
13	    """Do arithmetic operations on two numbers."""
14	    if operation == "add":
15	        return num1 + num2
16	    elif operation == "subtract":
17	        return num1 - num2
18	    elif operation == "multiply":
19	        return num1 * num2
20	    elif operation == "divide":
21	        return num1 / num2
22	    else:
23	        return "Invalid operation"
24	
25	
26	TOOL_JSON_SCHEMA = {
27	    "name": "calculator",
28	    "description": "Do arithmetic operations on two numbers.",
29	    "parameters": {
30	        "type": "object",
31	        "required": ["operation", "num1", "num2"],
32	        "properties": {
33	            "operation": {"type": "string"},
34	            "num1": {"type": "integer"},
35	            "num2": {"type": "integer"},
36	        },
37	        "additionalProperties": False,
38	    },
39	}
40	
41	
42	def call_model(messages: list[str]) -> str:
43	    output = openai.chat.completions.create(
44	        messages=messages,
45	        model="gpt-4o",
46	        tools=[
47	            {
48	                "type": "function",
49	                "function": TOOL_JSON_SCHEMA,
50	            }
51	        ],
52	        temperature=0.7,
53	    )
54	
55	    # Check if model asked for a tool call
56	    if output.choices[0].message.tool_calls:
57	        for tool_call in output.choices[0].message.tool_calls:
58	            arguments = json.loads(tool_call.function.arguments)
59	            if tool_call.function.name == "calculator":
60	                result = calculator(**arguments)
61	                return f"[TOOL CALL] {result}"
62	
63	    # Otherwise, return the LLM response
64	    return output.choices[0].message.content
65	
66	
67	def conversation():
68	    messages = [
69	        {
70	            "role": "system",
71	            "content": "You are a a groovy 80s surfer dude "
72	            "helping with math and science.",
73	        },
74	    ]
75	    while True:
76	        user_input = input("You: ")
77	        if user_input == "exit":
78	            break
79	        messages.append({"role": "user", "content": user_input})
80	        response = call_model(messages=messages)
81	        messages.append({"role": "assistant", "content": response})
82	        print(f"Agent: {response}")
83	
84	
85	if __name__ == "__main__":
86	    conversation()
Log to Humanloop

The agent works and is capable of function calling. However, we rely on inputs and outputs to reason about the behavior. Humanloop logging allows you to observe the steps taken by the agent, which we will demonstrate below.

1
Initialize the trace

Modify call_model to accept a trace_id argument. It will be used to associate Logs to the logging trace.

The trace of the conversation will be associated with a Flow. Initialize the trace at the start of the conversation.

Python
Typescript
agent.py
1	def call_model(trace_id: str, messages: list[str]) -> str:
2	    ...
3	
4	def conversation():
5	    trace_id = humanloop.flows.log(
6	        path="Logging Quickstart/QA Agent",
7	        flow={
8	            "attributes": {},
9	        },
10	    ).id
11	    messages = [
12	        {
13	            "role": "system",
14	            "content": "You are a a groovy 80s surfer dude "
15	            "helping with math and science.",
16	        },
17	    ]
18	    while True:
19	        user_input = input("You: ")
20	        if user_input == "exit":
21	            break
22	        messages.append({"role": "user", "content": user_input})
23	        response = call_model(trace_id=trace_id, messages=messages)
24	        messages.append({"role": "assistant", "content": response})
25	        print(f"Agent: {response}")
2
Add logging

We add log statements that will create the Logs contained in the trace.

Python
Typescript
agent.py
1	def call_model(trace_id: str, messages: list[str]) -> str:
2	    prompt_start_time = datetime.datetime.now()
3	    output = openai.chat.completions.create(
4	        messages=messages,
5	        model="gpt-4o",
6	        tools=[{
7	            "type": "function",
8	            "function": TOOL_JSON_SCHEMA,
9	        }],
10	        temperature=0.7,
11	    )
12	    prompt_log_id = humanloop.prompts.log(
13	        path="Logging Quickstart/QA Prompt",
14	        prompt={
15	            "model": "gpt-4o",
16	            "tools": [TOOL_JSON_SCHEMA],
17	            "temperature": 0.7,
18	        },
19	        output=output.choices[0].message.content,
20	        trace_parent_id=trace_id,
21	        start_time=prompt_start_time,
22	        end_time=datetime.datetime.now(),
23	    ).id
24	
25	    # Check if model asked for a tool call
26	    if output.choices[0].message.tool_calls:
27	        for tool_call in output.choices[0].message.tool_calls:
28	            arguments = json.loads(tool_call.function.arguments)
29	            if tool_call.function.name == "calculator":
30	                tool_start_time = datetime.datetime.now()
31	                result = calculator(**arguments)
32	                humanloop.tools.log(
33	                    path="Logging Quickstart/Calculator",
34	                    tool={
35	                        "name": "calculator",
36	                        "description": "Do arithmetic operations on two numbers.",
37	                        "function": TOOL_JSON_SCHEMA,
38	                    },
39	                    inputs=arguments,
40	                    output=result,
41	                    trace_parent_id=prompt_log_id,
42	                    start_time=tool_start_time,
43	                    end_time=datetime.datetime.now(),
44	                )
45	                return f"[TOOL CALL] {result}"
46	
47	    # Otherwise, return the LLM response
48	    return output.choices[0].message.content
3
Complete the trace

When the conversation is finished, we mark the trace as complete, signalling no more logs will be added.

Python
Typescript
agent.py
1	def conversation():
2	    trace_id = humanloop.flows.log(
3	        path="Logging Quickstart/QA Agent",
4	        flow={
5	            "attributes": {},
6	        },
7	    ).id
8	    messages = [
9	        {
10	            "role": "system",
11	            "content": "You are a a groovy 80s surfer dude "
12	            "helping with math and science.",
13	        },
14	    ]
15	    while True:
16	        user_input = input("You: ")
17	        if user_input == "exit":
18	            break
19	        messages.append({"role": "user", "content": user_input})
20	        response = call_model(trace_id=trace_id, messages=messages)
21	        messages.append({"role": "assistant", "content": response})
22	        print(f"Agent: {response}")
23	
24	    humanloop.flows.update_log(
25	        log_id=trace_id,
26	        output="",
27	        status="complete",
28	    )
Run the code

Have a conversation with the agent. When you’re done, type exit to close the program.

Python
TypeScript
$	python agent.py
>	You: Hi dude!
>	Agent: Tubular! I am here to help with math and science, what is groovin?
>	You: How does flying work?
>	Agent: ...
>	You: What is 5678 * 456?
>	Agent: [TOOL CALL] 2587968
>	You: exit
Check your workspace

Navigate to your workspace to see the logged conversation.

Inside the Logging Quickstart directory on the left, click the QA Agent Flow. Select the Logs tab from the top of the page and click the Log inside the table.

You will see the conversation’s trace, containing Logs corresponding to the Tool and the Prompt.

Change the agent and rerun

Modify the call_model function to use a different model and temperature.

Python
Typescript
agent.py
1	def call_model(trace_id: str, messages: list[str]) -> str:
2	    prompt_start_time = datetime.datetime.now()
3	    output = openai.chat.completions.create(
4	        messages=messages,
5	        model="gpt-4o-mini",
6	        tools=[{
7	            "type": "function",
8	            **TOOL_JSON_SCHEMA,
9	        }],
10	        temperature=0.2,
11	    )
12	    prompt_log_id = humanloop.prompts.log(
13	        path="Logging Quickstart/QA Prompt",
14	        prompt={
15	            "model": "gpt-4o-mini",
16	            "tools": [TOOL_JSON_SCHEMA],
17	            "temperature": 0.2,
18	        }
19	        output=output.choices[0].message.content,
20	        trace_parent_id=trace_id,
21	        start_time=prompt_start_time,
22	        end_time=datetime.datetime.now(),
23	    ).id
24	
25	    ...

Run the agent again, then head back to your workspace.

Click the QA Prompt Prompt, select the Dashboard tab from the top of the page and look at Uncommitted Versions.

By changing the hyperparameters of the OpenAI call, you have tagged a new version of the Prompt.

Next steps

Logging is the first step to observing your AI product. Read these guides to learn more about evals on Humanloop:

Add monitoring Evaluators to evaluate Logs as they’re made against a File.

See evals in action in our tutorial on evaluating an agent.

Was this page helpful?YesNo
Edit this page
Invite collaborators
Up Next
Built with