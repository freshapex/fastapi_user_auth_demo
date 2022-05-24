from fastapi import FastAPI


def setup(app: FastAPI):
    # 1. 导入博客管理应用
    from . import apis as friendship
    # 2. 注册普通路由
    from .apis import router
    app.include_router(router)
    # 3. 导入定时任务
    # from . import jobs