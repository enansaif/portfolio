"""
LeetQuizzer application views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Count
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.exceptions import TemplateDoesNotExist
from django.core.exceptions import FieldError
from django.contrib import messages
from leetquizzer.models import Problem, Topic, Difficulty
from leetquizzer.forms import CreateProblemForm, CreateTopicForm, UpdateProblemForm
from leetquizzer.utils.functions import make_qa_list, get_problem_description
from leetquizzer.utils.functions import get_info


class MainMenu(View):
    """
    View class for the main menu page.

    This class-based view handles the GET request for the main menu page.
    It retrieves a list of problems from the database and renders the 'leetquizzer/index.html' 
    template. The list of problems can be sorted based on the specified 'sorted_by' parameter, 
    which can be 'topic', 'difficulty', or None.
    """
    failure_url = 'leetquizzer/base.html'
    template = 'leetquizzer/index.html'
    def get(self, request, sorted_by=None):
        """
        Handle GET request for the main menu page.

        Args:
            sorted_by (str, optional): The sorting parameter. Can be 'topic', 'difficulty', or None.

        Returns:
            HttpResponse: The rendered response with the 'leetquizzer/index.html' template and the 
            problem list context.

        Note:
            The 'sorted_by' parameter determines the sorting order of the problem list.
            If 'sorted_by' is 'topic', the problems are sorted by topic name.
            If 'sorted_by' is 'difficulty', the problems are sorted by difficulty name.
            If 'sorted_by' is None, the problems are sorted by time (default order).
        """
        try:
            if sorted_by:
                problems = Problem.objects.order_by(sorted_by)
            else:
                problems = Problem.objects.order_by('time')
            context = {'problem_list': problems, 'current': sorted_by}
            return render(request, self.template, context)
        except FieldError:
            return render(request, self.failure_url)


class ProblemMenu(View):
    """
    View class for the problem menu page.
    """
    failure_url = 'leetquizzer/base.html'
    def get(self, request, problem_id):
        """
        Handle GET request for the problem menu page.
        """
        problem = get_object_or_404(Problem, pk=problem_id)
        q_list = make_qa_list(problem)
        problem_description = get_problem_description(problem.link).get('content', {})
        if problem_description:
            context = {'question_list': q_list, 'problem': problem,
                        'problem_desc': problem_description}
            return render(request, "leetquizzer/problem.html", context)
        return render(request, self.failure_url)

    def post(self, request, problem_id):
        """
        Handle POST request for the problem menu page.
        """
        problem = get_object_or_404(Problem, pk=problem_id)
        form_dict = request.POST.dict()
        form_dict.pop('csrfmiddlewaretoken')
        is_wrong = False
        for value in form_dict.values():
            if value == '0':
                is_wrong = True
        problem.wrong = is_wrong
        problem.save()
        return redirect(reverse_lazy('leetquizzer:main_menu'))


class ProblemMenuV1(View):
    """
    View class for the problem menu page.

    This class-based view handles the GET and POST requests for the problem menu page.
    It retrieves a specific problem from the database and renders the corresponding quiz template.
    The view supports storing and retrieving question lists in the session for each problem.

    Attributes:
        failure_url (str): The URL of the base template to render in case of failure.
        success_message (str): The success message to display when the answer is correct.
        failure_message (str): The failure message to display when the answer is incorrect.
    """
    failure_url = 'leetquizzer/base.html'
    success_message = "ABSOLUTELY CORRECT!!!"
    failure_message = "WRONG!!! please try again later"
    def get(self, request, problem_id):
        """
        Handle GET request for the problem menu page.

        Args:
            problem_id (int): The ID of the problem to display.

        Returns:
            HttpResponse: The rendered response with the corresponding quiz template and the 
            question list context.

        Note:
            This method retrieves the problem from the database based on the provided 'problem_id'.
            If the question list for the problem is not stored in the session, it generates a new 
            question list using the 'make_list' function.The rendered template depends on the 
            problem's 'number' attribute. The question list is stored in the session using the 
            'problem_id' as the key.
        """
        try:
            problem = get_object_or_404(Problem, pk=problem_id)
            key = f"q{problem_id}"
            if key not in request.session:
                q_list = make_qa_list(problem)
                request.session[key] = q_list
            context = {'question_list': request.session[key], 'link': problem.link,
                       'quiz_url': f"quizzes/{problem.number}.html"}
            return render(request, "leetquizzer/problem.html", context)
        except TemplateDoesNotExist:
            return render(request, self.failure_url)
    def post(self, request, problem_id):
        """
        Handle POST request for the problem menu page.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            HttpResponseRedirect: Redirects to the current page after processing the POST request.

        Note:
            This method retrieves the problem from the database based on the provided 'problem_id'.
            The answer is retrieved from the request's POST data. The question list for the problem 
            is removed from the session. The success or failure messages are stored in the messages 
            framework based on the correctness of the answer. The 'wrong' attribute of the problem 
            object is updated accordingly and saved. The response is redirected back to the current 
            page.
        """
        problem = get_object_or_404(Problem, pk=problem_id)
        key = f"q{problem_id}"
        answer = request.POST.get('answer', None)
        request.session.pop(key)
        _ = list(messages.get_messages(request))
        if answer == 'True':
            messages.info(request, self.success_message)
            problem.wrong = False
        else:
            messages.info(request, self.failure_message)
            problem.wrong = True
        problem.save()
        return redirect(self.request.path_info)


class CreateProblem(LoginRequiredMixin, View):
    """
    View class for creating a new problem.

    This class-based view handles the GET and POST requests for creating a new problem.
    It renders the 'problem_create.html' template for displaying the form to create a problem.
    The view performs form validation, checks for existing problems with the same name or number,
    and saves the new problem to the database if it passes all validations.

    Attributes:
        template (str): The name of the template to render.
        success_url (str): The URL to redirect to after successfully creating the problem.
        failure_url (str): The URL to redirect to after failed creating the problem.
    """
    template = 'leetquizzer/problem_create.html'
    failure_url = 'leetquizzer/base.html'
    success_url = reverse_lazy('leetquizzer:main_menu')
    def get(self, request):
        """
        Handle GET request for creating a new problem.
        """
        form = CreateProblemForm()
        context = {'form': form}
        return render(request, self.template, context)
    def post(self, request):
        """
        Handle POST request for creating a new problem.

        Returns:
            HttpResponseRedirect: Redirects to the success URL after creating the problem.
            HttpResponse: The rendered response with the create problem form and error message 
            if form validation fails.

        Note:
            This method performs form validation by checking if the form is valid.
            If the form is not valid, it re-renders the template with the form and appropriate 
            error messages. It then checks if a problem with the same name or number already 
            exists in the database. If a problem with the same name or number exists, it re-renders 
            the template with the form and an error message. If the form passes all validations, 
            a new Problem instance is created and saved to the database. The response is redirected 
            to the success URL.
        """
        form = CreateProblemForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template, context)
        question_link = form.cleaned_data['link']
        endpoints = question_link.split('/')
        info_dict = get_info(endpoints[-2])
        if not info_dict:
            return redirect(self.failure_url)
        number = info_dict['questionFrontendId']
        has_number = Problem.objects.filter(number=number).exists()
        if has_number:
            context = {'form': form, 'message': 'Problem already exists!'}
            return render(request, self.template, context)
        difficulty, _ = Difficulty.objects.get_or_create(name=info_dict['difficulty'])
        problem = Problem(link=endpoints[-2],
                          difficulty=difficulty,
                          number=number,
                          name=info_dict['title'],
                          topic=form.cleaned_data['topic'],
                          edge_case=form.cleaned_data['edge_case'],
                          solution=form.cleaned_data['solution'],
                          option1=form.cleaned_data['option1'],
                          option2=form.cleaned_data['option2'])
        problem.save()
        return redirect(self.success_url)


class UpdateProblem(LoginRequiredMixin, View):
    """
    A class-based view for updating a problem object.

    Attributes:
        template (str): The path to the template used for rendering the update form.
        success_url (str): The URL to redirect to after successfully updating the problem.
    """
    template = 'leetquizzer/problem_update.html'
    success_url = reverse_lazy('leetquizzer:main_menu')
    def get(self, request, problem_id):
        """
        Retrieves the problem object with the given problem_id and renders the update form
        with pre-filled data based on the problem's current values.

        Args:
            problem_id (int): The ID of the problem to be updated.
        """
        problem = get_object_or_404(Problem, pk=problem_id)
        initial_dict = {
        "topic": problem.topic,
        "solution": problem.solution,
        "edge_case": problem.edge_case,
        "option1": problem.option1,
        "option2": problem.option2,
        }
        form = UpdateProblemForm(initial=initial_dict)
        context = {'form': form}
        return render(request, self.template, context)
    def post(self, request, problem_id):
        """
        Handles the form submission and updates the problem object with the submitted data.

        Args:
            request (HttpRequest): The HTTP request object.
            problem_id (int): The ID of the problem to be updated.
        """
        form = UpdateProblemForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template, context)
        problem = get_object_or_404(Problem, pk=problem_id)
        problem.topic = form.cleaned_data['topic']
        problem.edge_case = form.cleaned_data['edge_case']
        problem.solution = form.cleaned_data['solution']
        problem.option1 = form.cleaned_data['option1']
        problem.option2 = form.cleaned_data['option2']
        problem.save()
        return redirect(self.success_url)


class DeleteProblem(LoginRequiredMixin, View):
    """
    Class to handle deleting a problem
    """
    success_url = reverse_lazy('leetquizzer:main_menu')
    def post(self, _, problem_id):
        """
        Get the problem form database and delete it
        """
        problem = get_object_or_404(Problem, pk=problem_id)
        problem.delete()
        return redirect(self.success_url)


class CreateTopic(View):
    """
    View class for creating a new topic.

    This class-based view handles the GET and POST requests for creating a new topic.
    It renders the 'topic_create.html' template for displaying the form to create a topic.
    The view performs form validation, checks for existing topics with the same name,
    and saves the new topic to the database if it passes all validations.

    Attributes:
        template (str): The name of the template to render.
        success_url (str): The URL to redirect to after successfully creating the topic.
    """
    template = 'leetquizzer/topic_create.html'
    success_url = reverse_lazy('leetquizzer:create_problem')
    def get(self, request):
        """
        Handle GET request for creating a new topic.
        """
        form = CreateTopicForm()
        topics = Topic.objects.annotate(Count('problem')).values_list('name', 'problem__count')
        context = {'form': form, 'topic_list': topics}
        return render(request, self.template, context)
    def post(self, request):
        """
        Handle POST request for creating a new topic.

        Returns:
            HttpResponseRedirect: Redirects to the success URL after creating the topic.
            HttpResponse: The rendered response with the create topic form and error message 
            if form validation fails.

        Note:
            This method performs form validation by checking if the form is valid. If the form 
            is not valid, it re-renders the template with the form and appropriate error messages.
            It then checks if a topic with the same name already exists in the database. If a 
            topic with the same name exists, it re-renders the template with the form and an 
            error message. If the form passes all validations, a new Topic instance is created 
            and saved to the database. The response is redirected to the success URL.
        """
        form = CreateTopicForm(request.POST)
        if not form.is_valid():
            topics = Topic.objects.annotate(Count('problem')).values_list('name', 'problem__count')
            context = {'form': form, 'topic_list': topics}
            return render(request, self.template, context)
        new_topic = form.cleaned_data['topic'].lower().title()
        has_topic = Topic.objects.filter(name=new_topic).exists()
        if has_topic:
            topics = Topic.objects.annotate(Count('problem')).values_list('name', 'problem__count')
            context = {'form': form, 'topic_list': topics,
                       'message': 'Topic with this name already exists!'}
            return render(request, self.template, context)
        topic = Topic(name=new_topic)
        topic.save()
        return redirect(self.success_url)
