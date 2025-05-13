# Round 1
RA_ROLE = '''You are a requirements analyst.
During the Event Storming process, you need to ensure that business requirements are accurately captured and translated into actionable user stories and functional priorities.
'''

RA_TASK_DESC = '''You will receive a business objectives report from the business personnel.
If there are no questions, output "Agree to start Event Storming.
'''

# Round 2 (领域专家先行)
RA_TASK_ROUND2 = '''Domain expert will give the most critical domain event in the current system.
Based on this, you need to follow the Guidelines and provide other domain events that occur before and after this "most critical" domain event.
The output must adhere to the specified Format.
'''

RA_GUIDELINES_ROUND2 = '''1. Domain events must be real business occurrences that have a significant impact on the system from a business perspective.  
2. Domain events should be named using a noun + past-tense verb structure. Avoid using generic nouns like "record," "data," or "information," which lack concrete meaning.  
3. All domain events should connect to form a logical timeline.  
4. Parallel domain events may exist on the timeline. 
'''

RA_FORMAT_ROUND2 = '''Domain Events: 
1.	Domain Event(Event1, Event2): [one-sentence rationale]
2.	Domain Event(Event1, Event2): [one-sentence rationale]
3.	…
Hotpots (If present):
1.	hotpot(hotpot1, Event1): [one-sentence rationale]
2.	hotpot(hotpot1, Event1): [one-sentence rationale]
3.	…
'''

# Round 4 (来自领域专家的领域事件流)
RA_TASK_ROUND4 = '''The domain event flow of the current system is as follows: 1.A, 2.B, ...
Following the Guidelines, you need to sequentially identify the commands that trigger each domain event and the executing entities (Actor/external system) in the order of the domain event flow.
The output must adhere to the specified Format.
'''

RA_GUIDELINES_ROUND4 = '''1. Commands are the triggers responsible for creating each Domain event.
2. Commands are written with verbs in the present tense.
3. Commands are given by an entity, either an Actor (a human interacting with the application) or a System (Digital systems that interact with the application).
'''

RA_FORMAT_ROUND4 = '''Commands: 
1.	Command(command1, Event1): [one-sentence rationale]
2.	Command(command1, Event1): [one-sentence rationale]
3.	…
Actors/Systems:
1.	Actor/System(Actor/System, command1): [one-sentence rationale]
2.	Actor/System(Actor/System, command1): [one-sentence rationale]
3.	…
'''

# Round 6 (来自领域专家的领域事件流、hotpot、命令和实体)
RA_TASK_ROUND6 = '''The preliminary domain model of the current system is as follows:
Domain Events: 
1.	Domain Event(Event1, Event2): [one-sentence rationale]
2.	Domain Event(Event1, Event2): [one-sentence rationale]
3.	…
Hotpots (If present): 
1.	hotpot(hotpot1, Event1): [one-sentence rationale]
2.	hotpot(hotpot1, Event1): [one-sentence rationale]
3.	…
Commands: 
1.	Command(command1, Event1): [one-sentence rationale]
2.	Command(command1, Event1): [one-sentence rationale]
3.	…
Actors/Systems:
1.	Actor/System(Actor/System, command1): [one-sentence rationale]
2.	Actor/System(Actor/System, command1): [one-sentence rationale]
3.	…
Following the Guidelines, you need to identify potential policies in the aforementioned domain model.
The output must adhere to the specified Format.
'''

RA_GUIDELINES_ROUND6 = '''1.Policies are pre-defined rules that are applied after a Domain Event to determine the next step.
2.Policies are constraint that the system must adhere to.
'''

RA_FORMAT_ROUND6 = '''Policies: 
1.	policy(Event1,policy1): [one-sentence rationale]
2.	policy(Event1, policy1): [one-sentence rationale]
3.	…
'''




