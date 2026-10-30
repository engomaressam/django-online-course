from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Question, Submission


class ExamTests(TestCase):
    """The assessment feature: submitting an exam and scoring it."""

    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="pw-12345")
        self.course = Course.objects.create(name="Django basics", description="Models, views and templates")
        Enrollment.objects.create(user=self.user, course=self.course)
        # q1: one correct answer; q2: two correct answers
        self.q1 = Question.objects.create(course=self.course, content="Which file holds the models?", grade=50)
        self.c1 = Choice.objects.create(question=self.q1, content="models.py", is_correct=True)
        self.c2 = Choice.objects.create(question=self.q1, content="urls.py", is_correct=False)
        self.q2 = Question.objects.create(course=self.course, content="Which are Django field types?", grade=50)
        self.c3 = Choice.objects.create(question=self.q2, content="CharField", is_correct=True)
        self.c4 = Choice.objects.create(question=self.q2, content="ForeignKey", is_correct=True)
        self.c5 = Choice.objects.create(question=self.q2, content="render", is_correct=False)
        self.client.login(username="learner", password="pw-12345")

    def submit(self, *choices):
        data = {f"choice_{c.id}": c.id for c in choices}
        return self.client.post(reverse("onlinecourse:submit", args=(self.course.id,)), data)

    def result(self, response):
        return self.client.get(response["Location"])

    def test_scoring_requires_exactly_the_correct_choices(self):
        self.assertTrue(self.q2.is_get_score([self.c3.id, self.c4.id]))
        self.assertFalse(self.q2.is_get_score([self.c3.id]))                       # one correct answer missing
        self.assertFalse(self.q2.is_get_score([self.c3.id, self.c4.id, self.c5.id]))  # a wrong one ticked too
        self.assertFalse(self.q1.is_get_score([]))

    def test_submit_saves_the_choices_and_redirects_to_the_result(self):
        response = self.submit(self.c1, self.c3, self.c4)
        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get()
        self.assertEqual(set(submission.choices.all()), {self.c1, self.c3, self.c4})
        self.assertIn(f"/submission/{submission.id}/result/", response["Location"])

    def test_full_marks_pass(self):
        page = self.result(self.submit(self.c1, self.c3, self.c4))
        self.assertEqual(page.context["total_score"], 100)
        self.assertTrue(page.context["passed"])

    def test_ticking_everything_does_not_score(self):
        page = self.result(self.submit(self.c1, self.c2, self.c3, self.c4, self.c5))
        self.assertEqual(page.context["total_score"], 0)
        self.assertFalse(page.context["passed"])

    def test_half_marks_still_pass(self):
        page = self.result(self.submit(self.c1, self.c3))  # q1 right, q2 incomplete
        self.assertEqual(page.context["total_score"], 50)
        self.assertTrue(page.context["passed"])

    def test_a_learner_cannot_open_someone_elses_result(self):
        location = self.submit(self.c1)["Location"]
        User.objects.create_user(username="other", password="pw-67890")
        self.client.login(username="other", password="pw-67890")
        self.assertEqual(self.client.get(location).status_code, 404)

    def test_submitting_requires_login(self):
        self.client.logout()
        response = self.submit(self.c1)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("onlinecourse:login"), response["Location"])
        self.assertFalse(Submission.objects.exists())
