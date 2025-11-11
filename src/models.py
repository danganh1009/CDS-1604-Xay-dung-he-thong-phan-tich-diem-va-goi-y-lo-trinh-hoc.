from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# Bảng liên kết cho môn học tiên quyết
prerequisites = Table(
    'prerequisites',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(10), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)  # Tên
    last_name = Column(String(50), nullable=False)   # Họ và tên đệm
    email = Column(String(100), unique=True)
    phone = Column(String(15))
    address = Column(String(200))
    class_name = Column(String(20), nullable=False)
    major = Column(String(100), nullable=False)  # Chuyên ngành
    entry_year = Column(Integer, nullable=False)  # Năm nhập học
    grades = relationship("Grade", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    
    @property
    def name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def gpa(self):
        if not self.grades:
            return 0.0
        total_credits = 0
        weighted_sum = 0
        for grade in self.grades:
            if grade.average_grade is not None and grade.course.credits:
                weighted_sum += grade.average_grade * grade.course.credits
                total_credits += grade.course.credits
        return weighted_sum / total_credits if total_credits > 0 else 0.0

    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', name='{self.name}', major='{self.major}')>"

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    # course_code is a short unique identifier like COMP101
    course_code = Column(String(20), unique=True, nullable=False)
    # course_name is the human readable name
    course_name = Column(String(100), nullable=False)
    description = Column(String(500))  # Mô tả môn học
    credits = Column(Integer, nullable=False)
    mandatory = Column(Integer, default=0)  # 0: không bắt buộc, 1: bắt buộc
    attendances = relationship("Attendance", back_populates="course")
    prerequisites = relationship(
        'Course',
        secondary='prerequisites',
        primaryjoin='Course.id==prerequisites.c.prerequisite_id',
        secondaryjoin='Course.id==prerequisites.c.course_id',
        backref='dependent_courses'
    )
    is_mandatory = Column(Integer, default=1)  # 1: bắt buộc, 0: tự chọn
    major = Column(String(100), nullable=False)  # Chuyên ngành
    
    grades = relationship("Grade", back_populates="course")

    def __repr__(self):
        return f"<Course(course_code='{getattr(self, 'course_code', None)}', course_name='{getattr(self, 'course_name', None)}', credits={self.credits})>"

class Grade(Base):
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    midterm_grade = Column(Float)
    final_grade = Column(Float)
    semester = Column(Integer, nullable=False)  # Học kỳ đã học
    year = Column(Integer, nullable=False)  # Năm học
    date_added = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    student = relationship("Student", back_populates="grades")
    course = relationship("Course", back_populates="grades")

    @property
    def attendance_grade(self):
        """Tính điểm chuyên cần dựa trên tỷ lệ đi học"""
        attendance_stats = self.get_attendance_stats()
        if not attendance_stats or attendance_stats['total_sessions'] == 0:
            return 0
        
        # Tính điểm dựa trên tỷ lệ đi học
        attendance_rate = attendance_stats['attendance_rate']
        if attendance_rate >= 80:  # Đi học >= 80%
            return 10
        elif attendance_rate >= 70:  # Đi học >= 70%
            return 8
        elif attendance_rate >= 60:  # Đi học >= 60%
            return 6
        elif attendance_rate >= 50:  # Đi học >= 50%
            return 4
        else:
            return 0

    def get_attendance_stats(self):
        """Lấy thống kê điểm danh cho sinh viên trong môn học này"""
        from sqlalchemy import and_
        attendances = self.student.attendances
        course_attendances = [a for a in attendances if a.course_id == self.course_id]
        
        total = len(course_attendances)
        if total == 0:
            return None
            
        present = len([a for a in course_attendances if a.status == 'present'])
        late = len([a for a in course_attendances if a.status == 'late'])
        absent = len([a for a in course_attendances if a.status == 'absent'])
        
        return {
            'total_sessions': total,
            'present': present,
            'late': late,
            'absent': absent,
            'attendance_rate': ((present + late) / total * 100) if total > 0 else 0
        }

    @property
    def average_grade(self):
        if self.midterm_grade is not None and self.final_grade is not None:
            attendance = self.attendance_grade
            return 0.1 * attendance + 0.3 * self.midterm_grade + 0.6 * self.final_grade
        return None

    @property
    def grade_status(self):
        if self.average_grade is None:
            return "Chưa có điểm"
        elif self.average_grade >= 5.0:
            return "Đạt"
        else:
            return "Không đạt"

    def __repr__(self):
        return f"<Grade(student_id={self.student_id}, course_id={self.course_id}, average_grade={self.average_grade})>"

class Curriculum(Base):
    __tablename__ = 'curriculums'
    
    id = Column(Integer, primary_key=True)
    major = Column(String(100), nullable=False)  # Chuyên ngành
    total_credits = Column(Integer, nullable=False)  # Tổng số tín chỉ cần tích lũy
    mandatory_credits = Column(Integer, nullable=False)  # Số tín chỉ bắt buộc
    elective_credits = Column(Integer, nullable=False)  # Số tín chỉ tự chọn
    max_credits_per_semester = Column(Integer, default=25)  # Số tín chỉ tối đa mỗi kỳ
    min_credits_per_semester = Column(Integer, default=10)  # Số tín chỉ tối thiểu mỗi kỳ
    description = Column(String(1000))  # Mô tả chương trình

    def __repr__(self):
        return f"<Curriculum(major='{self.major}', total_credits={self.total_credits})>"

class Attendance(Base):
    __tablename__ = 'attendances'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)  # present, absent, late
    note = Column(String)
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    student = relationship("Student", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")

class RiskAlert(Base):
    __tablename__ = 'risk_alerts'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    factors = Column(String(1000))  # JSON-encoded summary of contributing factors
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    student = relationship("Student")