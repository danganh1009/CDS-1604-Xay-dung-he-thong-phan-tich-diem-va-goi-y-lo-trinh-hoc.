from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from managers import Database, StudentManager, CourseManager, GradeManager, AttendanceManager
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super secret key'  # Cần thiết cho flash messages

# Khởi tạo database trong thư mục gốc của project
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'student_management.db')
db = Database(db_path)

# Khởi tạo các manager
student_manager = StudentManager(db.session)
course_manager = CourseManager(db.session)
grade_manager = GradeManager(db.session)
attendance_manager = AttendanceManager(db.session)

@app.route('/seed-demo')
def seed_demo():
    ok = db.seed_demo_data(num_students=40, num_courses=7)
    if ok:
        flash('Đã tạo dữ liệu demo: 40 sinh viên, 7 môn học và đầy đủ điểm.', 'success')
    else:
        flash('Có lỗi khi khởi tạo dữ liệu demo!', 'error')
    return redirect(url_for('list_students'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/students/<student_id>/forecast')
def student_forecast(student_id):
    roadmap = grade_manager.generate_study_roadmap(student_id)
    if not roadmap:
        flash('Không tìm thấy thông tin sinh viên!', 'error')
        return redirect(url_for('list_students'))

    # Pick next semester plan (first in dict order)
    next_semester_key = None
    next_semester = None
    for k, v in roadmap.get('recommended_path', {}).items():
        next_semester_key = k
        next_semester = v
        break

    # Projected GPA after next semester assuming expected grade 7.5 for planned courses
    expected_grade = 7.5
    # Current totals
    student = student_manager.get_student(student_id)
    current_weighted = 0.0
    current_credits = 0
    for g in grade_manager.get_student_grades(student_id):
        if g.average_grade is not None and g.course and g.course.credits:
            current_weighted += g.average_grade * g.course.credits
            current_credits += g.course.credits

    projected_weighted = current_weighted
    projected_credits = current_credits

    if next_semester:
        for c in next_semester['courses']:
            projected_weighted += expected_grade * c['credits']
            projected_credits += c['credits']

    projected_gpa = (projected_weighted / projected_credits) if projected_credits > 0 else 0.0

    return render_template(
        'students/forecast.html',
        roadmap=roadmap,
        next_semester_key=next_semester_key,
        next_semester=next_semester,
        current_gpa=student.gpa if student else 0.0,
        projected_gpa=projected_gpa,
        expected_grade=expected_grade
    )

@app.route('/students')
def list_students():
    students = student_manager.get_all_students()
    return render_template('students/list.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        class_name = request.form['class_name']
        major = request.form['major']
        enrollment_year = int(request.form['enrollment_year'])
        
        if student_manager.add_student(student_id, name, class_name, major, enrollment_year):
            flash('Thêm sinh viên thành công!', 'success')
            return redirect(url_for('list_students'))
        else:
            flash('Có lỗi xảy ra khi thêm sinh viên!', 'error')
    
    return render_template('students/add.html')

@app.route('/courses')
def list_courses():
    courses = course_manager.get_all_courses()
    return render_template('courses/list.html', courses=courses)

@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        credits = int(request.form['credits'])
        
        if course_manager.add_course(course_code, course_name, credits):
            flash('Thêm môn học thành công!', 'success')
            return redirect(url_for('list_courses'))
        else:
            flash('Có lỗi xảy ra khi thêm môn học!', 'error')
    
    return render_template('courses/add.html')

@app.route('/grades')
def list_grades():
    student_id = request.args.get('student_id')
    course_code = request.args.get('course_code')
    
    if student_id:
        student = student_manager.get_student(student_id)
        grades = grade_manager.get_student_grades(student_id)
        return render_template('grades/list.html', grades=grades, student=student)
    elif course_code:
        course = course_manager.get_course(course_code)
        grades = grade_manager.get_course_grades(course_code)
        return render_template('grades/list.html', grades=grades, course=course)
    else:
        # Hiển thị tất cả điểm của tất cả sinh viên
        grades = grade_manager.get_all_grades()
        return render_template('grades/list.html', grades=grades)

@app.route('/students/<student_id>/analysis')
def student_analysis(student_id):
    analysis = grade_manager.analyze_student_performance(student_id)
    if not analysis:
        flash('Không tìm thấy thông tin sinh viên!', 'error')
        return redirect(url_for('list_students'))
    
    # Dữ liệu đã được xử lý trong GradeManager
    return render_template(
        'students/analysis.html',
        analysis=analysis
    )
    
    return render_template(
        'students/analysis.html',
        analysis=analysis,
        completed_credits=completed_credits,
        in_progress_credits=in_progress_credits
    )

@app.route('/students/<student_id>/roadmap')
def student_roadmap(student_id):
    roadmap_data = grade_manager.generate_study_roadmap(student_id)
    if not roadmap_data:
        flash('Không tìm thấy thông tin sinh viên!', 'error')
        return redirect(url_for('list_students'))
    
    # Tính toán thông tin bổ sung cho view
    completed_courses = roadmap_data.get('completed_courses', [])
    remaining_courses = roadmap_data.get('remaining_courses', [])
    in_progress_courses = roadmap_data.get('in_progress_courses', [])

    total_credits = sum(
        course_info['course'].credits 
        for course_info in completed_courses 
        if isinstance(course_info, dict) and 'course' in course_info and hasattr(course_info['course'], 'credits')
    )

    remaining_credits = sum(
        course_info['course'].credits 
        for course_info in remaining_courses 
        if isinstance(course_info, dict) and 'course' in course_info and hasattr(course_info['course'], 'credits')
    )

    in_progress_credits = sum(
        course_info['course'].credits 
        for course_info in in_progress_courses 
        if isinstance(course_info, dict) and 'course' in course_info and hasattr(course_info['course'], 'credits')
    )
    
    return render_template(
        'students/roadmap.html',
        roadmap=roadmap_data,
        credits_info={
            'total': total_credits,
            'remaining': remaining_credits,
            'in_progress': in_progress_credits
        })

@app.route('/grades/add', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_code = request.form['course_code']
        midterm_grade = float(request.form['midterm_grade'])
        final_grade = float(request.form['final_grade'])
        semester = int(request.form['semester'])
        year = int(request.form['year'])
        
        if grade_manager.add_grade(student_id, course_code, midterm_grade, final_grade, semester, year):
            flash('Thêm điểm thành công!', 'success')
            return redirect(url_for('list_grades'))
        else:
            flash('Có lỗi xảy ra khi thêm điểm!', 'error')
    
    students = student_manager.get_all_students()
    courses = course_manager.get_all_courses()
    return render_template('grades/add.html', students=students, courses=courses)

@app.route('/attendance', methods=['GET'])
def list_attendance():
    student_id = request.args.get('student_id')
    course_code = request.args.get('course_code')
    date = request.args.get('date')
    
    if student_id and course_code:
        attendances = attendance_manager.get_student_attendance(student_id, course_code)
        stats = attendance_manager.get_attendance_stats(student_id, course_code)
        student = student_manager.get_student(student_id)
        course = course_manager.get_course(course_code)
        return render_template('attendance/list.html', 
                             attendances=attendances, 
                             stats=stats,
                             student=student,
                             course=course)
    elif course_code:
        attendances = attendance_manager.get_course_attendance(course_code, date)
        stats = attendance_manager.get_attendance_stats(course_code=course_code)
        course = course_manager.get_course(course_code)
        return render_template('attendance/list.html', 
                             attendances=attendances,
                             stats=stats,
                             course=course)
    elif student_id:
        attendances = attendance_manager.get_student_attendance(student_id)
        stats = attendance_manager.get_attendance_stats(student_id=student_id)
        student = student_manager.get_student(student_id)
        return render_template('attendance/list.html', 
                             attendances=attendances,
                             stats=stats,
                             student=student)
    else:
        return render_template('attendance/list.html')

@app.route('/attendance/add', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        course_code = request.form['course_code']
        date = request.form['date']
        semester = int(request.form['semester'])
        year = int(request.form['year'])
        success_count = 0
        error_count = 0
        
        # Lấy danh sách sinh viên
        students = student_manager.get_all_students()
        
        # Xử lý điểm danh cho từng sinh viên
        for student in students:
            status_key = f"status_{student.student_id}"
            note_key = f"note_{student.student_id}"
            
            if status_key in request.form:
                status = request.form[status_key]
                note = request.form.get(note_key)
                
                if attendance_manager.mark_attendance(student.student_id, course_code, date, status, semester, year, note):
                    success_count += 1
                else:
                    error_count += 1
        
        if error_count == 0:
            flash(f'Đã điểm danh thành công cho {success_count} sinh viên!', 'success')
        else:
            flash(f'Điểm danh thành công: {success_count}, thất bại: {error_count}', 'warning')
        return redirect(url_for('list_attendance', course_code=course_code))
    
    students = student_manager.get_all_students()
    courses = course_manager.get_all_courses()
    return render_template('attendance/add.html',
                         students=students,
                         courses=courses,
                         today=datetime.now().strftime("%Y-%m-%d"))

@app.route('/attendance/stats', methods=['GET'])
def attendance_stats():
    student_id = request.args.get('student_id')
    course_code = request.args.get('course_code')
    
    stats = attendance_manager.get_attendance_stats(student_id, course_code)
    if not stats:
        return jsonify({'error': 'No attendance records found'}), 404
    
    return jsonify(stats)

# ======================
# REST API (JSON) routes
# ======================

def serialize_student(student):
    return {
        'student_id': student.student_id,
        'name': student.name,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'phone': student.phone,
        'address': student.address,
        'class_name': student.class_name,
        'major': student.major,
        'entry_year': student.entry_year,
        'gpa': round(student.gpa, 2) if student.gpa is not None else 0.0
    }

def serialize_course(course):
    return {
        'course_code': getattr(course, 'course_code', None),
        'course_name': getattr(course, 'course_name', None),
        'credits': getattr(course, 'credits', None),
        'major': getattr(course, 'major', None),
        'is_mandatory': bool(getattr(course, 'is_mandatory', 0)),
        'description': getattr(course, 'description', None)
    }

def serialize_grade(grade):
    return {
        'student_id': grade.student.student_id if grade.student else None,
        'student_name': grade.student.name if grade.student else None,
        'course_code': grade.course.course_code if grade.course else None,
        'course_name': grade.course.course_name if grade.course else None,
        'midterm_grade': grade.midterm_grade,
        'final_grade': grade.final_grade,
        'average_grade': round(grade.average_grade, 2) if grade.average_grade is not None else None,
        'grade_status': grade.grade_status,
        'semester': grade.semester,
        'year': grade.year,
        'date_added': grade.date_added
    }

@app.route('/api/students', methods=['GET'])
def api_list_students():
    students = student_manager.get_all_students()
    return jsonify([serialize_student(s) for s in students])

@app.route('/api/students/<student_id>', methods=['GET'])
def api_student_detail(student_id):
    student = student_manager.get_student(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    grades = grade_manager.get_student_grades(student_id)
    return jsonify({
        'student': serialize_student(student),
        'grades': [serialize_grade(g) for g in grades]
    })

@app.route('/api/courses', methods=['GET'])
def api_list_courses():
    courses = course_manager.get_all_courses()
    return jsonify([serialize_course(c) for c in courses])

@app.route('/api/grades', methods=['GET'])
def api_list_grades():
    student_id = request.args.get('student_id')
    course_code = request.args.get('course_code')
    if student_id:
        grades = grade_manager.get_student_grades(student_id)
    elif course_code:
        grades = grade_manager.get_course_grades(course_code)
    else:
        grades = grade_manager.get_all_grades()
    return jsonify([serialize_grade(g) for g in grades])

if __name__ == '__main__':
    app.run(debug=True)