<br>

![tumblbug](https://media.vlpt.us/images/banana/post/0caa823e-22fc-4495-a841-6563b0980ed2/image.png)

## 프로젝트 소개

모든 사람의 창조적인 시도를 위한 크라우드펀딩 플랫폼 텀블벅(tumblbug) 웹사이트를 모티브로 한 팀프로젝트입니다.

<br>

## 텀블벅 기업 소개

크라우드펀딩 플랫폼 텀블벅은 1,000개가 넘는 국내 최다의 성공 사례와 누적 후원금 1,000억원, 일일 최다 활성 프로젝트 700개를 돌파하며 미술, 음악, 패션, 출판, 영화, 디자인, 만화, 게임 등 다양한 영역에서 국내외 창조적인 시도가 성공할 수 있는 탄탄한 기반을 만들고 있습니다.

<br>

![](https://user-images.githubusercontent.com/73244322/115367855-83830180-a201-11eb-9558-32ac3bde17b9.png)

# tumbluv

### 개발기간

**2021.03.02 ~ 2021.03.12(11일)**

<br>

## 팀원 소개

### Front-end

김종진(PM), 박지연

### Back-end

남채린, 이지윤, 허정윤

<br>

## Stack

- Front-end : HTML / CSS / JavaScript / React / CRA / React / Router DOM / React Hook / Styled-Components / SNS Login API / RESTfulAPI

- Back-end : Python / Django / bcrypt / pyjwt / RESTfulAPI / AqueryTool / MySQL / cors / AWS / Kakao Login API

- Communication tool : Notion / Slack / Trello / Git / GitHub / Zoom

<br>

## Back-end 구현 목록

### 모델링

- ERD(관계형 모델링 설계) 및 model 생성 / Aquery Tool을 활용한 모델링 구현 및 models.py 생성
- DB CSV 파일 작성
- db_uploader.py 작성

<br>

### 회원가입 및 로그인 (SignUp & SignIn)

- Django 내장 모듈을 사용하여 회원가입 시 이메일로 인증번호 전송
- bcrypt를 사용한 암호화
- 자체 로그인 기능 구현 및 unit test 
- jwt access token 전송 및 유효성 검사 기능 구현
- 카카오 소셜 로그인 구현 및 unit test
- 비회원, 회원 decorator 기능 구현 

<br>

### 프로젝트

- 프로젝트 리스트 기능 구현 / Django ORM을 활용한 다양한 filtering 구현 및 unit test
- 프로젝트 상세 페이지
- 프로젝트 올리기 페이지 / S3를 이용한 파일 업로드 기능 구현

<br>

## 프로젝트 결과 시연 영상

[시연 영상 유튜브 링크](https://youtu.be/VYgUzXvCOcM)
