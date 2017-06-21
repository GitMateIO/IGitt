from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken

def test_tokens():
    oauth_token = GitLabOAuthToken('test')
    assert oauth_token.parameter == {'access_token': 'test'}
    assert oauth_token.value == 'test'
    private_token = GitLabPrivateToken('test')
    assert private_token.parameter == {'private_token': 'test'}
    assert private_token.value == 'test'
