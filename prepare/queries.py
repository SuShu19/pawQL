search_100_nodes = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(first:100%s){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
          nodes{
            author{login}
            body
            createdAt
            url
          }
          totalCount
        }
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
          totalCount
        }
      }
    }
  }
}
"""


search_one_node = """
{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(number:%s){
      author{login}
      number
      url
      createdAt
      title
      body
      comments(first:100){
        pageInfo{
          hasNextPage
        }
        edges{
          cursor
        }
        nodes{
          author{login}
          body
          createdAt
          url
        }
        totalCount
      }
    }
  }
}
"""

sear_morethan_100_comments = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(number:%s){
      author{login}
      number
      url
      createdAt
      title
      body
      comments(first:100%s){
        pageInfo{
          hasNextPage
        }
        edges{
          cursor
        }
        nodes{
          author{login}
          body
          createdAt
          url
        }
        totalCount
      }
    }
  }
}
"""

sear_morethan_100_timelineItems = """{
  repository(owner: "%s", name: "%s") {
    owner{
        login
      }
    name
    %s(number:%s){
        author{login}
        number
        url
        createdAt
        title
        body
        timelineItems(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
          totalCount
          nodes{
          ... on CrossReferencedEvent{
            actor{
              login 
            }
            createdAt 
            id 
            isCrossRepository 
            referencedAt 
            resourcePath 
            source {
              ... on Issue{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
              }
              ... on PullRequest{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
                id 
              }
            }
            target {
              ... on Issue{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
              }
              ... on PullRequest{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
                id 
              }
            }
            url 
            willCloseTarget 
          }
        }
      }
    }
  }
}
"""

search_candidate_repos = """
{ 
  search(first:100,query:"stars:10000..%s",type:REPOSITORY){
    nodes{
      ... on Repository{
        owner{login}
        name
        description
        forkCount
        stargazerCount
        languages(first:20){
          totalCount
          nodes{
            name
          }
        }
        issues{
          totalCount
        }
        pullRequests{
          totalCount
        }
      }
    }
  }
}
"""