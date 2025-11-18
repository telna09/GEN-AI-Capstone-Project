# 🏥 Virtual Patient Simulator

An AI-powered interactive medical education platform that generates realistic patient cases for medical students to practice clinical diagnosis and patient interviewing skills.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Configuration](#api-configuration)
- [How It Works](#how-it-works)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

The Virtual Patient Simulator is an advanced educational tool designed for medical students and healthcare professionals to practice diagnostic reasoning in a safe, controlled environment. Using state-of-the-art AI (Llama 3.3 via Groq API), it generates clinically accurate patient cases with realistic personalities, symptoms, and medical histories.

### Why This Project?

- **Safe Learning Environment**: Practice without risk to real patients
- **Unlimited Cases**: Generate diverse patient scenarios on-demand
- **Immediate Feedback**: Get detailed evaluation of your diagnostic process
- **Realistic Interactions**: AI patients respond naturally based on their profile
- **Comprehensive Training**: Cover history taking, physical examination, and diagnosis

## ✨ Features

### 🎲 Dynamic Case Generation
- Generate realistic patient cases for any condition or symptom
- Clinically accurate vital signs and medical histories
- Random case generator for diverse practice

### 💬 Interactive Patient Interview
- Natural language conversation with AI patients
- Patients respond in character with appropriate emotions
- Tracks conversation history and revealed information
- Built-in hint system for guided learning

### 📊 Clinical Examination Tools
- Check vital signs (BP, HR, Temperature, SpO2, RR)
- Perform physical examinations by system
- Accumulate findings throughout the session

### 🩺 Diagnostic Evaluation
- Submit diagnosis with clinical reasoning
- Receive detailed performance feedback
- Scoring system (0-100 points)
- Identifies strengths and areas for improvement
- Highlights missed key findings

### 📈 Session Analytics
- Track questions asked
- Monitor examination completeness
- Session duration tracking
- Conversation history review

## 🖼️ Demo

### Main Interface
```
🏥 Virtual Patient Simulator
├── Configuration Sidebar
│   ├── API Key Input
│   └── Instructions
├── Patient Information Card
│   ├── ID, Age, Gender
│   └── Chief Complaint
└── Interactive Tabs
    ├── 💬 Interview
    ├── 📊 Vitals & Exam
    ├── 🩺 Diagnosis
    └── 📈 Summary
```

### Sample Workflow
1. **Start**: Enter "chest pain" as the condition
2. **Interview**: Ask "When did the pain start?" → Patient responds naturally
3. **Examine**: Check vitals, perform cardiovascular exam
4. **Diagnose**: Submit "Acute Myocardial Infarction" with reasoning
5. **Review**: Receive score and detailed feedback

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Groq API Key (get one at [console.groq.com](https://console.groq.com))
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/virtual-patient-simulator.git
cd virtual-patient-simulator
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

## 💻 Usage

### Getting Started

1. **Enter API Key**
   - Open the sidebar (⚙️ Configuration)
   - Enter your Groq API key
   - Wait for "✅ API Key configured" message

2. **Generate Patient Case**
   - Enter a condition (e.g., "diabetes", "headache", "fever")
   - Or leave blank for a random case
   - Click "🚀 Generate Case"

3. **Interview the Patient**
   - Switch to the "💬 Interview" tab
   - Type questions in natural language
   - Patient responds based on their profile
   - Use "💡 Get Hint" if you need guidance

4. **Perform Examination**
   - Go to "📊 Vitals & Exam" tab
   - Click "📊 Check Vital Signs"
   - Select body system and click "🔍 Perform Examination"

5. **Submit Diagnosis**
   - Navigate to "🩺 Diagnosis" tab
   - Enter your diagnosis
   - Provide detailed clinical reasoning
   - Click "✅ Submit Diagnosis"

6. **Review Performance**
   - View your score and correctness
   - Read detailed feedback
   - Check "📈 Summary" for session statistics

### Example Questions to Ask

**Good Opening Questions:**
- "What brings you in today?"
- "When did your symptoms start?"
- "Can you describe the pain/discomfort?"

**Follow-up Questions:**
- "Does anything make it better or worse?"
- "Have you experienced this before?"
- "Are you taking any medications?"
- "Any family history of similar conditions?"

## 📁 Project Structure

```
virtual-patient-simulator/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── Gen_AI_CLEANED_PROJECT.ipynb  # Original Jupyter notebook
│
└── [Future additions]
    ├── assets/                 # Images, logos
    ├── data/                   # Sample cases (if any)
    └── tests/                  # Unit tests
```

### Key Components in app.py

```python
# Core Classes
├── Llama3Processor            # Base LLM interaction handler
├── VirtualPatientGenerator    # Creates patient cases
├── PatientConversationHandler # Manages patient dialogue
├── DiagnosticEvaluator       # Evaluates student performance
└── PatientSessionManager      # Orchestrates entire session

# Pydantic Models
├── VitalSigns                 # Vital signs structure
├── PatientProfile             # Complete patient data
├── PatientResponse            # Patient's answer format
└── DiagnosticEvaluation       # Evaluation results format
```

## 🔑 API Configuration

### Getting a Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into the app

### API Key Security

⚠️ **Important Security Notes:**
- Never commit your API key to version control
- Don't share your API key publicly
- The app stores the key only in session state (not persisted)
- Consider using environment variables for production

**For production deployment:**
```bash
# Set environment variable
export GROQ_API_KEY="your-api-key-here"

# Modify app.py to read from environment
import os
api_key = os.getenv('GROQ_API_KEY')
```

## 🧠 How It Works

### 1. Patient Case Generation
```mermaid
User Input → VirtualPatientGenerator → Llama 3.3 LLM → 
Structured Patient Profile (Pydantic) → Display to User
```

The generator creates:
- Demographics appropriate for the condition
- Realistic chief complaint in patient's words
- Detailed medical history with timeline
- Consistent vital signs and physical findings
- Correct diagnosis + differential diagnoses

### 2. Conversation Flow
```mermaid
Student Question → PatientConversationHandler → 
Context Builder (Profile + History) → Llama 3.3 → 
Patient Response → Update History → Display
```

The patient:
- Stays in character throughout
- Uses layman's terms
- Shows appropriate emotions
- Only reveals relevant information
- Maintains consistency with profile

### 3. Diagnostic Evaluation
```mermaid
Student Diagnosis + Reasoning → DiagnosticEvaluator → 
Compare with Correct Diagnosis → Analyze Question Quality → 
Generate Feedback → Score (0-100) → Display Results
```

Evaluation criteria:
- Diagnostic accuracy
- Clinical reasoning quality
- History taking completeness
- Systematic approach
- Red flag identification

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Streamlit** | Web interface framework |
| **Groq API** | LLM inference (Llama 3.3) |
| **LangChain** | LLM orchestration and prompting |
| **Pydantic** | Data validation and parsing |
| **JSON** | Data serialization |

### Why These Technologies?

- **Streamlit**: Rapid UI development, perfect for data apps
- **Groq**: Fast inference with Llama 3.3 (70B parameters)
- **LangChain**: Structured output parsing for reliable data
- **Pydantic**: Type-safe data models with validation

## 📊 Performance Metrics

- **Response Time**: 2-5 seconds per patient response
- **Case Generation**: 10-15 seconds per case
- **Evaluation Time**: 5-8 seconds
- **Model**: Llama 3.3 70B (via Groq)
- **Temperature**: 0.7 (balanced creativity/consistency)

## 🐛 Troubleshooting

### Common Issues

**1. API Key Not Working**
```
Error: Invalid API key
Solution: Verify key at console.groq.com, check for extra spaces
```

**2. Slow Response Times**
```
Issue: Patient takes too long to respond
Solution: Check internet connection, Groq API status
```

**3. Import Errors**
```
ModuleNotFoundError: No module named 'streamlit'
Solution: pip install -r requirements.txt
```

**4. Chat Messages Not Visible**
```
Issue: Can't see patient responses
Solution: This has been fixed in the latest version
Ensure you're using the updated app.py with proper CSS
```

**5. Port Already in Use**
```
Error: Port 8501 is already in use
Solution: streamlit run app.py --server.port 8502
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Voice interaction (speech-to-text/text-to-speech)
- [ ] Image generation for patient visualization
- [ ] Downloadable session reports (PDF)
- [ ] Progress tracking across multiple sessions
- [ ] Difficulty levels (beginner, intermediate, advanced)
- [ ] Pre-built case library
- [ ] Collaborative sessions (multiple students)
- [ ] Integration with medical databases (PubMed, UpToDate)
- [ ] Mobile app version

### Research Directions
- Validation with medical educators
- Clinical accuracy assessment
- Learning outcome measurements
- Comparison with standardized patients

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
1. **Report Bugs**: Open an issue with details
2. **Suggest Features**: Share your ideas in issues
3. **Improve Documentation**: Fix typos, add examples
4. **Code Contributions**: Submit pull requests

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
4. Push to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Add docstrings to functions
- Include type hints where appropriate
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👨‍💻 Author

**[Your Name]**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

## 🙏 Acknowledgments

- **Anthropic** - For Claude and AI research inspiration
- **Groq** - For fast LLM inference infrastructure
- **Streamlit** - For the amazing web framework
- **Medical Education Community** - For feedback and testing
- **Open Source Contributors** - For all the libraries used

## 📞 Contact & Support

### Get Help
- 📧 Email: your.email@example.com
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/virtual-patient-simulator/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/virtual-patient-simulator/issues)

### Stay Updated
- ⭐ Star this repo to show support
- 👁️ Watch for updates
- 🔔 Enable notifications for new releases

## 📚 Additional Resources

### For Medical Students
- [Clinical Reasoning Guide](https://www.nejm.org/doi/full/10.1056/NEJMra0804570)
- [Physical Examination Techniques](https://www.ncbi.nlm.nih.gov/books/NBK201/)

### For Developers
- [Streamlit Documentation](https://docs.streamlit.io)
- [Groq API Docs](https://console.groq.com/docs)
- [LangChain Guide](https://python.langchain.com/docs/get_started/introduction)

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/virtual-patient-simulator&type=Date)](https://star-history.com/#yourusername/virtual-patient-simulator&Date)

---

**Built with ❤️ for medical education**

*Last Updated: November 2024*
