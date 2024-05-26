#!/usr/bin/env python3
#
# Whoswho.py

import os
import sys
import re
import time
from openai import OpenAI

class AIController:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)

    def chat(self, role, query, model='gpt-4o'):
        chat_history = []
        chat_history.append({"role": "system", "content": role})
        chat_history.append({"role": "user", "content": query})

        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=chat_history,
                stream=True,
            )
        except Exception as e:
            print(e)
            sys.exit(1)

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                response += chunk.choices[0].delta.content

        formatted_response = {"role": "assistant", "content": response}
        return formatted_response

    def extract_code(self, response):
        # Regular expression to find code blocks with language identifiers
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response['content'], re.DOTALL)
        return code_blocks


class Agent:
    def __init__(self, name, role_description, controller):
        self.name = name
        self.role_description = role_description
        self.controller = controller
        self.log = []

    def interact(self, query, model='gpt-4o', iterations=1):
        for _ in range(iterations):
            self.log_interaction(self.name, query)  # Log the query
            response = self.controller.chat(self.role_description, query, model)
            self.log_interaction("assistant", response['content'])  # Log the response
            query = response['content']  # Use the previous response as the new query
        return response

    def log_interaction(self, role, content):
        timestamp = int(time.time())  # Unix timestamp
        self.log.append({"timestamp": timestamp, "role": role, "content": content})

    def get_log(self):
        return self.log

    def get_log_by_role(self, role_name):
        return [entry for entry in self.log if entry['role'] == role_name]

    def update_role(self, new_role_description):
        self.role_description = new_role_description

    def extract_code(self, response):
        return self.controller.extract_code(response)


class Whoswho:
    def __init__(self):
        self.controller = AIController()
        self.agents = {}

    def add_agent(self, name, role_description):
        agent = Agent(name, role_description, self.controller)
        self.agents[name] = agent

    def get_agent(self, name):
        return self.agents.get(name, None)

    def remove_agent(self, name):
        if name in self.agents:
            del self.agents[name]

    def update_agent(self, name, new_role_description):
        agent = self.get_agent(name)
        if agent:
            agent.update_role(new_role_description)
        else:
            raise ValueError(f"Agent with name {name} does not exist.")

    def list_agents(self):
        return {name: agent.role_description for name, agent in self.agents.items()}

    def get_agent_log(self, name):
        agent = self.get_agent(name)
        if agent:
            return agent.get_log()
        return None

    def get_agent_log_by_role(self, name):
        agent = self.get_agent(name)
        if agent:
            return agent.get_log_by_role(name)
        return None

    def get_full_log(self):
        full_log = []
        for agent in self.agents.values():
            full_log.extend(agent.get_log())
        # Sort the full log by timestamp
        full_log.sort(key=lambda entry: entry['timestamp'])
        return full_log

# Example Usage:
if __name__ == "__main__":
    system = Whoswho()

    # Adding agents
    system.add_agent('Developer1', 'Write code according to the requirements.')
    system.add_agent('Developer2', 'Check code for errors.')
    system.add_agent('Developer3', 'Suggest new features and improvements.')

    # Listing agents with roles
    agents = system.list_agents()
    for name, role in agents.items():
        print(f"Agent Name: {name}, Role: {role}")

    # Updating agent role
    system.update_agent('Developer1', 'Write optimized and clean code according to the requirements.')
    agents = system.list_agents()
    for name, role in agents.items():
        print(f"Updated Agent Name: {name}, Role: {role}")

    # Interacting with agents
    developer1 = system.get_agent('Developer1')
    response = developer1.interact('Write a Python function to add two numbers.', iterations=1)
    print(response)

    # Extracting code from the response
    code_blocks = developer1.extract_code(response)
    for idx, code in enumerate(code_blocks, 1):
        print(f"Code Block {idx}:\n{code}\n")

    # Accessing full logs
    full_log = system.get_agent_log('Developer1')
    print("Full Log for Developer1:")
    for log_entry in full_log:
        print(log_entry)

    # Accessing logs filtered by role
    filtered_log = system.get_agent_log_by_role('Developer1')
    print("Filtered Log for Developer1:")
    for log_entry in filtered_log:
        print(log_entry)

    # Accessing the full log from all agents
    full_conversation_log = system.get_full_log()
    print("Full Conversation Log:")
    for log_entry in full_conversation_log:
        print(log_entry)

    developer2 = system.get_agent('Developer2')
    response = developer2.interact('Check the function for errors: def add(a, b): return a + b', iterations=1)
    print(response)

    developer3 = system.get_agent('Developer3')
    response = developer3.interact('Suggest a new feature for the add function.', iterations=1)
    print(response)

