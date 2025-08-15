from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

SYSTEM_PROMPT = """\
You are a careful triage assistant. Classify likely medical condition and severity from symptoms.
Return STRICT JSON with keys:
- condition_type: string in ['cardiac','respiratory','allergic','infectious','injury','neurological','gastrointestinal','unknown']
- severity: string in ['low','moderate','high','critical']
- confidence: float (0-1)
- red_flags: string[]
- recommended_actions: string[]  (short, stepwise, actionable)
- self_care_advice: string or null
No extra keys. If any red flags suggest life-threatening issues, severity must be 'high' or 'critical' and first action should be to call emergency services.
"""

USER_TEMPLATE = """\
Symptoms: {symptoms}
Age: {age}
Gender: {gender}
Location: {city}, {country}
"""

def build_condition_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_TEMPLATE),
    ])
    return prompt | llm | StrOutputParser()

