from django.db import models
from django.utils import timezone

#数値型の最小と最大を指定する
from django.core.validators import MinValueValidator,MaxValueValidator

#aggregateで平均を計算する時用
from django.db.models import Avg

#ユーザーモデルと1対多のリレーションを組む
#https://noauto-nolife.com/post/django-foreignkey-user/
from django.contrib.auth.models import User



#カテゴリ(1)
class Category(models.Model):

    # id(連番)
    name    = models.CharField(verbose_name="名前", max_length=100)
    icon    = models.ImageField(verbose_name="カテゴリアイコン",upload_to="sns/category/icon/")

    #TODO:ここにカテゴリのIDを文字列に直すモデルクラスのメソッドを追加する。
    def str_id(self):
        return str(self.id)

    def __str__(self):
        return self.name


#タグ(多)
class Tag(models.Model):

    #公園の特性(遊具がある、池があるなど)
    name    = models.CharField(verbose_name="名前", max_length=100)

    def __str__(self):
        return self.name

#公園(多)
class Park(models.Model):

    #id (連番)数値型

    #このcategoryはCategoryのidが記録される。
    category    = models.ForeignKey(Category,verbose_name="カテゴリ",on_delete=models.PROTECT)

    #TODO:タグとのManyToManyFieldを作る
    #タグの未指定を許す場合、ここでblank=Trueを書く
    tag         = models.ManyToManyField(Tag,verbose_name="タグ",blank=True)

    name        = models.CharField(verbose_name="名前",max_length=100)
    dt          = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    lat         = models.DecimalField(verbose_name="緯度",max_digits=9, decimal_places=6)
    lon         = models.DecimalField(verbose_name="経度",max_digits=9, decimal_places=6)


    #レビュー数を表示するメソッド
    def amount_review(self):
        #この公園に対してのレビューのみ絞り込む。.count()で数をカウントする
        return Review.objects.filter(park=self.id).count()


    #レビューの平均点を返す
    def avg_star_score(self):
        #紐づくレビューを全て取り出す。aggregateを使って取り出したモデルオブジェクトの集計(SumやAvg)をする
        reviews  = Review.objects.filter(park=self.id).aggregate(Avg("star"))
        print(reviews)

        if reviews["star__avg"]:
            return int(reviews["star__avg"]) * " "
        else:
            return 0 * " "

    #レビューの平均点の小数部を返す
    def avg_star_few(self):
        #この公園に紐付いたレビューを集計(aggregate)する。starで平均を集計する
        reviews = Review.objects.filter(park=self.id).aggregate(Avg("star"))
        #reviews は辞書型 { "star__avg":3.5 }

        avg     = reviews["star__avg"]

        #平均スコアなしの場合は0を返す(星を描画しないようにする)
        if not avg:
            return 0

        #少数指定の場合、小数部を表示(0~0.4は0、0.4~0.6は0.5、0.6~1は1と表現)
        few     = avg - int(avg)

        if 0.4 > few and few >= 0:
            return 0
        elif 0.6 > few and few >= 0.4:
            return 0.5
        else:
            return 1 


    def __str__(self):
        return self.name


class Review(models.Model):

    # 公園(1)とレビュー(多)の関係
    park    = models.ForeignKey(Park,verbose_name="レビュー対象の公園",on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    comment = models.CharField(verbose_name="コメント",max_length=500)
    star    = models.IntegerField(verbose_name="星の数",validators=[MinValueValidator(1),MaxValueValidator(5)])

    # ユーザーモデルと1対多のリレーションを組む
    user    = models.ForeignKey(User, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    #DTLでループさせるため、星の数だけスペース文字列を作る
    def star_range(self):
        return " " * self.star



#ユーザーモデルに紐づく1対1フィールド
class UserDetail(models.Model):

    user        = models.OneToOneField(User, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    nickname    = models.CharField(verbose_name="ニックネーム",max_length=20)
    description = models.CharField(verbose_name="自己紹介文",max_length=500)

    icon        = models.ImageField(verbose_name="アイコン",upload_to="sns/user_detail/icon/",null=True,blank=True)






