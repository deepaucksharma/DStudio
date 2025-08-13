#!/usr/bin/env python3
"""
BYJU'S Learning Analytics MLOps System
Episode 44: MLOps at Scale

यह example BYJU'S का student learning analytics और adaptive learning system दिखाता है
Personalized content recommendation, performance prediction, और engagement optimization।

Production Stats:
- BYJU'S: 100+ million registered students
- Daily active learners: 5.5+ million
- Content pieces: 50,000+ videos/lessons
- Learning sessions: 1+ billion annually
- Adaptive learning accuracy: 90%+
"""

import asyncio
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Embedding
from tensorflow.keras.optimizers import Adam
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from mlflow.tracking import MlflowClient
import redis
import warnings
warnings.filterwarnings('ignore')

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Student:
    """Student profile data structure"""
    student_id: str
    age: int
    grade: int  # Class 1-12
    learning_style: str  # visual, auditory, kinesthetic, reading
    subscription_type: str  # free, premium, premium_plus
    parent_involvement: float  # 0-1 scale
    device_type: str  # mobile, tablet, desktop
    location: str  # city name
    first_language: str
    subjects_enrolled: List[str]
    learning_goals: List[str]

@dataclass
class LearningSession:
    """Individual learning session data"""
    session_id: str
    student_id: str
    content_id: str
    subject: str
    topic: str
    content_type: str  # video, quiz, practice, game
    start_time: datetime
    duration_minutes: float
    completion_rate: float  # 0-1
    engagement_score: float  # 0-1
    quiz_score: Optional[float]  # 0-100 if applicable
    attempts: int
    help_sought: bool
    difficulty_level: str  # easy, medium, hard
    device_used: str

@dataclass
class ContentItem:
    """Learning content metadata"""
    content_id: str
    title: str
    subject: str
    topic: str
    subtopic: str
    grade_level: int
    content_type: str
    duration_minutes: float
    difficulty_level: str
    prerequisites: List[str]
    learning_objectives: List[str]
    engagement_score: float  # Historical average
    completion_rate: float  # Historical average

@dataclass
class LearningPrediction:
    """Prediction output for student learning"""
    student_id: str
    content_id: str
    predicted_completion_rate: float
    predicted_engagement: float
    predicted_score: Optional[float]
    difficulty_match: float  # How well content matches student level
    recommendation_confidence: float
    next_best_contents: List[str]
    learning_path_suggestions: List[str]
    prediction_timestamp: datetime

class StudentProfileBuilder:
    """Build comprehensive student profiles from learning data"""
    
    def __init__(self):
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
            "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
            "Indore", "Thane", "Bhopal", "Visakhapatnam", "Kochi", "Agra"
        ]
        
        self.subjects_by_grade = {
            1: ["Math", "English", "Hindi", "EVS"],
            2: ["Math", "English", "Hindi", "EVS"],
            3: ["Math", "English", "Hindi", "EVS", "General Knowledge"],
            4: ["Math", "English", "Hindi", "Science", "Social Studies"],
            5: ["Math", "English", "Hindi", "Science", "Social Studies"],
            6: ["Math", "English", "Hindi", "Science", "Social Studies"],
            7: ["Math", "English", "Hindi", "Science", "Social Studies"],
            8: ["Math", "English", "Hindi", "Science", "Social Studies"],
            9: ["Math", "English", "Hindi", "Physics", "Chemistry", "Biology", "Social Studies"],
            10: ["Math", "English", "Hindi", "Physics", "Chemistry", "Biology", "Social Studies"],
            11: ["Math", "English", "Physics", "Chemistry", "Biology", "Computer Science", "Commerce"],
            12: ["Math", "English", "Physics", "Chemistry", "Biology", "Computer Science", "Commerce"]
        }
        
        self.learning_goals_by_grade = {
            1: ["Basic reading", "Number recognition", "Shape identification"],
            2: ["Reading fluency", "Addition/Subtraction", "Time telling"],
            3: ["Comprehension", "Multiplication tables", "Money concepts"],
            4: ["Grammar basics", "Division", "Science basics"],
            5: ["Essay writing", "Fractions", "History basics"],
            6: ["Literature", "Decimals", "Geography"],
            7: ["Creative writing", "Algebra basics", "Biology intro"],
            8: ["Advanced grammar", "Geometry", "Chemistry intro"],
            9: ["Board exam prep", "Advanced math", "Science concepts"],
            10: ["Board exam mastery", "Problem solving", "Career guidance"],
            11: ["Competitive exam prep", "Specialization", "Advanced concepts"],
            12: ["JEE/NEET prep", "Board excellence", "College readiness"]
        }
    
    def generate_student_profile(self) -> Student:
        """Generate realistic student profile"""
        grade = np.random.randint(1, 13)  # Class 1-12
        age = grade + 5 + np.random.randint(-1, 2)  # Age roughly grade + 5-6
        
        # Learning style distribution (research-based)
        learning_styles = ["visual", "auditory", "kinesthetic", "reading"]
        style_weights = [0.4, 0.3, 0.2, 0.1]  # Visual learners dominate
        learning_style = np.random.choice(learning_styles, p=style_weights)
        
        # Subscription distribution (freemium model)
        subscription_types = ["free", "premium", "premium_plus"]
        sub_weights = [0.7, 0.25, 0.05]  # Most users are free
        subscription_type = np.random.choice(subscription_types, p=sub_weights)
        
        # Parent involvement (higher for younger kids)
        if grade <= 5:
            parent_involvement = np.random.beta(3, 1)  # High involvement
        elif grade <= 8:
            parent_involvement = np.random.beta(2, 2)  # Medium involvement
        else:
            parent_involvement = np.random.beta(1, 3)  # Lower involvement
        
        # Device usage patterns (mobile-first in India)
        device_types = ["mobile", "tablet", "desktop"]
        device_weights = [0.65, 0.25, 0.1]
        device_type = np.random.choice(device_types, p=device_weights)
        
        # Location (tier-wise distribution)
        location = np.random.choice(self.indian_cities)
        
        # First language (Hindi dominance with regional languages)
        languages = ["Hindi", "English", "Tamil", "Telugu", "Marathi", "Bengali", "Gujarati"]
        lang_weights = [0.4, 0.2, 0.1, 0.1, 0.08, 0.07, 0.05]
        first_language = np.random.choice(languages, p=lang_weights)
        
        # Subjects enrolled (grade-appropriate)
        available_subjects = self.subjects_by_grade.get(grade, ["Math", "English", "Science"])
        num_subjects = np.random.randint(2, len(available_subjects) + 1)
        subjects_enrolled = np.random.choice(available_subjects, size=num_subjects, replace=False).tolist()
        
        # Learning goals (grade-appropriate)
        available_goals = self.learning_goals_by_grade.get(grade, ["Academic excellence"])
        num_goals = np.random.randint(1, min(4, len(available_goals) + 1))
        learning_goals = np.random.choice(available_goals, size=num_goals, replace=False).tolist()
        
        return Student(
            student_id=f"student_{np.random.randint(100000, 999999)}",
            age=age,
            grade=grade,
            learning_style=learning_style,
            subscription_type=subscription_type,
            parent_involvement=parent_involvement,
            device_type=device_type,
            location=location,
            first_language=first_language,
            subjects_enrolled=subjects_enrolled,
            learning_goals=learning_goals
        )

class ContentGenerator:
    """Generate realistic educational content metadata"""
    
    def __init__(self):
        self.content_types = ["video", "quiz", "practice", "game", "reading"]
        self.type_weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        
        self.topics_by_subject = {
            "Math": {
                1: ["Numbers 1-10", "Shapes", "Patterns", "Counting"],
                2: ["Numbers 1-100", "Addition", "Subtraction", "Time"],
                3: ["Multiplication", "Division", "Fractions", "Money"],
                4: ["Large Numbers", "Factors", "Geometry", "Data"],
                5: ["Decimals", "Percentages", "Area", "Volume"],
                6: ["Integers", "Algebra basics", "Symmetry", "Graphs"],
                7: ["Rational Numbers", "Linear Equations", "Triangles", "Statistics"],
                8: ["Square Numbers", "Linear Equations Advanced", "Quadrilaterals"],
                9: ["Polynomials", "Coordinate Geometry", "Surface Areas"],
                10: ["Real Numbers", "Trigonometry", "Probability"],
                11: ["Sets", "Functions", "Limits", "Derivatives"],
                12: ["Integrals", "Differential Equations", "Vector Algebra"]
            },
            "English": {
                1: ["Alphabets", "Phonics", "Simple Words", "Rhymes"],
                2: ["Reading", "Spelling", "Grammar basics", "Stories"],
                3: ["Comprehension", "Vocabulary", "Sentence formation"],
                4: ["Grammar", "Essay writing", "Literature basics"],
                5: ["Advanced grammar", "Story writing", "Poetry"],
                6: ["Literature", "Creative writing", "Speech"],
                7: ["Advanced literature", "Debate", "Drama"],
                8: ["Critical thinking", "Advanced writing", "Analysis"],
                9: ["Board literature", "Advanced grammar", "Composition"],
                10: ["Board mastery", "Literature analysis", "Writing skills"],
                11: ["Advanced literature", "Critical analysis", "Creative expression"],
                12: ["Mastery level", "Exam preparation", "Communication skills"]
            },
            "Science": {
                4: ["Plants", "Animals", "Light", "Sound"],
                5: ["Matter", "Motion", "Living things", "Environment"],
                6: ["Food", "Body systems", "Motion and forces", "Natural resources"],
                7: ["Nutrition", "Reproduction", "Heat", "Acids and bases"],
                8: ["Crop production", "Microorganisms", "Force", "Sound"],
                9: ["Matter", "Living world", "Motion", "Sound"],
                10: ["Life processes", "Natural resources", "Light", "Electricity"]
            }
        }
    
    def generate_content_library(self, size: int = 1000) -> List[ContentItem]:
        """Generate realistic content library"""
        logger.info(f"🎓 Generating content library with {size} items...")
        
        content_library = []
        
        for i in range(size):
            # Random subject and grade
            subject = np.random.choice(list(self.topics_by_subject.keys()))
            grade_levels = list(self.topics_by_subject[subject].keys())
            grade = np.random.choice(grade_levels)
            
            # Random topic from subject/grade
            available_topics = self.topics_by_subject[subject][grade]
            topic = np.random.choice(available_topics)
            
            # Content type
            content_type = np.random.choice(self.content_types, p=self.type_weights)
            
            # Duration based on content type
            duration_ranges = {
                "video": (5, 15),
                "quiz": (3, 8),
                "practice": (10, 25),
                "game": (8, 20),
                "reading": (5, 12)
            }
            duration = np.random.uniform(*duration_ranges[content_type])
            
            # Difficulty level
            difficulty_levels = ["easy", "medium", "hard"]
            if grade <= 3:
                difficulty_weights = [0.7, 0.25, 0.05]
            elif grade <= 8:
                difficulty_weights = [0.4, 0.5, 0.1]
            else:
                difficulty_weights = [0.2, 0.5, 0.3]
            
            difficulty = np.random.choice(difficulty_levels, p=difficulty_weights)
            
            # Engagement and completion rates (realistic distributions)
            if content_type == "video":
                engagement_score = np.random.beta(3, 1.5)  # Videos generally engaging
                completion_rate = np.random.beta(2, 2)
            elif content_type == "game":
                engagement_score = np.random.beta(4, 1)  # Games highly engaging
                completion_rate = np.random.beta(3, 1.5)
            elif content_type == "quiz":
                engagement_score = np.random.beta(2, 2)  # Moderate engagement
                completion_rate = np.random.beta(3, 1)  # High completion
            else:
                engagement_score = np.random.beta(2, 1.5)
                completion_rate = np.random.beta(2, 2)
            
            content_item = ContentItem(
                content_id=f"content_{i:06d}",
                title=f"{topic} - {content_type.title()}",
                subject=subject,
                topic=topic,
                subtopic=f"{topic} Level {grade}",
                grade_level=grade,
                content_type=content_type,
                duration_minutes=duration,
                difficulty_level=difficulty,
                prerequisites=[],  # Simplified for demo
                learning_objectives=[f"Master {topic}", f"Apply {topic} concepts"],
                engagement_score=engagement_score,
                completion_rate=completion_rate
            )
            
            content_library.append(content_item)
        
        logger.info(f"✅ Generated {len(content_library)} content items")
        return content_library

class LearningSessionSimulator:
    """Simulate realistic learning sessions"""
    
    def __init__(self, students: List[Student], content_library: List[ContentItem]):
        self.students = students
        self.content_library = content_library
        
        # Create lookup for grade-appropriate content
        self.content_by_grade = {}
        for content in content_library:
            grade = content.grade_level
            if grade not in self.content_by_grade:
                self.content_by_grade[grade] = []
            self.content_by_grade[grade].append(content)
    
    def simulate_session(self, student: Student, content: ContentItem) -> LearningSession:
        """Simulate a realistic learning session"""
        
        # Session timing (realistic patterns for Indian students)
        current_time = datetime.now()
        
        # Study time patterns based on grade
        if student.grade <= 5:
            # Primary students - afternoon/evening
            study_hours = [14, 15, 16, 17, 18, 19]
            weights = [0.1, 0.15, 0.2, 0.25, 0.2, 0.1]
        elif student.grade <= 8:
            # Middle school - after school hours
            study_hours = [15, 16, 17, 18, 19, 20, 21]
            weights = [0.1, 0.15, 0.2, 0.25, 0.15, 0.1, 0.05]
        else:
            # High school - longer hours including late night
            study_hours = [16, 17, 18, 19, 20, 21, 22, 23]
            weights = [0.1, 0.15, 0.15, 0.2, 0.2, 0.1, 0.05, 0.05]
        
        study_hour = np.random.choice(study_hours, p=weights)
        start_time = current_time.replace(hour=study_hour, minute=np.random.randint(0, 60))
        
        # Duration influenced by content type, student characteristics
        base_duration = content.duration_minutes
        
        # Attention span by age (research-based)
        attention_spans = {
            5: 10, 6: 12, 7: 14, 8: 16, 9: 18, 10: 20,
            11: 22, 12: 25, 13: 30, 14: 35, 15: 40, 16: 45, 17: 50
        }
        max_attention = attention_spans.get(student.age, 30)
        
        # Duration factors
        duration_multiplier = 1.0
        
        if student.learning_style == "kinesthetic" and content.content_type == "game":
            duration_multiplier *= 1.3  # Kinesthetic learners engage more with games
        elif student.learning_style == "visual" and content.content_type == "video":
            duration_multiplier *= 1.2  # Visual learners engage more with videos
        
        if student.parent_involvement > 0.7:
            duration_multiplier *= 1.1  # Higher parent involvement = more time
        
        if student.subscription_type == "premium_plus":
            duration_multiplier *= 1.2  # Premium users spend more time
        
        actual_duration = min(base_duration * duration_multiplier, max_attention)
        actual_duration = max(1.0, actual_duration)  # At least 1 minute
        
        # Completion rate based on duration ratio and other factors
        duration_ratio = actual_duration / base_duration
        
        completion_base = min(1.0, duration_ratio)
        
        # Adjust based on difficulty match
        grade_diff = abs(content.grade_level - student.grade)
        if grade_diff == 0:
            difficulty_factor = 1.0
        elif grade_diff == 1:
            difficulty_factor = 0.8
        else:
            difficulty_factor = 0.6
        
        completion_rate = completion_base * difficulty_factor
        
        # Add some randomness
        completion_rate *= np.random.uniform(0.7, 1.2)
        completion_rate = np.clip(completion_rate, 0.0, 1.0)
        
        # Engagement score based on multiple factors
        engagement_factors = []
        
        # Content type preference by learning style
        style_preferences = {
            "visual": {"video": 1.3, "reading": 1.1, "quiz": 0.9, "practice": 0.8, "game": 1.0},
            "auditory": {"video": 1.2, "reading": 0.8, "quiz": 1.0, "practice": 0.9, "game": 1.1},
            "kinesthetic": {"video": 0.8, "reading": 0.7, "quiz": 0.9, "practice": 1.2, "game": 1.4},
            "reading": {"video": 0.9, "reading": 1.4, "quiz": 1.1, "practice": 1.0, "game": 0.8}
        }
        
        style_factor = style_preferences[student.learning_style].get(content.content_type, 1.0)
        engagement_factors.append(style_factor)
        
        # Time of day factor (students less engaged very late)
        if study_hour <= 18:
            time_factor = 1.0
        elif study_hour <= 21:
            time_factor = 0.9
        else:
            time_factor = 0.7
        engagement_factors.append(time_factor)
        
        # Subscription factor
        sub_factors = {"free": 0.9, "premium": 1.0, "premium_plus": 1.1}
        engagement_factors.append(sub_factors[student.subscription_type])
        
        base_engagement = content.engagement_score
        final_engagement = base_engagement * np.prod(engagement_factors)
        final_engagement = np.clip(final_engagement, 0.0, 1.0)
        
        # Quiz score (if applicable)
        quiz_score = None
        if content.content_type in ["quiz", "practice"]:
            # Base score influenced by completion rate and engagement
            base_score = 60 + (completion_rate * 30) + (final_engagement * 10)
            
            # Difficulty adjustment
            if content.difficulty_level == "easy":
                base_score += 10
            elif content.difficulty_level == "hard":
                base_score -= 10
            
            # Add noise
            quiz_score = np.clip(base_score + np.random.normal(0, 8), 0, 100)
        
        # Help sought (more likely for difficult content or struggling students)
        help_probability = 0.1  # Base probability
        if completion_rate < 0.5:
            help_probability = 0.4
        elif completion_rate < 0.8:
            help_probability = 0.2
        
        if grade_diff > 0:  # Content above grade level
            help_probability += 0.2
        
        help_sought = np.random.random() < help_probability
        
        # Attempts (more for difficult content or if help was sought)
        attempts = 1
        if help_sought or completion_rate < 0.7:
            attempts = np.random.poisson(1) + 1
        
        return LearningSession(
            session_id=f"session_{int(time.time())}_{np.random.randint(1000, 9999)}",
            student_id=student.student_id,
            content_id=content.content_id,
            subject=content.subject,
            topic=content.topic,
            content_type=content.content_type,
            start_time=start_time,
            duration_minutes=actual_duration,
            completion_rate=completion_rate,
            engagement_score=final_engagement,
            quiz_score=quiz_score,
            attempts=attempts,
            help_sought=help_sought,
            difficulty_level=content.difficulty_level,
            device_used=student.device_type
        )
    
    def generate_sessions(self, num_sessions: int = 5000) -> List[LearningSession]:
        """Generate multiple learning sessions"""
        logger.info(f"📚 Generating {num_sessions:,} learning sessions...")
        
        sessions = []
        
        for _ in range(num_sessions):
            # Random student
            student = np.random.choice(self.students)
            
            # Choose appropriate content for student's grade
            grade_content = self.content_by_grade.get(student.grade, [])
            if not grade_content:
                # If no exact grade match, use nearby grades
                nearby_grades = [g for g in self.content_by_grade.keys() 
                               if abs(g - student.grade) <= 2]
                if nearby_grades:
                    random_grade = np.random.choice(nearby_grades)
                    grade_content = self.content_by_grade[random_grade]
                else:
                    continue
            
            content = np.random.choice(grade_content)
            session = self.simulate_session(student, content)
            sessions.append(session)
        
        logger.info(f"✅ Generated {len(sessions):,} learning sessions")
        return sessions

class ByjuLearningAnalytics:
    """Complete BYJU'S Learning Analytics MLOps System"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.student_builder = StudentProfileBuilder()
        self.content_generator = ContentGenerator()
        
        # MLflow setup
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("byju_learning_analytics")
        
        # Redis for caching
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # Model storage
        self.model_path = Path("./models/byju_models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Models and preprocessors
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # Content library and students
        self.content_library = []
        self.students = []
    
    def initialize_system(self):
        """Initialize the complete learning system"""
        logger.info("🚀 Initializing BYJU'S Learning Analytics System...")
        
        # Generate student profiles
        self.students = [self.student_builder.generate_student_profile() 
                        for _ in range(1000)]  # 1000 students for demo
        
        # Generate content library
        self.content_library = self.content_generator.generate_content_library(500)  # 500 content items
        
        logger.info(f"✅ System initialized:")
        logger.info(f"   Students: {len(self.students):,}")
        logger.info(f"   Content Items: {len(self.content_library):,}")
    
    def generate_training_data(self) -> pd.DataFrame:
        """Generate comprehensive training data"""
        logger.info("📊 Generating training data from learning sessions...")
        
        # Generate learning sessions
        simulator = LearningSessionSimulator(self.students, self.content_library)
        sessions = simulator.generate_sessions(3000)  # 3000 sessions for demo
        
        # Convert to training format
        training_data = []
        
        student_lookup = {s.student_id: s for s in self.students}
        content_lookup = {c.content_id: c for c in self.content_library}
        
        for session in sessions:
            student = student_lookup[session.student_id]
            content = content_lookup[session.content_id]
            
            # Create feature vector
            feature_row = {
                # Student features
                'student_age': student.age,
                'student_grade': student.grade,
                'learning_style': student.learning_style,
                'subscription_type': student.subscription_type,
                'parent_involvement': student.parent_involvement,
                'device_type': student.device_type,
                'first_language': student.first_language,
                
                # Content features
                'content_duration': content.duration_minutes,
                'content_type': content.content_type,
                'difficulty_level': content.difficulty_level,
                'content_grade_level': content.grade_level,
                'historical_engagement': content.engagement_score,
                'historical_completion': content.completion_rate,
                
                # Context features
                'grade_difference': abs(content.grade_level - student.grade),
                'study_hour': session.start_time.hour,
                'is_weekend': session.start_time.weekday() >= 5,
                'device_match': session.device_used == student.device_type,
                
                # Subject matching
                'subject_enrolled': content.subject in student.subjects_enrolled,
                
                # Targets
                'completion_rate': session.completion_rate,
                'engagement_score': session.engagement_score,
                'quiz_score': session.quiz_score if session.quiz_score is not None else 0,
                'help_sought': session.help_sought,
                'attempts': session.attempts
            }
            
            training_data.append(feature_row)
        
        df = pd.DataFrame(training_data)
        logger.info(f"✅ Training data generated: {df.shape}")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Preprocess data for multiple ML models"""
        
        # Separate features and targets
        feature_columns = [col for col in df.columns 
                          if col not in ['completion_rate', 'engagement_score', 'quiz_score', 'help_sought', 'attempts']]
        
        categorical_features = ['learning_style', 'subscription_type', 'device_type', 
                              'first_language', 'content_type', 'difficulty_level']
        numerical_features = [col for col in feature_columns if col not in categorical_features]
        
        # Process categorical features
        processed_features = []
        
        for cat_feature in categorical_features:
            if cat_feature not in self.encoders:
                self.encoders[cat_feature] = LabelEncoder()
                encoded = self.encoders[cat_feature].fit_transform(df[cat_feature].astype(str))
            else:
                encoded = self.encoders[cat_feature].transform(df[cat_feature].astype(str))
            
            processed_features.append(encoded.reshape(-1, 1))
        
        # Process numerical features
        numerical_data = df[numerical_features].values
        
        if 'main_scaler' not in self.scalers:
            self.scalers['main_scaler'] = StandardScaler()
            scaled_numerical = self.scalers['main_scaler'].fit_transform(numerical_data)
        else:
            scaled_numerical = self.scalers['main_scaler'].transform(numerical_data)
        
        processed_features.append(scaled_numerical)
        
        # Combine features
        X = np.hstack(processed_features)
        
        # Prepare targets
        targets = {
            'completion_rate': df['completion_rate'].values,
            'engagement_score': df['engagement_score'].values,
            'quiz_score': df['quiz_score'].values,
            'help_sought': df['help_sought'].astype(int).values
        }
        
        return X, targets
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Train multiple prediction models"""
        
        with mlflow.start_run():
            logger.info("🤖 Training learning prediction models...")
            
            # Preprocess data
            X, targets = self.preprocess_data(df)
            
            metrics = {}
            
            # 1. Completion Rate Prediction (Regression)
            logger.info("📈 Training completion rate prediction model...")
            y_completion = targets['completion_rate']
            X_train, X_test, y_train, y_test = train_test_split(X, y_completion, test_size=0.2, random_state=42)
            
            completion_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
            completion_model.fit(X_train, y_train)
            
            completion_pred = completion_model.predict(X_test)
            completion_mse = np.mean((y_test - completion_pred) ** 2)
            completion_r2 = 1 - (np.sum((y_test - completion_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
            
            self.models['completion_rate'] = completion_model
            metrics['completion_rate'] = {'mse': completion_mse, 'r2': completion_r2}
            
            # 2. Engagement Score Prediction (Regression)
            logger.info("❤️ Training engagement prediction model...")
            y_engagement = targets['engagement_score']
            X_train, X_test, y_train, y_test = train_test_split(X, y_engagement, test_size=0.2, random_state=42)
            
            engagement_model = RandomForestRegressor(n_estimators=100, random_state=42)
            engagement_model.fit(X_train, y_train)
            
            engagement_pred = engagement_model.predict(X_test)
            engagement_mse = np.mean((y_test - engagement_pred) ** 2)
            engagement_r2 = 1 - (np.sum((y_test - engagement_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
            
            self.models['engagement_score'] = engagement_model
            metrics['engagement_score'] = {'mse': engagement_mse, 'r2': engagement_r2}
            
            # 3. Help Seeking Prediction (Classification)
            logger.info("🆘 Training help-seeking prediction model...")
            y_help = targets['help_sought']
            X_train, X_test, y_train, y_test = train_test_split(X, y_help, test_size=0.2, random_state=42)
            
            help_model = RandomForestClassifier(n_estimators=100, random_state=42)
            help_model.fit(X_train, y_train)
            
            help_pred = help_model.predict(X_test)
            help_accuracy = accuracy_score(y_test, help_pred)
            help_f1 = f1_score(y_test, help_pred)
            
            self.models['help_sought'] = help_model
            metrics['help_sought'] = {'accuracy': help_accuracy, 'f1': help_f1}
            
            # Log metrics to MLflow
            for model_name, model_metrics in metrics.items():
                for metric_name, value in model_metrics.items():
                    mlflow.log_metric(f"{model_name}_{metric_name}", value)
            
            # Save models
            for model_name, model in self.models.items():
                model_path = self.model_path / f"{model_name}_model.joblib"
                joblib.dump(model, model_path)
                mlflow.sklearn.log_model(model, model_name)
            
            # Save preprocessors
            joblib.dump(self.scalers, self.model_path / "scalers.joblib")
            joblib.dump(self.encoders, self.model_path / "encoders.joblib")
            
            logger.info("✅ Model training completed")
            return metrics
    
    def predict_learning_outcome(self, 
                                student: Student, 
                                content: ContentItem) -> LearningPrediction:
        """Predict learning outcomes for student-content pair"""
        
        # Create feature vector
        feature_data = {
            'student_age': student.age,
            'student_grade': student.grade,
            'learning_style': student.learning_style,
            'subscription_type': student.subscription_type,
            'parent_involvement': student.parent_involvement,
            'device_type': student.device_type,
            'first_language': student.first_language,
            'content_duration': content.duration_minutes,
            'content_type': content.content_type,
            'difficulty_level': content.difficulty_level,
            'content_grade_level': content.grade_level,
            'historical_engagement': content.engagement_score,
            'historical_completion': content.completion_rate,
            'grade_difference': abs(content.grade_level - student.grade),
            'study_hour': datetime.now().hour,
            'is_weekend': datetime.now().weekday() >= 5,
            'device_match': True,  # Assuming same device
            'subject_enrolled': content.subject in student.subjects_enrolled
        }
        
        # Convert to DataFrame for preprocessing
        df = pd.DataFrame([feature_data])
        X = self.preprocess_data(df)[0]
        
        # Make predictions
        predictions = {}
        
        if 'completion_rate' in self.models:
            predictions['completion_rate'] = self.models['completion_rate'].predict(X)[0]
        else:
            predictions['completion_rate'] = 0.7  # Default
        
        if 'engagement_score' in self.models:
            predictions['engagement_score'] = self.models['engagement_score'].predict(X)[0]
        else:
            predictions['engagement_score'] = 0.7  # Default
        
        if 'help_sought' in self.models:
            help_prob = self.models['help_sought'].predict_proba(X)[0][1]
            predictions['help_probability'] = help_prob
        else:
            predictions['help_probability'] = 0.2  # Default
        
        # Calculate difficulty match score
        grade_diff = abs(content.grade_level - student.grade)
        difficulty_match = max(0.0, 1.0 - (grade_diff * 0.3))
        
        # Calculate recommendation confidence
        confidence_factors = [
            predictions['completion_rate'],
            predictions['engagement_score'],
            difficulty_match,
            1.0 if content.subject in student.subjects_enrolled else 0.5
        ]
        recommendation_confidence = np.mean(confidence_factors)
        
        # Find next best contents (simplified)
        next_best_contents = [f"content_{i:06d}" for i in range(3)]
        learning_path_suggestions = [f"path_{i}" for i in range(2)]
        
        return LearningPrediction(
            student_id=student.student_id,
            content_id=content.content_id,
            predicted_completion_rate=max(0.0, min(1.0, predictions['completion_rate'])),
            predicted_engagement=max(0.0, min(1.0, predictions['engagement_score'])),
            predicted_score=None,  # Would require quiz-specific model
            difficulty_match=difficulty_match,
            recommendation_confidence=recommendation_confidence,
            next_best_contents=next_best_contents,
            learning_path_suggestions=learning_path_suggestions,
            prediction_timestamp=datetime.now()
        )
    
    def get_personalized_recommendations(self, 
                                       student: Student, 
                                       num_recommendations: int = 5) -> List[LearningPrediction]:
        """Get personalized content recommendations for student"""
        
        # Filter appropriate content for student
        appropriate_content = [
            content for content in self.content_library
            if abs(content.grade_level - student.grade) <= 2  # Within 2 grades
            and content.subject in student.subjects_enrolled
        ]
        
        if not appropriate_content:
            appropriate_content = self.content_library[:10]  # Fallback
        
        # Get predictions for all appropriate content
        predictions = []
        for content in appropriate_content:
            try:
                prediction = self.predict_learning_outcome(student, content)
                predictions.append(prediction)
            except Exception as e:
                logger.warning(f"Error predicting for {content.content_id}: {e}")
                continue
        
        # Sort by recommendation confidence and engagement
        predictions.sort(
            key=lambda p: (p.recommendation_confidence, p.predicted_engagement), 
            reverse=True
        )
        
        return predictions[:num_recommendations]

async def main():
    """Main demo function"""
    print("🎓 Starting BYJU'S Learning Analytics MLOps System")
    print("📚 Complete adaptive learning platform with personalized recommendations...")
    print("🤖 Training ML models for engagement prediction और learning optimization...\n")
    
    # Initialize system
    analytics = ByjuLearningAnalytics()
    analytics.initialize_system()
    
    try:
        # Phase 1: Data Generation and Model Training
        print("📊 Phase 1: Training Data Generation and ML Model Training")
        training_data = analytics.generate_training_data()
        
        print(f"📈 Training data statistics:")
        print(f"   Total sessions: {len(training_data):,}")
        print(f"   Average completion rate: {training_data['completion_rate'].mean():.2%}")
        print(f"   Average engagement score: {training_data['engagement_score'].mean():.2f}")
        print(f"   Help sought rate: {training_data['help_sought'].mean():.2%}")
        
        # Train models
        metrics = analytics.train_models(training_data)
        
        print(f"\n✅ Model Training Results:")
        for model_name, model_metrics in metrics.items():
            print(f"   {model_name}:")
            for metric, value in model_metrics.items():
                if metric in ['mse']:
                    print(f"     {metric.upper()}: {value:.4f}")
                elif metric in ['r2', 'accuracy', 'f1']:
                    print(f"     {metric.upper()}: {value:.3f}")
        
        # Phase 2: Personalized Recommendations
        print(f"\n🎯 Phase 2: Personalized Learning Recommendations")
        
        # Select sample students from different grades
        sample_students = []
        for grade in [3, 6, 9, 12]:
            grade_students = [s for s in analytics.students if s.grade == grade]
            if grade_students:
                sample_students.append(grade_students[0])
        
        for student in sample_students:
            print(f"\n👨‍🎓 Student Profile: {student.student_id}")
            print(f"   Grade: {student.grade}, Age: {student.age}")
            print(f"   Learning Style: {student.learning_style}")
            print(f"   Subjects: {', '.join(student.subjects_enrolled)}")
            print(f"   Device: {student.device_type}, Location: {student.location}")
            
            # Get personalized recommendations
            recommendations = analytics.get_personalized_recommendations(student, 3)
            
            print(f"   📚 Top Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                content = next((c for c in analytics.content_library if c.content_id == rec.content_id), None)
                if content:
                    print(f"     {i}. {content.title}")
                    print(f"        Predicted Completion: {rec.predicted_completion_rate:.1%}")
                    print(f"        Predicted Engagement: {rec.predicted_engagement:.2f}/1.0")
                    print(f"        Confidence: {rec.recommendation_confidence:.2f}/1.0")
        
        # Phase 3: Learning Analytics Dashboard
        print(f"\n📊 Phase 3: Learning Analytics Insights")
        
        # Aggregate insights
        print(f"📈 System-wide Analytics:")
        
        # Grade-wise performance
        grade_stats = training_data.groupby('student_grade').agg({
            'completion_rate': 'mean',
            'engagement_score': 'mean',
            'quiz_score': 'mean'
        }).round(3)
        
        print(f"   Grade-wise Performance:")
        for grade, stats in grade_stats.iterrows():
            print(f"     Grade {grade}: Completion {stats['completion_rate']:.1%}, "
                  f"Engagement {stats['engagement_score']:.2f}, "
                  f"Quiz Score {stats['quiz_score']:.1f}")
        
        # Content type effectiveness
        content_stats = training_data.groupby('content_type').agg({
            'completion_rate': 'mean',
            'engagement_score': 'mean'
        }).round(3)
        
        print(f"   Content Type Effectiveness:")
        for content_type, stats in content_stats.iterrows():
            print(f"     {content_type.title()}: Completion {stats['completion_rate']:.1%}, "
                  f"Engagement {stats['engagement_score']:.2f}")
        
        # Learning style insights
        style_stats = training_data.groupby('learning_style').agg({
            'completion_rate': 'mean',
            'engagement_score': 'mean'
        }).round(3)
        
        print(f"   Learning Style Performance:")
        for style, stats in style_stats.iterrows():
            print(f"     {style.title()}: Completion {stats['completion_rate']:.1%}, "
                  f"Engagement {stats['engagement_score']:.2f}")
        
        # Device usage patterns
        device_stats = training_data.groupby('device_type').size().sort_values(ascending=False)
        print(f"   Device Usage Distribution:")
        for device, count in device_stats.items():
            percentage = (count / len(training_data)) * 100
            print(f"     {device.title()}: {percentage:.1f}% ({count:,} sessions)")
        
    except Exception as e:
        logger.error(f"❌ Error in demo: {e}")
        raise
    
    finally:
        print(f"\n🎯 DEMO COMPLETED!")
        print(f"💡 In production, BYJU'S Learning Analytics would:")
        print(f"   - Process 100M+ student interactions daily")
        print(f"   - Serve personalized recommendations in <100ms")
        print(f"   - Adapt learning paths based on real-time performance")
        print(f"   - Optimize content difficulty for maximum engagement")
        print(f"   - Provide actionable insights to educators and parents")
        print(f"   - Support 10+ Indian languages और regional preferences")

if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(main())