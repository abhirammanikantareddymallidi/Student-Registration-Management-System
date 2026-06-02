from portal_app.models import Student
students = Student.objects.all()[:5]
print('STUDENTS:')
for s in students:
    print(f'ID: {s.student_id}, Pass: {s.student_id[-5:]}')
print('\nMENTORS:')
mentors = Student.objects.values('mentor_id', 'mentor_phone', 'mentor_name').distinct()[:5]
for m in mentors:
    print(f'ID: {m["mentor_id"]}, Phone (Pass): {m["mentor_phone"]}, Name: {m["mentor_name"]}')
