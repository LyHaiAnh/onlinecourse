from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)

    if request.method == 'POST':
        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))

        submission = Submission.objects.create(enrollment=enrollment)
        selected_choices = Choice.objects.filter(id__in=selected_ids)
        submission.choices.set(selected_choices)
        submission.save()

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    return redirect('onlinecourse:course_details', course_id=course.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_choices = submission.choices.all()

    total_score = 0
    max_score = 0

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            max_score += question.grade
            selected_ids = [choice.id for choice in selected_choices if choice.question == question]
            if question.is_get_score(selected_ids):
                total_score += question.grade

    grade = (total_score / max_score * 100) if max_score > 0 else 0

    context['course'] = course
    context['submission'] = submission
    context['selected_choices'] = selected_choices
    context['total_score'] = total_score
    context['max_score'] = max_score
    context['grade'] = grade
    context['passed'] = grade >= 70

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
