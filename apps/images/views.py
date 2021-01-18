import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, TemplateView, DeleteView

from .models import Image

# Create your views here.
class IndexView(TemplateView):
    template_name = 'images/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        search_term = self.request.GET.get('q') or ''
        colors = self.request.GET.getlist('color' or [])
        colors = list(filter(('').__ne__, colors))  # filter out empty strings
        properties = self.request.GET.getlist('property' or [])
        properties = list(filter(('').__ne__, properties))  # filter out empty strings

        # populate the public image list
        context['public_image_list'] = Image.objects.filter(private=False).order_by("-created").select_related('owner')
        if search_term != '': context['public_image_list'] = context['public_image_list'].filter(title__icontains=search_term)
        if len(colors) > 0:
            for color in colors:
                context['public_image_list'] = context['public_image_list'].filter(colors__icontains=color)
        if len(properties) > 0:
            for image_property in properties:
                context['public_image_list'] = context['public_image_list'].filter(properties__icontains=image_property)
        #filter public list based on searches

        # populate a user's private image list
        try:
            context['private_image_list'] = Image.objects.filter(owner=self.request.user, private=True).order_by("-created")
            if search_term != '': context['private_image_list'] = context['private_image_list'].filter(title__icontains=search_term)
            if len(colors) > 0:
                for color in colors:
                    context['private_image_list'] = context['private_image_list'].filter(colors__icontains=color)
            if len(properties) > 0:
                for image_property in properties:
                    context['private_image_list'] = context['private_image_list'].filter(properties__icontains=image_property)
        except Exception as e:
            print(e)
        
        return context


@method_decorator(login_required, name='dispatch')
class ImageCreateView(CreateView):
    model = Image
    fields = ['title', 'photo', 'private',]
    template_name = 'images/create.html'

    def post(self, request, **kwargs):
        captcha_response = request.POST.get('g-recaptcha-response' or '')
        valid_request = False

        if captcha_response != '':
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {'secret': settings.GOOGLE_RECAPTCHA_SECRET,'response': captcha_response})
            if response.json()['success']:
                valid_request = True
        
        if valid_request:
            return super(ImageCreateView, self).post(request, **kwargs)
        else:
            return super(ImageCreateView, self).get(request)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(ImageCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('images:home')


@method_decorator(login_required, name='dispatch')
class ImageDeleteView(DeleteView):
    model = Image
    template_name = 'images/delete.html'
    # success_url = '/'

    def get_success_url(self):
        return reverse('images:home')

    def post(self, request, pk, **kwargs):
        # allow delete if user is the image owner
        if Image.objects.get(pk=pk).owner == request.user:
            return super(ImageDeleteView, self).post(request, **kwargs)
        
        return super(ImageDeleteView, self).get(request, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ImageDeleteView, self).get_context_data(*args, **kwargs)
        if kwargs['object'].owner != self.request.user:
            context['unauthorized'] = True
        return context
