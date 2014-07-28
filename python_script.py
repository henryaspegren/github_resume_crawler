import requests
import json
import csv
import os

class User ():
  def __init__ (self, name, username, project, commits,
    company, location, email, blog):

    self.company = ' '
    self.location = ' '
    self.email = ' '
    self.blog = ' '

    # CSV module only takes ASCII, no unicode
    if company is not None:
      self.company = company.encode('ascii', 'ignore')
    if location is not None:
      self.location = location.encode('ascii', 'ignore')
    if email is not None:
      self.email = email.encode('ascii', 'ignore')
    if blog is not None:
      self.blog = blog.encode('ascii', 'ignore')

    # Gauranteed to be != None
    self.name = name.encode('ascii', 'ignore')

    self.project = project
    self.commits = commits
    self.username = username

  def __str__ (self):
    return self.name

  def to_csv (self):
    return [self.name, self.company, self.location, self.email, self.username,
     self.project, self.commits, self.blog]


def get_contributors(owner, repository):
  request = requests.get("https://api.github.com/repos/"+owner
    +"/"+repository+"/stats/contributors", auth=(os.environ.get('GIT_USERNAME'),
     os.environ.get('GIT_PASSWORD')))
  data = json.loads(request.text)
  contributors = []
  print "API request remaining: "+request.headers.get('x-ratelimit-remaining')
  if request.status_code != 200:
    raise StandardError("Github API rejected request: "+data['message'])
  for contributor in data:
    login = contributor['author']['login']
    commits = contributor['total']
    contributors.append((login, commits))
  contributors.sort(key= lambda x: x[1], reverse=True)
  return contributors


def get_user_information(username, project, commits):
  request = requests.get("https://api.github.com/users/"+username,
    auth=(os.environ.get('GIT_USERNAME'), os.environ.get('GIT_PASSWORD')))
  print "API request remaining: "+request.headers.get('x-ratelimit-remaining')
  if request.status_code != 200:
    raise StandardError("Github API rejected request: "+data['message'])
  data = json.loads(request.text)
  if data.get('name') is not None:
    user = User(data.get('name'), username, project, commits, data.get('company'),
      data.get('location'), data.get('email'), data.get('blog'))
  else:
    user = None
  return user

def repository_crawl(owner, repository, project):
  contributors = get_contributors(owner, repository)
  user_list = []
  for (login, commits) in contributors:
    user = get_user_information(login, project, commits)
    if user is not None:
      user_list.append(user)
      print login, user, commits
  with open(project+'.csv', 'wb') as csvfile:
    userwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    userwriter.writerow(['Name', 'Current Company', 'Location', 'Email',
      'Github Username', 'Project', 'Commits', 'Blog'])
    for user in user_list:
      userwriter.writerow(user.to_csv())


# print (os.environ.get('GIT_USERNAME'), os.environ.get('GIT_PASSWORD'))
#get_contributors("angular","angular.js")
repository_crawl(owner="angular", repository="angular.js", project="Angular JS")
#repository_crawl(owner="henryaspegren", repository="wateryourtree", project="Water Your Tree")
#print get_user_information("shairez", "angular JS", 12)
