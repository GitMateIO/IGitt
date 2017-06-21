from IGitt.GitHub import GitHubToken

def test_tokens():
    github_token = GitHubToken('test')
    assert github_token.parameter == {'access_token': 'test'}
    assert github_token.value == 'test'
