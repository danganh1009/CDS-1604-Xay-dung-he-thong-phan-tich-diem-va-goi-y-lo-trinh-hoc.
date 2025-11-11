import os
from managers import Database, StudentManager, CourseManager, GradeManager
from learning_path import LearningPathManager
from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama

class Interface:
    def __init__(self, db_path='student_management.db'):
        self.db = Database(db_path)
        self.student_manager = StudentManager(self.db.session)
        self.course_manager = CourseManager(self.db.session)
        self.grade_manager = GradeManager(self.db.session)
        self.learning_path_manager = LearningPathManager(self.db.session)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu(self):
        self.clear_screen()
        print(Fore.CYAN + "\n=== HỆ THỐNG QUẢN LÝ ĐIỂM VÀ PHÂN TÍCH LỘ TRÌNH HỌC ===")
        print(Fore.YELLOW + "\n1. Quản lý Sinh viên")
        print("2. Quản lý Môn học")
        print("3. Quản lý Điểm")
        print("4. Phân tích Học tập")
        print("0. Thoát")

    def print_student_menu(self):
        self.clear_screen()
        print(Fore.CYAN + "\n=== QUẢN LÝ SINH VIÊN ===")
        print(Fore.YELLOW + "\n1. Thêm sinh viên")
        print("2. Xem danh sách sinh viên")
        print("3. Cập nhật thông tin sinh viên")
        print("4. Xóa sinh viên")
        print("0. Quay lại")

    def print_course_menu(self):
        self.clear_screen()
        print(Fore.CYAN + "\n=== QUẢN LÝ MÔN HỌC ===")
        print(Fore.YELLOW + "\n1. Thêm môn học")
        print("2. Xem danh sách môn học")
        print("0. Quay lại")

    def print_grade_menu(self):
        self.clear_screen()
        print(Fore.CYAN + "\n=== QUẢN LÝ ĐIỂM ===")
        print(Fore.YELLOW + "\n1. Nhập điểm")
        print("2. Xem điểm theo sinh viên")
        print("3. Xem điểm theo môn học")
        print("0. Quay lại")

    def add_student(self):
        print(Fore.CYAN + "\n=== THÊM SINH VIÊN ===")
        student_id = input("Nhập mã sinh viên: ")
        name = input("Nhập họ tên: ")
        class_name = input("Nhập lớp: ")
        major = input("Nhập chuyên ngành: ")
        enrollment_year = input("Nhập năm nhập học: ")
        
        try:
            enrollment_year = int(enrollment_year)
            if self.student_manager.add_student(student_id, name, class_name, major, enrollment_year):
                print(Fore.GREEN + "\nThêm sinh viên thành công!")
            else:
                print(Fore.RED + "\nLỗi: Không thể thêm sinh viên!")
        except ValueError:
            print(Fore.RED + "\nLỗi: Năm nhập học phải là số!")
        input("\nNhấn Enter để tiếp tục...")

    def view_students(self):
        students = self.student_manager.get_all_students()
        if students:
            headers = ["Mã SV", "Họ Tên", "Lớp", "Chuyên ngành", "Năm nhập học", "GPA"]
            data = [[
                s.student_id,
                s.name,
                s.class_name,
                s.major,
                s.enrollment_year,
                f"{s.gpa:.2f}"
            ] for s in students]
            print(Fore.CYAN + "\n=== DANH SÁCH SINH VIÊN ===")
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "\nKhông có sinh viên nào trong hệ thống!")
        input("\nNhấn Enter để tiếp tục...")

    def update_student(self):
        print(Fore.CYAN + "\n=== CẬP NHẬT THÔNG TIN SINH VIÊN ===")
        student_id = input("Nhập mã sinh viên cần cập nhật: ")
        student = self.student_manager.get_student(student_id)
        
        if student:
            print(f"\nThông tin hiện tại:")
            print(f"Họ tên: {student.name}")
            print(f"Lớp: {student.class_name}")
            print(f"Chuyên ngành: {student.major}")
            print(f"Năm nhập học: {student.enrollment_year}")
            
            name = input("\nNhập họ tên mới (Enter để bỏ qua): ")
            class_name = input("Nhập lớp mới (Enter để bỏ qua): ")
            major = input("Nhập chuyên ngành mới (Enter để bỏ qua): ")
            enrollment_year = input("Nhập năm nhập học mới (Enter để bỏ qua): ")
            
            try:
                enrollment_year = int(enrollment_year) if enrollment_year else None
                if self.student_manager.update_student(
                    student_id,
                    name if name else None,
                    class_name if class_name else None,
                    major if major else None,
                    enrollment_year
                ):
                    print(Fore.GREEN + "\nCập nhật thông tin thành công!")
                else:
                    print(Fore.RED + "\nLỗi: Không thể cập nhật thông tin!")
            except ValueError:
                print(Fore.RED + "\nLỗi: Năm nhập học phải là số!")
        else:
            print(Fore.RED + "\nKhông tìm thấy sinh viên!")
        input("\nNhấn Enter để tiếp tục...")

    def delete_student(self):
        print(Fore.CYAN + "\n=== XÓA SINH VIÊN ===")
        student_id = input("Nhập mã sinh viên cần xóa: ")
        
        if self.student_manager.delete_student(student_id):
            print(Fore.GREEN + "\nXóa sinh viên thành công!")
        else:
            print(Fore.RED + "\nLỗi: Không thể xóa sinh viên!")
        input("\nNhấn Enter để tiếp tục...")

    def add_course(self):
        print(Fore.CYAN + "\n=== THÊM MÔN HỌC ===")
        course_code = input("Nhập mã môn học: ")
        course_name = input("Nhập tên môn học: ")
        try:
            credits = int(input("Nhập số tín chỉ: "))
            recommended_semester = int(input("Nhập học kỳ đề xuất (1-3): "))
            is_mandatory = input("Môn học bắt buộc? (y/n): ").lower() == 'y'
            major = input("Nhập chuyên ngành: ")
            description = input("Nhập mô tả môn học: ")
            
            if not (1 <= recommended_semester <= 3):
                print(Fore.RED + "\nHọc kỳ phải từ 1 đến 3!")
                return
            
            if self.course_manager.add_course(
                course_code, course_name, credits, recommended_semester,
                1 if is_mandatory else 0, major, description
            ):
                print(Fore.GREEN + "\nThêm môn học thành công!")
            else:
                print(Fore.RED + "\nLỗi: Không thể thêm môn học!")
        except ValueError:
            print(Fore.RED + "\nLỗi: Số tín chỉ và học kỳ phải là số!")
        input("\nNhấn Enter để tiếp tục...")

    def view_courses(self):
        courses = self.course_manager.get_all_courses()
        if courses:
            headers = ["Mã MH", "Tên Môn Học", "TC", "HK đề xuất", "Loại", "Chuyên ngành", "Mô tả"]
            data = [[
                c.course_code,
                c.course_name,
                c.credits,
                c.recommended_semester,
                "Bắt buộc" if c.is_mandatory else "Tự chọn",
                c.major,
                c.description
            ] for c in courses]
            print(Fore.CYAN + "\n=== DANH SÁCH MÔN HỌC ===")
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "\nKhông có môn học nào trong hệ thống!")
        input("\nNhấn Enter để tiếp tục...")

    def add_grade(self):
        print(Fore.CYAN + "\n=== NHẬP ĐIỂM ===")
        student_id = input("Nhập mã sinh viên: ")
        course_code = input("Nhập mã môn học: ")
        try:
            semester = int(input("Nhập học kỳ (1-3): "))
            year = int(input("Nhập năm học: "))
            midterm_grade = float(input("Nhập điểm giữa kỳ: "))
            final_grade = float(input("Nhập điểm cuối kỳ: "))
            
            if not (1 <= semester <= 3):
                print(Fore.RED + "\nHọc kỳ phải từ 1 đến 3!")
                return
                
            if 0 <= midterm_grade <= 10 and 0 <= final_grade <= 10:
                if self.grade_manager.add_grade(student_id, course_code, midterm_grade, final_grade, semester, year):
                    print(Fore.GREEN + "\nNhập điểm thành công!")
                else:
                    print(Fore.RED + "\nLỗi: Không thể nhập điểm!")
            else:
                print(Fore.RED + "\nĐiểm phải nằm trong khoảng 0-10!")
        except ValueError:
            print(Fore.RED + "\nLỗi: Điểm, học kỳ và năm học phải là số!")
        input("\nNhấn Enter để tiếp tục...")

    def view_student_grades(self):
        print(Fore.CYAN + "\n=== XEM ĐIỂM THEO SINH VIÊN ===")
        student_id = input("Nhập mã sinh viên: ")
        student = self.student_manager.get_student(student_id)
        grades = self.grade_manager.get_student_grades(student_id)
        
        if student and grades:
            print(f"\nSinh viên: {student.name}")
            print(f"GPA: {student.gpa:.2f}")
            
            # Sắp xếp điểm theo năm học và học kỳ
            sorted_grades = sorted(grades, key=lambda g: (g.year, g.semester))
            
            headers = ["Môn học", "Điểm GK", "Điểm CK", "Điểm TB", "Học kỳ", "Năm học", "Trạng thái"]
            courses_data = [
                [g.course.course_name,
                 g.midterm_grade,
                 g.final_grade,
                 f"{g.average_grade:.1f}" if g.average_grade else "N/A",
                 g.semester,
                 g.year,
                 g.grade_status
                ] for g in sorted_grades
            ]
            print("\n" + tabulate(courses_data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "\nKhông có điểm nào được tìm thấy!")
        input("\nNhấn Enter để tiếp tục...")

    def view_course_grades(self):
        print(Fore.CYAN + "\n=== XEM ĐIỂM THEO MÔN HỌC ===")
        course_code = input("Nhập mã môn học: ")
        grades = self.grade_manager.get_course_grades(course_code)
        
        if grades:
            headers = ["Sinh viên", "Mã SV", "Điểm GK", "Điểm CK", "Điểm TB", "Học kỳ", "Năm", "Trạng thái"]
            data = [
                [g.student.name,
                 g.student.student_id,
                 g.midterm_grade,
                 g.final_grade,
                 f"{g.average_grade:.1f}" if g.average_grade else "N/A",
                 g.semester,
                 g.year,
                 g.grade_status
                ] for g in sorted(grades, key=lambda g: (g.year, g.semester, g.student.name))
            ]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "\nKhông có điểm nào được tìm thấy!")
        input("\nNhấn Enter để tiếp tục...")

    def print_analysis_menu(self):
        self.clear_screen()
        print(Fore.CYAN + "\n=== PHÂN TÍCH HỌC TẬP ===")
        print(Fore.YELLOW + "\n1. Xem tiến độ học tập")
        print("2. Xem phân tích kết quả học tập")
        print("3. Xem các môn học có thể đăng ký")
        print("4. Đề xuất môn học cho kỳ tiếp theo")
        print("0. Quay lại")

    def view_student_progress(self):
        print(Fore.CYAN + "\n=== TIẾN ĐỘ HỌC TẬP ===")
        student_id = input("Nhập mã sinh viên: ")
        progress = self.learning_path_manager.get_student_progress(student_id)
        
        if progress:
            print(f"\nSinh viên: {progress['student'].name}")
            print(f"GPA hiện tại: {progress['gpa']:.2f}")
            print("\nTiến độ tích lũy tín chỉ:")
            print(f"- Tổng số tín chỉ yêu cầu: {progress['total_credits']}")
            print(f"- Số tín chỉ đã tích lũy: {progress['credits_earned']}")
            print(f"- Số tín chỉ còn thiếu: {progress['credits_remaining']}")
            print(f"- Hoàn thành: {progress['completion_percentage']:.1f}%")
            
            print("\nTín chỉ bắt buộc:")
            print(f"- Yêu cầu: {progress['mandatory_credits']['required']}")
            print(f"- Đã tích lũy: {progress['mandatory_credits']['earned']}")
            print(f"- Còn thiếu: {progress['mandatory_credits']['remaining']}")
            
            print("\nTín chỉ tự chọn:")
            print(f"- Yêu cầu: {progress['elective_credits']['required']}")
            print(f"- Đã tích lũy: {progress['elective_credits']['earned']}")
            print(f"- Còn thiếu: {progress['elective_credits']['remaining']}")
        else:
            print(Fore.RED + "\nKhông tìm thấy thông tin sinh viên!")
        
        input("\nNhấn Enter để tiếp tục...")

    def view_academic_analysis(self):
        print(Fore.CYAN + "\n=== PHÂN TÍCH KẾT QUẢ HỌC TẬP ===")
        student_id = input("Nhập mã sinh viên: ")
        analysis = self.learning_path_manager.analyze_academic_performance(student_id)
        
        if analysis:
            print(f"\nSinh viên: {analysis['student'].name}")
            print(f"GPA tích lũy: {analysis['overall_gpa']:.2f}")
            print(f"Tổng số tín chỉ đã học: {analysis['total_credits_attempted']}")
            print(f"Số môn không đạt: {analysis['courses_failed']}")
            
            print("\nKết quả theo học kỳ:")
            for semester, data in sorted(analysis['semesters'].items()):
                print(f"\nHọc kỳ {semester}:")
                print(f"- GPA học kỳ: {data['gpa']:.2f}")
                print(f"- Số tín chỉ: {data['credits']}")
                
                headers = ["Môn học", "Điểm TB", "Trạng thái"]
                courses_data = [[c['course'].course_name, 
                               f"{c['grade']:.1f}", 
                               c['status']] for c in data['courses']]
                print("\n" + tabulate(courses_data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.RED + "\nKhông tìm thấy thông tin sinh viên!")
        
        input("\nNhấn Enter để tiếp tục...")

    def view_available_courses(self):
        print(Fore.CYAN + "\n=== CÁC MÔN HỌC CÓ THỂ ĐĂNG KÝ ===")
        student_id = input("Nhập mã sinh viên: ")
        courses = self.learning_path_manager.get_available_courses(student_id)
        
        if courses:
            headers = ["Mã MH", "Tên Môn Học", "Tín chỉ", "Học kỳ đề xuất", "Loại"]
            data = [[c.course_code, 
                    c.course_name, 
                    c.credits,
                    c.recommended_semester or "N/A",
                    "Bắt buộc" if c.is_mandatory else "Tự chọn"] for c in courses]
            print("\n" + tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "\nKhông tìm thấy môn học có thể đăng ký!")
        
        input("\nNhấn Enter để tiếp tục...")

    def view_course_suggestions(self):
        print(Fore.CYAN + "\n=== ĐỀ XUẤT MÔN HỌC CHO KỲ TIẾP THEO ===")
        student_id = input("Nhập mã sinh viên: ")
        suggestion = self.learning_path_manager.suggest_next_semester_courses(student_id)
        
        if suggestion:
            print(f"\nSố tín chỉ đề xuất: {suggestion['total_credits']}")
            print(f"(Tối thiểu: {suggestion['min_credits']}, Tối đa: {suggestion['max_credits']})")
            
            if suggestion['suggested_courses']:
                headers = ["Mã MH", "Tên Môn Học", "Tín chỉ", "Loại"]
                data = [[c.course_code, 
                        c.course_name, 
                        c.credits,
                        "Bắt buộc" if c.is_mandatory else "Tự chọn"] 
                       for c in suggestion['suggested_courses']]
                print("\nCác môn học đề xuất:")
                print(tabulate(data, headers=headers, tablefmt="grid"))
            else:
                print(Fore.YELLOW + "\nKhông có đề xuất môn học nào!")
        else:
            print(Fore.RED + "\nKhông tìm thấy thông tin sinh viên!")
        
        input("\nNhấn Enter để tiếp tục...")

    def run(self):
        while True:
            self.print_menu()
            choice = input("\nNhập lựa chọn của bạn: ")
            
            if choice == "1":
                while True:
                    self.print_student_menu()
                    sub_choice = input("\nNhập lựa chọn của bạn: ")
                    
                    if sub_choice == "1":
                        self.add_student()
                    elif sub_choice == "2":
                        self.view_students()
                    elif sub_choice == "3":
                        self.update_student()
                    elif sub_choice == "4":
                        self.delete_student()
                    elif sub_choice == "0":
                        break
            
            elif choice == "2":
                while True:
                    self.print_course_menu()
                    sub_choice = input("\nNhập lựa chọn của bạn: ")
                    
                    if sub_choice == "1":
                        self.add_course()
                    elif sub_choice == "2":
                        self.view_courses()
                    elif sub_choice == "0":
                        break
            
            elif choice == "3":
                while True:
                    self.print_grade_menu()
                    sub_choice = input("\nNhập lựa chọn của bạn: ")
                    
                    if sub_choice == "1":
                        self.add_grade()
                    elif sub_choice == "2":
                        self.view_student_grades()
                    elif sub_choice == "3":
                        self.view_course_grades()
                    elif sub_choice == "0":
                        break
            
            elif choice == "4":
                while True:
                    self.print_analysis_menu()
                    sub_choice = input("\nNhập lựa chọn của bạn: ")
                    
                    if sub_choice == "1":
                        self.view_student_progress()
                    elif sub_choice == "2":
                        self.view_academic_analysis()
                    elif sub_choice == "3":
                        self.view_available_courses()
                    elif sub_choice == "4":
                        self.view_course_suggestions()
                    elif sub_choice == "0":
                        break

            elif choice == "0":
                print(Fore.GREEN + "\nCảm ơn bạn đã sử dụng chương trình!")
                break