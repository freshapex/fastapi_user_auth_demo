# 业务模型的核心，设计好
'''
fastapi-amis-admin由三部分核心模块组成,其中amis, fastapi-sqlmodel-crud 可作为独立模块单独使用,amis_admin基于前者共同构建.

    amis: 基于baidu amis的pydantic数据模型构建库,用于快速生成/解析amis json 数据.
    fastapi-sqlmodel-crud: 基于FastAPI+SQLModel, 用于快速构建Create,Read,Update,Delete通用API接口.
    amis_admin: 启发自Django-Admin, 结合amis+fastapi-sqlmodel-crud, 用于快速构建Web Admin管理后台.

FastAPI-User-Auth是一个基于 FastAPI-Amis-Admin 的应用插件,与FastAPI-Amis-Admin深度结合,为其提供用户认证与授权.
 本系统采用的RBAC模型如下, 你也可以根据自己的需求进行拓展.
 参考: 权限系统的设计

'''



from sqlmodel import SQLModel,Relationship
from typing  import Optional,List
from sqlalchemy import Column, String
from fastapi_amis_admin.models.fields import Field  # Field 从amis_admin.models.field 导入，有一些设置
from fastapi_amis_admin.amis.components import InputRichText, InputImage, ColumnImage
from fastapi_amis_admin.models.enums import IntegerChoices

from fastapi_user_auth.auth.models import User

from datetime import datetime,date


class CityBase(SQLModel):

    id:Optional[int] = Field(default=None, primary_key=True, nullable=False)
    cityname: Optional[str] = Field(title='城市名', sa_column=Column(String(100), unique=True, index=True, nullable=False))
    province : Optional[str] = Field(title='省份', max_length=20,index=True)  # 可以更改成下拉菜单
    telephone : Optional[str] =Field(title='电话', max_length=20)
    tax : Optional[str] = Field(title='传真', max_length=20)
    cityaddress : Optional[str] = Field(title='地址', max_length=100)

    content : Optional[str] = Field(default='', title='城市简介', amis_form_item='textarea')
    # content : Optional[str] = Field(..., title='CityIntro', amis_form_item=InputRichText())
    # user_id:Optional[int] = Field(default=None)
    # user_id: int = Field(default=None, foreign_key="auth_user.id", title='UserId')
    # user: User = Relationship()
    class Config:
        use_enum_values = True


## ShCity
class ShCity(CityBase,table=True):
    __tablename__ = 'shcity'
    # id:Optional[int] = Field(default=None,primary_key=True)

    friendcity:List["Friendship"] = Relationship(back_populates="shcity")

    user_id: int = Field(default=None, foreign_key="auth_user.id", title='用户Id')
    user: User = Relationship()
    # class Config:
    #     use_enum_values = True


## FriendCity
class FriendCity(CityBase,table=True):
    __tablename__ = 'friendcity'
    # id: Optional[int] = Field(default=None,primary_key=True)

    shcity:List["Friendship"] = Relationship(back_populates="friendcity")

    user_id: int = Field(default=None, foreign_key="auth_user.id", title='用户Id')
    user: User = Relationship()

    class Config:
        use_enum_values = True


######### 
######### friendship
class FriendshipStatus(IntegerChoices):
    pre_sign = 0, '未签，准备结对'
    signed = 1, '已签，关系存续中'
    hanged = 2, '还未解除，但准备解除'
    disabled = 3, '已解除友城关系'


class Friendship(SQLModel,table=True):
    __tablename__ = 'friendship'
    id:Optional[int] = Field(default=None,primary_key=True,nullable=False)

    filename : Optional[str] = Field(default='', title='协议名称', amis_form_item='textarea')   
    shcitysignman : Optional[str] = Field(title='上海方签署人', max_length=20)
    friendcitysignman : Optional[str] =Field(title='外城签署人', max_length=20)    
    sign_time: Optional[date] = Field(default_factory=date.today, title='签署日期')    
    modify_time: Optional[date] = Field(default_factory=date.today, title='修订日期')
    end_time: Optional[date] = Field(default_factory=date.today, title='结束日期')
    # status: Optional[FriendshipStatus] = Field(FriendshipStatus.signed, title='status')  

    # shcity_id: Optional[int] = Field(default=None,foreign_key="shcity.id",primary_key=True) 
    # 不能像上面一样增加primary_key ，此处的Field不同于SQLModel 中的Field 否则会在增加记录时报错“已经有key”
    shcity_id: Optional[int] = Field(default=None, foreign_key="shcity.id", title='上海城区ID') 
    friendcity_id: Optional[int] = Field(default=None,foreign_key="friendcity.id", title='外城Id')

    status: Optional[FriendshipStatus] = Field(FriendshipStatus.signed, title='关系状态')  
    
    shcity:ShCity = Relationship(back_populates="friendcity")
    friendcity:FriendCity = Relationship(back_populates="shcity")



