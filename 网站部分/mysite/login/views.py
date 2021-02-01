from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import render, redirect
from . import models
from pyecharts import Geo, Style, Bar
# Create your views here.
from . import forms
import earthquakeparser.seismic_intensity as si
import pymongo
import pandas as pd
import random
import urllib
from datetime import datetime,timedelta


REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def si_detail(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    if request.method == 'GET':
        ptime = request.GET.get('time')
        client = pymongo.MongoClient('localhost', 27017)
        db = client['earthquake']
        si_col = db["earthquake_SI"]
        for item in si_col.find():
            if item['name'][0:8] == ptime:
                nitem = {}
                icol = db[item['name']]
                nitem['name'] = item['name'][10:]
                nitem['time'] = item['time']
                nitem['count'] = icol.count()
                nitem['urltime'] = item['time'][0:4] + item['time'][5:7] + item['time'][8:10]
                nitem['SIV'] = item['SI-V']
                nitem['SIIV'] = item['SI-IV']
                nitem['SIIII'] = item['SI-III']
                nitem['SIII'] = item['SI-II']
                nitem['SII'] = item['SI-I']
                nitem['SIV'] *= 100
                nitem['SIIV'] *= 100
                nitem['SIIII'] *= 100
                nitem['SIII'] *= 100
                nitem['SII'] *= 100
                nitem['SIV'] = round(nitem['SIV'], 2)
                nitem['SIIV'] = round(nitem['SIIV'], 2)
                nitem['SIIII'] = round(nitem['SIIII'], 2)
                nitem['SIII'] = round(nitem['SIII'], 2)
                nitem['SII'] = round(nitem['SII'], 2)

                '''
                nitem['SI-V'] = float('%.2f' % float(item['SI-V'])*100)
                nitem['SI-IV'] = float('%.2f' % float(item['SI-V'])*100)
                nitem['SI-III'] = float('%.2f' % float(item['SI-V'])*100)
                nitem['SI-II'] = float('%.2f' % float(item['SI-V'])*100)
                nitem['SI-I'] = float('%.2f' % float(item['SI-V'])*100)
                '''
                nitem['label'] = item['label']
                nitem['personalNum0'] = item['personalNum'][0]
                nitem['totalNum0'] = item['totalNum'][0]
                nitem['personalNum1'] = item['personalNum'][1]
                nitem['totalNum1'] = item['totalNum'][1]
                nitem['personalNum2'] = item['personalNum'][2]
                nitem['totalNum2'] = item['totalNum'][2]
                nitem['personalNum3'] = item['personalNum'][3]
                nitem['totalNum3'] = item['totalNum'][3]
                nitem['personalNum4'] = item['personalNum'][4]
                nitem['totalNum4'] = item['totalNum'][4]
                nitem['personalNum5'] = item['personalNum'][5]
                nitem['totalNum5'] = item['totalNum'][5]
                return render(request, 'function/si_result.html', {'data': nitem})

def refer(request):
    return render(request, 'login/reference.html')

def tweets(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    client = pymongo.MongoClient('localhost', 27017)
    db = client['earthquake']
    si_col = db["earthquake_SI"]
    datalist = []
    for item in si_col.find():
        nitem = {}
        nitem['name'] = item['name'][10:]
        nitem['time'] = item['time']
        nitem['dbname'] = item['name']
        datalist.append(nitem)
        print(nitem)
    paginator = Paginator(datalist, 10)
    if request.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page')
        try:
            items = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            items = paginator.page(paginator.num_pages)

    return render(request, 'function/tweets.html', {'items': items})

def tweet_detail(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    if request.method == 'GET':
        dbname = request.GET.get('dbname')
        dbname = urllib.parse.unquote(dbname)
        print('dbname ', dbname)
        info = {}
        info['dbname'] = dbname
        client = pymongo.MongoClient('localhost', 27017)
        db = client['earthquake']
        col = db[dbname]
        dlist = []
        for item in col.find():
            nitem = {}
            nitem['pic'] = random.randint(1, 15)
            nitem['user_name'] = item['user_name']
            nitem['user_blog'] = item['user_blog']
            nitem['t_time'] = item['t_time']
            nitem['content'] = item['content']
            nitem['lon'] = round(item['epi_lon'], 2)
            nitem['lat'] = round(item['epi_lat'], 2)
            dlist.append(nitem)
        paginator = Paginator(dlist, 8)
        if request.method == "GET":
            # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
            page = request.GET.get('page')
            try:
                items = paginator.page(page)
            # todo: 注意捕获异常
            except PageNotAnInteger:
                # 如果请求的页数不是整数, 返回第一页。
                items = paginator.page(1)
            except InvalidPage:
                items = paginator.page(1)
            except EmptyPage:
                # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
                items = paginator.page(paginator.num_pages)
        return render(request, "function/tweet_list.html", {'items': items,'info':info})

def si_list(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    client = pymongo.MongoClient('localhost', 27017)
    db = client['earthquake']
    si_col = db["earthquake_SI"]
    datalist = []
    for item in si_col.find():
        nitem = {}
        nitem['name'] = item['name'][10:]
        nitem['time'] = item['time']
        nitem['urltime'] = item['time'][0:4] + item['time'][5:7] + item['time'][8:10]
        nitem['label'] = item['label']
        datalist.append(nitem)
        print(nitem)
    paginator = Paginator(datalist, 10)
    if request.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page')
        try:
            items = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            items = paginator.page(paginator.num_pages)
    return render(request, "function/SI_views.html", {'items': items})

def index(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    return render(request, 'login/index.html')

def time_distribution(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    if request.method == 'GET':
        ptime = request.GET.get('time')
        client = pymongo.MongoClient('localhost', 27017)
        db = client['earthquake']
        col = db['earthquake_SI']
        for item in col.find():
            if item['name'][0:8] == ptime:
                start_time = item['time']
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                personList = item['personalNum']
                totalList = item['totalNum']
                timeIndex = []
                for i in range(6):
                    start_time += timedelta(hours=1)
                    timeIndex.append(start_time)
                # style = Style(title_pos="center",
                #               width=1200, height=700)
                bar = Bar('时间分布图',  width=1200, height=700)
                bar.add('个人用户', timeIndex, personList, mark_point=["max", "min"], is_stack=True)
                bar.add('微博总数', timeIndex, totalList, mark_point=["max", "min"], is_stack=True)
                context = dict(
                    myechart=bar.render_embed(),
                    host=REMOTE_HOST,
                    script_list=bar.get_js_dependencies()
                )
                return render(request, "function/echart_base.html", context)

def timeBar(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    client = pymongo.MongoClient('localhost', 27017)
    db = client['earthquake']
    si_col = db["earthquake_SI"]
    datalist = []
    for item in si_col.find():
        nitem = {}
        nitem['name'] = item['name'][10:]
        nitem['time'] = item['time']
        nitem['urltime'] = item['time'][0:4] + item['time'][5:7] + item['time'][8:10]
        datalist.append(nitem)
        print(nitem)
    paginator = Paginator(datalist, 10)
    if request.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page')
        try:
            items = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            items = paginator.page(paginator.num_pages)
    return render(request, "function/time_distribute.html", {'items': items})

def geo_echarts(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    if request.method == 'GET':
        ptime = request.GET.get('time')
        ptype = request.GET.get('type')
        phour = request.GET.get('hour')
        client = pymongo.MongoClient('localhost', 27017)
        db = client['earthquake']
        col = db['geo_'+ptime]
        lon = []
        lat = []
        value = []
        cities = []
        print(col.count())
        for item in col.find():
            if item['index'] < int(phour):
                lon.append(item['lon'])
                lat.append(item['lat'])
                cities.append(item['city'])
                value.append(item['value'])

        style = Style(title_color="#fff", title_pos="center",
                      width=1000, height=800, background_color="#404a59")

        df_dic = {'lon': lon, 'lat': lat, 'city': cities, 'value': value}
        df = pd.DataFrame(df_dic)
        print(df)
        attr = list(df['city'])
        value = list(df['value'])
        geo_coords = {df.iloc[i]['city']: [df.iloc[i]['lat'], df.iloc[i]['lon']] for i in range(len(df))}
        if ptype == "0":
            # normal
            total_geo = Geo(ptime + '地震' + str(phour) + '小时内分布图', **style.init_style)
            total_geo.add("", attr, value, visual_range=[1, 10], symbol_size=5,
                          visual_text_color="#fff",
                          is_visualmap=True, maptype='china', visual_split_number=10,
                          geo_cities_coords=geo_coords)
        elif ptype == "1":
            # heatmap
            total_geo = Geo(ptime+'地震'+str(phour)+'小时内热力分布图', **style.init_style)
            total_geo.add("", attr, value, visual_range=[1, 10], symbol_size=5,
                           visual_text_color="#fff", type="heatmap",
                           is_visualmap=True, maptype='china', visual_split_number=10,
                           geo_cities_coords=geo_coords)

        context = dict(
            myechart=total_geo.render_embed(),
            host=REMOTE_HOST,
            script_list=total_geo.get_js_dependencies()
        )
        return render(request, "function/echart_base.html", context)

def geo_img(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    client = pymongo.MongoClient('localhost', 27017)
    db = client['earthquake']
    si_col = db["earthquake_SI"]
    datalist = []
    for item in si_col.find():
        nitem = {}
        nitem['name'] = item['name'][10:]
        nitem['time'] = item['time']
        nitem['urltime'] = item['time'][0:4] + item['time'][5:7] + item['time'][8:10]
        datalist.append(nitem)
        print(nitem)
    paginator = Paginator(datalist, 10)
    if request.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page')
        try:
            items = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            items = paginator.page(paginator.num_pages)
    return render(request, "function/geo_img.html", {'items': items})

def register(request):
    if request.method == "POST":
        register_form = forms.RegisterUserForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            pwd1 = register_form.cleaned_data['password1']
            pwd2 = register_form.cleaned_data['password2']
            user_sex = register_form.cleaned_data['sex']
            if pwd1 == pwd2:
                if models.User.objects.filter(name=username):
                    message = "用户名已存在！"
                    return render(request, 'login/register.html', {'register_form': register_form, 'message': message})
                else:
                    try:
                        new_user = models.User()
                        new_user.name = username
                        new_user.password = pwd1
                        new_user.sex = user_sex
                        new_user.save()
                        return redirect('/index/')
                    except Exception as e:
                        return render(request, 'login/register.html', {'register_form': register_form, 'message': str(e)})
            else:
                message = '两次密码不一致'
                return render(request, 'login/register.html', {'message': message})
        else:
            message = '用户名不能为空'
            return render(request, 'login/register.html', {'message': message})
    register_form = forms.RegisterUserForm()
    return render(request, 'login/register.html', {'register_form': register_form})

def login(request):
    if request.method == "POST":
        login_form = forms.LoginUserForm(request.POST)
        message = ""
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect("/index/")
                else:
                    message = '密码错误'
            except:
                message = "用户名不存在"
        return render(request, 'login/login.html', locals())
    login_form = forms.LoginUserForm()
    return render(request, 'login/login.html', {'login_form': login_form})

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    return render(request, "login/index.html", {'message': '注销成功！'})

