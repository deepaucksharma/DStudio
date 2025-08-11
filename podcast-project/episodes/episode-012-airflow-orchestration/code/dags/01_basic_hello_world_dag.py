"""
Apache Airflow Basic DAG - Hello World with Indian Context
Episode 12: Workflow Orchestration Fundamentals

Author: Code Developer Agent
Language: Python with Hindi Comments
Context: Basic DAG introduction with Indian timezone
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pytz

# भारतीय टाइम जोन सेट करना
IST = pytz.timezone('Asia/Kolkata')

# डिफ़ॉल्ट आर्गुमेंट्स - हर DAG में होना चाहिए
default_args = {
    'owner': 'data-engineer',  # DAG का मालिक
    'depends_on_past': False,  # पिछले run पर depend नहीं करता
    'start_date': days_ago(1),  # कल से शुरू
    'email_on_failure': True,  # फेल होने पर email भेजो
    'email_on_retry': False,   # retry पर email नहीं
    'retries': 1,              # 1 बार retry करो
    'retry_delay': timedelta(minutes=5),  # 5 मिनट बाद retry
    'email': ['admin@mycompany.co.in']    # भारतीय email domain
}

# DAG परिभाषा
dag = DAG(
    dag_id='hello_world_indian_style',  # DAG का unique ID
    default_args=default_args,
    description='सबसे पहला DAG - Hello World भारतीय स्टाइल में',
    schedule_interval=timedelta(hours=1),  # हर घंटे चलेगा
    catchup=False,  # पुराने dates को catch up नहीं करना
    max_active_runs=1,  # एक समय में केवल एक run
    tags=['basic', 'tutorial', 'hindi'],  # Tags for organization
)

def greet_india():
    """भारतीय अभिवादन function"""
    current_time = datetime.now(IST)
    if current_time.hour < 12:
        greeting = "नमस्ते! शुभ प्रभात!"
    elif current_time.hour < 17:
        greeting = "नमस्ते! शुभ दोपहर!"
    else:
        greeting = "नमस्ते! शुभ संध्या!"
    
    print(f"{greeting}")
    print(f"समय: {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("Apache Airflow से Hello World!")
    print("यह आपका पहला successful DAG run है! 🎉")
    
    return greeting

# Task 1: Bash command से system info
system_info_task = BashOperator(
    task_id='get_system_info',  # Task का unique ID
    bash_command='''
    echo "==== भारतीय सिस्टम की जानकारी ===="
    echo "होस्टनेम: $(hostname)"
    echo "वर्तमान यूजर: $(whoami)"  
    echo "सिस्टम टाइम: $(date)"
    echo "डिस्क स्पेस:"
    df -h | head -2
    echo "मेमोरी उपयोग:"
    free -m | head -2
    echo "==== सिस्टम चेक पूरा ===="
    ''',
    dag=dag
)

# Task 2: Python function से greeting
greeting_task = PythonOperator(
    task_id='indian_greeting',  # Task का ID
    python_callable=greet_india,  # कौन सा function चलाना है
    dag=dag
)

# Task 3: Success message
success_task = BashOperator(
    task_id='success_message',
    bash_command='''
    echo "🎊 बधाई हो! आपका पहला Airflow DAG सफलतापूर्वक चला!"
    echo "अब आप workflow orchestration के मास्टर बनने की राह पर हैं!"
    echo "अगला कदम: IRCTC Tatkal booking DAG बनाना!"
    ''',
    dag=dag
)

# Task dependencies - कौन सा task कब चलेगा
# पहले system info, फिर greeting, फिर success message
system_info_task >> greeting_task >> success_task

# Alternative dependency syntax:
# system_info_task.set_downstream(greeting_task)
# greeting_task.set_downstream(success_task)

"""
इस DAG की खासियतें:
1. भारतीय timezone (IST) का उपयोग
2. Hindi comments और messages
3. Proper error handling और retries
4. Email notifications
5. System information gathering
6. Task dependencies

चलाने के लिए:
1. Airflow webserver start करें
2. Web UI में जाकर DAG को enable करें
3. Manual trigger करें या schedule के लिए wait करें

Production में इस्तेमाल:
- Monitoring scripts के लिए
- Health checks के लिए  
- Daily reports के लिए
"""