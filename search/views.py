from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

import math
import QuerySearch

import json

# Create your views here.

def index(request):
    return render(request,'search/index.html')


def results(request):
    referer = request.META.get('HTTP_REFERER')
    query = request.GET.get('query', '')
    page = int(request.GET.get('page', 1))
    if query == '':
        return HttpResponse('Invalid query.')
    if page <= 0:
        return HttpResponse('Invalid Page.')

    #valid query
    numofresults, qSearchRet = QuerySearch.engineSearch(query, page - 1)
    resultlist = []
    for item in qSearchRet:
        temp = {'title': item[2], 'url': item[1], 'description': item[3]}
        resultlist.append(temp)
    
    numofpages = math.ceil(numofresults/10.0)
    

    ##### page numbers at bottom
    pagedivpagesbefore = []
    pagedivpagesafter = []
    pagesinsertedbefore = 0
    pagesinsertedafter = 0
    pagesinserted = 0
    for i in range (page - 2, page):
        if i < 1:
            continue
        pagedivpagesbefore.append(i)
        pagesinsertedbefore+=1
        pagesinserted+=1
    for i in range(page + 1, page + 3):
        if i > numofpages:
            continue
        pagedivpagesafter.append(i)
        pagesinsertedafter+=1
        pagesinserted+=1
    if pagesinserted < 4:
        if pagesinsertedafter > pagesinsertedbefore:
            for i in range(page + pagesinsertedafter + 1, page + pagesinsertedafter + 3):
                if pagesinserted == 4:
                    break
                if i <= numofpages:
                    pagedivpagesafter.append(i)
                    pagesinserted+=1
    if pagesinserted < 4:
        if pagesinsertedbefore > pagesinsertedafter:
            for i in range(page - pagesinsertedbefore - 1, page - pagesinsertedbefore - 3, -1):
                if pagesinserted == 4:
                    break
                if i > 1:
                    pagedivpagesbefore.insert(0,i)
                    pagesinserted+=1
    #########

                    
    context = { 'query': query,
                'page': page,
                'results': resultlist,
                'numofpages': numofpages,
                'numofresults': numofresults,
                'pagedivpagesbefore': pagedivpagesbefore,
                'pagedivpagesafter': pagedivpagesafter
        }

    return render(request, 'search/results.html', context)

def suggestions(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        
        #call function that get suggestions based on term
        suggestions = QuerySearch.getSuggestion(q)
        results = []
        for idx, suggestion in enumerate(suggestions):
            my_json = {}
            my_json['id'] = idx
            my_json['label'] = suggestion
            my_json['value'] = suggestion
            results.append(my_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
