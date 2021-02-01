from django import forms
from django.forms import widgets
from captcha.fields import CaptchaField


class LoginUserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=15, min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               required=True)
    password = forms.CharField(label="密\xa0\xa0 码",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               required=True)
    captcha = CaptchaField(label="验证码", required=True)
    widget = widgets.Textarea()


class EchartsForm(forms.Form):
    hours = (
        ('1', '1小时内'),
        ('2', '2小时内'),
        ('3', '3小时内'),
        ('4', '4小时内'),
        ('5', '5小时内'),
        ('6', '6小时内'),
    )
    ptypes = (
        ('heatmap', "热力图"),
        ('normal', "分布图"),
    )
    hour = forms.ChoiceField(label="时间", choices=hours, required=True)
    ptype = forms.ChoiceField(label="类型", choices=ptypes, required=True)

class RegisterUserForm(forms.Form):
    gender = (
        ('male', 'M'),
        ('female', 'F'),
    )
    username = forms.CharField(label="用户名", max_length=15, min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               required=True)
    password1 = forms.CharField(label="输入密码", max_length=15, min_length=5,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                required=True)
    password2 = forms.CharField(label="确认密码", max_length=15, min_length=5,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                required=True)
    sex = forms.ChoiceField(label="性别", choices=gender, required=True)

