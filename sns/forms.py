from django import forms

from .models import Park,Review,UserDetail

#ユーザーモデルのフォームを作る
from django.contrib.auth.models import User





class ParkForm(forms.ModelForm):

    class Meta:
        model   = Park
        fields  = ["category","name","tag","lat","lon"]

class CategorySearchForm(forms.ModelForm):
    class Meta:
        # ForeignKeyフィールドを使うことで、1対多の1側に存在するidであることをチェックできる。
        model   = Park
        fields  = ["category"]

class TagSearchForm(forms.ModelForm):

    class Meta:
        model   = Park
        fields  = ["tag"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model   = Review
        fields  = ["park","comment","star","user"] #userフィールドをバリデーションする


#ユーザーの姓名を書き換える
class UserForm(forms.ModelForm):
    class Meta:
        model   = User
        fields  = ["first_name","last_name"]


class UserDetailForm(forms.ModelForm):
    class Meta:
        model   = UserDetail
        fields  = ["user","nickname","description","icon"]




