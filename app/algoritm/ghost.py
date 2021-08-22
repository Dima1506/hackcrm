import json, requests, jwt
from datetime import datetime as dt
from io import BytesIO

class GhostAdmin():
    def __init__(self, siteName):
        self.siteName = siteName
        self.site = None
        self.setSiteData()
        self.token = None
        self.headers = None
        self.createHeaders()

    def setSiteData(self):
        sites = [{'name': '85.143.173.90:3001', 'url': 'http://85.143.173.90:3001/', 'AdminAPIKey': '612226d7fcc3cb0001f95afa:df56d83076d6dc6bc9f41dbff895fed5e8ed8ad543ab4408c306b3e2d58994cb', 'ContentAPIKey': '0fa80f54bf44ec7224c32db295'},\
       {'name': '85.143.173.90:3001', 'url': 'http://85.143.173.90:3001/', 'AdminAPIKey': '612226d7fcc3cb0001f95afa:df56d83076d6dc6bc9f41dbff895fed5e8ed8ad543ab4408c306b3e2d58994cb', 'ContentAPIKey': '0fa80f54bf44ec7224c32db295'}] 
        self.site = next((site for site in sites if site['name'] == self.siteName), None)


        return None

    def createToken(self):
        key = self.site['AdminAPIKey']
        id, secret = key.split(':')
        iat = int(dt.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
        payload = {'iat': iat, 'exp': iat + (5 * 60), 'aud': '/v3/admin/'}
        self.token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

        return self.token

    def createHeaders(self):
        if self.site != None:
            self.createToken()
            self.headers = {'Authorization': 'Ghost {}'.format(self.token)}

        return self.headers
        
    def getPostById(self, id):
        url = self.site['url'] + 'ghost/api/v3/admin/posts/' + id + '/'
        params = {'formats':'html,mobiledoc'}
        result = requests.get(url, params=params, headers=self.headers)
        if result.ok: post = json.loads(result.text)['posts'][0]    # post = dict with keys: slug,id,uuid,title etc.
        else: post = json.loads(result.text)                        # post = dict with key 'errors'

        return post


    def getAllPosts(self):
        url = self.site['url'] + 'ghost/api/v3/admin/posts/'
        params = {'formats': 'html,mobiledoc', 'limit': 'all', 'filter': 'slug: -tags'}
        result = requests.get(url,  params=params, headers=self.headers)
        posts = json.loads(result.text)['posts']

        return posts

    def getPostByTitle(self,title):
        allPosts = self.getAllPosts()
        posts = []
        for i in allPosts:
            if i['title'] == title:
                posts.append(i)

        return posts

    def deletePostById(self, id):
        url = self.site['url'] + 'ghost/api/v3/admin/posts/' + id + '/'
        result = requests.delete(url, headers=self.headers)
        if result.ok: result = 'success: post deleted (status_code:' + str(result.status_code) + ')'
        else: result = 'error: post NOT deleted (status_code:' + str(result.status_code) + ')'

        return result

    def loadImage(self, imagePathAndName):
        image = open(imagePathAndName, 'rb')
        imageObject = image.read()
        image.close()
        image = BytesIO(imageObject)

        return image

    def imageUpload(self, imageName, imageObject):
        url = self.site['url'] + 'ghost/api/v3/admin/images/upload/'
        files = {"file": (imageName, imageObject, 'image/jpeg')}
        params = {'purpose': 'image', 'ref': imageName}   # 'image', 'profile_image', 'icon'
        result = requests.post(url, files=files, params=params, headers=self.headers)
        if result.ok: result = 'success: '+json.loads(result.text)['images'][0]['url']
        else: result = 'error: upload failed (' + str(result.status_code) + ')'

        return result

    def createPost(self, title, body, bodyFormat='html', excerpt = None, tags=None, authors=None, status='draft', featured=False, featureImage=None, slug=None):
        """
        Args:
            body (string): the content of a post
            bodyFormat (string): 'html','markdown'
            excerpt (string): the excerpt for a post
            tags (list): a list of dictionaries e.g. [{'name':'my new tag', 'description': 'a very new tag'}]
            authors (list): a list of dictionaries e.g. [{'name':'Jacques Bopp', 'slug': 'jacques'}]
            status (string): 'published' or 'draft'
            featured (bool): if the post should be featured
            featureImage (string): the image url (e.g. "content/images/2020/09/featureImage1.jpg" -> see uploadImage()

        Returns:
            result (string): if the creation was successful or not
        """
        content = {'title': title}
        if bodyFormat == 'markdown': content['mobiledoc'] = json.dumps({ 'version': '0.3.1', 'markups': [], 'atoms': [], 'cards': [['markdown', {'cardName': 'markdown', 'markdown': body}]], 'sections': [[10, 0]]});
        else: content['html'] = body
        if excerpt != None: content['custom_excerpt'] = excerpt
        if tags != None: content['tags'] = tags
        if authors != None: content['authors'] = authors
        content['status'] = status
        content['featured'] = featured
        if featureImage != None: content['feature_image'] = self.site['url']+featureImage
        if slug != None: content['slug'] = slug

        url = self.site['url']+'ghost/api/v3/admin/posts/'
        params = {'source': 'html'}
        result = requests.post(url, params=params, json={"posts": [content]}, headers=self.headers)
        if result.ok: result = 'success: post created (status_code:'+str(result.status_code)+')'
        else: result = 'error: post not created (status_code:'+str(result.status_code)+')'

        return result


def ghost(text, name = 'Dmitry'):
    ga = GhostAdmin('85.143.173.90:3001')
    title = 'Мой пост о ИИ'
    body = '<div>'+text+'</div>'
    excerpt = text[0:15]+'...'
    tags = [{'name':'ИИ', 'description': 'Искуственный интелект'}]
    featureImage = 'https://avatars.mds.yandex.net/get-zen_doc/4387099/pub_6097aedca38d215d4eb251ab_6097aee1c235fb60b6da1ac5/scale_1200'
    authors = [{'name':name, 'slug': 'jacques'}]
    result = ga.createPost(title, body, bodyFormat='html', excerpt=excerpt, tags=tags, authors=auth
