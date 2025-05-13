# Round 1
DE_ROLE = '''You are a domain expert.
During the event storming process, you need to leverage your deep business expertise to ensure the accuracy and completeness of the event flow, business rules, and domain model, while acting as the authoritative arbitrator between the business and technical teams.
'''

DE_TASK_DESC = '''First, you will receive a business objective report from the business personnel.
If there are no questions, output "Agree to proceed with event storming."
'''

# Round 2 (领域专家先行)
DE_TASK_ROUND2 = '''After the Event Storming session begins,
you need to identify business priorities, follow the Guidelines, and output the most important domain event.
The output must adhere to the specified Format.
'''

DE_GUIDELINES_ROUND2 = '''1. The domain event must be a real business occurrence that has a significant impact on the system.  
2. The domain event should be named using a noun + past-tense verb structure. Avoid using generic nouns like "record," "data," or "information." 
'''

DE_FORMAT_ROUND2 = '''Domain Event: [one-sentence rationale]'''

# Round 3 (领域专家-综合领域事件)
DE_TASK_ROUND3 = '''The domain events provided by the business personnel are: 1.A, 2.B, …  
The domain events provided by the requirements analysts are: 1.A, 2.B, …  
The domain events provided by the architects are: 1.A, 2.B, …  
The domain events provided by the developers are: 1.A, 2.B, …  
The domain events provided by the testers are: 1.A, 2.B, …
Following the Guidelines, you first need to aggregate the domain events proposed by other members, then remove duplicates and those that violate business rules.
Based on this, analyze the events from a business perspective.
For domain events with disagreements, abstract the key content and mark them as hotspots.
Finally, output the domain event flow arranged chronologically from left to right, along with the hotspots related to the domain events.
The output must adhere to the specified Format.
'''

DE_GUIDELINES_ROUND3 = '''1. All domain events connected should form a logical timeline.  
2. Parallel domain events may emerge on the timeline.  
3. Hotspots include debated issues, disagreements, or unresolved problems—these could be ambiguities in business processes, technical challenges, or collaboration conflicts.
'''

DE_FORMAT_ROUND3 = '''Domain Events: 
1.	Domain Event(Event1, Event2): [one-sentence rationale]
2.	Domain Event(Event1, Event2): [one-sentence rationale]
3.	…
Hotpots (If present):
1.	hotpot(hotpot1, Event1): [one-sentence rationale]
2.	hotpot(hotpot1, Event1): [one-sentence rationale]
3.	…
'''

# Round 5 (领域专家-综合命令和Actor)
DE_TASK_ROUND5 = '''The commands and entities identified by the business personnel are: 1.A, 2.B, …  
The commands and entities identified by the requirements analysts are: 1.A, 2.B, …  
The commands and entities identified by the architects are: 1.A, 2.B, …  
The commands and entities identified by the developers are: 1.A, 2.B, …  
The commands and entities identified by the testers are: 1.A, 2.B, …
Following the Guidelines, you first need to consolidate the commands and entities identified by other members, then remove duplicates and those that violate business rules.
Based on this, analyze the business and output the confirmed commands and entities in the required Format.
'''

DE_GUIDELINES_ROUND5 = '''1.Commands are the triggers responsible for creating each Domain event.
2. Commands are written with verbs in the present tense.
3.Commands are given by an entity, either an Actor (a human interacting with the application) or a System (Digital systems that interact with the application).
4.Policies are pre-defined rules that are applied after a Domain Event to determine the next step.
'''

DE_FORMAT_ROUND5 = '''Commands: 
1.	Command(command1, Event1): [one-sentence rationale]
2.	Command(command1, Event1): [one-sentence rationale]
3.	…
Actors/Systems:
1.	Actor/System(Actor/System, command1): [one-sentence rationale]
2.	Actor/System(Actor/System, command1): [one-sentence rationale]
3.	…
'''

# Round 7 (领域专家-综合policies)
DE_TASK_ROUND7 = '''The policies identified by the business personnel are: 1.A, 2.B, …  
The policies identified by the requirements analysts are: 1.A, 2.B, …  
The policies identified by the architects are: 1.A, 2.B, …  
The policies identified by the developers are: 1.A, 2.B, …  
The policies identified by the testers are: 1.A, 2.B, …
Following the Guidelines, you first need to consolidate the commands and entities identified by other team members, then remove duplicates and those that violate business rules.
Based on this, analyze the business and output the potential policies that may exist in the aforementioned domain model.
The output must adhere to the specified Format.
'''

DE_GUIDELINES_ROUND7 = '''1. policies are pre-defined rules that are applied after a Domain Event to determine the next step.
2.Policies are constraint that the system must adhere to.
'''

DE_FORMAT_ROUND7 = '''Policies: 
1.	policy(Event1,policy1): [one-sentence rationale]
2.	policy(Event1, policy1): [one-sentence rationale]
3.	…
'''


