# Tutr.ai

Intelligent Post-Lecture tutor for students.

A teacher can create a class. Students can register for the class.


## Installation

Clone the repository and install the dependencies.

```bash
git clone
cd berri_ai_hack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

1) Create a telegram bot with botfather
2) Make a copy of .env.example and rename it to .env
3) Add your telegram bot token to .env
4) Add DB name into .env
5) Run the following commands

```bash
python3 main.py
```

6) Find telegram bot by its username and interact with it

## TODO

1) Upload transcript
2) Send MCQ questions to students
3) Send customized feedback and remediation plan based on student performance
4) Customized practice questions for students