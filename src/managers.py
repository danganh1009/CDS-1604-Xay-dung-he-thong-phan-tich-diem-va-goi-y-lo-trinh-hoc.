from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Student, Course, Grade, Curriculum, Attendance
import os

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'student_management.db')
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self._init_sample_data()

    def seed_demo_data(self, num_students=40, num_courses=7):
        """Clear existing data and seed deterministic demo data for presentation."""
        from sqlalchemy import text
        try:
            # Clear existing tables respecting FK constraints
            self.session.execute(text('DELETE FROM risk_alerts'))
            self.session.execute(text('DELETE FROM attendances'))
            self.session.execute(text('DELETE FROM grades'))
            self.session.execute(text('DELETE FROM prerequisites'))
            self.session.execute(text('DELETE FROM courses'))
            self.session.execute(text('DELETE FROM students'))
            self.session.commit()
        except Exception:
            self.session.rollback()

        try:
            # Seed 7 courses for CNTT major
            base_courses = [
                ('COMP101', 'Lập trình cơ bản', 3, 1),
                ('COMP102', 'Cấu trúc dữ liệu', 4, 1),
                ('COMP201', 'Lập trình hướng đối tượng', 4, 1),
                ('COMP202', 'Cơ sở dữ liệu', 4, 1),
                ('COMP203', 'Mạng máy tính', 3, 1),
                ('MATH101', 'Giải tích', 4, 1),
                ('ENG101', 'Tiếng Anh 1', 2, 0),
            ]
            courses = []
            for code, name, credits, is_mandatory in base_courses[:num_courses]:
                courses.append(Course(
                    course_code=code,
                    course_name=name,
                    credits=credits,
                    description='',
                    is_mandatory=is_mandatory,
                    major='Công nghệ thông tin'
                ))
            self.session.add_all(courses)
            self.session.flush()

            # Seed 40 students
            classes = ['CN1', 'CN2']
            years = [2023, 2024]
            last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Võ', 'Đặng']
            first_names = ['An', 'Bình', 'Chi', 'Dũng', 'Hà', 'Hải', 'Hân', 'Hiếu', 'Huy', 'Khánh',
                           'Lan', 'Linh', 'Long', 'Minh', 'Nam', 'Ngọc', 'Phúc', 'Quân', 'Quỳnh', 'Thảo']
            students = []
            for idx in range(1, num_students + 1):
                last = last_names[(idx - 1) % len(last_names)]
                first = first_names[(idx - 1) % len(first_names)]
                class_name = classes[(idx - 1) % len(classes)]
                entry_year = years[(idx - 1) % len(years)]
                sid = f"{entry_year}CN{idx:03d}"
                email = f"{sid.lower()}@example.com"
                students.append(Student(
                    student_id=sid,
                    first_name=first,
                    last_name=last,
                    email=email,
                    class_name=class_name,
                    major='Công nghệ thông tin',
                    entry_year=entry_year
                ))
            self.session.add_all(students)
            self.session.flush()

            # Seed grades: distribute courses over two years and two semesters
            grades_to_add = []
            for s_idx, student in enumerate(students, start=1):
                # Create slight variation per student
                for c_idx, course in enumerate(courses, start=1):
                    # Assign semester/year deterministically
                    year = 2023 if (c_idx <= len(courses)//2 + 1) else 2024
                    semester = 1 if (c_idx % 2 == 1) else 2
                    # Generate midterm/final with some variability and pass/fail spread
                    base = 6.5 + ((s_idx + c_idx) % 5) * 0.5  # 6.5,7.0,...,8.5,9.0
                    # Increase proportion of low scores for demo (about ~20%)
                    if ((s_idx + c_idx) % 7 == 0) or (s_idx % 13 == 0 and c_idx % 3 == 0):
                        base = 3.5
                    midterm = max(0.0, min(10.0, base - 0.5))
                    final = max(0.0, min(10.0, base + 0.3))
                    grades_to_add.append(Grade(
                        student_id=student.id,
                        course_id=course.id,
                        semester=semester,
                        year=year,
                        midterm_grade=midterm,
                        final_grade=final
                    ))
            self.session.add_all(grades_to_add)
            self.session.commit()
            return True
        except Exception as e:
            print('Error seeding demo data:', e)
            self.session.rollback()
            return False

    def _init_sample_data(self):
        # Thêm dữ liệu mẫu nếu chưa có
        if not self.session.query(Student).first():
            try:
                students = [
                    Student(student_id='2023CN001', first_name='Văn An', last_name='Nguyễn', 
                           class_name='CN1', major='Công nghệ thông tin', entry_year=2023, email='an@example.com'),
                    Student(student_id='2023CN002', first_name='Thị Bình', last_name='Trần', 
                           class_name='CN1', major='Công nghệ thông tin', entry_year=2023, email='binh@example.com'),
                    Student(student_id='2022CN001', first_name='Văn Phúc', last_name='Trương', 
                           class_name='CN2', major='Công nghệ thông tin', entry_year=2022, email='phuc@example.com'),
                    Student(student_id='2023KT001', first_name='Thị Uyên', last_name='Lý', 
                           class_name='KT1', major='Kế toán', entry_year=2023, email='uyen@example.com'),
                    Student(student_id='2023CN003', first_name='Minh Hiếu', last_name='Phạm', 
                           class_name='CN1', major='Công nghệ thông tin', entry_year=2023, email='hieu@example.com')
                ]
                self.session.add_all(students)
                self.session.flush()  # Để lấy được ID của các sinh viên

                courses = [
                    Course(course_code='COMP101', course_name='Lập trình cơ bản', credits=3,
                          description='Nhập môn lập trình', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='COMP102', course_name='Cấu trúc dữ liệu', credits=4,
                          description='Cấu trúc dữ liệu', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='COMP201', course_name='Lập trình hướng đối tượng', credits=4,
                          description='Lập trình OOP', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='COMP202', course_name='Cơ sở dữ liệu', credits=4,
                          description='Thiết kế và quản lý CSDL', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='COMP203', course_name='Mạng máy tính', credits=3,
                          description='Mạng và truyền thông', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='MATH101', course_name='Giải tích', credits=4,
                          description='Toán cao cấp 1', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='MATH102', course_name='Đại số', credits=3,
                          description='Đại số tuyến tính', is_mandatory=1, major='Công nghệ thông tin'),
                    Course(course_code='ENG101', course_name='Tiếng Anh 1', credits=2,
                          description='Tiếng Anh cơ bản', is_mandatory=1, major='Công nghệ thông tin')
                ]
                self.session.add_all(courses)
                self.session.flush()  # Để lấy được ID của các môn học

                # Thêm điểm số mẫu cho sinh viên CNTT
                for student in self.session.query(Student).filter_by(major='Công nghệ thông tin').all():
                    grades = []
                    # Học kỳ 1/2023
                    for course in [courses[0], courses[5], courses[6], courses[7]]:
                        grade = Grade(
                            student=student,
                            course=course,
                            semester=1,
                            year=2023,
                            midterm_grade=7.5,
                            final_grade=8.0
                        )
                        grades.append(grade)
                    
                    # Học kỳ 2/2023
                    for course in [courses[1], courses[2]]:
                        grade = Grade(
                            student=student,
                            course=course,
                            semester=2,
                            year=2023,
                            midterm_grade=6.5,
                            final_grade=7.0
                        )
                        grades.append(grade)
                    
                    self.session.add_all(grades)

                # Commit tất cả thay đổi
                self.session.commit()

            except Exception as e:
                print('Error initializing sample data in managers:', e)
                self.session.rollback()

class StudentManager:
    def __init__(self, db_session):
        self.session = db_session

    def add_student(self, student_id, name_or_first, class_name, major, entry_year):
        # Accept either full name or separate names for compatibility
        if isinstance(name_or_first, str) and ' ' in name_or_first:
            parts = name_or_first.split(' ', 1)
            last_name, first_name = parts[0], parts[1]
        else:
            # If caller passes first name only, store it in first_name and leave last empty
            first_name = name_or_first
            last_name = ''
        student = Student(student_id=student_id, first_name=first_name, last_name=last_name, class_name=class_name, major=major, entry_year=entry_year)
        self.session.add(student)
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print('Error adding student:', e)
            return False

    def get_student(self, student_id):
        return self.session.query(Student).filter_by(student_id=student_id).first()

    def get_all_students(self):
        return self.session.query(Student).all()

class CourseManager:
    def __init__(self, db_session):
        self.session = db_session

    def add_course(self, course_code, course_name, credits):
        course = Course(course_code=course_code, course_name=course_name, credits=credits, description='', is_mandatory=1, major='Công nghệ thông tin')
        self.session.add(course)
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print('Error adding course:', e)
            return False

    def get_course(self, course_code):
        return self.session.query(Course).filter_by(course_code=course_code).first()

    def get_all_courses(self):
        return self.session.query(Course).all()

class GradeManager:
    def __init__(self, db_session):
        self.session = db_session

    def add_grade(self, student_id, course_code, midterm, final, semester, year):
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        course = self.session.query(Course).filter_by(course_code=course_code).first()
        if not student or not course:
            return False
        grade = Grade(student_id=student.id, course_id=course.id, midterm_grade=midterm, final_grade=final, semester=semester, year=year)
        self.session.add(grade)
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print('Error adding grade:', e)
            return False

    def get_student_grades(self, student_id):
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return []
        return student.grades

    def get_course_grades(self, course_code):
        course = self.session.query(Course).filter_by(course_code=course_code).first()
        if not course:
            return []
        return course.grades

    def get_all_grades(self):
        return self.session.query(Grade).all()

    def generate_study_roadmap(self, student_id):
        """Generate a unified roadmap including status lists and a recommended path."""
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        # All courses in major
        all_courses = self.session.query(Course).filter_by(major=student.major).all()

        # Map course_id -> grade
        student_grades_by_course = {grade.course_id: grade for grade in student.grades}

        completed_courses = []
        in_progress_courses = []
        remaining_courses = []

        completed_course_objs = set()

        for course in all_courses:
            grade = student_grades_by_course.get(course.id)
            if grade is None:
                remaining_courses.append({
                    'course': course,
                    'prerequisites': [p.course_code for p in course.prerequisites]
                })
            else:
                if grade.grade_status == "Đạt":
                    completed_courses.append({
                        'course': course,
                        'grade': grade.average_grade
                    })
                    completed_course_objs.add(course)
                else:
                    in_progress_courses.append({
                        'course': course,
                        'current_grade': grade.average_grade
                    })

        # Build recommended path (respect simple prerequisite readiness and credit caps)
        max_credits_per_semester = 20
        recommended_path = {}
        current_semester_num = 1
        current_year = student.entry_year
        semester_credits = 0

        # Determine remaining details with prerequisite flags
        remaining_with_flags = []
        completed_codes = {c.course_code for c in completed_course_objs}
        for item in remaining_courses:
            course = item['course']
            prereqs_codes = [p.course_code for p in course.prerequisites]
            prerequisites_met = all(code in completed_codes for code in prereqs_codes)
            remaining_with_flags.append({
                'course_code': course.course_code,
                'course_name': course.course_name,
                'credits': course.credits,
                'is_mandatory': course.is_mandatory,
                'prerequisites_met': prerequisites_met,
                'prerequisites': prereqs_codes
            })

        # Prioritize: prerequisites met first, mandatory first, higher credits first
        remaining_with_flags.sort(key=lambda x: (not x['prerequisites_met'], not x['is_mandatory'], -x['credits']))

        for course in remaining_with_flags:
            if semester_credits + course['credits'] > max_credits_per_semester:
                current_semester_num += 1
                if current_semester_num > 2:
                    current_semester_num = 1
                    current_year += 1
                semester_credits = 0
            semester_key = f"Học kỳ {current_semester_num} - Năm {current_year}"
            if semester_key not in recommended_path:
                recommended_path[semester_key] = {'courses': [], 'total_credits': 0}
            recommended_path[semester_key]['courses'].append(course)
            recommended_path[semester_key]['total_credits'] += course['credits']
            semester_credits += course['credits']

        return {
            'student_info': {
                'name': student.name,
                'student_id': student.student_id,
                'major': student.major,
                'class': student.class_name
            },
            'completed_courses': completed_courses,
            'in_progress_courses': in_progress_courses,
            'remaining_courses': [{'course': item['course'], 'prerequisites': item['prerequisites']} for item in remaining_courses],
            'recommended_path': recommended_path
        }

    def analyze_student_performance(self, student_id):
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        # Lấy tất cả điểm của sinh viên
        all_grades = student.grades
        completed_grades = [g for g in all_grades if g.grade_status == "Đạt"]
        failed_grades = [g for g in all_grades if g.grade_status == "Không đạt"]
        
        # Tính số tín chỉ đã hoàn thành và còn lại
        credits_completed = sum(g.course.credits for g in completed_grades)
        credits_remaining = sum(g.course.credits for g in failed_grades)

        # Tìm các môn học xuất sắc và cần cải thiện
        best_courses = []
        for grade in sorted(all_grades, key=lambda g: g.average_grade if g.average_grade is not None else -1, reverse=True)[:5]:
            if grade.average_grade is not None:
                best_courses.append({
                    'course': grade.course.course_name,
                    'grade': grade.average_grade
                })

        failed_courses = [{
            'course': grade.course.course_name,
            'grade': grade.average_grade if grade.average_grade is not None else 0.0
        } for grade in failed_grades]

        # Phân tích theo học kỳ
        performance_by_semester = {}
        for grade in all_grades:
            semester = f"{grade.semester}/{grade.year}"
            if semester not in performance_by_semester:
                performance_by_semester[semester] = {
                    'semester': grade.semester,
                    'year': grade.year,
                    'grades': [],
                    'credits': 0,
                    'weighted_sum': 0.0
                }
            
            data = performance_by_semester[semester]
            data['grades'].append({
                'course': grade.course.course_name,
                'credits': grade.course.credits,
                'grade': grade.average_grade
            })

            if grade.average_grade is not None:
                data['credits'] += grade.course.credits
                data['weighted_sum'] += grade.average_grade * grade.course.credits

        # Tính điểm trung bình cho từng học kỳ
        for data in performance_by_semester.values():
            if data['credits'] > 0:
                data['average'] = data['weighted_sum'] / data['credits']
            else:
                data['average'] = 0.0

        return {
            'student_info': {
                'name': student.name,
                'student_id': student.student_id,
                'major': student.major,
                'enrollment_year': student.entry_year,
                'gpa': student.gpa
            },
            'credits_completed': credits_completed,
            'credits_remaining': credits_remaining,
            'best_courses': best_courses,
            'failed_courses': failed_courses,
            'performance_by_semester': performance_by_semester
        }

    # Note: older duplicate generate_study_roadmap removed and unified above

class AttendanceManager:
    def __init__(self, db_session):
        self.session = db_session

    def mark_attendance(self, student_id, course_code, date, status, semester, year, note=None):
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        course = self.session.query(Course).filter_by(course_code=course_code).first()
        if not student or not course:
            return False
        attendance = Attendance(student_id=student.id, course_id=course.id, date=date, status=status, semester=semester, year=year, note=note)
        self.session.add(attendance)
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print('Error marking attendance:', e)
            return False

    def get_student_attendance(self, student_id, course_code=None):
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return []
        query = self.session.query(Attendance).filter(Attendance.student_id == student.id)
        if course_code:
            course = self.session.query(Course).filter_by(course_code=course_code).first()
            if not course:
                return []
            query = query.filter(Attendance.course_id == course.id)
        return query.all()

    def get_course_attendance(self, course_code, date=None):
        course = self.session.query(Course).filter_by(course_code=course_code).first()
        if not course:
            return []
        query = self.session.query(Attendance).filter(Attendance.course_id == course.id)
        if date:
            query = query.filter(Attendance.date == date)
        return query.all()

    def get_attendance_stats(self, student_id=None, course_code=None):
        query = self.session.query(Attendance)
        if student_id:
            student = self.session.query(Student).filter_by(student_id=student_id).first()
            if not student:
                return None
            query = query.filter(Attendance.student_id == student.id)
        if course_code:
            course = self.session.query(Course).filter_by(course_code=course_code).first()
            if not course:
                return None
            query = query.filter(Attendance.course_id == course.id)
        records = query.all()
        if not records:
            return None
        total = len(records)
        present = len([r for r in records if r.status == 'present'])
        late = len([r for r in records if r.status == 'late'])
        absent = len([r for r in records if r.status == 'absent'])
        return {
            'total_sessions': total,
            'present': present,
            'late': late,
            'absent': absent,
            'attendance_rate': ((present + late) / total * 100) if total > 0 else 0
        }
