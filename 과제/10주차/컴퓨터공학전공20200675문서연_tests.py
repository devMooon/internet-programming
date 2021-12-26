from bs4 import BeautifulSoup
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Post, Category, Tag


# <6. 테스트 주도 개발>
# pip install beautifulsoup4 로 beautifulsoup4 설치하고 사용

# 1. python manage.py test 테스트 하는 명령어
# 2. blog/test.py에 TestCase를 상속받고 이름이 'Test'로 시ㅔㅛ작하는 클래스를 정의 (TestView)
# 2. TestView에 'test'로 시작하는 함수를 정의 (test_post_list, test_post_detail)


class TestView(TestCase):
    # 테스트를 실행하기 전에 공통적으로 수행할 어떤 작업의 내용을 넣어줌
    def setUp(self):
        self.client = Client()  # Client 클래스를 통해 실제 경로의 view와 매치해서 테스트를 진행
        self.user_james = User.objects.create_user(username='James', password='somepassword')
        self.user_trump = User.objects.create_user(username='Trump', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_culture = Category.objects.create(name='culture', slug='culture')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        # 3.1. 포스트(게시물)가 3개 존재하는 경우엔
        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Hello world. We are the world',
            author=self.user_james,
            category=self.category_programming,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.',
            content='1등이 전부가 아니잖아요',
            author=self.user_trump,
            category=self.category_culture,
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.',
            content='세번째 포스트 입니다.',
            author=self.user_trump,
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)

    def navbar_test(self, soup):
        # 1.4. 네비게이션 바가 있다.
        navbar = soup.nav
        # 1.5. 네비게이션바에 Blog, About Me 라는 문구가 있다.
        self.assertIn('Blog', navbar.text)  # 네비게이션 바의 내용과 같은 것이 아니고 부분적으로 들어있으니 assertIn
        self.assertIn('About Me', navbar.text)

        logo = navbar.find('a', text='Internet Programming')
        self.assertEqual(logo.attrs['href'], '/')
        logo = navbar.find('a', text='Home')
        self.assertEqual(logo.attrs['href'], '/')
        logo = navbar.find('a', text='Blog')
        self.assertEqual(logo.attrs['href'], '/blog/')
        logo = navbar.find('a', text='About Me')
        self.assertEqual(logo.attrs['href'], '/about_me/')

    def category_test(self, soup):
        category = soup.find('div', id='categories-card')
        self.assertIn('Categories', category.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', category.text)
        self.assertIn(f'{self.category_culture.name} ({self.category_culture.post_set.count()})', category.text)
        self.assertIn(f'미분류 (1)', category.text)

    def test_category_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리 name을 포함하고 있는지
        self.assertIn(self.category_programming.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리 name을 포함하고 있는지
        self.assertIn(self.tag_hello.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 1.1. 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='Trump', password='somepassword')
        response = self.client.get('/blog/create_post/')  # 목록페이지에 대해 요청된 결과가 들어있음. 정상 작동이면 200 반환
        # 1.2. 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)  # http에서 응답받는 값과 코드.

        # 1.3. 페이지 타이틀이 'Blog'이다.
        soup = BeautifulSoup(response.content, 'html.parser')  # BeautifulSoup는 페이지 분석을 하는 라이브러리고, 그 일을 수행하는 것은 parser
        self.assertEqual(soup.title.text, 'Create Post - Blog')
        main_area = soup.find('div', id="main-area")
        self.assertIn('Create new Post', main_area.text)

        self.client.post('/blog/create_post/',
                         {
                             'title': "Post form 만들기",
                             'content': "Post form 페이지 만들기",
                         })
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post form 만들기")
        self.assertEqual(last_post.author.username, 'Trump')

    # 포스트 목록 페이지 테스트 코드
    def test_post_list(self):
        # 1.1. 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/')  # 목록페이지에 대해 요청된 결과가 들어있음. 정상 작동이면 200 반환
        # 1.2. 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)  # http에서 응답받는 값과 코드.
        # 1.3. 페이지 타이틀이 'Blog'이다.
        soup = BeautifulSoup(response.content, 'html.parser')  # BeautifulSoup는 페이지 분석을 하는 라이브러리고, 그 일을 수행하는 것은 parser
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)
        self.category_test(soup)

        # 3.3. main-area에 포스트 3개의 제목이 존재한다.
        main_area = soup.find('div', id="main-area")
        # 3.4. '아직 게시물이 없습니다.'라는 문구는 더이상 나타나지 않는다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_james.username.upper(), main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)

        # 포스트에 게시물이 하나도 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        # 1.1. 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/')  # 목록페이지에 대해 요청된 결과가 들어있음. 정상 작동이면 200 반환
        # 1.2. 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)  # http에서 응답받는 값과 코드.
        # 1.3. 페이지 타이틀이 'Blog'이다.
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2. main area에 "아직 게시물이 없습니다."라는 문구가 나타난다.
        main_area = soup.find('div', id="main-area")  # find는 태그를 찾는 함수
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    # 포스트 목록 페이지 테스트 코드
    def test_post_detail(self):
        # 1.1. Post가 하나 있다.
        post_000 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Hello world. We are the world',
            author=self.user_james,
            category=self.category_culture,
        )
        # 1.2. 그 포스트의 url은 '/blog/1'dlek.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2 첫 번째 포스트의 상세 페이지 테스트
        # 2.1. 첫 번째 post url로 접근하면 정상적으로 작동한다. (status_code = 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_test(soup)

        # 2.3. 첫 번째 포스트의 제목(title)이 웹브라우저 탭 title에 들어있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 첫 번째 포스트의 제목(title)이 포스트 영역(post_area)에 있다.
        main_area = soup.find('div', id="main-area")
        post_area = main_area.find('div', id="post-area")
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        # 2.5. 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        # 아직 작성 불가
        self.assertIn(self.user_james.username.upper(), post_area.text)
        # 2.6. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)
