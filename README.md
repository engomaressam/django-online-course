# Online course app with exams (Django)

A Django web app where learners register, enrol in courses, take a multiple-choice exam and see their score. The assessment feature (questions, choices, submissions, scoring and the result page) is my part; the course, lesson and enrolment parts came with the starter app.

Final project for IBM's *Django Application Development with SQL and Databases* course.

![Data model](static/media/course_images/onlinecourse_app_er.png)

## What it does

- **Accounts:** registration, login and logout with Django's auth.
- **Courses:** a course list and course pages with lessons and instructors; learners enrol with one click.
- **Exams:** a course page shows its questions as checkboxes. A submission stores the chosen answers, and the result page shows the score per question, the total and whether the learner passed (50% or more).

## Data model

`Course` has `Lesson`s, `Instructor`s and learners through `Enrollment`. The assessment adds `Question` (belongs to a course, carries a grade), `Choice` (belongs to a question, marked correct or not) and `Submission` (belongs to an enrolment, many-to-many with the chosen `Choice`s). A question scores its grade when exactly its correct choices are selected (`Question.is_get_score`).

## Run it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser        # add courses, questions and choices in /admin
python manage.py runserver              # http://127.0.0.1:8000/onlinecourse/
python manage.py test onlinecourse      # 7 tests for the exam feature
```

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`0` in production) and `DJANGO_ALLOWED_HOSTS` come from the environment; the defaults are for local development.

## Changes after the course

- **Scoring:** a question now scores only when exactly its correct choices are ticked. The original logic gave full marks whenever every correct choice was ticked, so ticking every box always scored 100%.
- **Privacy:** the result page and the submit view need a login, and a learner can only open their own submissions. Before, any submission could be opened by changing the ID in the URL.
- **Tests:** seven tests cover the scoring rules, the submit-and-result flow, pass/fail, login and the ownership check. The starter app had none.
- **Settings:** the secret key, debug flag and allowed hosts come from the environment instead of being hard-coded. The requirements are trimmed to what the app uses (Django 4.2 LTS, Pillow, gunicorn), and the IBM Cloud Foundry files are gone.

## History

Built in August 2025 on another GitHub account and moved here in October 2026 with its full commit history (the early commits are the IBM starter's).

---

Omar Essam El Sherbiny · [omaressam.web.app](https://omaressam.web.app) · [LinkedIn](https://www.linkedin.com/in/omar-essam-el-sherbiny-b602279b/)
