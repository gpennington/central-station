'''
    Author: Derek Stegelman
    Package: Projects App

'''

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from projects.models import *
from projects.forms import *
from django.contrib.auth.models import User
from issues.models import Milestone
from django.contrib.auth.decorators import login_required
from newsfeed.models import Activity


@login_required
def app_list(request):
    context = {'apps': App.objects.all()}
    return render(request, 'projects/app_list.html', context)

@login_required
def add_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save()
            app.users.add(request.user)
            activity = Activity(application=app)
            activity.action = "Created a new application, %s" % app.name
            activity.user = request.user
            activity.save()
            return redirect("app", app.slug)
    else:
        form = ApplicationForm()
    context = {'form': form}

    return render(request, 'projects/add_form.html', context)


@login_required
def app(request, app_slug):
    context = {'app': get_object_or_404(App, slug=app_slug)}
    context['feed'] = Activity.objects.by_app(app_slug)
    context['milestones'] = Milestone.objects.filter(app__slug=app_slug)
    return render(request, 'projects/app_index.html', context)

'''
    Settings View - Show and enable the change of settings per project
'''
@login_required
def settings(request, app_slug):
    app = get_object_or_404(App, slug=app_slug)
    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=app)
        if form.is_valid():
            new_app = form.save()
            activity = Activity(application=app)
            activity.action = "Updated the settings on %s" % app.name
            activity.user = request.user
            activity.save()
            return redirect('app', app.slug)
    else:
        form = ApplicationForm(instance=app)
    context = {'form':form, 'app':app}
    return render(request, 'projects/project_settings.html', context)

@login_required
def users(request, app_slug):
    context = {}
    app = get_object_or_404(App, slug=app_slug)
    context['users'] = User.objects.all()
    context['app'] = app
    return render(request, "projects/users.html", context)

def add_users(request, app_slug):
    context = {}
    app = get_object_or_404(App, slug=app_slug)
    context['app'] = app
    context['users'] = User.objects.all()
    if request.method == "POST":
        for item in request.POST:
            if item != "csrfmiddlewaretoken":
                user = User.objects.get(pk=item)
                app.users.add(user)
                app.save()
    return render(request, "projects/users.html", context)

