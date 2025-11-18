import streamlit as st
import json
import random
import time
from datetime import datetime
from typing import List, Dict
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class VitalSigns(BaseModel):
    """Patient vital signs"""
    temperature: str = Field(..., description="Body temperature (e.g., 98.6°F)")
    blood_pressure: str = Field(..., description="BP reading (e.g., 120/80 mmHg)")
    heart_rate: str = Field(..., description="Beats per minute (e.g., 75 bpm)")
    respiratory_rate: str = Field(..., description="Breaths per minute (e.g., 16/min)")
    oxygen_saturation: str = Field(..., description="SpO2 percentage (e.g., 98%)")

class PatientProfile(BaseModel):
    """Complete patient medical profile"""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., description="Patient age in years")
    gender: str = Field(..., description="Male/Female/Other")
    chief_complaint: str = Field(..., description="Main reason for visit in patient's words")
    history_of_present_illness: str = Field(..., description="Detailed symptom timeline and characteristics")
    past_medical_history: List[str] = Field(default=[], description="Previous medical conditions")
    medications: List[str] = Field(default=[], description="Current medications with dosages")
    allergies: List[str] = Field(default=[], description="Known drug/food allergies")
    family_history: List[str] = Field(default=[], description="Family medical conditions")
    social_history: str = Field(..., description="Lifestyle, occupation, smoking, alcohol, drugs")
    vital_signs: VitalSigns
    physical_exam_findings: str = Field(..., description="Observable physical examination findings")
    probable_diagnosis: str = Field(..., description="The correct diagnosis (hidden from student)")
    differential_diagnoses: List[str] = Field(..., description="2-3 other possible diagnoses")
    recommended_tests: List[str] = Field(..., description="Diagnostic tests to confirm diagnosis")
    red_flags: List[str] = Field(default=[], description="Warning signs requiring immediate attention")
    patient_personality: str = Field(default="cooperative", description="Patient's demeanor and communication style")

class PatientResponse(BaseModel):
    """Structure for patient's response to questions"""
    response_text: str = Field(..., description="What the patient says")
    reveals_info: List[str] = Field(default=[], description="Key clinical information revealed")
    emotional_tone: str = Field(default="neutral", description="Patient's emotional state")

class DiagnosticEvaluation(BaseModel):
    """Evaluation of student's diagnostic performance"""
    is_correct: bool = Field(..., description="Whether diagnosis is correct")
    accuracy_score: int = Field(..., description="Score from 0-100")
    feedback: str = Field(..., description="Detailed constructive feedback")
    strengths: List[str] = Field(..., description="What student did well")
    areas_for_improvement: List[str] = Field(..., description="What to improve")
    key_findings_missed: List[str] = Field(default=[], description="Important information not gathered")

# ============================================================================
# CORE CLASSES
# ============================================================================

class Llama3Processor:
    """Base class for all LLM interactions"""
    client = None

    def __init__(self):
        self.user_input = None
        self.pydantic_object = None
        self.system_prompt = None

    def prompt_llama3(self, text: str) -> str:
        """Send prompt to Llama and get structured JSON response"""
        user_input = f"{self.user_input}:\n{text}"
        
        pydantic_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": pydantic_parser.get_format_instructions()},
        )
        
        _input = prompt.format(query=user_input)
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": _input}
            ],
            temperature=0.7,
        )
        
        return pydantic_parser.parse(response.choices[0].message.content).model_dump_json()

class VirtualPatientGenerator(Llama3Processor):
    """Generates realistic patient cases using LLM"""

    def __init__(self):
        super().__init__()
        self.system_prompt = (
            "You are an expert medical educator creating realistic patient cases for medical student training. "
            "Generate clinically accurate, detailed patient profiles that mirror real-world presentations. "
            "Include both typical and atypical features to make cases educational and challenging. "
            "Ensure all vital signs, symptoms, and findings are medically consistent with the diagnosis. "
            "The case should have appropriate complexity for a medical student at clinical rotation level. "
            "Include realistic timelines, risk factors, and social determinants of health."
        )

        self.user_input = (
            "Create a comprehensive patient case with the following components:\n"
            "1. Patient demographics (age, gender appropriate for the condition)\n"
            "2. Chief complaint (exactly as a patient would describe it, in their own words)\n"
            "3. History of present illness (detailed timeline: onset, duration, character, severity, "
            "aggravating/relieving factors, associated symptoms)\n"
            "4. Past medical history (relevant conditions)\n"
            "5. Current medications (with generic names and dosages)\n"
            "6. Allergies (medications, foods, environmental)\n"
            "7. Family history (relevant hereditary conditions)\n"
            "8. Social history (occupation, smoking, alcohol, drugs, living situation, support system)\n"
            "9. Vital signs (realistic values consistent with the condition)\n"
            "10. Physical examination findings (specific, observable findings)\n"
            "11. Probable diagnosis (the correct answer - be specific)\n"
            "12. Differential diagnoses (2-3 plausible alternatives)\n"
            "13. Recommended diagnostic tests (to confirm diagnosis)\n"
            "14. Red flag symptoms (signs requiring immediate intervention)\n"
            "15. Patient personality (communication style, cooperation level, anxiety level)"
        )

        self.pydantic_object = PatientProfile

    def generate_patient(self, disease_or_symptoms: str) -> Dict:
        """Generate a complete patient case"""
        prompt = (
            f"Create a realistic, detailed patient case for: {disease_or_symptoms}\n\n"
            f"Ensure the case is medically accurate, educationally valuable, and has appropriate "
            f"complexity for medical students. Include subtle findings that students should discover "
            f"through good questioning. Make the patient's presentation realistic - not textbook perfect."
        )
        
        result = self.prompt_llama3(prompt)
        return json.loads(result)

class PatientConversationHandler(Llama3Processor):
    """Handles realistic patient-student interactions"""

    def __init__(self, patient_profile: Dict):
        super().__init__()
        self.patient_profile = patient_profile
        self.conversation_history = []
        self.revealed_information = set()
        self.question_count = 0

        personality = patient_profile.get('patient_personality', 'cooperative')
        age = patient_profile.get('age', 50)
        education_level = "high school" if age > 60 else "college"

        self.system_prompt = (
            f"You are roleplaying as a {age}-year-old {patient_profile['gender'].lower()} patient "
            f"with {personality} personality seeking medical care. "
            f"Your education level is {education_level}. "
            f"Respond naturally and realistically as this specific patient would, using first-person language. "
            f"\n\nIMPORTANT GUIDELINES:\n"
            f"- Use simple, everyday language (avoid medical jargon unless your background suggests medical knowledge)\n"
            f"- Describe symptoms in layman's terms (e.g., 'burning feeling' not 'dyspepsia')\n"
            f"- Show appropriate emotions: worry, confusion, relief, pain, frustration\n"
            f"- Be specific when you know details (exact times, durations, locations)\n"
            f"- Be vague about things patients typically don't know (exact blood pressure numbers, medical terms)\n"
            f"- Only reveal information directly answering the question asked\n"
            f"- If you don't understand the question, ask for clarification\n"
            f"- Show hesitation or uncertainty when appropriate\n"
            f"- Mention concerns or questions you might have as a patient\n"
            f"- Stay consistent with your patient profile throughout the conversation"
        )

        self.user_input = "Stay in character as the patient. Answer the medical student's question."
        self.pydantic_object = PatientResponse

    def respond_to_question(self, student_question: str) -> Dict:
        """Generate realistic patient response to student's question"""
        self.question_count += 1

        recent_history = self.conversation_history[-3:] if len(self.conversation_history) > 0 else []
        history_text = "\n".join([
            f"Student asked: {h['student']}\nYou responded: {h['patient']}"
            for h in recent_history
        ])

        context = f"""
PATIENT PROFILE:
- Age: {self.patient_profile['age']}, Gender: {self.patient_profile['gender']}
- Chief Complaint: {self.patient_profile['chief_complaint']}
- History: {self.patient_profile['history_of_present_illness']}
- Past Medical History: {', '.join(self.patient_profile['past_medical_history'])}
- Medications: {', '.join(self.patient_profile['medications'])}
- Social History: {self.patient_profile['social_history']}
- Physical Findings: {self.patient_profile['physical_exam_findings']}
- Personality: {self.patient_profile.get('patient_personality', 'cooperative')}

RECENT CONVERSATION:
{history_text if history_text else "This is the first question."}

STUDENT'S CURRENT QUESTION: {student_question}

INSTRUCTIONS:
Answer as the patient would. Be specific and helpful, but don't volunteer information
beyond what's asked. Show appropriate emotion. Use everyday language. If it's a yes/no
question, answer it but add a brief detail if it seems natural.
"""

        response = self.prompt_llama3(context)
        response_data = json.loads(response)

        self.conversation_history.append({
            "student": student_question,
            "patient": response_data["response_text"],
            "reveals_info": response_data.get("reveals_info", [])
        })

        self.revealed_information.update(response_data.get("reveals_info", []))

        return response_data

class DiagnosticEvaluator(Llama3Processor):
    """Evaluates student's diagnostic reasoning and provides feedback"""

    def __init__(self):
        super().__init__()
        self.system_prompt = (
            "You are an experienced medical educator evaluating a medical student's diagnostic reasoning. "
            "Provide constructive, specific feedback that helps students learn and improve. "
            "Be encouraging while pointing out areas for improvement. "
            "Focus on the reasoning process, not just the final diagnosis. "
            "Highlight good clinical practices and suggest better approaches where needed."
        )

        self.user_input = "Evaluate the student's diagnostic performance"
        self.pydantic_object = DiagnosticEvaluation

    def evaluate(self, patient_profile: Dict, student_diagnosis: str,
                 questions_asked: List[str], reasoning: str) -> Dict:
        """Comprehensive evaluation of student performance"""

        context = f"""
CORRECT DIAGNOSIS: {patient_profile['probable_diagnosis']}
DIFFERENTIAL DIAGNOSES: {', '.join(patient_profile['differential_diagnoses'])}

STUDENT'S DIAGNOSIS: {student_diagnosis}
STUDENT'S REASONING: {reasoning}

NUMBER OF QUESTIONS ASKED: {len(questions_asked)}

QUESTIONS ASKED BY STUDENT:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions_asked))}

PATIENT INFORMATION:
- Chief Complaint: {patient_profile['chief_complaint']}
- Age: {patient_profile['age']}, Gender: {patient_profile['gender']}
- Key History: {patient_profile['history_of_present_illness'][:200]}...
- Vital Signs: BP {patient_profile['vital_signs']['blood_pressure']},
              HR {patient_profile['vital_signs']['heart_rate']},
              Temp {patient_profile['vital_signs']['temperature']}
- Physical Exam: {patient_profile['physical_exam_findings'][:200]}...
- Past Medical History: {', '.join(patient_profile['past_medical_history'])}

EVALUATION CRITERIA:
1. Diagnostic Accuracy: Is the diagnosis correct or in the differential?
2. Clinical Reasoning: Is the logic sound and evidence-based?
3. History Taking: Were appropriate questions asked? Any critical omissions?
4. Systematic Approach: Did student follow a logical diagnostic process?
5. Risk Awareness: Did student identify red flags or urgent concerns?

Provide a thorough evaluation with specific examples. Score from 0-100.
Be constructive and educational in your feedback.
"""

        response = self.prompt_llama3(context)
        return json.loads(response)

class PatientSessionManager:
    """Manages the entire patient encounter session"""

    def __init__(self):
        self.current_patient = None
        self.conversation_handler = None
        self.questions_asked = []
        self.session_start_time = None
        self.vitals_checked = False
        self.physical_exam_performed = []

    def start_new_session(self, disease_or_symptoms: str) -> Dict:
        """Initialize a new patient case"""
        generator = VirtualPatientGenerator()
        self.current_patient = generator.generate_patient(disease_or_symptoms)
        self.conversation_handler = PatientConversationHandler(self.current_patient)
        self.questions_asked = []
        self.session_start_time = datetime.now()
        self.vitals_checked = False
        self.physical_exam_performed = []

        return {
            "patient_id": self.current_patient["patient_id"],
            "initial_presentation": self.current_patient["chief_complaint"],
            "age": self.current_patient["age"],
            "gender": self.current_patient["gender"]
        }

    def ask_question(self, question: str) -> Dict:
        """Student asks patient a question"""
        self.questions_asked.append(question)
        response = self.conversation_handler.respond_to_question(question)
        return response

    def get_vital_signs(self) -> Dict:
        """Simulate taking vital signs"""
        self.vitals_checked = True
        return self.current_patient["vital_signs"]

    def perform_physical_exam(self, exam_type: str) -> str:
        """Simulate physical examination"""
        self.physical_exam_performed.append(exam_type)
        findings = self.current_patient["physical_exam_findings"]
        return findings

    def submit_diagnosis(self, diagnosis: str, reasoning: str) -> Dict:
        """Evaluate student's diagnosis"""
        evaluator = DiagnosticEvaluator()
        evaluation = evaluator.evaluate(
            self.current_patient,
            diagnosis,
            self.questions_asked,
            reasoning
        )

        eval_data = evaluation

        duration = datetime.now() - self.session_start_time

        return {
            "correct_diagnosis": self.current_patient["probable_diagnosis"],
            "differential_diagnoses": self.current_patient["differential_diagnoses"],
            "student_diagnosis": diagnosis,
            "evaluation": eval_data,
            "session_stats": {
                "questions_asked": len(self.questions_asked),
                "vitals_checked": self.vitals_checked,
                "physical_exams": self.physical_exam_performed,
                "duration_minutes": duration.total_seconds() / 60,
                "revealed_info": list(self.conversation_handler.revealed_information)
            }
        }

    def get_hint(self) -> str:
        """Provide a subtle learning hint"""
        hints = [
            "Consider asking about the onset and progression of symptoms.",
            "Have you checked the patient's vital signs?",
            "Think about risk factors relevant to this age group.",
            "Consider asking about associated symptoms.",
            "What about the patient's past medical history?",
            "Are there any red flags that require immediate attention?",
            "Consider the patient's medications - any relevant interactions?",
            "Think about the differential diagnoses for this presentation.",
        ]
        return random.choice(hints)

# ============================================================================
# STREAMLIT APP
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = None
    if 'patient_loaded' not in st.session_state:
        st.session_state.patient_loaded = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'diagnosis_submitted' not in st.session_state:
        st.session_state.diagnosis_submitted = False

def main():
    st.set_page_config(
        page_title="Virtual Patient Simulator",
        page_icon="🏥",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1e88e5;
            text-align: center;
            padding: 1rem;
            border-bottom: 3px solid #1e88e5;
            margin-bottom: 2rem;
        }
        .patient-card {
            background-color: #f0f8ff;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #1e88e5;
            margin-bottom: 1rem;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        .student-message {
            background-color: #e3f2fd;
            border-left: 4px solid #1e88e5;
        }
        .patient-message {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        .vitals-box {
            background-color: #e8f5e9;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
        }
        </style>
    """, unsafe_allow_html=True)

    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🏥 Virtual Patient Simulator</h1>', unsafe_allow_html=True)

    # Sidebar for API key and controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "Enter Groq API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_key else "",
            help="Get your API key from https://console.groq.com"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            Llama3Processor.client = Groq(api_key=api_key)
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your Groq API key to continue")
            return

        st.divider()
        st.header("📋 Instructions")
        st.markdown("""
        1. **Start a Case**: Enter a condition or symptom
        2. **Interview**: Ask the patient questions
        3. **Examine**: Check vitals and perform exams
        4. **Diagnose**: Submit your diagnosis with reasoning
        5. **Review**: Get detailed feedback
        """)

        if st.session_state.patient_loaded:
            st.divider()
            if st.button("🔄 Start New Case", use_container_width=True):
                st.session_state.session_manager = None
                st.session_state.patient_loaded = False
                st.session_state.chat_history = []
                st.session_state.diagnosis_submitted = False
                st.rerun()

    # Main content area
    if not st.session_state.patient_loaded:
        # Case Generation
        st.subheader("🎲 Generate Patient Case")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            condition = st.text_input(
                "Enter a condition or symptom (or leave blank for random)",
                placeholder="e.g., diabetes, chest pain, headache"
            )
        with col2:
            st.write("")
            st.write("")
            generate_button = st.button("🚀 Generate Case", use_container_width=True)

        if generate_button:
            if not condition:
                conditions = ["hypertension", "diabetes", "chest pain", "headache", 
                            "fever", "abdominal pain", "shortness of breath"]
                condition = random.choice(conditions)
            
            with st.spinner(f"🔬 Generating patient case for: **{condition.upper()}**..."):
                try:
                    st.session_state.session_manager = PatientSessionManager()
                    patient_info = st.session_state.session_manager.start_new_session(condition)
                    st.session_state.patient_loaded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error generating case: {str(e)}")

    else:
        # Display Patient Information
        manager = st.session_state.session_manager
        patient = manager.current_patient

        # Patient Card
        st.markdown(f"""
        <div class="patient-card">
            <h3>👤 Patient Information</h3>
            <p><strong>ID:</strong> {patient['patient_id']}</p>
            <p><strong>Age:</strong> {patient['age']} years</p>
            <p><strong>Gender:</strong> {patient['gender']}</p>
            <p><strong>Chief Complaint:</strong> "{patient['chief_complaint']}"</p>
        </div>
        """, unsafe_allow_html=True)

        # Tabs for different actions
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Interview", "📊 Vitals & Exam", "🩺 Diagnosis", "📈 Summary"])

        with tab1:
            st.subheader("Patient Interview")
            
            # Display chat history
            for msg in st.session_state.chat_history:
                if msg['type'] == 'student':
                    st.markdown(f'<div class="chat-message student-message"><strong>👨‍⚕️ You:</strong> {msg["text"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message patient-message"><strong>🗣️ Patient:</strong> {msg["text"]}</div>', 
                              unsafe_allow_html=True)

            # Question input
            question = st.text_input("Ask the patient a question:", key="question_input")
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💡 Get Hint"):
                    hint = manager.get_hint()
                    st.info(hint)
            with col2:
                if st.button("📤 Ask Question", disabled=not question):
                    if question:
                        with st.spinner("🤔 Patient is thinking..."):
                            response = manager.ask_question(question)
                            st.session_state.chat_history.append({
                                'type': 'student',
                                'text': question
                            })
                            st.session_state.chat_history.append({
                                'type': 'patient',
                                'text': response['response_text']
                            })
                        st.rerun()

        with tab2:
            st.subheader("Vital Signs & Physical Examination")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Check Vital Signs"):
                    vitals = manager.get_vital_signs()
                    st.markdown(f"""
                    <div class="vitals-box">
                        <h4>Vital Signs</h4>
                        <p>🌡️ <strong>Temperature:</strong> {vitals['temperature']}</p>
                        <p>💓 <strong>Blood Pressure:</strong> {vitals['blood_pressure']}</p>
                        <p>❤️ <strong>Heart Rate:</strong> {vitals['heart_rate']}</p>
                        <p>🫁 <strong>Respiratory Rate:</strong> {vitals['respiratory_rate']}</p>
                        <p>💨 <strong>Oxygen Saturation:</strong> {vitals['oxygen_saturation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                exam_area = st.selectbox(
                    "Select examination area:",
                    ["General", "Cardiovascular", "Respiratory", "Abdominal", "Neurological"]
                )
                if st.button("🔍 Perform Examination"):
                    findings = manager.perform_physical_exam(exam_area)
                    st.info(f"**Physical Examination Findings:**\n\n{findings}")

        with tab3:
            st.subheader("Submit Your Diagnosis")
            
            if not st.session_state.diagnosis_submitted:
                diagnosis = st.text_input("Primary Diagnosis:", placeholder="Enter your diagnosis")
                reasoning = st.text_area(
                    "Clinical Reasoning:",
                    placeholder="Explain your reasoning, key findings, and why you ruled out differentials...",
                    height=150
                )
                
                if st.button("✅ Submit Diagnosis", disabled=not (diagnosis and reasoning)):
                    if diagnosis and reasoning:
                        with st.spinner("⏳ Evaluating your diagnosis..."):
                            result = manager.submit_diagnosis(diagnosis, reasoning)
                            st.session_state.diagnosis_result = result
                            st.session_state.diagnosis_submitted = True
                        st.rerun()
            else:
                # Display evaluation results
                result = st.session_state.diagnosis_result
                eval_data = result['evaluation']
                
                # Result header
                if eval_data['is_correct']:
                    st.success(f"✅ CORRECT! Score: {eval_data['accuracy_score']}/100")
                else:
                    st.error(f"❌ INCORRECT. Score: {eval_data['accuracy_score']}/100")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**🎯 Correct Diagnosis:**\n{result['correct_diagnosis']}")
                with col2:
                    st.warning(f"**📋 Your Diagnosis:**\n{result['student_diagnosis']}")
                
                st.markdown("**📊 Differential Diagnoses:**")
                for diff in result['differential_diagnoses']:
                    st.write(f"• {diff}")
                
                st.divider()
                st.markdown("**💬 Detailed Feedback:**")
                st.write(eval_data['feedback'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success("**✨ Strengths:**")
                    for strength in eval_data['strengths']:
                        st.write(f"• {strength}")
                
                with col2:
                    st.info("**📚 Areas for Improvement:**")
                    for area in eval_data['areas_for_improvement']:
                        st.write(f"• {area}")
                
                if eval_data['key_findings_missed']:
                    st.warning("**⚠️ Key Findings Missed:**")
                    for finding in eval_data['key_findings_missed']:
                        st.write(f"• {finding}")

        with tab4:
            st.subheader("Session Summary")
            
            stats = result['session_stats'] if st.session_state.diagnosis_submitted else None
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                q_count = len(manager.questions_asked)
                st.metric("❓ Questions Asked", q_count)
            with col2:
                st.metric("📊 Vitals Checked", "✅" if manager.vitals_checked else "❌")
            with col3:
                st.metric("🔍 Exams Performed", len(manager.physical_exam_performed))
            with col4:
                if stats:
                    duration = stats['duration_minutes']
                    st.metric("⏱️ Duration", f"{duration:.1f} min")
            
            if stats and stats['revealed_info']:
                st.markdown("**📝 Information Gathered:**")
                for info in stats['revealed_info']:
                    st.write(f"• {info}")

if __name__ == "__main__":
    main()
