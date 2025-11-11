from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
import os
import pandas as pd
from werkzeug.utils import secure_filename
import numpy as np
import json

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base, Student, Course, Grade
from managers import Database, StudentManager, CourseManager, GradeManager
from learning_path import LearningPathManager
from risk_manager import RiskManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'student_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Tạo thư mục uploads nếu chưa tồn tại
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Tạo instance của Database để khởi tạo cơ sở dữ liệu và dữ liệu mẫu
database = Database(db_path=app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))

# Initialize managers với session từ Database instance
student_manager = StudentManager(database.session)
course_manager = CourseManager(database.session)
grade_manager = GradeManager(database.session)
learning_path_manager = LearningPathManager(database.session)
risk_manager = RiskManager(database.session)

@app.route('/')
def index():
    return render_template('index.html')

# -------- Admin utilities (dev only) --------
@app.route('/admin/reset-db')
def admin_reset_db():
    # Remove SQLite file(s), then recreate and seed sample data
    try:
        db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///','')
        if os.path.exists(db_file):
            os.remove(db_file)
    except Exception:
        pass
    # Reinitialize Database and managers
    global database, student_manager, course_manager, grade_manager, learning_path_manager, risk_manager
    database = Database(db_path=app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///',''))
    student_manager = StudentManager(database.session)
    course_manager = CourseManager(database.session)
    grade_manager = GradeManager(database.session)
    learning_path_manager = LearningPathManager(database.session)
    risk_manager = RiskManager(database.session)
    # Seed sample
    try:
        database._init_sample_data()
    except Exception:
        pass
    return redirect(url_for('students'))

@app.route('/admin/seed')
def admin_seed():
    try:
        database._init_sample_data()
    except Exception:
        pass
    return redirect(url_for('students'))

@app.route('/students')
def students():
    all_students = student_manager.get_all_students()
    return render_template('students.html', students=all_students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            student_id = request.form['student_id']
            name = request.form['name']
            class_name = request.form['class_name']
            major = request.form['major']
            enrollment_year = int(request.form['enrollment_year'])
            
            if student_manager.add_student(student_id, name, class_name, major, enrollment_year):
                flash('Thêm sinh viên thành công!', 'success')
                return redirect(url_for('students'))
            else:
                flash('Không thể thêm sinh viên!', 'error')
        except ValueError:
            flash('Năm nhập học không hợp lệ!', 'error')
            
    return render_template('add_student.html')

@app.route('/import/students', methods=['POST'])
def import_students():
    if 'file' not in request.files:
        flash('Không tìm thấy file!', 'error')
        return redirect(url_for('students'))
    file = request.files['file']
    if file.filename == '':
        flash('Chưa chọn file!', 'error')
        return redirect(url_for('students'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    success_count = 0
    error_count = 0
    try:
        df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            try:
                student_id = str(row.get('ma_sinh_vien') or row.get('student_id') or row.get('MSSV'))
                name = str(row.get('ho_ten') or row.get('name') or '').strip()
                class_name = str(row.get('lop') or row.get('class_name') or '')
                major = str(row.get('chuyen_nganh') or row.get('major') or '')
                enrollment_year = int(row.get('nam_nhap_hoc') or row.get('enrollment_year') or 0)
                if not student_id or not name or not class_name or not major or not enrollment_year:
                    error_count += 1
                    continue
                if student_manager.add_student(student_id, name, class_name, major, enrollment_year):
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
                continue
        if success_count:
            flash(f'Đã thêm {success_count} sinh viên.', 'success')
        if error_count:
            flash(f'{error_count} dòng lỗi.', 'warning')
    except Exception as e:
        flash(f'Lỗi khi đọc Excel: {str(e)}', 'error')
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass
    return redirect(url_for('students'))

@app.route('/courses')
def courses():
    all_courses = course_manager.get_all_courses()
    return render_template('courses.html', courses=all_courses)

@app.route('/import/courses', methods=['POST'])
def import_courses():
    if 'file' not in request.files:
        flash('Không tìm thấy file!', 'error')
        return redirect(url_for('courses'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Chưa chọn file!', 'error')
        return redirect(url_for('courses'))
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_excel(filepath)
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    course_code = str(row['ma_mon_hoc'])
                    course_name = str(row['ten_mon_hoc'])
                    credits = int(row['so_tin_chi'])
                    recommended_semester = int(row.get('hoc_ky_de_xuat', 1))
                    is_mandatory = bool(row.get('bat_buoc', True))
                    major = str(row.get('chuyen_nganh', ''))
                    description = str(row.get('mo_ta', ''))
                    
                    if course_manager.add_course(
                        course_code, course_name, credits,
                        recommended_semester, is_mandatory,
                        major, description
                    ):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except (ValueError, KeyError) as e:
                    error_count += 1
                    continue
            
            os.remove(filepath)  # Xóa file sau khi đã xử lý
            
            if success_count > 0:
                flash(f'Đã thêm thành công {success_count} môn học!', 'success')
            if error_count > 0:
                flash(f'Có {error_count} môn học không thể thêm!', 'warning')
                
        except Exception as e:
            flash(f'Lỗi khi đọc file Excel: {str(e)}', 'error')
            
    return redirect(url_for('courses'))

@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        try:
            course_code = request.form['course_code']
            course_name = request.form['course_name']
            credits = int(request.form['credits'])
            recommended_semester = int(request.form['recommended_semester'])
            is_mandatory = request.form.get('is_mandatory') == 'yes'
            major = request.form['major']
            description = request.form['description']
            
            if course_manager.add_course(course_code, course_name, credits, 
                                       recommended_semester, is_mandatory, 
                                       major, description):
                flash('Thêm môn học thành công!', 'success')
                return redirect(url_for('courses'))
            else:
                flash('Không thể thêm môn học!', 'error')
        except ValueError:
            flash('Dữ liệu không hợp lệ!', 'error')
            
    return render_template('add_course.html')

@app.route('/grades')
def grades():
    student_id = request.args.get('student_id')
    course_code = request.args.get('course_code')
    
    if student_id:
        grades = grade_manager.get_student_grades(student_id)
        student = student_manager.get_student(student_id)
        return render_template('student_grades.html', grades=grades, student=student)
    elif course_code:
        grades = grade_manager.get_course_grades(course_code)
        course = course_manager.get_course(course_code)
        return render_template('course_grades.html', grades=grades, course=course)
    
    return render_template('grades.html')

@app.route('/import/grades', methods=['POST'])
def import_grades():
    if 'file' not in request.files:
        flash('Không tìm thấy file!', 'error')
        return redirect(url_for('grades'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Chưa chọn file!', 'error')
        return redirect(url_for('grades'))
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_excel(filepath)
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    student_id = str(row['ma_sinh_vien'])
                    course_code = str(row['ma_mon_hoc'])
                    midterm_grade = float(row['diem_giua_ky'])
                    final_grade = float(row['diem_cuoi_ky'])
                    semester = int(row['hoc_ky'])
                    year = int(row['nam_hoc'])
                    
                    if 0 <= midterm_grade <= 10 and 0 <= final_grade <= 10 and 1 <= semester <= 3:
                        if grade_manager.add_grade(
                            student_id, course_code,
                            midterm_grade, final_grade,
                            semester, year
                        ):
                            success_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                        
                except (ValueError, KeyError) as e:
                    error_count += 1
                    continue
            
            os.remove(filepath)  # Xóa file sau khi đã xử lý
            
            if success_count > 0:
                flash(f'Đã thêm thành công {success_count} điểm!', 'success')
            if error_count > 0:
                flash(f'Có {error_count} điểm không thể thêm!', 'warning')
                
        except Exception as e:
            flash(f'Lỗi khi đọc file Excel: {str(e)}', 'error')
            
    return redirect(url_for('grades'))

@app.route('/grades/add', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        try:
            student_id = request.form['student_id']
            course_code = request.form['course_code']
            midterm_grade = float(request.form['midterm_grade'])
            final_grade = float(request.form['final_grade'])
            semester = int(request.form['semester'])
            year = int(request.form['year'])
            
            if 0 <= midterm_grade <= 10 and 0 <= final_grade <= 10:
                if grade_manager.add_grade(student_id, course_code, 
                                         midterm_grade, final_grade,
                                         semester, year):
                    flash('Thêm điểm thành công!', 'success')
                    return redirect(url_for('grades'))
                else:
                    flash('Không thể thêm điểm!', 'error')
            else:
                flash('Điểm phải nằm trong khoảng 0-10!', 'error')
        except ValueError:
            flash('Dữ liệu không hợp lệ!', 'error')
    
    students = student_manager.get_all_students()
    courses = course_manager.get_all_courses()
    return render_template('add_grade.html', students=students, courses=courses)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/analysis/progress')
def student_progress():
    student_id = request.args.get('student_id')
    if student_id:
        progress = learning_path_manager.get_student_progress(student_id)
        return render_template('student_progress.html', progress=progress)
    return redirect(url_for('analysis'))

@app.route('/analysis/performance')
def academic_performance():
    student_id = request.args.get('student_id')
    if student_id:
        analysis = learning_path_manager.analyze_academic_performance(student_id)
        return render_template('academic_performance.html', analysis=analysis)
    return redirect(url_for('analysis'))

@app.route('/analysis/available-courses')
def available_courses():
    student_id = request.args.get('student_id')
    if student_id:
        courses = learning_path_manager.get_available_courses(student_id)
        return render_template('available_courses.html', courses=courses)
    return redirect(url_for('analysis'))

@app.route('/analysis/suggestions')
def course_suggestions():
    student_id = request.args.get('student_id')
    if student_id:
        suggestion = learning_path_manager.suggest_next_semester_courses(student_id)
        return render_template('course_suggestions.html', suggestion=suggestion)
    return redirect(url_for('analysis'))

@app.route('/analysis/risk')
def risk_dashboard():
    semester = request.args.get('semester', type=int)
    year = request.args.get('year', type=int)
    # If term not provided, try to infer latest term from grades
    if semester is None or year is None:
        latest = None
        grades = database.session.query(Grade).all()
        for g in grades:
            key = (g.year, g.semester)
            if latest is None or key > latest:
                latest = key
        if latest:
            year, semester = latest
        else:
            year, semester = 2025, 1

    alerts = risk_manager.list_alerts(semester=semester, year=year)
    if not alerts:
        # Generate alerts if missing
        alerts = risk_manager.regenerate_alerts(semester=semester, year=year)
    for a in alerts:
        try:
            setattr(a, "_parsed_factors", json.loads(a.factors) if a.factors else {})
        except Exception:
            setattr(a, "_parsed_factors", {})
    return render_template('risk_dashboard.html', alerts=alerts, semester=semester, year=year)

@app.route('/api/risk/<student_id>')
def risk_api(student_id):
    payload = risk_manager.get_student_latest_alert(student_id)
    if not payload:
        return {"error": "No risk data"}, 404
    return payload

# ======================
# REST API (JSON) routes
# ======================

def _serialize_student(student: Student):
    return {
        'student_id': student.student_id,
        'name': f"{student.last_name} {student.first_name}",
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

def _serialize_course(course: Course):
    return {
        'course_code': getattr(course, 'course_code', None),
        'course_name': getattr(course, 'course_name', None),
        'credits': getattr(course, 'credits', None),
        'major': getattr(course, 'major', None),
        'is_mandatory': bool(getattr(course, 'is_mandatory', 0)),
        'description': getattr(course, 'description', None)
    }

def _serialize_grade(grade: Grade):
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
    return jsonify([_serialize_student(s) for s in students])

@app.route('/api/students/<student_id>', methods=['GET'])
def api_student_detail(student_id):
    student = student_manager.get_student(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    grades = grade_manager.get_student_grades(student_id)
    return jsonify({
        'student': _serialize_student(student),
        'grades': [_serialize_grade(g) for g in grades]
    })

@app.route('/api/courses', methods=['GET'])
def api_list_courses():
    courses = course_manager.get_all_courses()
    return jsonify([_serialize_course(c) for c in courses])

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
    return jsonify([_serialize_grade(g) for g in grades])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)