#!/usr/bin/env python3
"""
Domain-Driven Design: Hexagonal Architecture - Byju's Learning Platform
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Hexagonal Architecture (Ports & Adapters) 
का इस्तेमाल करके Byju's learning platform बनाते हैं। 
Core business logic को external dependencies से isolate करना।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass, asdict
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import json

# ====================================================================
# CORE DOMAIN - Business Logic (Center of Hexagon)
# ====================================================================

# Domain Enums
class StudentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class CourseLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LessonType(Enum):
    VIDEO = "video"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    LIVE_CLASS = "live_class"

class ProgressStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Domain Value Objects
@dataclass(frozen=True)
class StudentId:
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 5:
            raise ValueError("Student ID must be at least 5 characters")

@dataclass(frozen=True)
class CourseId:
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.startswith("COURSE_"):
            raise ValueError("Course ID must start with COURSE_")

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

@dataclass(frozen=True)
class Grade:
    score: int
    max_score: int
    
    def __post_init__(self):
        if not (0 <= self.score <= self.max_score):
            raise ValueError("Invalid score range")
    
    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0

@dataclass(frozen=True)
class LearningGoal:
    subject: str
    target_completion_date: datetime
    target_score_percentage: float
    
    def __post_init__(self):
        if not (0 <= self.target_score_percentage <= 100):
            raise ValueError("Target score must be between 0-100")

# Domain Entities
class Student:
    """
    Student Entity - Core domain entity
    Student entity - core business logic
    """
    
    def __init__(
        self,
        student_id: StudentId,
        name: str,
        age: int,
        grade_level: int,
        email: str
    ):
        self._student_id = student_id
        self._name = name
        self._age = age
        self._grade_level = grade_level
        self._email = email
        
        # Student state
        self._status = StudentStatus.ACTIVE
        self._enrolled_courses: List[CourseId] = []
        self._learning_goals: List[LearningGoal] = []
        self._total_study_time_minutes = 0
        self._created_at = datetime.now()
        self._last_activity_at = datetime.now()
        
        # Performance tracking
        self._completed_lessons = 0
        self._total_quiz_score = 0
        self._total_quizzes_taken = 0
        
        print(f"👨‍🎓 Student registered: {name} (Grade {grade_level})")
    
    @property
    def student_id(self) -> StudentId:
        return self._student_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def age(self) -> int:
        return self._age
    
    @property
    def grade_level(self) -> int:
        return self._grade_level
    
    @property
    def status(self) -> StudentStatus:
        return self._status
    
    @property
    def enrolled_courses(self) -> List[CourseId]:
        return self._enrolled_courses.copy()
    
    @property
    def average_quiz_score(self) -> float:
        if self._total_quizzes_taken == 0:
            return 0.0
        return self._total_quiz_score / self._total_quizzes_taken
    
    def enroll_in_course(self, course_id: CourseId) -> None:
        """Enroll student in a course"""
        if self._status != StudentStatus.ACTIVE:
            raise ValueError("Only active students can enroll")
        
        if course_id not in self._enrolled_courses:
            self._enrolled_courses.append(course_id)
            self._last_activity_at = datetime.now()
            
            print(f"📚 {self._name} enrolled in course: {course_id.value}")
    
    def add_learning_goal(self, goal: LearningGoal) -> None:
        """Add learning goal for student"""
        self._learning_goals.append(goal)
        print(f"🎯 Learning goal added: {goal.subject} (Target: {goal.target_score_percentage}%)")
    
    def record_lesson_completion(self, lesson_duration_minutes: int) -> None:
        """Record lesson completion"""
        self._completed_lessons += 1
        self._total_study_time_minutes += lesson_duration_minutes
        self._last_activity_at = datetime.now()
        
        print(f"✅ Lesson completed: {self._completed_lessons} total")
    
    def record_quiz_attempt(self, grade: Grade) -> None:
        """Record quiz attempt and score"""
        self._total_quizzes_taken += 1
        self._total_quiz_score += grade.percentage
        self._last_activity_at = datetime.now()
        
        print(f"📝 Quiz completed: {grade.score}/{grade.max_score} ({grade.percentage:.1f}%)")
    
    def suspend_student(self, reason: str) -> None:
        """Suspend student account"""
        self._status = StudentStatus.SUSPENDED
        print(f"🚫 Student suspended: {reason}")
    
    def activate_student(self) -> None:
        """Activate student account"""
        self._status = StudentStatus.ACTIVE
        print(f"✅ Student activated")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get student performance summary"""
        return {
            "student_id": self._student_id.value,
            "name": self._name,
            "total_study_hours": round(self._total_study_time_minutes / 60, 2),
            "completed_lessons": self._completed_lessons,
            "quizzes_taken": self._total_quizzes_taken,
            "average_quiz_score": round(self.average_quiz_score, 2),
            "enrolled_courses": len(self._enrolled_courses),
            "learning_goals": len(self._learning_goals),
            "last_activity": self._last_activity_at.isoformat()
        }

class Course:
    """Course Entity"""
    
    def __init__(
        self,
        course_id: CourseId,
        title: str,
        subject: str,
        level: CourseLevel,
        price: Money
    ):
        self._course_id = course_id
        self._title = title
        self._subject = subject
        self._level = level
        self._price = price
        
        # Course content
        self._lessons: List[Dict[str, Any]] = []
        self._total_duration_minutes = 0
        self._enrolled_students_count = 0
        
        print(f"📖 Course created: {title} ({subject})")
    
    @property
    def course_id(self) -> CourseId:
        return self._course_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def subject(self) -> str:
        return self._subject
    
    @property
    def level(self) -> CourseLevel:
        return self._level
    
    @property
    def price(self) -> Money:
        return self._price
    
    def add_lesson(self, title: str, lesson_type: LessonType, duration_minutes: int) -> str:
        """Add lesson to course"""
        lesson_id = str(uuid4())
        lesson = {
            "lesson_id": lesson_id,
            "title": title,
            "type": lesson_type.value,
            "duration_minutes": duration_minutes,
            "order": len(self._lessons) + 1
        }
        
        self._lessons.append(lesson)
        self._total_duration_minutes += duration_minutes
        
        print(f"📚 Lesson added: {title} ({duration_minutes} min)")
        return lesson_id
    
    def enroll_student(self) -> None:
        """Increment enrolled students count"""
        self._enrolled_students_count += 1
    
    def get_course_info(self) -> Dict[str, Any]:
        """Get course information"""
        return {
            "course_id": self._course_id.value,
            "title": self._title,
            "subject": self._subject,
            "level": self._level.value,
            "price": float(self._price.amount),
            "total_lessons": len(self._lessons),
            "total_duration_hours": round(self._total_duration_minutes / 60, 2),
            "enrolled_students": self._enrolled_students_count
        }

# Domain Services
class LearningRecommendationService:
    """
    Domain service for learning recommendations
    Learning recommendations के लिए domain service
    """
    
    @staticmethod
    def recommend_courses_for_student(
        student: Student,
        available_courses: List[Course]
    ) -> List[Course]:
        """Recommend courses based on student profile"""
        recommendations = []
        
        for course in available_courses:
            # Skip if already enrolled
            if course.course_id in student.enrolled_courses:
                continue
            
            # Grade-level matching
            if course.subject.lower() in ["math", "science", "english"]:
                # Core subjects suitable for grade level
                if student.grade_level >= 5:  # Middle school and above
                    if course.level == CourseLevel.BEGINNER and student.average_quiz_score < 60:
                        recommendations.append(course)
                    elif course.level == CourseLevel.INTERMEDIATE and 60 <= student.average_quiz_score < 80:
                        recommendations.append(course)
                    elif course.level == CourseLevel.ADVANCED and student.average_quiz_score >= 80:
                        recommendations.append(course)
        
        # Sort by relevance (simplified)
        recommendations.sort(key=lambda c: c.level.value)
        
        return recommendations[:3]  # Top 3 recommendations

# ====================================================================
# PORTS - Interfaces (Hexagon Boundaries)
# ====================================================================

# Primary Ports (Driving - inbound)
class LearningPlatformService(Protocol):
    """Primary port for learning platform operations"""
    
    def register_student(self, name: str, age: int, grade_level: int, email: str) -> StudentId:
        ...
    
    def enroll_student_in_course(self, student_id: StudentId, course_id: CourseId) -> bool:
        ...
    
    def record_lesson_progress(self, student_id: StudentId, lesson_id: str, duration_minutes: int) -> bool:
        ...
    
    def submit_quiz(self, student_id: StudentId, quiz_id: str, answers: List[str]) -> Grade:
        ...
    
    def get_student_dashboard(self, student_id: StudentId) -> Dict[str, Any]:
        ...

# Secondary Ports (Driven - outbound)
class StudentRepository(ABC):
    """Port for student data persistence"""
    
    @abstractmethod
    def save_student(self, student: Student) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, student_id: StudentId) -> Optional[Student]:
        pass
    
    @abstractmethod
    def find_all_active(self) -> List[Student]:
        pass

class CourseRepository(ABC):
    """Port for course data persistence"""
    
    @abstractmethod
    def save_course(self, course: Course) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        pass
    
    @abstractmethod
    def find_by_subject(self, subject: str) -> List[Course]:
        pass

class NotificationPort(ABC):
    """Port for sending notifications"""
    
    @abstractmethod
    def send_enrollment_confirmation(self, student_email: str, course_title: str) -> bool:
        pass
    
    @abstractmethod
    def send_progress_update(self, student_email: str, progress_data: Dict[str, Any]) -> bool:
        pass

class AnalyticsPort(ABC):
    """Port for analytics and reporting"""
    
    @abstractmethod
    def track_lesson_completion(self, student_id: str, lesson_id: str, duration_minutes: int) -> None:
        pass
    
    @abstractmethod
    def track_quiz_attempt(self, student_id: str, quiz_id: str, score: float) -> None:
        pass

class PaymentPort(ABC):
    """Port for payment processing"""
    
    @abstractmethod
    def process_course_payment(self, student_id: str, course_id: str, amount: Decimal) -> Dict[str, Any]:
        pass

# ====================================================================
# CORE APPLICATION SERVICE (Orchestrates Domain Logic)
# ====================================================================

class LearningPlatformApplicationService:
    """
    Application Service - Orchestrates domain logic
    Application service - domain logic को orchestrate करती है
    """
    
    def __init__(
        self,
        student_repository: StudentRepository,
        course_repository: CourseRepository,
        notification_port: NotificationPort,
        analytics_port: AnalyticsPort,
        payment_port: PaymentPort
    ):
        self._student_repo = student_repository
        self._course_repo = course_repository
        self._notification_port = notification_port
        self._analytics_port = analytics_port
        self._payment_port = payment_port
        
        print("🏗️ Learning Platform Application Service initialized")
    
    def register_student(self, name: str, age: int, grade_level: int, email: str) -> StudentId:
        """Register new student"""
        student_id = StudentId(f"STUDENT_{uuid4()}")
        
        student = Student(student_id, name, age, grade_level, email)
        self._student_repo.save_student(student)
        
        # Send welcome notification
        self._notification_port.send_enrollment_confirmation(
            email, "Welcome to Byju's Learning Platform!"
        )
        
        return student_id
    
    def enroll_student_in_course(self, student_id: StudentId, course_id: CourseId) -> bool:
        """Enroll student in a course"""
        student = self._student_repo.find_by_id(student_id)
        course = self._course_repo.find_by_id(course_id)
        
        if not student or not course:
            return False
        
        # Process payment first
        payment_result = self._payment_port.process_course_payment(
            student_id.value, course_id.value, course.price.amount
        )
        
        if payment_result.get("status") != "success":
            print(f"❌ Payment failed for course enrollment")
            return False
        
        # Enroll student
        student.enroll_in_course(course_id)
        course.enroll_student()
        
        # Save changes
        self._student_repo.save_student(student)
        self._course_repo.save_course(course)
        
        # Send confirmation
        self._notification_port.send_enrollment_confirmation(
            student._email, course.title
        )
        
        return True
    
    def record_lesson_progress(self, student_id: StudentId, lesson_id: str, duration_minutes: int) -> bool:
        """Record student lesson progress"""
        student = self._student_repo.find_by_id(student_id)
        if not student:
            return False
        
        # Record progress
        student.record_lesson_completion(duration_minutes)
        self._student_repo.save_student(student)
        
        # Track analytics
        self._analytics_port.track_lesson_completion(
            student_id.value, lesson_id, duration_minutes
        )
        
        # Check for milestones and send progress updates
        if student._completed_lessons % 10 == 0:  # Every 10 lessons
            progress_data = student.get_performance_summary()
            self._notification_port.send_progress_update(
                student._email, progress_data
            )
        
        return True
    
    def submit_quiz(self, student_id: StudentId, quiz_id: str, answers: List[str]) -> Optional[Grade]:
        """Submit quiz and calculate grade"""
        student = self._student_repo.find_by_id(student_id)
        if not student:
            return None
        
        # Simplified quiz grading (in real system, this would be more complex)
        correct_answers = len(answers)  # Assume all answers are correct for demo
        total_questions = len(answers) + 2  # Add some incorrect ones
        
        grade = Grade(correct_answers, total_questions)
        
        # Record quiz attempt
        student.record_quiz_attempt(grade)
        self._student_repo.save_student(student)
        
        # Track analytics
        self._analytics_port.track_quiz_attempt(
            student_id.value, quiz_id, grade.percentage
        )
        
        return grade
    
    def get_student_dashboard(self, student_id: StudentId) -> Optional[Dict[str, Any]]:
        """Get comprehensive student dashboard"""
        student = self._student_repo.find_by_id(student_id)
        if not student:
            return None
        
        # Get enrolled courses info
        enrolled_courses = []
        for course_id in student.enrolled_courses:
            course = self._course_repo.find_by_id(course_id)
            if course:
                enrolled_courses.append(course.get_course_info())
        
        # Get recommendations
        all_courses = self._course_repo.find_by_subject("All")  # Get all courses
        recommendations = LearningRecommendationService.recommend_courses_for_student(
            student, all_courses
        )
        
        recommendation_data = [course.get_course_info() for course in recommendations]
        
        # Build dashboard
        dashboard = {
            "student_info": student.get_performance_summary(),
            "enrolled_courses": enrolled_courses,
            "recommended_courses": recommendation_data,
            "achievements": self._calculate_achievements(student),
            "next_goals": self._get_suggested_goals(student)
        }
        
        return dashboard
    
    def _calculate_achievements(self, student: Student) -> List[Dict[str, str]]:
        """Calculate student achievements"""
        achievements = []
        
        if student._completed_lessons >= 50:
            achievements.append({"title": "Lesson Master", "description": "Completed 50+ lessons"})
        
        if student.average_quiz_score >= 90:
            achievements.append({"title": "Quiz Champion", "description": "90%+ average quiz score"})
        
        if student._total_study_time_minutes >= 1800:  # 30 hours
            achievements.append({"title": "Study Warrior", "description": "30+ hours of study time"})
        
        return achievements
    
    def _get_suggested_goals(self, student: Student) -> List[Dict[str, Any]]:
        """Get suggested learning goals"""
        suggestions = []
        
        if student.average_quiz_score < 70:
            suggestions.append({
                "goal": "Improve quiz performance",
                "target": "Achieve 80% average score",
                "timeline": "2 weeks"
            })
        
        if student._completed_lessons < 20:
            suggestions.append({
                "goal": "Complete more lessons",
                "target": "Complete 30 lessons",
                "timeline": "1 month"
            })
        
        return suggestions

# ====================================================================
# ADAPTERS - External Interface Implementations
# ====================================================================

# Secondary Adapters (Outbound)
class InMemoryStudentRepository(StudentRepository):
    """In-memory student repository adapter"""
    
    def __init__(self):
        self._students: Dict[str, Student] = {}
    
    def save_student(self, student: Student) -> None:
        self._students[student.student_id.value] = student
        print(f"💾 Student saved: {student.student_id.value}")
    
    def find_by_id(self, student_id: StudentId) -> Optional[Student]:
        return self._students.get(student_id.value)
    
    def find_all_active(self) -> List[Student]:
        return [s for s in self._students.values() if s.status == StudentStatus.ACTIVE]

class InMemoryCourseRepository(CourseRepository):
    """In-memory course repository adapter"""
    
    def __init__(self):
        self._courses: Dict[str, Course] = {}
    
    def save_course(self, course: Course) -> None:
        self._courses[course.course_id.value] = course
        print(f"💾 Course saved: {course.course_id.value}")
    
    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        return self._courses.get(course_id.value)
    
    def find_by_subject(self, subject: str) -> List[Course]:
        if subject == "All":
            return list(self._courses.values())
        return [c for c in self._courses.values() if c.subject.lower() == subject.lower()]

class EmailNotificationAdapter(NotificationPort):
    """Email notification adapter"""
    
    def send_enrollment_confirmation(self, student_email: str, course_title: str) -> bool:
        print(f"📧 Email sent to {student_email}: Enrolled in '{course_title}'")
        return True
    
    def send_progress_update(self, student_email: str, progress_data: Dict[str, Any]) -> bool:
        print(f"📧 Progress update sent to {student_email}")
        print(f"   Completed lessons: {progress_data['completed_lessons']}")
        print(f"   Study hours: {progress_data['total_study_hours']}")
        return True

class ConsoleAnalyticsAdapter(AnalyticsPort):
    """Console analytics adapter"""
    
    def track_lesson_completion(self, student_id: str, lesson_id: str, duration_minutes: int) -> None:
        print(f"📊 Analytics: Lesson completed by {student_id} ({duration_minutes} min)")
    
    def track_quiz_attempt(self, student_id: str, quiz_id: str, score: float) -> None:
        print(f"📊 Analytics: Quiz attempt by {student_id} (Score: {score:.1f}%)")

class MockPaymentAdapter(PaymentPort):
    """Mock payment processing adapter"""
    
    def process_course_payment(self, student_id: str, course_id: str, amount: Decimal) -> Dict[str, Any]:
        print(f"💳 Processing payment: ₹{amount} for course {course_id}")
        
        # Simulate payment processing
        import random
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            transaction_id = f"TXN_{uuid4()}"
            print(f"✅ Payment successful: {transaction_id}")
            return {
                "status": "success",
                "transaction_id": transaction_id,
                "amount": float(amount)
            }
        else:
            print(f"❌ Payment failed")
            return {"status": "failed", "reason": "Insufficient funds"}

# Primary Adapter (Inbound)
class RESTAPIAdapter:
    """REST API adapter - Primary adapter"""
    
    def __init__(self, learning_service: LearningPlatformApplicationService):
        self._service = learning_service
    
    def register_student_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """REST endpoint for student registration"""
        try:
            student_id = self._service.register_student(
                name=request_data["name"],
                age=request_data["age"],
                grade_level=request_data["grade_level"],
                email=request_data["email"]
            )
            
            return {
                "status": "success",
                "student_id": student_id.value,
                "message": "Student registered successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def enroll_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """REST endpoint for course enrollment"""
        try:
            success = self._service.enroll_student_in_course(
                StudentId(request_data["student_id"]),
                CourseId(request_data["course_id"])
            )
            
            return {
                "status": "success" if success else "failed",
                "message": "Enrollment successful" if success else "Enrollment failed"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def dashboard_endpoint(self, student_id: str) -> Dict[str, Any]:
        """REST endpoint for student dashboard"""
        try:
            dashboard = self._service.get_student_dashboard(StudentId(student_id))
            
            if dashboard:
                return {
                    "status": "success",
                    "data": dashboard
                }
            else:
                return {
                    "status": "error",
                    "message": "Student not found"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# ====================================================================
# USAGE EXAMPLE AND TESTING
# ====================================================================

def create_byju_learning_system():
    """Create complete Byju's learning system with hexagonal architecture"""
    
    print("🏗️ Building Byju's Learning System")
    print("=" * 35)
    
    # Create adapters (external dependencies)
    student_repo = InMemoryStudentRepository()
    course_repo = InMemoryCourseRepository()
    notification_adapter = EmailNotificationAdapter()
    analytics_adapter = ConsoleAnalyticsAdapter()
    payment_adapter = MockPaymentAdapter()
    
    # Create core application service (injecting dependencies)
    learning_service = LearningPlatformApplicationService(
        student_repo,
        course_repo,
        notification_adapter,
        analytics_adapter,
        payment_adapter
    )
    
    # Create primary adapter (REST API)
    api_adapter = RESTAPIAdapter(learning_service)
    
    # Create sample courses
    courses = [
        Course(
            CourseId("COURSE_MATH_101"),
            "Mathematics Fundamentals",
            "Math",
            CourseLevel.BEGINNER,
            Money(Decimal("999.00"))
        ),
        Course(
            CourseId("COURSE_SCI_101"),
            "Science Explorations",
            "Science",
            CourseLevel.BEGINNER,
            Money(Decimal("799.00"))
        ),
        Course(
            CourseId("COURSE_ENG_201"),
            "Advanced English",
            "English",
            CourseLevel.INTERMEDIATE,
            Money(Decimal("1199.00"))
        )
    ]
    
    # Add lessons to courses
    for course in courses:
        course.add_lesson("Introduction", LessonType.VIDEO, 30)
        course.add_lesson("Practice Quiz", LessonType.QUIZ, 15)
        course.add_lesson("Assignment", LessonType.ASSIGNMENT, 45)
        course_repo.save_course(course)
    
    return api_adapter, learning_service, courses

def simulate_student_journey():
    """Simulate complete student learning journey"""
    
    print("🎓 Simulating Student Learning Journey")
    print("=" * 40)
    
    # Create system
    api_adapter, learning_service, courses = create_byju_learning_system()
    
    # Step 1: Register student
    print(f"\n📝 Step 1: Student Registration")
    registration_data = {
        "name": "Arjun Patel",
        "age": 14,
        "grade_level": 8,
        "email": "arjun.patel@example.com"
    }
    
    registration_result = api_adapter.register_student_endpoint(registration_data)
    print(f"   Result: {registration_result}")
    
    if registration_result["status"] != "success":
        return
    
    student_id = registration_result["student_id"]
    
    # Step 2: Enroll in course
    print(f"\n📚 Step 2: Course Enrollment")
    enrollment_data = {
        "student_id": student_id,
        "course_id": "COURSE_MATH_101"
    }
    
    enrollment_result = api_adapter.enroll_endpoint(enrollment_data)
    print(f"   Result: {enrollment_result}")
    
    # Step 3: Record learning activity
    print(f"\n📖 Step 3: Learning Activity")
    
    # Record some lesson progress
    learning_service.record_lesson_progress(StudentId(student_id), "lesson_1", 30)
    learning_service.record_lesson_progress(StudentId(student_id), "lesson_2", 25)
    learning_service.record_lesson_progress(StudentId(student_id), "lesson_3", 40)
    
    # Submit quiz
    quiz_answers = ["A", "B", "C", "A", "B"]
    grade = learning_service.submit_quiz(StudentId(student_id), "quiz_1", quiz_answers)
    print(f"   Quiz grade: {grade.score}/{grade.max_score} ({grade.percentage:.1f}%)")
    
    # Step 4: Get student dashboard
    print(f"\n📊 Step 4: Student Dashboard")
    dashboard_result = api_adapter.dashboard_endpoint(student_id)
    
    if dashboard_result["status"] == "success":
        dashboard = dashboard_result["data"]
        
        print(f"   Student: {dashboard['student_info']['name']}")
        print(f"   Study Hours: {dashboard['student_info']['total_study_hours']}")
        print(f"   Completed Lessons: {dashboard['student_info']['completed_lessons']}")
        print(f"   Average Quiz Score: {dashboard['student_info']['average_quiz_score']}%")
        print(f"   Enrolled Courses: {len(dashboard['enrolled_courses'])}")
        print(f"   Achievements: {len(dashboard['achievements'])}")
        print(f"   Recommended Courses: {len(dashboard['recommended_courses'])}")
        
        # Show achievements
        if dashboard['achievements']:
            print(f"\n   🏆 Achievements:")
            for achievement in dashboard['achievements']:
                print(f"     - {achievement['title']}: {achievement['description']}")
        
        # Show recommendations
        if dashboard['recommended_courses']:
            print(f"\n   💡 Recommended Courses:")
            for course in dashboard['recommended_courses']:
                print(f"     - {course['title']} (₹{course['price']})")
    
    print(f"\n✨ Student journey completed successfully!")

def main():
    """Main function demonstrating hexagonal architecture"""
    
    print("🏛️ Byju's Hexagonal Architecture - DDD Example")
    print("=" * 50)
    
    simulate_student_journey()
    
    print(f"\n✨ Hexagonal Architecture Benefits:")
    print(f"   ✅ Core business logic isolated")
    print(f"   ✅ External dependencies injected")
    print(f"   ✅ Easy to test core domain")
    print(f"   ✅ Framework-independent design")
    print(f"   ✅ Adapter pattern for external systems")
    print(f"   ✅ Domain logic remains pure")
    
    print(f"\n✨ Ready for production Byju's-scale system!")
    print(f"✨ Scalable and maintainable architecture!")

if __name__ == "__main__":
    main()