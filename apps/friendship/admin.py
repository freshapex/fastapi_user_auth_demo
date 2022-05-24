
from datetime import date
from fastapi import HTTPException,status
from fastapi_amis_admin.amis_admin import admin
from fastapi_amis_admin.amis.components import PageSchema,ColumnImage,TableColumn
from fastapi_amis_admin.crud.schema import Paginator,BaseApiOut
from starlette.requests import Request
from sqlmodel.sql.expression import Select,select
from sqlmodel import SQLModel,or_,and_
from pydantic import BaseModel
from typing import Optional,List,Dict,Any,Union,Type

from .models import FriendshipStatus, ShCity,FriendCity,Friendship
from fastapi_user_auth.auth.models import User,Role,UserRoleLink


class ShcityAdmin(admin.ModelAdmin):
    group_schema: Union[PageSchema, str] = None
    page_schema: Union[PageSchema, str] = PageSchema(label="上海城区",icon="")

    model: Type[SQLModel] = ShCity

    list_display = [ShCity.cityname,ShCity.province,ShCity.content,ShCity.cityaddress,User.username]
    search_field = [ShCity.cityname,ShCity.province,ShCity.content,ShCity.cityaddress,User.username]

    link_models= [Friendship,FriendCity]  # 最好设定，才好查找

    # 自定义查询选择器
    async def get_select(self, request: Request) -> Select:
        sel = await super().get_select(request)
        return sel.join(User, isouter=True)


    # 权限验证
    async def has_page_permission(self, request: Request) -> bool:
        return True

    async def has_list_permission(
            self, request: Request, paginator: Paginator,
            filter: BaseModel = None, **kwargs
    ) -> bool:
        # 用户不需登录,不可按标题过滤,并且最多每页最多只能查看10条数据.
        # return bool(
        #     await self.site.auth.requires(response=False)(request)
        #     or (paginator.perPage <= 10 and filter.title == '')
        # )
        return True

    async def has_create_permission(
            self, request: Request, data: BaseModel,**kwargs
    ) -> bool:
        # 用户已登录,并且注册时间大于3天,才可以发布文章
        # return bool(
        #     await self.site.auth.requires(response=True)(request)
        #     and request.user.id==
        #     and request.user.create_time < datetime.now() - timedelta(days=3)
        # )
        # 用户已登录,
        if await self.site.auth.requires(response=False)(request):
            # if item_id is None:
            #     return True
            async with self.site.db.session_maker() as session:
                # 管理员可以创建.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,上海用户可以创建.
                if await request.user.has_role(['shusers'],session):
                    return True
                # result = await session.execute(
                #     select(ShCity.id).where(
                #         ShCity.id == item_id[0], ShCity.user_id == request.user.id
                #     ).limit(1)
                # )
            # if result.first():
            #     return True
        return False
    
    async def on_create_pre(
            self, request: Request, obj: BaseModel, **kwargs
    ) -> Dict[str, Any]:
        data = await super().on_create_pre(request, obj, **kwargs)
        # 创建新ShCity时,设置当前用户为ShCity的user_id
        data['user_id'] = request.user.id
        data['province'] = "上海市"
        return data

    async def has_delete_permission(
            self, request: Request, item_id: List[str],**kwargs   # 特别注意has_delete_permission 等权限函数的参数
    ) -> bool:
        # 必须管理员才可以删除记录.
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以删除.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,上海用户可以删除ShCity中user_id 与自己user.id 相同的ShCity，且一次只能删除一个
                result = await session.scalar(select(ShCity.id).where(ShCity.id==item_id[0],ShCity.user_id == request.user.id))
                if result is None:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="只能删除用户自己管理的城市")
                    # return BaseApiOut(status=status.HTTP_403_FORBIDDEN, msg='只能删除用户自己管理的城市')  不能这样设置,否则报错
                else:
                    result_friendship_id = await session.scalar(select(Friendship.id).where(Friendship.shcity_id==item_id[0]))
                    if result_friendship_id:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="还有友城关系没有删除，请先删除涉及本城市的友城关系")
                    else:
                        return True
        return False 
        

    async def has_update_permission(
            self, request: Request, item_id: List[str],
            data: BaseModel, **kwargs
    ) -> bool:
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以修改全部记录, 并且可以批量修改.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,只能修改shcity中user_id为用户user.id的Shcity信息,并且不可批量修改.
                result = await session.execute(
                    select(ShCity.id).where(
                        ShCity.id == item_id[0], ShCity.user_id == request.user.id
                    ).limit(1)
                )
            if result.first():
                return True
        return False

    



class FriendcityAdmin(admin.ModelAdmin):
    group_schema: Union[PageSchema, str] = None
    page_schema: Union[PageSchema, str] = PageSchema(label="外地城市",icon="")

    model: Type[SQLModel] = FriendCity

    list_display = [FriendCity.cityname,FriendCity.province,FriendCity.content,FriendCity.cityaddress,User.username]
    search_field = [FriendCity.cityname,FriendCity.province,FriendCity.content,FriendCity.cityaddress,User.username]

    link_models= [Friendship,FriendCity]  # 最好设定，才好查找

    # 自定义查询选择器
    async def get_select(self, request: Request) -> Select:
        sel = await super().get_select(request)
        return sel.join(User, isouter=True)

    # 权限验证
    async def has_page_permission(self, request: Request) -> bool:
        return True

    async def has_list_permission(
            self, request: Request, paginator: Paginator,
            filter: BaseModel = None, **kwargs
    ) -> bool:
        
        return True

    async def has_create_permission(
            self, request: Request, data: BaseModel,**kwargs
    ) -> bool:
        # 用户已登录
        if await self.site.auth.requires(response=False)(request):
            
            async with self.site.db.session_maker() as session:
                # 管理员可以创建.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,外城用户可以创建.
                if await request.user.has_role(['fcusers'],session):
                    return True
            
        return False

    async def has_delete_permission(
            self, request: Request, item_id: List[str],**kwargs   # 特别注意has_delete_permission 等权限函数的参数
    ) -> bool:
        # 必须管理员才可以删除记录.
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以删除.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,外城用户可以删除FriendCity中user_id 与自己user.id 相同的FriendCity，且一次只能删除一个
                
                result = await session.scalar(select(FriendCity.id).where(FriendCity.id==item_id[0],FriendCity.user_id == request.user.id))
                if result is None:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="只能删除用户自己管理的城市")
                else:
                    result_friendship_id = await session.scalar(select(Friendship.id).where(Friendship.friendcity_id==item_id[0]))
                    if result_friendship_id:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="还有友城关系没有删除，请先删除涉及本城市的友城关系")
                    else:
                        return True
        return False 
        

    async def has_update_permission(
            self, request: Request, item_id: List[str],
            data: BaseModel, **kwargs
    ) -> bool:
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以修改全部记录, 并且可以批量修改.
                if await request.user.has_role(['admin'], session):
                    return True
                # 非管理员,只能修改friendcity中user_id为用户user.id的Friendcity信息,并且不可批量修改.
                result = await session.execute(
                    select(FriendCity.id).where(FriendCity.id == item_id[0], FriendCity.user_id == request.user.id).limit(1))
            if result.first():
                return True
        return False

    async def on_create_pre(
            self, request: Request, obj: BaseModel, **kwargs
    ) -> Dict[str, Any]:
        data = await super().on_create_pre(request, obj, **kwargs)
        # 创建新FriendCity时,设置当前用户为FriendCity的user_id
        data['user_id'] = request.user.id
        return data


class FriendshipAdmin(admin.ModelAdmin):
    group_schema: Union[PageSchema, str] = None
    page_schema: Union[PageSchema, str] = PageSchema(label="友城关系",icon="")

    model: Type[SQLModel] = Friendship

    list_display = [ShCity.cityname,FriendCity.cityname,Friendship.filename,Friendship.status,
                    Friendship.sign_time,Friendship.modify_time,Friendship.end_time,
                    Friendship.shcitysignman,Friendship.friendcitysignman]

    search_field = [ShCity.cityname,FriendCity.cityname,Friendship.filename,Friendship.status,
                    Friendship.sign_time,Friendship.modify_time,Friendship.end_time,
                    Friendship.shcitysignman,Friendship.friendcitysignman] 

    link_models= [ShCity,FriendCity]  # 最好设定，才好查找

    # 自定义查询选择器
    async def get_select(self, request: Request) -> Select:
        sel = await super().get_select(request)
        return sel.join(ShCity, isouter=True).join(FriendCity,isouter=True)

    
        # 权限验证
    async def has_page_permission(self, request: Request) -> bool:
        return True

    async def has_list_permission(
            self, request: Request, paginator: Paginator,
            filter: BaseModel = None, **kwargs
    ) -> bool:
        
        return True

    async def has_create_permission(
            self, request: Request, data: BaseModel,**kwargs
    ) -> bool:
        # 用户已登录
        if await self.site.auth.requires(response=False)(request):
            
            async with self.site.db.session_maker() as session:
                # 管理员可以创建.
                if await request.user.has_role(['admin'], session):
                    return True                

                # 非管理员,外城用户可以创建. # 具体创建条件在on_create_pre 函数判断
                if await request.user.has_role(['fcusers'],session):                               
                    return True

                # 非管理员,上海用户可以创建.# 具体创建条件在on_create_pre 函数判断
                if await request.user.has_role(['shusers'],session):  
                    return True                   
        # 如果返回异常，则页面打不开，弹出一个提示窗口”没有权限“
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="没有权限")  
        # 如果返回 False， 则可以正常打开页面，但页面没有增加按钮
        return False

    async def on_create_pre(
            self, request: Request, obj: BaseModel, **kwargs
    ) -> Dict[str, Any]:
        data = await super().on_create_pre(request, obj, **kwargs)        
        async with self.site.db.session_maker() as session:  # 调用函数，要加await 不然不会执行函数

            # 两个城市不能重复创建友城关系
            friendship_set = await session.scalar(select(Friendship).where(Friendship.shcity_id == data["shcity_id"],Friendship.friendcity_id==data["friendcity_id"]))
            if friendship_set:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="这两个城市已建立友城关系") 

            if await request.user.has_role(["admin"],session=session):
                return data
            
            # 如果上海用户，则只允许创建上海用户管理的城市与外城建立友好关系
            # request.user.has_role()
            if await request.user.has_role(["shusers"],session=session):
                # 只能基于自己创建的城市建立友城关系        
                shcity_id_from_user =  await session.scalars(select(ShCity.id).where(ShCity.user_id==request.user.id))                
                if data["shcity_id"] not in shcity_id_from_user.all():
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="只能基于自己创建的城市建立友城关系")
                else:                    
                    return data

            # 如果为外城用户，则只允许创建外城用户管理的城市与上海城区建立友好关系
            if await request.user.has_role(["fcusers"],session=session):
                # 只能基于自己创建的城市建立友城关系   scalars()才有all（）,scalar() 是一个标量    
                friendcity_id_from_user =  await session.scalars(select(FriendCity.id).where(FriendCity.user_id==request.user.id))
                if data["friendcity_id"] not in friendcity_id_from_user.all():
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="只能基于自己创建的城市建立友城关系")  
                else:
                    return data
        return None
               

    async def has_delete_permission(
            self, request: Request, item_id: List[str],**kwargs   # 特别注意has_delete_permission 等权限函数的参数
    ) -> bool:
        # 必须登陆才可以删除记录.
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以删除.
                if await request.user.has_role(['admin'], session):                    
                    return True                
            
                # 或者非管理员,上海用户可以删除Friendship中Shcity的user_id 与自己user.id 相同的Friendship，且一次只能删除一个
                if await request.user.has_role(["shusers"], session):
                    # 需要查找Friendship.id, 从后往前看，通过request.user.id==ShCity.user_id 查找 user的ShCity，
                    # 再通过Friendship.shcity_id==ShCity.id 查找 对应的Friendship
                    # 再通过Friendship.id==item_id[0] c查找Friendship里是否有对应item_id[0]的id
                    friendship_id_for_shuser = await session.scalar(select(Friendship.id).where(Friendship.id==item_id[0],Friendship.shcity_id==ShCity.id,ShCity.user_id==request.user.id))                    
                    if friendship_id_for_shuser:
                        return True
                    else:
                        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="没有权限，只可以删除自己创建的城市的友城关系")                                   

                # 非管理员,外城用户可以删除Friendship中FriendCity中user_id 与自己user.id 相同的Friendship，且一次只能删除一个
                if await request.user.has_role(["fcusers"], session):
                                    
                    friendship_id_for_fcuser = await session.scalar(select(Friendship.id).where(FriendCity.user_id==request.user.id,Friendship.friendcity_id==FriendCity.id,Friendship.id==item_id[0]))
                    if friendship_id_for_fcuser:
                        return True
                    else:
                        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="没有权限，只可以删除自己创建的城市的友城关系")                                                
            
        return False 
        

    async def has_update_permission(
            self, request: Request, item_id: List[str],
            data: BaseModel, **kwargs
    ) -> bool:
        # 必须登陆才可以更新记录.
        if await self.site.auth.requires(response=False)(request):
            if item_id is None:
                return True
            async with self.site.db.session_maker() as session:
                # 管理员可以更新.
                if await request.user.has_role(['admin'], session):                    
                        return True                
                
                # 或者非管理员,上海用户可以更新Friendship中Shcity的user_id 与自己user.id 相同的Friendship，且一次只能更新一个
                if await request.user.has_role(["shusers"], session): 

                    result_friendship_for_shuser = await session.scalar(select(Friendship.id).where(ShCity.user_id==request.user.id,Friendship.shcity_id==ShCity.id,Friendship.id==item_id[0]))
                    if result_friendship_for_shuser:
                        return True
                    else:
                        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="没有权限，只可以更新自己创建的城市的友城关系")   
                                   

                # 非管理员,外城用户可以更新Friendship中FriendCity中user_id 与自己user.id 相同的Friendship，且一次只能更新一个
                if await request.user.has_role(["fcusers"], session):                                    
                    
                    result_friendship_for_fcuser = await session.scalar(select(Friendship.id).where(FriendCity.user_id==request.user.id,Friendship.friendcity_id==FriendCity.id,Friendship.id==item_id[0]))
                    if result_friendship_for_fcuser:
                        return True
                    else:
                        raise  HTTPException(status.HTTP_401_UNAUTHORIZED,detail="没有权限，只可以更新自己创建的城市的友城关系")                                
            
        return False 

    


