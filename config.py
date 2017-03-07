#coding=utf-8
import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'	
	SQLALCHEMY_TRACK_MODIFICATIONS = True	
	
	MAIL_SERVER = 'smtp.126.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'xautxuqiang'
	MAIL_PASSWORD = '********'

	MAIL_SUBJECT_PREFIX = u'Minion博客园'
	MAIL_SENDER = 'xautxuqiang@126.com'
	ADMIN = 'xautxuqiang@126.com'

	POSTS_PER_PAGE = 12
	FOLLOWERS_PER_PAGE = 20
	COMMENTS_PER_PAGE = 10

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
	TESTING = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,

'default': DevelopmentConfig,

}
