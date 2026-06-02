from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from .models import Student, Subject, SubjectMaster, SpecializationMapping
from .forms import StudentForm, ExcelUploadForm
import pandas as pd

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1. Admin Login
        if username == 'admin' and password == 'admin123':
            request.session['role'] = 'admin'
            return redirect('admin_dashboard')

        # 2. Mentor Login
        # If a record exists in the Student table where mentor_id matches the username
        mentor_student = Student.objects.filter(mentor_id=username).first()
        if mentor_student:
            # Check password: prioritize mentor_password if it exists, fallback to mentor_phone
            stored_password = mentor_student.mentor_password if mentor_student.mentor_password else mentor_student.mentor_phone
            if password == stored_password:
                request.session['role'] = 'mentor'
                request.session['user_id'] = mentor_student.mentor_id
                request.session['mentor_id'] = mentor_student.mentor_id
                request.session['mentor_name'] = mentor_student.mentor_name
                return redirect('mentor_dashboard')
            else:
                messages.error(request, 'Invalid mentor credentials')
                return render(request, 'home.html')

        # 3. Student Login
        try:
            student = Student.objects.get(student_id=username)
            expected_password = student.student_id[-5:] if len(student.student_id) >= 5 else student.student_id
            if password == expected_password:
                request.session['role'] = 'student'
                request.session['user_id'] = student.student_id
                request.session['student_id'] = student.student_id
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid student credentials')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid credentials')
            
    return render(request, 'home.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def admin_dashboard(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    students = Student.objects.all().order_by('student_id')
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(student_name__icontains=query) |
            Q(mentor_name__icontains=query)
        )
        
    total_students = students.count()
    # Count unique mentors from student records
    total_mentors = Student.objects.values('mentor_id').distinct().count()
    
    return render(request, 'admin_dashboard.html', {
        'students': students, 
        'total_students': total_students,
        'total_mentors': total_mentors
    })

def mentor_dashboard(request):
    if request.session.get('role') != 'mentor':
        return redirect('login')
        
    mentor_id = request.session.get('user_id')
    # Filter students assigned to this mentor ID
    students = Student.objects.filter(mentor_id=mentor_id).order_by('student_id')
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(student_name__icontains=query)
        )
        
    return render(request, 'mentor_dashboard.html', {'students': students})

def add_student(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            
            # Use upper() for specialization matching
            if student.specialization:
                student.specialization = student.specialization.strip().upper()
                student.save()
            
            # Handle dynamic subjects
            subject_ids = request.POST.getlist('subject_id[]')
            subject_names = request.POST.getlist('subject_name[]')
            buckets = request.POST.getlist('bucket[]')
            completions = request.POST.getlist('course_completed[]')
            
            for i in range(len(subject_ids)):
                sid = subject_ids[i]
                sname = subject_names[i]
                bucket = buckets[i] if i < len(buckets) else None
                
                if sid:
                    subject_master = SubjectMaster.objects.filter(subject_id=sid).first()
                    if not sname:
                        sname = subject_master.subject_name if subject_master else ""
                    
                    # Copy cluster values from SubjectMaster (now Integers)
                    c1 = subject_master.cluster_start if subject_master else None
                    c2 = subject_master.cluster_end if subject_master else None
                    
                    Subject.objects.create(
                        student=student,
                        subject_id=sid,
                        subject_name=sname,
                        bucket=bucket,
                        cluster1=c1,
                        cluster2=c2,
                        course_completed=str(i) in completions
                    )
            
            messages.success(request, 'Student added successfully')
            return redirect('admin_dashboard')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

def edit_student(request, student_id):
    role = request.session.get('role')
    if role not in ['admin', 'mentor']:
        return redirect('login')
        
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        if role == 'admin':
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                student = form.save()
                if student.specialization:
                    student.specialization = student.specialization.strip().upper()
                if student.department:
                    student.department = student.department.strip().upper()
                student.save()
                
                # Update subjects
                Subject.objects.filter(student=student).delete()
                subject_ids = request.POST.getlist('subject_id[]')
                subject_names = request.POST.getlist('subject_name[]')
                buckets = request.POST.getlist('bucket[]')
                completions = request.POST.getlist('course_completed[]')
                
                cluster1_starts = request.POST.getlist('cluster1_start[]')
                cluster1_ends = request.POST.getlist('cluster1_end[]')
                cluster2_starts = request.POST.getlist('cluster2_start[]')
                cluster2_ends = request.POST.getlist('cluster2_end[]')
                
                for i in range(len(subject_ids)):
                    sid = subject_ids[i]
                    sname = subject_names[i]
                    
                    if sid:
                        subject_master = SubjectMaster.objects.filter(subject_id=sid).first()
                        if not sname:
                            sname = subject_master.subject_name if subject_master else ""
                        
                        # Handle clusters as integers
                        try:
                            c1_start = int(request.POST.getlist('cluster1_start[]')[i]) if i < len(request.POST.getlist('cluster1_start[]')) and request.POST.getlist('cluster1_start[]')[i] else (subject_master.cluster_start if subject_master else None)
                        except (ValueError, TypeError, IndexError):
                            c1_start = subject_master.cluster_start if subject_master else None
                            
                        try:
                            c1_end = int(request.POST.getlist('cluster1_end[]')[i]) if i < len(request.POST.getlist('cluster1_end[]')) and request.POST.getlist('cluster1_end[]')[i] else (subject_master.cluster_end if subject_master else None)
                        except (ValueError, TypeError, IndexError):
                            c1_end = subject_master.cluster_end if subject_master else None

                        try:
                            c2_start = int(request.POST.getlist('cluster2_start[]')[i]) if i < len(request.POST.getlist('cluster2_start[]')) and request.POST.getlist('cluster2_start[]')[i] else None
                        except (ValueError, TypeError, IndexError):
                            c2_start = None

                        try:
                            c2_end = int(request.POST.getlist('cluster2_end[]')[i]) if i < len(request.POST.getlist('cluster2_end[]')) and request.POST.getlist('cluster2_end[]')[i] else None
                        except (ValueError, TypeError, IndexError):
                            c2_end = None
                        
                        bucket = buckets[i] if i < len(buckets) else None
                        Subject.objects.create(
                            student=student,
                            subject_id=sid,
                            subject_name=sname,
                            course_completed=str(i) in completions,
                            bucket=bucket,
                            cluster1_start=c1_start,
                            cluster1_end=c1_end,
                            cluster2_start=c2_start,
                            cluster2_end=c2_end
                        )
                messages.success(request, 'Student updated successfully')
                return redirect('admin_dashboard')
        else:
            # Mentor logic - update completion status
            completions = request.POST.getlist('course_completed[]')
            subjects = student.subjects.all()
            for i, subject in enumerate(subjects):
                subject.course_completed = str(i) in completions
                subject.save()
            messages.success(request, 'Subject status updated')
            return redirect('mentor_dashboard')
    else:
        form = StudentForm(instance=student)
        
    return render(request, 'edit_student.html', {
        'form': form, 
        'student': student, 
        'is_mentor': role == 'mentor'
    })

def delete_student(request, student_id):
    if request.session.get('role') != 'admin':
        return redirect('login')
    student = get_object_or_404(Student, student_id=student_id)
    student.delete()
    messages.success(request, 'Student record deleted')
    return redirect('admin_dashboard')

def student_dashboard(request):
    if request.session.get('role') != 'student':
        return redirect('login')
        
    student_id = request.session.get('user_id')
    student = get_object_or_404(Student, student_id=student_id)
    subjects = student.subjects.all()
    
    return render(request, 'student_dashboard.html', {'student': student, 'subjects': subjects})

def upload_student_page(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    return render(request, "upload_student.html")

def upload_subject_page(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    return render(request, "upload_subject.html")

def upload_specialization_page(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    return render(request, "upload_specialization.html")

def upload_student_excel(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        try:
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.strip().str.lower()
            
            success_count = 0
            for _, row in df.iterrows():
                student_id = str(row.get('reg.no', '')).strip().split('.')[0]
                if not student_id or student_id.lower() == 'nan':
                    continue

                # 1. Create or update the student
                student, created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        'student_name': str(row.get('student name', 'Unknown')).strip(),
                        'department': str(row.get('department', '')).strip().upper(),
                        'mentor_name': str(row.get('name of the counselor', '')).strip(),
                        'mentor_id': str(row.get('emp id', '')).strip().split('.')[0],
                        'mentor_phone': str(row.get('consellor contact number', '')).strip().split('.')[0],
                        'mentor_email': str(row.get('counsellor email', '')).strip(),
                        'specialization': str(row.get('specilization', row.get('specialization', ''))).strip().upper()
                    }
                )
                success_count += 1
            
            messages.success(request, f"Successfully processed {success_count} students.")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error processing student excel: {str(e)}")
            
    return redirect('admin_dashboard')

def upload_subject_excel(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        try:
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            df.columns = df.columns.astype(str).str.strip().str.lower()
            
            success_count = 0
            for _, row in df.iterrows():
                subject_id = str(row.get('subject id', '')).strip().split('.')[0]
                if not subject_id or subject_id.lower() == 'nan':
                    continue
                
                department = str(row.get('department', '')).strip().upper()
                specialization = str(row.get('specialization', '')).strip().upper()
                
                try:
                    c1_s = int(row.get('cluster 1 start', 0))
                except (ValueError, TypeError):
                    c1_s = 0
                try:
                    c1_e = int(row.get('cluster 1 end', 0))
                except (ValueError, TypeError):
                    c1_e = 0
                try:
                    c2_s = int(row.get('cluster 2 start', 0))
                except (ValueError, TypeError):
                    c2_s = 0
                try:
                    c2_e = int(row.get('cluster 2 end', 0))
                except (ValueError, TypeError):
                    c2_e = 0

                SubjectMaster.objects.update_or_create(
                    subject_id=subject_id,
                    specialization=specialization,
                    department=department,
                    defaults={
                        'subject_name': str(row.get('subject name', 'Unknown')).strip(),
                        'cluster1_start': c1_s,
                        'cluster1_end': c1_e,
                        'cluster2_start': c2_s,
                        'cluster2_end': c2_e,
                    }
                )
                success_count += 1
            
            messages.success(request, f"Subject Master uploaded successfully. {success_count} subjects processed.")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error processing subject excel: {str(e)}")
            
    return redirect('admin_dashboard')

def upload_specialization_excel(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    if request.method == "POST":
        try:
            file = request.FILES["file"]
            df = pd.read_excel(file)
            
            # STEP 1: Normalize column names for search
            df.columns = df.columns.str.strip().str.lower()
            
            # Find the actual specilization column name used
            spec_col = 'specilization' if 'specilization' in df.columns else 'specialization'
            
            # NOTE: Removed aggressive drop_duplicates(subset=["department", spec_col]) 
            # to ensure different mapping rows for the same spec (different buckets) are processed.
            # Identity check is performed inside the loop using .exists().
            
            original_columns = df.columns.tolist()

            # Clear existing mappings to avoid duplicates
            SpecializationMapping.objects.all().delete()

            for _, row in df.iterrows():
                # Use .get if column exists, or positional if it's based on expected schema
                # For safety following user's iloc-based suggestion:
                try:
                    # Find department and speciliation indices
                    dept_idx = -1
                    spec_idx = -1
                    for i, col in enumerate(df.columns):
                        if col == 'department': dept_idx = i
                        if col in ['specilization', 'specialization']: spec_idx = i
                    
                    department = str(row.iloc[dept_idx]).strip().upper() if dept_idx != -1 else "UNKNOWN"
                    specialization = str(row.iloc[spec_idx]).strip().upper() if spec_idx != -1 else "UNKNOWN"
                except Exception:
                    department = str(row.get("department", "")).strip().upper()
                    specialization = str(row.get("specilization", row.get("specialization", ""))).strip().upper()

                if not specialization or specialization == 'NAN':
                    continue

                for i, col in enumerate(df.columns):
                    if col.startswith("c"):
                        subject_id = row.iloc[i]
                        if pd.isna(subject_id):
                            continue
                            
                        # Use ORIGINAL column name (C0, C0, C1)
                        bucket_name = str(original_columns[i]).strip().upper()
                        # If pandas added .1 suffix, strip it
                        if '.' in bucket_name and bucket_name.split('.')[-1].isdigit():
                            bucket_name = bucket_name.split('.')[0]
                        
                        sid_str = str(subject_id).strip().split('.')[0]
                        if sid_str.lower() == 'nan' or not sid_str:
                            continue

                        # STEP 4: OPTIONAL SAFETY CHECK - Only create if NOT exists
                        if not SpecializationMapping.objects.filter(
                            department=department,
                            specialization=specialization,
                            bucket=bucket_name,
                            subject_id=sid_str
                        ).exists():
                            SpecializationMapping.objects.create(
                                department=department,
                                specialization=specialization,
                                bucket=bucket_name,
                                subject_id=sid_str
                            )
                            print(f"Stored Mapping: {bucket_name} - {sid_str}")
            
            # TRIGGER ASSIGNMENT LOGIC
            assign_subjects()
            
            messages.success(request, "Specialization mapping stored and subjects assigned successfully.")
        except Exception as e:
            messages.error(request, f"Error processing specialization excel: {str(e)}")
            
        return redirect("admin_dashboard")
    
    return redirect("admin_dashboard")

def assign_subjects():
    """DB-Driven assignment logic with strict filtering and duplicate support."""
    # 1. Clear existing assignments to avoid duplicates
    Subject.objects.all().delete()

    students = Student.objects.all()
    for student in students:
        student_spec = str(student.specialization or "").strip().upper()
        student_dept = str(student.department or "").strip().upper()
        
        # Cluster logic (last 3 digits of student_id)
        try:
            student_id_str = str(student.student_id).strip()
            student_cluster = int(student_id_str[-3:]) if len(student_id_str) >= 3 else 0
        except ValueError:
            student_cluster = 0
            
        print("Student:", student.student_id, student_spec, student_dept)
        
        if not student_spec or not student_dept:
            continue

        # Find mappings for this specialization and department
        mappings = SpecializationMapping.objects.filter(
            specialization=student_spec,
            department=student_dept
        )
        
        print("Mappings Count:", mappings.count())

        for map_obj in mappings:
            # SMART MATCHING: Try strict Spec + Dept first
            subjects = SubjectMaster.objects.filter(
                subject_id=map_obj.subject_id,
                specialization=student_spec,
                department=student_dept
            )
            
            # FALLBACK: If strict match fails, try Dept only (common subjects)
            if not subjects.exists():
                print(f"No strict match for {map_obj.subject_id} in {student_spec}. Trying {student_dept} wide...")
                subjects = SubjectMaster.objects.filter(
                    subject_id=map_obj.subject_id,
                    department=student_dept
                )

            print("Subjects Found for", map_obj.subject_id, ":", subjects.count())

            for subject in subjects:
                # DEBUG ADD (MANDATORY)
                print("Student:", student.student_id)
                print("Cluster:", student_cluster)
                print("C1:", subject.cluster1_start, "-", subject.cluster1_end)
                print("C2:", subject.cluster2_start, "-", subject.cluster2_end)
                
                # CLUSTER VALIDITY LOGIC (Calculated but temporarily ignored to ensure all students get subjects)
                range1_defined = (subject.cluster1_start and subject.cluster1_start != 0) or (subject.cluster1_end and subject.cluster1_end != 0)
                range2_defined = (subject.cluster2_start and subject.cluster2_start != 0) or (subject.cluster2_end and subject.cluster2_end != 0)
                
                is_valid = False
                if not range1_defined and not range2_defined:
                    is_valid = True # Global
                elif range1_defined and subject.cluster1_start <= student_cluster <= subject.cluster1_end:
                    is_valid = True
                elif range2_defined and subject.cluster2_start <= student_cluster <= subject.cluster2_end:
                    is_valid = True

                if not is_valid:
                    print(f"!!! ALERT: Cluster {student_cluster} out of range for {subject.subject_id} ({subject.cluster1_start}-{subject.cluster1_end}). BUT ASSIGNING ANYWAY (Solution 3).")
                
                # ASSIGNMENT (Always run for valid mapping entries)
                Subject.objects.create(
                    student=student,
                    subject_id=subject.subject_id,
                    subject_name=subject.subject_name,
                    bucket=map_obj.bucket,
                    cluster1_start=subject.cluster1_start,
                    cluster1_end=subject.cluster1_end,
                    cluster2_start=subject.cluster2_start,
                    cluster2_end=subject.cluster2_end
                )
                print(f"Assigned: {subject.subject_id} to Bucket: {map_obj.bucket}")

from django.http import HttpResponseForbidden

def edit_student_subjects(request, student_id):
    role = request.session.get('role')
    if role not in ['admin', 'mentor']:
        return redirect('login')
        
    student = get_object_or_404(Student, student_id=student_id)
    
    # Ownership Check for Mentors
    if role == 'mentor' and student.mentor_name != request.session.get('mentor_name'):
        return HttpResponseForbidden("You are not authorized to edit subjects for this student.")
        
    if request.method == 'POST':
        # Reuse existing logic for saving subjects
        Subject.objects.filter(student=student).delete()
        subject_ids = request.POST.getlist('subject_id[]')
        subject_names = request.POST.getlist('subject_name[]')
        buckets = request.POST.getlist('bucket[]')
        completions = request.POST.getlist('course_completed[]')
        cluster1_starts = request.POST.getlist('cluster1_start[]')
        cluster1_ends = request.POST.getlist('cluster1_end[]')
        cluster2_starts = request.POST.getlist('cluster2_start[]')
        cluster2_ends = request.POST.getlist('cluster2_end[]')
        
        for i in range(len(subject_ids)):
            sid = subject_ids[i]
            if sid:
                sname = subject_names[i] if i < len(subject_names) else ""
                bucket = buckets[i] if i < len(buckets) else None
                
                # Convert clusters to int
                try:
                    c1_start = int(request.POST.getlist('cluster1_start[]')[i]) if i < len(request.POST.getlist('cluster1_start[]')) and request.POST.getlist('cluster1_start[]')[i] else 0
                except (ValueError, TypeError, IndexError):
                    c1_start = 0
                try:
                    c1_end = int(request.POST.getlist('cluster1_end[]')[i]) if i < len(request.POST.getlist('cluster1_end[]')) and request.POST.getlist('cluster1_end[]')[i] else 0
                except (ValueError, TypeError, IndexError):
                    c1_end = 0
                try:
                    c2_start = int(request.POST.getlist('cluster2_start[]')[i]) if i < len(request.POST.getlist('cluster2_start[]')) and request.POST.getlist('cluster2_start[]')[i] else 0
                except (ValueError, TypeError, IndexError):
                    c2_start = 0
                try:
                    c2_end = int(request.POST.getlist('cluster2_end[]')[i]) if i < len(request.POST.getlist('cluster2_end[]')) and request.POST.getlist('cluster2_end[]')[i] else 0
                except (ValueError, TypeError, IndexError):
                    c2_end = 0
                
                Subject.objects.create(
                    student=student,
                    subject_id=sid,
                    subject_name=sname,
                    bucket=bucket,
                    cluster1_start=c1_start,
                    cluster1_end=c1_end,
                    cluster2_start=c2_start,
                    cluster2_end=c2_end,
                    course_completed=str(i) in completions
                )
        
        messages.success(request, 'Student subjects updated successfully')
        if role == 'admin':
            return redirect('admin_dashboard')
        return redirect('mentor_dashboard')
        
    return render(request, 'edit_student_subjects.html', {
        'student': student,
        'is_mentor': role == 'mentor'
    })

def mentor_change_password(request):
    if request.session.get('role') != 'mentor':
        return redirect('login')
        
    mentor_id = request.session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Get one student record to check current password
        mentor_student = Student.objects.filter(mentor_id=mentor_id).first()
        if not mentor_student:
            messages.error(request, "Mentor account not found.")
            return redirect('login')
            
        stored_password = mentor_student.mentor_password if mentor_student.mentor_password else mentor_student.mentor_phone
        
        if current_password != stored_password:
            messages.error(request, "Current password does not match.")
        elif new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
        elif not new_password:
            messages.error(request, "New password cannot be empty.")
        else:
            # Update ALL students associated with this mentor_id
            Student.objects.filter(mentor_id=mentor_id).update(mentor_password=new_password)
            messages.success(request, "Password updated successfully!")
            return redirect('mentor_dashboard')
            
    return render(request, 'mentor_change_password.html')

def admin_mentor_list(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    query = request.GET.get('search', '').strip()
    
    # Get distinct mentors from student records
    mentors_qs = Student.objects.values(
        'mentor_id', 'mentor_name', 'mentor_email', 'mentor_phone'
    ).distinct()
    
    if query:
        mentors_qs = mentors_qs.filter(
            Q(mentor_id__icontains=query) |
            Q(mentor_name__icontains=query) |
            Q(mentor_email__icontains=query)
        )
    
    # Prepare mentor data with student counts
    mentor_list = []
    for m in mentors_qs:
        if m['mentor_id']: # Only include if mentor ID exists
            m['student_count'] = Student.objects.filter(mentor_id=m['mentor_id']).count()
            mentor_list.append(m)
            
    total_mentors = len(mentor_list)
    
    return render(request, 'admin_mentor_list.html', {
        'mentors': mentor_list,
        'total_mentors': total_mentors
    })

def admin_change_mentor_password(request, mentor_id):
    if request.session.get('role') != 'admin':
        return redirect('login')
        
    # Get any one student record to show mentor name/details
    mentor_info = Student.objects.filter(mentor_id=mentor_id).first()
    if not mentor_info:
        messages.error(request, "Mentor record not found.")
        return redirect('mentor_list')
        
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password:
            messages.error(request, "Password cannot be empty.")
        elif new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # Update ALL students associated with this mentor_id
            Student.objects.filter(mentor_id=mentor_id).update(mentor_password=new_password)
            messages.success(request, f"Password for {mentor_info.mentor_name} updated successfully!")
            return redirect('mentor_list')
            
    return render(request, 'admin_change_mentor_password.html', {'mentor': mentor_info})
