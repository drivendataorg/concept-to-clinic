from django.shortcuts import render


def open_image(request):
    return render(request, 'open_image.html')


def detect_and_select(request):
    return render(request, 'detect_and_select.html')


def annotate_and_segment(request):
    return render(request, 'annotate_and_segment.html')


def report_and_export(request):
    return render(request, 'report_and_export.html')
