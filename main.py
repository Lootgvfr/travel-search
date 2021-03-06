import tornado.ioloop
import tornado.web
import mongoengine

from settings import *
from url import urls


def main():
    mongoengine.connect(mongo_db_name)

    app = tornado.web.Application(urls, **settings)
    app.listen(port, address='0.0.0.0')
    print('Server running on port ' + str(port))
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
