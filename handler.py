#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from django.utils import simplejson
import re, datetime, logging


class MainHandler(webapp.RequestHandler):

  content_type = 'text/plain'

  def getHatena(self, id):
    _tmp = "http://www.st-hatena.com/users/%s/%s/profile.gif" % (id[0:2], id)
    result = urlfetch.fetch(_tmp)
    logging.debug(int(result.headers.get('Content-Length')))
    if int(result.headers.get('Content-Length')) != 563: #allways return default image
      self.content_type = 'image/gif'
      return result.content
    return None

  def getTwitter(self, id):
    #status/show not work.
    _tmp = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=%s" % id
    result = urlfetch.fetch(_tmp)
    if result.status_code == 200:
      dect = simplejson.loads(result.content)
      _url = dect[0]['user']['profile_image_url']
      image = urlfetch.fetch(_url)
      if image.status_code == 200:
        if re.search('\.png$', _url):
          self.content_type = 'image/png'
        elif re.search('\.gif$', _url):
          self.content_type = 'image/gif'
        else:
          self.content_type = 'image/jpg'
        return image.content

    return None

  def get(self, type, id):
    ret = None
    if type == 't':
      ret = self.getTwitter(id)
    elif type == 'h':
      ret = self.getHatena(id)
    else:
      ret = self.getTwitter(id)
      if ret is None:
        ret = self.getHatena(id)

    if ret is not None:
      self.response.headers['Content-Type'] = self.content_type
      self.response.headers['Cache-Control']='public, max-age=259200' # 60 * 60 * 24 * 3
      self.response.headers['Expires'] = (datetime.datetime.today() + datetime.timedelta(3)).strftime("%a, %d %b %Y %H:%M:%S GMT")
      self.response.out.write(ret)
    else:
      self.redirect('/img/noimage.gif')

def main():
  application = webapp.WSGIApplication([('/(i|t|h)/(.+)', MainHandler)],
                                       debug=False)
  #logging.getLogger().setLevel(logging.DEBUG)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
