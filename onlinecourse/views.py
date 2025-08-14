from django.shortcuts import render
from django.http import HttpResponseRedirect
# Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# Task 5: Submission and Result Views

# A view to handle exam submission
def submit(request, course_id):
    if request.method == 'POST':
        enrollment = Enrollment.objects.get(
            user=request.user,
            course_id=course_id
        )
        submission = Submission(enrollment=enrollment)
        submission.save()

        selected_choice_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_choice_ids.append(int(value))
        
        choices = Choice.objects.filter(id__in=selected_choice_ids)
        submission.choices.set(choices)

        return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission.id,)))


# A view to show the exam result
def show_exam_result(request, course_id, submission_id):
    submission = Submission.objects.get(id=submission_id)
    course = Course.objects.get(id=course_id)
    questions = course.question_set.all()
    
    total_score = 0
    for question in questions:
        selected_choices_for_question = submission.choices.filter(question=question)
        if question.is_get_score([choice.id for choice in selected_choices_for_question]):
            total_score += question.grade
    
    # Calculate the total max score
    total_max_score = 0
    for question in questions:
        total_max_score += question.grade

    # Determine if the user passed (score >= 50%)
    passed = total_score >= total_max_score / 2

    context = {
        'submission': submission,
        'total_score': total_score,
        'total_max_score': total_max_score,
        'passed': passed, # Add passed status to context
        'course': course
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)