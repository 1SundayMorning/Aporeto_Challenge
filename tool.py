import requests
from requests.auth import HTTPBasicAuth
import time
import getpass
import threading
from threading import Thread
import datetime

#Global vars
url = 'https://api.github.com/'
final_array = [0]*365
final_array_lock = threading.Lock()
global_now = datetime.datetime.now()

#function takes user credentials
#returns list of names of user repos
def getUserRepos(kwargs):
    global url
    x = 1
    repo_list = []
    auth=HTTPBasicAuth(kwargs['username'], kwargs['password'])
    while True:
        curr_url = ''
        page = '?page=' + str(x)
        curr_url = url + 'users/' + kwargs['username'] + '/repos' + page
        r = requests.get(curr_url , auth=auth).json()
        if(len(r) == 0):
            break
        else:
            x += 1
        for i in range(0, len(r)):
            repo_list.append(r[i]['name'])
    return repo_list

#Function takes name of repo and user credentials
#Updates global data struct with number of user issues opened per day
def getRepoIssues(repo, kwargs):
    global global_now
    x=1
    auth=HTTPBasicAuth(kwargs['username'], kwargs['password'])
    while True:
        curr_url = ''
        page = '?page=' + str(x)
        curr_url = url+'repos/'+kwargs['username']+'/'+repo+'/issues'+page
        issues = requests.get(curr_url, auth=auth).json()
        if(len(issues) == 0):
            break
        else:
            x += 1
        for i in range(0, len(issues)):
            try:
                print(issues[i]['pull_request'])
            except KeyError:
                issue_timestamp = datetime.datetime.strptime(unicode(issues[i]['created_at']), "%Y-%m-%dT%H:%M:%SZ")
                with final_array_lock:
                    day = (global_now - issue_timestamp).days
                    if(day == -1):
                        day = 0
                    final_array[364 - day] += 1

#Function takes name of repo and user credentials
#Updates global data struct with number of user commits made by day
def getRepoCommits(repo, kwargs):
    global global_now
    x=1
    auth=HTTPBasicAuth(kwargs['username'], kwargs['password'])
    while True:
        curr_url = ''
        page = '?page=' + str(x)
        curr_url = url+'repos/'+kwargs['username']+'/'+repo+'/commits'+page
        commits = requests.get(curr_url, auth=auth).json()
        if(len(commits) == 0):
            break
        else:
            x += 1
        for i in range(0, len(commits)):
            if (commits[i]['committer']['login'] == kwargs['username']):
                commit_timestamp = datetime.datetime.strptime(
                                    unicode(commits[i]['commit']['committer']['date']),
                                        "%Y-%m-%dT%H:%M:%SZ")
                with final_array_lock:
                    day = (global_now - commit_timestamp).days
                    if(day == -1):
                        day = 0
                    final_array[364-day] += 1

#Function takes name of repo and user credentials
#Updates global data struct with number of user pulls made by day
def getRepoPulls(repo, kwargs):
    global global_now
    x=1
    auth=HTTPBasicAuth(kwargs['username'], kwargs['password'])
    while True:
        curr_url = ''
        page = '?page=' + str(x)
        curr_url = url+'repos/'+kwargs['username']+'/'+repo+'/pulls'+page
        pulls = requests.get(curr_url, auth=auth).json()
        if (len(pulls) == 0):
            break
        else:
            x += 1
        for i in range(0, len(pulls)):
            if (pulls[i]['user']['login'] == kwargs['username']):
                pull_timestamp = datetime.datetime.strptime(
                                    unicode(pulls[i]['created_at']), "%Y-%m-%dT%H:%M:%SZ")
                with final_array_lock:
                    day = (global_now - pull_timestamp).days
                    if(day == -1):
                        day = 0
                    final_array[364-day] += 1


#SIGN IN TO GET AUTH
print("please sign in to authenticate")
username = raw_input("username: ")
password = getpass.getpass("password: ")
creds = {'username':username, 'password':password}


#Get list of user repos
repos = getUserRepos(creds)
for repo in repos:
    issues_thread = Thread(target = getRepoIssues, args = (repo, creds, ))
    issues_thread.start()
    commits_thread = Thread(target = getRepoCommits, args = (repo, creds, ))
    commits_thread.start()
    pulls_thread = Thread(target = getRepoPulls, args = (repo, creds, ))
    pulls_thread.start()
    issues_thread.join()
    commits_thread.join()
    pulls_thread.join()

print(final_array)
