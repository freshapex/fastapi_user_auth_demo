from fastapi import APIRouter,Depends
from fastapi_amis_admin.amis.components import PageSchema
from fastapi_amis_admin.amis_admin import admin
from typing import Union,Optional,List

from .admin import ShcityAdmin,FriendcityAdmin,FriendshipAdmin
from core.adminsite import site


router = APIRouter(prefix="",tags=["Friendship"])

@site.register_admin
class FriendAPP(admin.AdminApp):
    page_schema: Union[PageSchema, str] = PageSchema(label="友城关系应用",icon="")
    router_prefix: Optional[str] = "/friendship"

    def __init__(self, app: "admin.AdminApp"):
        super().__init__(app)
        self.register_admin(ShcityAdmin,FriendcityAdmin,FriendshipAdmin)


