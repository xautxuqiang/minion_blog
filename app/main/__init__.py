#coding=utf-8
from flask import Blueprint

main = Blueprint('main', __name__)

from . import errors, views
from ..models import Permission

#把Permission加入上下文处理器，让变量全局可访问
@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)
