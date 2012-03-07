from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from issues.models import *
from issues.choices import *
from issues.forms import *
import datetime
from newsfeed.models import Activity
from projects.models import App
from django.contrib import messages

def project_milestones(app_slug=None):
    return Milestone.objects.filter(app__slug=app_slug)

def all_issues(request):
    context = {'issues': Issue.objects.open()}
    return render(request, 'issues/issue_list.html', context)

def issue_list(request):
    context = {'defect_count': Defect.objects.count()}
    context['defects'] = Defect.objects.all()
    paginator = Paginator(context['defects'], 40)
    page = request.GET.get('page', 1)
    try:
        context['defects'] = paginator.page(page)
    except PageNotAnInteger:
        context['defects'] = paginator.page(1)
    except EmptyPage:
        context['defects'] = paginator.page(paginator.num_pages)
    return render(request, 'issues/issue_list.html', context)

def open_app_issues(request, app_slug):
    app = get_object_or_404(App, slug=app_slug)
    context = {'issues': Issue.objects.open().by_app(app_slug), 'app':app, 'project_milestones':project_milestones()}
    paginator = Paginator(context['issues'], 20)
    context['open'] = True
    page = request.GET.get('page', 1)
    try:
        context['issues'] = paginator.page(page)
    except PageNotAnInteger:
        context['issues'] = paginator.page(1)
    except EmptyPage:
        context['issues'] = paginator.page(paginator.num_pages)
    return render(request, 'issues/project_list.html', context)

def closed_app_issues(request, app_slug):
    app = get_object_or_404(App, slug=app_slug)
    context = {'issues': Issue.objects.closed().by_app(app_slug), 'app':app, 'project_milestones':project_milestones()}
    paginator = Paginator(context['issues'], 20)
    context['closed'] = True
    page = request.GET.get('page', 1)
    try:
        context['issues'] = paginator.page(page)
    except PageNotAnInteger:
        context['issues'] = paginator.page(1)
    except EmptyPage:
        context['issues'] = paginator.page(paginator.num_pages)
    return render(request, 'issues/project_list.html', context)

def no_filter_app_issues(request, app_slug):
    app = get_object_or_404(App, slug=app_slug)
    context = {'issues': Issue.objects.all().by_app(app_slug), 'app':app, 'project_milestones':project_milestones()}
    paginator = Paginator(context['issues'], 20)
    context['all'] = True
    page = request.GET.get('page', 1)
    try:
        context['issues'] = paginator.page(page)
    except PageNotAnInteger:
        context['issues'] = paginator.page(1)
    except EmptyPage:
        context['issues'] = paginator.page(paginator.num_pages)
    return render(request, 'issues/project_list.html', context)

def close_issue(request, app_slug, issue_id):
    issue = Issue.objects.get(pk=issue_id)
    issue.status = "closed"
    issue.save()
    messages.add_message(request, messages.INFO, "Issue %s Closed" % issue_id)
    return redirect("defect_detail", defect_id=issue_id, app_slug=issue.application.slug)

def handle_comment(request):
    if request.POST:
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            issue = get_object_or_404(Issue, pk=request.POST.get('issue_id'))
            obj = form.save(commit=False)
            obj.author = request.user
            obj.issue = issue
            obj.save()
            messages.add_message(request, messages.SUCCESS, "Comment Added")
            return redirect("defect_detail", defect_id=issue.id, app_slug=issue.application.slug)
    return redirect("newsfeed.views.dashboard")


def defect_detail(request, defect_id, app_slug=None):
    app = get_object_or_404(App, slug=app_slug)
    issue = get_object_or_404(Issue, pk=defect_id)
    comments = Comment.objects.filter(issue=issue)
    context = {'defect': issue}
    context['app'] = app
    context['comments'] = comments    
    if request.method == "POST":
        form = IssueForm(app, request.POST, instance=issue)
        if form.is_valid():
            obj = form.save()
            obj.status = "open"
            obj.last_modified_date = datetime.date.today()
            obj.save()
            messages.add_message(request, messages.SUCCESS, "Issue Saved")
            return redirect("defect_detail", defect_id=obj.id, app_slug=app.slug)
    else:
        form = IssueForm(app, instance=context['defect'])
        comment_form = CommentForm()
        context['form'] = form
        context['comment_form'] = comment_form
    return render(request, 'issues/defect_detail_dep.html', context)


def add_defect(request, app_slug):
    context = {}
    app = get_object_or_404(App, slug=app_slug)
    context['app'] = app
    if request.method == "POST":
        form = IssueForm(app, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.creator = request.user
            obj.status = "open"
            obj.application = app
            obj.save()

            activity = Activity(application=obj.application)
            activity.user = request.user
            activity.action = "Added a new defect #%s" % obj.id
            activity.issue = obj
            activity.save()

            return redirect("open_app_issues", app_slug=app.slug)
            #return redirect("defect_detail", defect_id=obj.id)
    else:
        form = IssueForm(app)
    context['form'] = form
    
    return render(request, 'issues/add_defect.html', context)
    
    
def add_milestone(request, app_slug):
    context = {}
    app = get_object_or_404(App, slug=app_slug)
    context['app'] = app
    if request.method == "POST":
        form = MilestoneForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.application = app
            obj.save()
            
            return redirect("milestone_list", app_slug=app.slug)
    else:
        form = MilestoneForm()
    context['form'] = form
    return render(request, 'issues/add_milestone.html', context)
    
# Milestones
def milestone_list(request, app_slug):
    context = {}
    app = get_object_or_404(App, slug=app_slug)
    context['app'] = app
    context['milestones'] = Milestone.objects.filter(app=app)
    return render(request, 'issues/milestones.html', context)
        
