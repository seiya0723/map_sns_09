from django.shortcuts import render,redirect
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from .models import Park,Category,Tag,Review,UserDetail
from .forms import ParkForm,CategorySearchForm,TagSearchForm,ReviewForm,UserForm,UserDetailForm

from django.db.models import Q
from django.db.models import Count

#LoginRequiredMixinにより未認証ユーザーはこのIndexViewが実行されず。ログインページへリダイレクトされる。
class IndexView(LoginRequiredMixin,View):

    #重複を除去する。(モデルオブジェクトから重複を取り除く)
    def distinct(self,obj):
        id_list     = [] # モデルオブエジェクトのidを記録する
        new_obj     = [] # 重複を除去した新しいモデルオブジェクトのリスト

        #モデルオブジェクトのリストから1つ取り出す。
        for o in obj:
            # idがid_listに含まれている場合
            if o.id in id_list:
                #次のループに行く(for文で使える構文、この命令を実行すると以降の処理はスキップして次のループに行く)
                continue

            #モデルオブジェクトのidを記録する
            id_list.append(o.id)
            #モデルオブジェクトを新しいリストに入れる
            new_obj.append(o)

        return new_obj

    def get(self, request, *args, **kwargs):

        context = {}
        context["categories"]   = Category.objects.all()
        context["tags"]         = Tag.objects.all()

        #TODO:ここで公園を検索するバリデーションを行う。

        #公園名の検索
        query   = Q()


        #パラメータの中にsearchがあるかどうかをチェック
        if "search" in request.GET:
            #searchを取り出す
            search      = request.GET["search"]

            raw_words   = search.replace("　"," ").split(" ")
            words       = [ w for w in raw_words if w != "" ]

            for w in words:
                query &= Q(name__contains=w)


        #カテゴリの検索
        form    = CategorySearchForm(request.GET)

        #カテゴリ検索を実現するには、入力値が数値であること、Categoryモデルに存在するidであることを確認する必要がある
        if form.is_valid():
            cleaned = form.clean()
            query &= Q(category=cleaned["category"].id)


        #多対多の検索
        form    = TagSearchForm(request.GET)

        if form.is_valid():
            # request.GET["tag"] = 全て文字列型 クエリパラメータ(クエリストリング)
            # cleaned = { "tag":["id","id",] }
            cleaned         = form.clean()
            selected_tags   = cleaned["tag"] 
            
            """
            #タグ未指定による検索を除外する(タグ未選択でもバリデーションOKになるので、ここで空リストを除外する)
            if selected_tags:
                # 指定したタグのいずれかを含む検索(重複あり)
                query &= Q(tag__in=selected_tags)
                
            for selected_tag in selected_tags:
                query &= Q(tag__in=selected_tag)
            """

            #公園で検索した結果
            parks       = Park.objects.filter(query).order_by("-dt")

            #タグ検索をする(中間テーブル未使用、指定したタグを全て含む)
            for tag in selected_tags:
                #絞り込みした結果の一時的に格納するリスト
                new_parks   = []

                #内包表記でも可
                for park in parks:
                    if tag in park.tag.all():
                        #指定したタグを含むモデルオブジェクトをnew_parksにアペンド
                        new_parks.append(park)

                #次の絞り込みで使用するため、parksへ代入(上書き)
                parks       = new_parks

            print(parks)
            context["parks"]    = parks

            """
            中間テーブルを使用する方法(概要)

            1、中間テーブルのモデルでタグ検索
            2、Parkモデルでqueryを使って検索
            3、1と2を突き合わせる

            このやり方ではかえって難しいため、今回はあえて見送った。
            今回のやり方はループを繰り返すだけで実現でき、distinctも不要なので更にシンプルに実現できる
            """
        else:

            #ここでループしてモデルオブジェクト比較し、重複除去をする。
            context["parks"]    = Park.objects.filter(query).order_by("-dt")

        return render(request, "sns/index.html", context)

    def post(self, request, *args, **kwargs):

        form    = ParkForm(request.POST)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print("バリデーションNG")
            print(form.errors)

        return redirect("sns:index")

index   = IndexView.as_view()

#公園の個別ページ
class SingleView(LoginRequiredMixin,View):
    def get(self, request, pk, *args, **kwargs):

        #TODO:ここで公園を一意に特定する必要がある。(Parkのidを取得する)←URL引数を使って(URLの中に型を指定した引数をViewsに与える)
        context = {}

        #一意に特定しているので、単数のモデルオブジェクトを返却する.first()を使用する
        context["park"] = Park.objects.filter(id=pk).first()

        #TIPS:これで最新データの取り出し方(単一)
        #newest = Park.objects.order_by("-dt").first()


        # 投稿したコメントを取得
        context["reviews"]  = Review.objects.filter(park=pk).order_by("-dt")

        return render(request,"sns/single.html",context)

    def post(self, request, pk, *args, **kwargs):

        print(request.POST)
        #TODO:pkをrequest.POSTに含めて保存する
        #request.POST["park"] = pk #これはエラー

        #イミュータブル(書き換えできない)なオブジェクトであるrequestは一旦コピーをした上で、書き換えをする。
        copied          = request.POST.copy()
        copied["park"]  = pk
        copied["user"]  = request.user.id
        #copiedにはstarとcommentとparkとuserが含まれている

        form    = ReviewForm(copied)

        if form.is_valid():
            print("保存")
            form.save()

        return redirect("sns:single", pk)

single  = SingleView.as_view()


#TODO:ここにfirst_nameとlast_nameを編集するViewを作る
class UserEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        context                 = {}
        context["user"]         = User.objects.filter(id=request.user.id).first()
        context["user_detail"]  = UserDetail.objects.filter(user=request.user.id).first()


        return render(request, "sns/user.html", context)

    def post(self, request, *args, **kwargs):

        #TODO:編集対象のUserを特定し、バリデーションして保存
        user    = User.objects.filter(id=request.user.id).first()

        form    = UserForm(request.POST,instance=user)

        if not form.is_valid():
            print(form.errors)
            return redirect("sns:user_edit")

        print("ユーザーの姓名保存")
        form.save()


        #TODO:編集対象のUserDetailを特定する
        user_detail = UserDetail.objects.filter(user=request.user.id).first()

        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        #form            = UserDetailForm(copied,instance=user_detail)

        #画像をアップロードする
        form            = UserDetailForm(copied,request.FILES,instance=user_detail)

        if not form.is_valid():
            print(form.errors)
            return redirect("sns:user_edit")

        print("ユーザーの詳細保存")
        form.save()


        return redirect("sns:user_edit")

user_edit = UserEditView.as_view()

