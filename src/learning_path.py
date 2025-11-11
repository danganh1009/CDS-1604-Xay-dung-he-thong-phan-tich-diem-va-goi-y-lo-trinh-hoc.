from sqlalchemy import func
from models import Student, Course, Grade, Curriculum
from collections import defaultdict

class LearningPathManager:
    def __init__(self, db_session):
        self.session = db_session

    def get_student_progress(self, student_id):
        """Phân tích tiến độ học tập của sinh viên"""
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        curriculum = self.session.query(Curriculum).filter_by(major=student.major).first()
        if not curriculum:
            return None

        # Tính toán số tín chỉ đã tích lũy
        completed_courses = self.session.query(Course, Grade).join(Grade).\
            filter(Grade.student_id == student.id).\
            filter(Grade.average_grade >= 5.0).all()

        total_credits_earned = sum(course.credits for course, grade in completed_courses)
        mandatory_credits_earned = sum(course.credits for course, grade in completed_courses 
                                     if course.is_mandatory == 1)
        elective_credits_earned = sum(course.credits for course, grade in completed_courses 
                                    if course.is_mandatory == 0)

        # Tạo báo cáo tiến độ
        progress_report = {
            'student': student,
            'total_credits': curriculum.total_credits,
            'credits_earned': total_credits_earned,
            'credits_remaining': curriculum.total_credits - total_credits_earned,
            'mandatory_credits': {
                'required': curriculum.mandatory_credits,
                'earned': mandatory_credits_earned,
                'remaining': curriculum.mandatory_credits - mandatory_credits_earned
            },
            'elective_credits': {
                'required': curriculum.elective_credits,
                'earned': elective_credits_earned,
                'remaining': curriculum.elective_credits - elective_credits_earned
            },
            'completion_percentage': (total_credits_earned / curriculum.total_credits) * 100,
            'gpa': student.gpa
        }

        return progress_report

    def get_available_courses(self, student_id):
        """Lấy danh sách các môn học có thể đăng ký"""
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return []

        # Lấy các môn đã học và đạt
        passed_courses = set(
            course.id for course, grade in 
            self.session.query(Course, Grade).join(Grade)
            .filter(Grade.student_id == student.id)
            .filter(Grade.average_grade >= 5.0)
        )

        # Lấy tất cả các môn trong chương trình học của sinh viên
        all_courses = self.session.query(Course).filter_by(major=student.major).all()
        
        available_courses = []
        for course in all_courses:
            # Kiểm tra nếu chưa học qua môn này
            if course.id not in passed_courses:
                # Kiểm tra điều kiện tiên quyết
                prerequisites_met = all(
                    prereq.id in passed_courses
                    for prereq in course.prerequisites_of
                )
                if prerequisites_met:
                    available_courses.append(course)

        return available_courses

    def suggest_next_semester_courses(self, student_id):
        """Đề xuất các môn học cho học kỳ tiếp theo"""
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        curriculum = self.session.query(Curriculum).filter_by(major=student.major).first()
        available_courses = self.get_available_courses(student_id)
        
        # Sắp xếp môn học theo độ ưu tiên
        suggested_courses = []
        total_credits = 0
        
        # Ưu tiên môn bắt buộc trước
        mandatory_courses = [c for c in available_courses if c.is_mandatory == 1]
        mandatory_courses.sort(key=lambda x: (x.recommended_semester or 999, -len(x.required_for)))
        
        # Thêm môn bắt buộc
        for course in mandatory_courses:
            if total_credits + course.credits <= curriculum.max_credits_per_semester:
                suggested_courses.append(course)
                total_credits += course.credits

        # Nếu còn slots, thêm môn tự chọn
        if total_credits < curriculum.min_credits_per_semester:
            elective_courses = [c for c in available_courses if c.is_mandatory == 0]
            elective_courses.sort(key=lambda x: (x.recommended_semester or 999, -len(x.required_for)))
            
            for course in elective_courses:
                if total_credits + course.credits <= curriculum.max_credits_per_semester:
                    suggested_courses.append(course)
                    total_credits += course.credits
                if total_credits >= curriculum.min_credits_per_semester:
                    break

        return {
            'suggested_courses': suggested_courses,
            'total_credits': total_credits,
            'min_credits': curriculum.min_credits_per_semester,
            'max_credits': curriculum.max_credits_per_semester
        }

    def analyze_academic_performance(self, student_id):
        """Phân tích chi tiết kết quả học tập"""
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        # Lấy tất cả điểm của sinh viên
        grades = self.session.query(Grade).filter_by(student_id=student.id).all()
        
        # Phân tích theo học kỳ
        semester_analysis = defaultdict(lambda: {
            'credits': 0,
            'gpa': 0.0,
            'courses': [],
            'total_grade_points': 0
        })

        for grade in grades:
            semester_key = f"{grade.year}.{grade.semester}"
            semester = semester_analysis[semester_key]
            
            if grade.average_grade is not None:
                semester['courses'].append({
                    'course': grade.course,
                    'grade': grade.average_grade,
                    'status': grade.grade_status
                })
                semester['credits'] += grade.course.credits
                semester['total_grade_points'] += grade.average_grade * grade.course.credits

        # Tính GPA cho từng học kỳ
        for semester in semester_analysis.values():
            if semester['credits'] > 0:
                semester['gpa'] = semester['total_grade_points'] / semester['credits']

        return {
            'student': student,
            'overall_gpa': student.gpa,
            'semesters': dict(semester_analysis),
            'total_credits_attempted': sum(s['credits'] for s in semester_analysis.values()),
            'courses_failed': len([g for g in grades if g.average_grade and g.average_grade < 5.0])
        }